import abc
import dataclasses
import itertools
import json
import logging
import os
import typing

from bloodytools.utils.simulation_objects import Simulation_Group
from bloodytools.utils.utils import create_base_json_dict
from bloodytools.utils.config import Config
from bloodytools.utils.data_type import DataType
from simc_support.game_data.WowSpec import WowSpec

logger = logging.getLogger(__name__)


class UnknownFightStyleError(Exception):
    pass


@dataclasses.dataclass
class Simulator(abc.ABC):
    """Abstract baseclass for chart related simulations.
    Children will usually be used by invoking the run() method.

    Required to implement:
        - add_simulation_data

    Extendable:
        - post_processing
    """

    name: str
    snake_case_name: str
    wow_spec: WowSpec
    fight_style: str
    settings: Config

    def run(self) -> None:
        """Manages the simulation flow. You can adjust by overwriting the provided methods."""
        logger.debug(f"Start pipeline for {self.name} of {self.wow_spec}")
        data_dict = create_base_json_dict(
            self.name, self.wow_spec, self.fight_style, self.settings
        )

        logger.debug("Starting pre processing")
        data_dict = self.pre_processing(data_dict)

        simulation_group = Simulation_Group(
            name="simulation_group",
            threads=self.settings.threads,
            profileset_work_threads=self.settings.profileset_work_threads,
            executable=self.settings.executable,
            remove_files=not self.settings.keep_files,
        )
        self.add_simulation_data(
            simulation_group, data_dict["profile"], data_dict.get("covenant_profiles")
        )

        self._simulate(simulation_group)

        data_dict["data"] = self._collect_data(
            simulation_group, self.settings.data_type
        )

        logger.debug("Starting post processing")
        data_dict = self.post_processing(data_dict)

        self._write(data_dict)

    def _simulate(self, simulation_group: Simulation_Group) -> None:
        if self.settings.use_raidbots and self.settings.apikey:
            self.settings.simc_hash = simulation_group.simulate_with_raidbots(
                self.settings.apikey
            )
        else:
            simulation_group.simulate()

    def pre_processing(self, data_dict: dict) -> dict:
        """Adjusts data_dict before simulations are done. Use this update profile information.

        Args:
            data_dict (dict): all data of the simulation, information will be used by the frontend to power charts

        Returns:
            dict: updated data_dict after pre_processing is done
        """
        logger.debug(f"data_dict {json.dumps(data_dict)}")
        return data_dict

    @abc.abstractmethod
    def add_simulation_data(
        self,
        simulation_group: Simulation_Group,
        profile: dict,
        additional_profiles: typing.Optional[dict] = None,
    ) -> None:
        """Add SimulationData instances to simulation_group

        Args:
            simulation_group (Simulation_Group): Empty Simulation_Group instance
        """
        pass

    def _collect_data(
        self, simulation_group: Simulation_Group, data_type: DataType
    ) -> dict:
        """Extract information from a simulated simulation_group and creates the "data" part of the result dictionary/json.

        This function expects the following structure in profile names:
            - <Primary Name>[_<nested key 1>[_<nested key2>[...]]]

        Primary Name will be used 'as is' in the resulting data dict.

        E.g. the name "Trinket of Doom_Dwarf_300" will create the following data entry:
            "Trinket of Doom": {
                "Dwarf": {
                    "300": <VALUE>
                }
            }

        Args:
            simulation_group (Simulation_Group): an already simulated Simulation_Group instance
            data_type (DataType): declares what data should be extracted, e.g. DPS

        Returns:
            dict: dictionary with simulated data
        """
        data = {}
        for profile in simulation_group.profiles:
            wanted_value = -1
            if data_type == DataType.DPS:
                wanted_value = profile.get_dps()
            logger.debug(f"Profile '{profile.name}' {data_type.value}: {wanted_value}")

            name_parts = profile.name.split("_")
            name = name_parts[0]
            try:
                nested_keys = name_parts[1:]
            except KeyError:
                nested_keys = []

            if name not in data:
                data[name] = {}

            # create keys if necessary
            local_dict = data[name]
            for key in nested_keys[:-1]:
                if key not in local_dict:
                    local_dict[key] = {}
                local_dict = local_dict[key]

            # set value of the last valid key
            last_key = name
            if nested_keys:
                last_key = nested_keys[-1]
            last_dict = data
            if nested_keys:
                last_dict = last_dict[name]
                for key in nested_keys[:-1]:
                    last_dict = last_dict[key]
            last_dict[last_key] = wanted_value

            logger.debug(
                "Added '{}' with {} dps to dictionary.".format(
                    profile.name, profile.get_dps()
                )
            )

        logger.debug(f"data dictionary: {json.dumps(data, ensure_ascii=False)}")
        return data

    def post_processing(self, data_dict: dict) -> dict:
        """Enriches data_dict after simulations are done. Use this to add information like data["translations"].

        Args:
            data_dict (dict): all data of the simulation, information will be used by the frontend to power charts

        Returns:
            dict: enriched data_dict after post_processing is done
        """
        logger.debug(f"data_dict {json.dumps(data_dict)}")
        return data_dict

    def _write(self, data_dict: dict) -> None:
        """Write data_dict to disk.

        Args:
            data_dict (dict): [description]
        """
        path = os.path.join("results", self.snake_case_name)
        if not os.path.isdir(path):
            os.makedirs(path)

        file_name = f"{self.wow_spec.wow_class.simc_name}_{self.wow_spec.simc_name}_{self.fight_style.lower()}.json"
        full_path = os.path.join(path, file_name)
        logger.debug(f"Writing data to {full_path}")
        # write json to file
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    data_dict,
                    sort_keys=True,
                    indent=4 if self.settings.pretty else None,
                    ensure_ascii=False,
                )
            )


class SimulatorFactory:
    def __init__(self) -> None:
        self._simulators: typing.Dict[str, typing.Type[Simulator]] = {}

    def register_simulator(self, simulation_type: str, klass: typing.Type[Simulator]):
        self._simulators[simulation_type] = klass

    def get_simulator(
        self,
        simulation_type: str,
    ) -> typing.Type[Simulator]:
        """Get an appropriate Simulator class for the provided simulation_type."""

        return self._simulators[simulation_type]


def simulator_wrapper(
    simulation_type: str,
    simulator_factory: SimulatorFactory,
    settings: Config,
):
    """Iterate over all WowSpecs and FightStyles in settings and run their
    appropriate Simulator flow.

    Args:
        name (str): [description]
        simulation_type (str): [description]
        simulator_factory (SimulatorFactory): [description]
        settings (Config): [description]
    """
    for wow_spec, fight_style in itertools.product(
        settings.wow_class_spec_list, settings.fight_styles
    ):
        simulator = simulator_factory.get_simulator(simulation_type)
        simulator(
            wow_spec=wow_spec,
            fight_style=fight_style,
            settings=settings,
        ).run()

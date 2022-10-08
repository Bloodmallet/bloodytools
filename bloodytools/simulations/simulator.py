import abc
import dataclasses
import json
import logging
import os
import typing

from bloodytools.utils.config import Config
from bloodytools.utils.data_type import DataType
from bloodytools.utils.simulation_objects import Simulation_Group
from bloodytools.utils.utils import create_base_json_dict
from simc_support.game_data.WowSpec import WowSpec

logger = logging.getLogger(__name__)


class UnknownFightStyleError(Exception):
    pass


@dataclasses.dataclass  # type: ignore # known mypy issue (abstract class + dataclass)
class Simulator(abc.ABC):
    """Abstract baseclass for chart related simulations.
    Children will usually be used by invoking the run() method.

    Required class methods to implement:
        - name

    Required methods to implement:
        - add_simulation_data

    Extendable:
        - pre_processing
        - post_processing
    """

    wow_spec: WowSpec
    fight_style: str
    settings: Config

    @classmethod
    @abc.abstractmethod
    def name(cls) -> str:
        """Upper case human readable name.

        Returns:
            str: name of the simulation done by this simulator
        """
        ...

    @classmethod
    def snake_case_name(cls) -> str:
        """CLI terminonology

        Returns:
            str: cli name of the simulation done by this simulator
        """
        return str(cls.name()).lower().replace(" ", "_")

    def run(self) -> None:
        """Manages the simulation flow. You can adjust by overwriting the provided methods."""
        logger.debug(f"Start pipeline for {self.name()} of {self.wow_spec}")
        data_dict = create_base_json_dict(
            self.name(), self.wow_spec, self.fight_style, self.settings
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
            simulation_group,
            data_dict,
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
        """Adjusts data_dict before simulations are done. Use this to update profile information.

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
        data_dict: dict,
    ) -> None:
        """Add SimulationData instances to simulation_group

        Args:
            simulation_group (Simulation_Group): Empty Simulation_Group instance
        """
        pass

    def profile_split_character(self) -> str:
        return "/"

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
        data: typing.Dict[str, typing.Any] = {}
        for profile in simulation_group.profiles:
            wanted_value = -1
            if data_type == DataType.DPS:
                wanted_value = profile.get_dps()
            logger.debug(f"Profile '{profile.name}' {data_type.value}: {wanted_value}")

            name_parts = profile.name.split(self.profile_split_character())
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
            last_dict.update({last_key: wanted_value})

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
        path = os.path.join("results", self.snake_case_name())
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

    def create_sorted_key_value_data(
        self,
        data_dict: dict,
        result_key: str = "sorted_data_keys",
        ignore_key: str = "",
    ) -> dict:
        """Sort data if it's organized as direct key-value pairs. E.g.
        {
            "data": {
                "key a": 200,
                "key b": 300
            }
        }

        Args:
            data_dict (dict): [description]
            result_key (str, optional): name of the key added to data_dict. Defaults to "sorted_data_keys"
            ignore_key (str, optional): entry of data_dict["data"] to be ignored when creating sorted key value data. Defaults to "", thus nothing being filtered

        Returns:
            dict: initial dictionary but with the added key <result_key> containing the sorting result
        """
        # create ordered data name list
        tmp_list: typing.List[str] = [
            name for name in data_dict["data"].keys() if name != ignore_key
        ]
        logger.debug("tmp_list: {}".format(tmp_list))

        def get_value(data: dict, key: str) -> int:
            """This function exists to make mypy happy."""
            value: int = data[key]
            return value

        sorted_list = sorted(
            tmp_list,
            key=lambda name: get_value(data_dict["data"], name),
            reverse=True,
        )
        logger.debug("Sorted tmp_list: {}".format(sorted_list))
        winner = sorted_list[0]
        logger.info("'{}' won with {} dps.".format(winner, data_dict["data"][winner]))

        data_dict[result_key] = sorted_list

        return data_dict

    def create_sorted_key_key_value_data(
        self,
        data_dict: dict,
        result_key: str = "sorted_data_keys",
        ignore_key: str = "",
        ignore_keys: typing.Optional[typing.List[str]] = None,
    ) -> dict:
        """Sort data if it's organized as key-key-value pairs. E.g.
        {
            "data": {
                "key a": {
                    "key a a": 200,
                    "key a b": 220
                },
                "key b": {
                    "key b a": 300,
                    "key b a": 320
                }
            }
        }

        Args:
            data_dict (dict): [description]
            result_key (str, optional): name of the key added to data_dict. Defaults to "sorted_data_keys"
            ignore_key (str, optional): entry of data_dict["data"] to be ignored when creating sorted key value data. Defaults to "", thus nothing being filtered

        Returns:
            dict: initial dictionary but with the added key <result_key> containing the sorting result
        """
        # create ordered trinket name list
        tmp_list = [name for name in data_dict["data"].keys() if name != ignore_key]
        if ignore_keys:
            tmp_list = [name for name in tmp_list if name not in ignore_keys]
        logger.debug("tmp_list: {}".format(tmp_list))

        def get_max_value(data: dict, key: str) -> int:
            """This function exists to make mypy happy."""
            values: typing.List[int] = list(data[key].values())
            return max(values)

        sorted_list = sorted(
            tmp_list,
            key=lambda name: get_max_value(data_dict["data"], name),
            # key=lambda name: max(data_dict["data"][name].values()),
            reverse=True,
        )
        logger.debug("Sorted tmp_list: {}".format(tmp_list))
        winner = sorted_list[0]
        logger.info("'{}' won with {} dps.".format(winner, data_dict["data"][winner]))

        data_dict[result_key] = sorted_list

        return data_dict

    def get_profile_name(self, group_name: str, profile_name: str) -> str:
        """Get the appropriate name of a key-key-value profile structure.

        Args:
            group_name (str): e.g. "Category A"
            profile_name (str): e.g. "Trinket 1"

        Raises:
            ValueError: Raised if the Simulator specific profile_split_character is contained in group_name and profile_name.

        Returns:
            str: an appropriate combination of group_name and profile_name
        """
        if self.profile_split_character() in group_name + profile_name:
            raise ValueError(
                f"Character '{self.profile_split_character()}' is the split character. It's not allowed in group and profile names. Override it."
            )
        return self.profile_split_character().join([group_name, profile_name])


class SimulatorFactory:
    """Factory to make Simulators available by snake_case_names()."""

    def __init__(self) -> None:
        self._simulators: typing.Dict[str, typing.Type[Simulator]] = {}

    def register_simulator(self, klass: typing.Type[Simulator]):
        """Register an implemented Simulator.

        Args:
            klass (typing.Type[Simulator]): [description]
        """
        # str call makes mypy happy
        self._simulators[str(klass.snake_case_name())] = klass

    def get_simulator(
        self,
        simulator_name: str,
    ) -> typing.Type[Simulator]:
        """Get an appropriate Simulator class for the provided simulator_name (snake_case_name())."""

        try:
            simulator = self._simulators[simulator_name]
        except KeyError:
            names = [s.snake_case_name() for s in self.list_simulators()]
            raise KeyError(
                f"No Simulator found matching '{simulator_name}'. Available options: {names}"
            )

        return simulator

    def list_simulators(self) -> typing.List[typing.Type[Simulator]]:
        """List available Simulators.

        Returns:
            typing.List[typing.Type[Simulator]]: [description]
        """
        return list(self._simulators.values())

"""
external_buffs.power_infusion="0,108,216,324"
external_buffs.pool=power_infusion:120:1
"""

import enum
import logging
import typing

from bloodytools.utils.simulation_objects import Simulation_Data, Simulation_Group
from bloodytools.simulations.simulator import Simulator
from bloodytools.utils.utils import create_base_json_dict, get_profile
from simc_support.game_data.WowSpec import WOWSPECS


logger = logging.getLogger(__name__)


class PowerInfusionEnum(enum.Enum):
    PI = "power infusion"
    NO_PI = "no power infusion"


PI_OPTIONS = {
    PowerInfusionEnum.PI.value: ["external_buffs.pool=power_infusion:120:1"],
    PowerInfusionEnum.NO_PI.value: ["external_buffs.pool=power_infusion:120:0"],
}


class MissingTalentTreePathFileError(Exception):
    pass


KeyType = typing.TypeVar("KeyType")


def _deep_update(
    mapping: typing.Dict[KeyType, typing.Any],
    *updating_mappings: typing.Dict[KeyType, typing.Any],
) -> typing.Dict[KeyType, typing.Any]:
    updated_mapping = mapping.copy()
    for updating_mapping in updating_mappings:
        for k, v in updating_mapping.items():
            if (
                k in updated_mapping
                and isinstance(updated_mapping[k], dict)
                and isinstance(v, dict)
            ):
                updated_mapping[k] = _deep_update(updated_mapping[k], v)
            else:
                updated_mapping[k] = v
    return updated_mapping


class PowerInfusionSimulator(Simulator):
    @classmethod
    def name(cls) -> str:
        return "Power Infusion"

    def add_simulation_data(
        self, simulation_group: Simulation_Group, data_dict: dict
    ) -> None:
        pass

    def pre_processing(self, data_dict: dict) -> dict:
        data_dict = super().pre_processing(data_dict)

        data_dict["title"] = " | ".join([self.name(), self.fight_style.title()])

        return data_dict

    def post_processing(self, data_dict: dict) -> dict:
        data_dict = super().post_processing(data_dict)

        data_dict = self.create_sorted_key_value_data(data_dict)

        simple_profile_names: typing.List[str] = []
        for name in data_dict["data"]:
            if name[0] != "{" and name[-1] != "}":
                simple_profile_names.append(name)

        # create new sorted_data_keys based on percentage gain
        data_key_value_pairs: typing.List[typing.Tuple[str, float]] = []
        for spec_name in simple_profile_names:
            increase = (
                data_dict["data"][spec_name] / data_dict["data"][f"{{{spec_name}}}"]
            )
            data_key_value_pairs.append((spec_name, increase))

        sorted_data_key_value_pairs = sorted(
            data_key_value_pairs, key=lambda pair: pair[1], reverse=True
        )

        data_dict["sorted_data_keys"] = [
            name for name, _ in sorted_data_key_value_pairs
        ]

        # create new sorted_data_keys_2 based on absolute gain
        data_key_value_pairs = []
        for spec_name in simple_profile_names:
            increase = (
                data_dict["data"][spec_name] - data_dict["data"][f"{{{spec_name}}}"]
            )
            data_key_value_pairs.append((spec_name, increase))

        sorted_data_key_value_pairs = sorted(
            data_key_value_pairs, key=lambda pair: pair[1], reverse=True
        )

        data_dict["sorted_data_keys_2"] = [
            name for name, _ in sorted_data_key_value_pairs
        ]

        logger.debug("talent_simulations end")
        return data_dict

    def run(self) -> None:
        """Manages the simulation flow. You can adjust by overwriting the provided methods."""
        logger.debug(f"Start pipeline for {self.name()} of {self.wow_spec}")
        data_dict = create_base_json_dict(
            self.name(), self.wow_spec, self.fight_style, self.settings
        )

        del data_dict["profile"]

        logger.debug("Starting pre processing")
        data_dict = self.pre_processing(data_dict)

        for spec in WOWSPECS:
            try:
                profile = get_profile(spec, self.fight_style, self.settings)
            except FileNotFoundError:
                logger.warning(f"Profile for {spec} was not found. Skipping.")
                continue

            simulation_group = Simulation_Group(
                name="simulation_group",
                threads=self.settings.threads,
                profileset_work_threads=self.settings.profileset_work_threads,
                executable=self.settings.executable,
                remove_files=not self.settings.keep_files,
            )

            for pi_name, pi_override in PI_OPTIONS.items():
                pi_override = pi_override.copy()

                full_spec_name = " ".join([spec.full_name, spec.wow_class.full_name])
                if pi_name == PowerInfusionEnum.NO_PI.value:
                    full_spec_name = f"{{{full_spec_name}}}"

                simulation_data = Simulation_Data(
                    name=full_spec_name,
                    fight_style=self.fight_style,
                    profile=profile,
                    simc_arguments=pi_override,
                    target_error=self.settings.target_error.get(
                        self.fight_style, "0.1"
                    ),
                    ptr=self.settings.ptr,
                    default_actions=self.settings.default_actions,
                    executable=self.settings.executable,
                    iterations=self.settings.iterations,
                    remove_files=not self.settings.keep_files,
                )

                simulation_group.add(simulation_data)

            logger.info(f"Simulating {spec}.")
            simulation_group.simulate()

            data = self._collect_data(simulation_group, self.settings.data_type)

            data_dict["data"] = _deep_update(data_dict["data"], data)

        logger.debug("Starting post processing")
        data_dict = self.post_processing(data_dict)

        self._write(data_dict)

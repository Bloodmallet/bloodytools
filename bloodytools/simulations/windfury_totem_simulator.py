import enum
import logging
import typing

from bloodytools.simulations.simulator import Simulator
from bloodytools.utils.profile_extraction import get_profile
from bloodytools.utils.simulation_objects import Simulation_Data, Simulation_Group
from bloodytools.utils.utils import create_base_json_dict
from simc_support.game_data.WowSpec import WOWSPECS, ENHANCEMENT
from simc_support.game_data.Role import Role
from simc_support.game_data.Stat import Stat


logger = logging.getLogger(__name__)

ENHANCEMENT_EXTERNAL_WINDFURY: typing.Dict[str, typing.List[str]] = {
    "castingpatchwerk": ["spec_talents+=/windfury_totem:0/stormflurry:1"],
    "castingpatchwerk3": ["spec_talents+=/windfury_totem:0/sundering:1"],
    "castingpatchwerk5": ["spec_talents+=/windfury_totem:0/sundering:1"],
}
"""List of simc arguments to properly communicate how an Enhancement profile performs if given an external Windfury Totem."""

ENHANCEMENT_OWN_WINDFURY: typing.Dict[str, typing.List[str]] = {
    "castingpatchwerk": [],
    "castingpatchwerk3": [],
    "castingpatchwerk5": [],
}
"""List of simc arguments to properly communicate how an Enhancement profile performs if they have to cast Windfury Totem on their own."""


class WindfuryEnum(enum.Enum):
    WINDFURY = "windfury"
    NO_WINDFURY = "no windfury"


WINDFURY_OPTIONS = {
    WindfuryEnum.WINDFURY.value: ["override.windfury_totem=1"],
    WindfuryEnum.NO_WINDFURY.value: ["override.windfury_totem=0"],
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


class WindfuryTotemSimulator(Simulator):
    @classmethod
    def name(cls) -> str:
        return "Windfury Totem"

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

        melee_specs = [
            spec
            for spec in WOWSPECS
            if spec.role == Role.MELEE and spec.stat != Stat.INTELLECT
        ]

        for melee_spec in melee_specs:
            try:
                profile = get_profile(melee_spec, self.fight_style, self.settings)
            except FileNotFoundError:
                logger.warning(f"Profile for {melee_spec} was not found. Skipping.")
                continue

            simulation_group = Simulation_Group(
                name="simulation_group",
                threads=self.settings.threads,
                profileset_work_threads=self.settings.profileset_work_threads,
                executable=self.settings.executable,
                remove_files=not self.settings.keep_files,
            )

            for windfury_name, windfury_override in WINDFURY_OPTIONS.items():
                windfury_override = windfury_override.copy()
                if (
                    melee_spec == ENHANCEMENT
                    and windfury_name == "windfury"
                    and ENHANCEMENT_EXTERNAL_WINDFURY.get(self.fight_style.lower(), [])
                ):
                    windfury_override.append(
                        *ENHANCEMENT_EXTERNAL_WINDFURY[self.fight_style.lower()]
                    )
                if (
                    melee_spec == ENHANCEMENT
                    and windfury_name == "no windfury"
                    and ENHANCEMENT_OWN_WINDFURY.get(self.fight_style.lower(), [])
                ):
                    windfury_override.append(
                        *ENHANCEMENT_OWN_WINDFURY[self.fight_style.lower()]
                    )

                full_spec_name = " ".join(
                    [melee_spec.full_name, melee_spec.wow_class.full_name]
                )
                if windfury_name == WindfuryEnum.NO_WINDFURY.value:
                    full_spec_name = f"{{{full_spec_name}}}"

                simulation_data = Simulation_Data(
                    name=full_spec_name,
                    fight_style=self.fight_style,
                    profile=profile,
                    simc_arguments=windfury_override,
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

            logger.info(f"Simulating {melee_spec}.")
            simulation_group.simulate()

            data = self._collect_data(simulation_group, self.settings.data_type)

            data_dict["data"] = _deep_update(data_dict["data"], data)

        logger.debug("Starting post processing")
        data_dict = self.post_processing(data_dict)

        self._write(data_dict)

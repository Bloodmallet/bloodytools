import dataclasses
import itertools
import logging
import typing

from bloodytools.simulations.legendary_simulator import remove_bonus_ids
from bloodytools.simulations.simulator import Simulator
from bloodytools.utils.simulation_objects import Simulation_Data, Simulation_Group
from bloodytools.utils.utils import EmptyFileError, extract_profile
from simc_support.game_data.Conduit import Conduit, get_conduits_for_spec
from simc_support.game_data.Covenant import COVENANTS, Covenant
from simc_support.game_data.Legendary import Legendary, get_legendaries_for_spec
from simc_support.game_data.SoulBind import SOULBINDS, SoulBindTalent, get_soul_bind
from simc_support.game_data.WowSpec import WowSpec

logger = logging.getLogger(__name__)

CONDUIT_MAX_RANK = 11


def _are_all_covenants_present(profiles: dict) -> bool:
    return len(profiles.keys()) == 4


def _is_dps_node(talent: SoulBindTalent) -> bool:
    return (
        talent.is_dps_increase
        and not (talent.is_endurance or talent.is_finesse or talent.is_potency)
        or talent.full_name == "Party Favors"
    )


def find_legendary_bonus_ids(
    profile: dict, lookup_ids: typing.Iterable[int]
) -> typing.List[int]:
    ids_found: typing.List[int] = []
    for item in profile["items"]:
        item_bonus_ids: typing.List[str] = []
        try:
            tmp_item_bonus_ids = profile["items"][item]["bonus_id"].split("/")
        except KeyError:
            continue

        for element in tmp_item_bonus_ids:
            for b_id in element.split(":"):
                item_bonus_ids.append(b_id)

        if item_bonus_ids and any(item_bonus_ids):
            for b_id in item_bonus_ids:
                if int(b_id) in lookup_ids:
                    ids_found.append(int(b_id))
    return ids_found


def inject_bonus_id(profile: dict, legendary_id: int) -> None:
    """bonus_id is injected into the helmet. Thus a helmet needs to be present.

    Args:
        profile (dict): _description_
        legendary_id (int): _description_
    """
    if not "head" in profile["items"]:
        raise ValueError("'head' item slot is required.")
    if "bonus_id" in profile["items"]["head"]:
        profile["items"]["head"]["bonus_id"] = "/".join(
            [
                profile["items"]["head"]["bonus_id"],
                str(legendary_id),
            ]
        )
    else:
        profile["items"]["head"]["bonus_id"] = str(legendary_id)


def _get_unity(legendaries: typing.List[Legendary], wow_spec: WowSpec) -> Legendary:
    for legendary in legendaries:
        if wow_spec in legendary.wow_specs and legendary.full_name == "Unity":
            return legendary
    raise ValueError("'Unity' Legendary not found in provided list.")


@dataclasses.dataclass
class SoulbindSimulator(Simulator):
    """Simulator deals with all Nodes and Conduits of all Soulbinds
    individually. If a Node requires another active Node that additional Node
    will be active and its own worth will be removed after simulations are
    done.
    """

    def __post_init__(
        self,
    ) -> None:

        self.nodes: typing.Iterable[SoulBindTalent] = []
        for soul_bind in SOULBINDS:
            for talent in soul_bind.soul_bind_talents:
                if _is_dps_node(talent):
                    self.nodes.append(talent)

        self.conduits: typing.Iterable[Conduit] = get_conduits_for_spec(self.wow_spec)

    @classmethod
    def name(cls) -> str:
        return "Soulbinds"

    @classmethod
    def snake_case_name(cls) -> str:
        """Function is provided to keep downwards-compatibility to 9.1.0 spelling error - damn"""
        return "soul_binds"

    def pre_processing(self, data_dict: dict) -> dict:
        data_dict = super().pre_processing(data_dict)

        legendaries = get_legendaries_for_spec(self.wow_spec)

        # we're assuming here that all profiles will always have a covenant legendary
        # replace covenant specific bonus ids and use unity instead
        unity = _get_unity(list(legendaries), self.wow_spec)
        covenant_legendary_ids = [
            legendary.bonus_id
            for legendary in legendaries
            if len(legendary.covenants) == 1
        ]
        remove_bonus_ids(
            data_dict["profile"], covenant_legendary_ids + [unity.bonus_id]
        )
        inject_bonus_id(data_dict["profile"], unity.bonus_id)
        for covenant_profile in data_dict["covenant_profiles"].values():
            remove_bonus_ids(
                covenant_profile, covenant_legendary_ids + [unity.bonus_id]
            )
            inject_bonus_id(covenant_profile, unity.bonus_id)

        if self.settings.custom_profile:
            # make sure custom profiles non-covenant legendary is used by all covenants
            # replace non-covenant legendaries by custom profile input
            non_covenant_legendary_ids: typing.List[int] = [
                legendary.bonus_id
                for legendary in legendaries
                if len(legendary.covenants) > 1 and legendary.full_name != "Unity"
            ]

            legendary_ids = find_legendary_bonus_ids(
                data_dict["profile"], non_covenant_legendary_ids
            )

            if legendary_ids:
                for covenant_profile in data_dict["covenant_profiles"].values():
                    remove_bonus_ids(covenant_profile, non_covenant_legendary_ids)
                    for bonus_id in legendary_ids:
                        inject_bonus_id(covenant_profile, bonus_id)

            data_dict["covenant_profiles"] = self._adjust_covenant_profiles_itemlevels(
                data_dict["profile"], data_dict["covenant_profiles"]
            )

        # remove soulbind information
        data_dict["profile"]["character"]["soulbind"] = ""
        for profile in data_dict["covenant_profiles"].values():
            profile["character"]["soulbind"] = ""

        return data_dict

    def add_simulation_data(
        self,
        simulation_group: Simulation_Group,
        data_dict: dict,
    ) -> None:
        profile = data_dict["profile"]
        additional_profiles = data_dict["covenant_profiles"]

        full_path_simulations = self._create_full_path_simulations(
            profile, additional_profiles
        )

        for simulation in full_path_simulations:
            simulation_group.add(simulation)

    def post_processing(self, data_dict: dict) -> dict:
        data_dict = super().post_processing(data_dict)

        logger.debug("Setting covenant_ids of Covenants")
        data_dict["covenant_ids"] = {}
        for covenant in COVENANTS:
            data_dict["covenant_ids"][covenant.full_name] = covenant.id
            data_dict["translations"][
                covenant.full_name
            ] = covenant.translations.get_dict()

        logger.debug("Setting covenant_mapping")
        data_dict["covenant_mapping"] = {}
        for soul_bind in SOULBINDS:
            data_dict["translations"][
                soul_bind.full_name
            ] = soul_bind.translations.get_dict()
            data_dict["covenant_mapping"][soul_bind.full_name] = [soul_bind.covenant.id]

        logger.debug("Setting spell_ids")
        data_dict["spell_ids"] = {}
        for node in self.nodes:
            soulbind = get_soul_bind(id=node.soulbind_id)
            data_dict["translations"][node.full_name] = node.translations.get_dict()
            data_dict["spell_ids"][node.full_name] = node.spell_id
            data_dict["covenant_mapping"][node.full_name] = [soulbind.covenant.id]

        logger.debug("Settings conduits")
        data_dict["conduits"] = []
        for conduit in self.conduits:
            data_dict["translations"][
                conduit.full_name
            ] = conduit.translations.get_dict()
            data_dict["spell_ids"][conduit.full_name] = conduit.spell_id
            data_dict["covenant_mapping"][conduit.full_name] = list(
                [conduit.id for conduit in conduit.covenants]
            )
            data_dict["conduits"].append(conduit.full_name)

        logger.debug("Setting simulated_steps")
        data_dict["simulated_steps"] = [CONDUIT_MAX_RANK]

        data_dict = self.create_sorted_key_key_value_data(
            data_dict, ignore_key="baseline"
        )

        return data_dict

    def _get_covenant_profile(
        self, profile: dict, additional_profiles: dict, covenant: Covenant
    ) -> dict:
        if _are_all_covenants_present(additional_profiles):
            return additional_profiles.get(covenant.simc_name, profile)
        return profile

    def _create_full_path_simulations(
        self, profile: dict, additional_profiles: dict
    ) -> typing.List[Simulation_Data]:

        profiles: typing.List[Simulation_Data] = []

        def purge_non_dps_elements(
            path: typing.List[SoulBindTalent],
        ) -> typing.List[SoulBindTalent]:
            return [element for element in path if element.is_dps_increase]

        def get_unique_dps_paths(
            paths: typing.List[typing.List[SoulBindTalent]],
        ) -> typing.List[typing.List[SoulBindTalent]]:
            unique_dps_paths: typing.Dict[str, typing.List[SoulBindTalent]] = {}
            for path in paths:
                dps_path = purge_non_dps_elements(path)
                dps_path_name = "".join([e.full_name for e in dps_path])
                unique_dps_paths[dps_path_name] = dps_path
            return list(unique_dps_paths.values())

        def get_longest_unique_paths(
            paths: typing.List[typing.List[SoulBindTalent]],
        ) -> typing.List[typing.List[SoulBindTalent]]:

            unique_paths: typing.List[typing.List[SoulBindTalent]] = []

            sorted_paths = sorted(paths, key=lambda path: len(path), reverse=True)

            # reduce paths to only the longest unique ones
            for path in sorted_paths:
                is_path_in_unique_paths = []
                for unique_path in unique_paths:
                    simc_names = [e.simc_name for e in unique_path]
                    is_path_in_unique_path = all(
                        [element.simc_name in simc_names for element in path]
                    ) and count_potency_conduits(path) <= count_potency_conduits(
                        unique_path
                    )
                    is_path_in_unique_paths.append(is_path_in_unique_path)

                if not any(is_path_in_unique_paths):
                    unique_paths.append(path)

            return unique_paths

        def count_potency_conduits(path: typing.List[SoulBindTalent]) -> int:
            return sum([1 if e.is_potency else 0 for e in path])

        def get_potency_combinations(
            potency_count: int, covenant: Covenant, conduits: typing.Iterable[Conduit]
        ) -> typing.List[typing.Tuple[Conduit, ...]]:
            appropriate_conduits = [
                c
                for c in conduits
                if len(c.covenants) > 1
                or len(c.covenants) == 1
                and c.covenants[0] == covenant
            ]

            return list(itertools.combinations(appropriate_conduits, r=potency_count))

        counter = 0
        for soulbind in SOULBINDS:
            covenant_profile = self._get_covenant_profile(
                profile=profile,
                additional_profiles=additional_profiles,
                covenant=soulbind.covenant,
            )

            # print(soulbind.full_name)
            unique_paths = get_unique_dps_paths(soulbind.talent_paths)
            paths = get_longest_unique_paths(unique_paths)
            for path in paths:
                # print(f"  {count_potency_conduits(path)} {path}")
                potency_count = count_potency_conduits(path)
                potency_combinations = get_potency_combinations(
                    potency_count, soulbind.covenant, self.conduits
                )

                no_potency_path = [
                    element for element in path if not element.is_potency
                ]

                for potency_combination in potency_combinations:
                    # print(f"{no_potency_path} {potency_combination}")
                    counter += 1

                    path_name = "+".join(
                        [element.full_name for element in no_potency_path]
                        + [c.full_name for c in potency_combination]
                    )

                    name = self.profile_split_character().join(
                        [
                            soulbind.full_name,
                            path_name,
                        ]
                    )
                    soulbind_string = "soulbind="
                    soulbind_string += "/".join(
                        [str(talent.spell_id) for talent in no_potency_path]
                    )
                    soulbind_string += "/" + "/".join(
                        [
                            f"{conduit.id}:{CONDUIT_MAX_RANK}:1"
                            for conduit in potency_combination
                        ]
                    )
                    simulation_data = Simulation_Data(
                        name=name,
                        fight_style=self.fight_style,
                        profile=covenant_profile,
                        simc_arguments=[
                            f"covenant={soulbind.covenant.simc_name}",
                            soulbind_string,
                        ],
                        target_error=self.settings.target_error.get(
                            self.fight_style, "0.1"
                        ),
                        ptr=self.settings.ptr,
                        default_actions=self.settings.default_actions,
                        executable=self.settings.executable,
                        iterations=self.settings.iterations,
                    )

                    profiles.append(simulation_data)

        return profiles

    def _adjust_covenant_profiles_itemlevels(
        self, profile: dict, covenant_profiles: dict
    ) -> dict:
        """Adjust itemlevel IF a custom profile was submitted. Otherwise more or less equal base profiles are assumed.

        Args:
            profile (dict): _description_
            covenant_profiles (dict): _description_

        Returns:
            dict: _description_
        """

        try:
            extract_profile("custom_profile.txt", self.wow_spec.wow_class)
        except EmptyFileError:
            logger.info("Nothing to adjust. No custom profile found.")
            return covenant_profiles

        simulation = Simulation_Data(
            name="Grab dem average itemlevel",
            fight_style=self.fight_style,
            target_error="0.1",
            iterations="1",
            profile=profile,
            ptr=self.settings.ptr,
            default_actions=self.settings.default_actions,
            executable=self.settings.executable,
        )
        simulation.simulate()

        logger.debug("Mini simulation is done")

        ilevels = [
            slot["ilevel"]
            for slot in simulation.json_data["sim"]["players"][0]["gear"].values()
            if slot["ilevel"] > 0
        ]
        average_itemlevel = sum(ilevels) / len(ilevels)
        logger.debug(f"Calculated average itemlevel to be: {average_itemlevel}")

        for covenant_profile in covenant_profiles.values():
            for slot in covenant_profile["items"].values():
                slot["ilevel"] = str(int(average_itemlevel))

        logger.debug("Adjusted covenant profiles to new average itemlevel")

        return covenant_profiles

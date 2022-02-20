import dataclasses
import itertools
import logging
from math import gamma
import typing

from bloodytools.simulations.legendary_simulator import (
    remove_legendary_bonus_ids,
)
from bloodytools.simulations.simulator import Simulator
from bloodytools.utils.simulation_objects import Simulation_Data, Simulation_Group
from simc_support.game_data.Conduit import Conduit, get_conduits_for_spec
from simc_support.game_data.Covenant import COVENANTS, Covenant
from simc_support.game_data.Legendary import get_legendaries_for_spec, Legendary
from simc_support.game_data.SoulBind import (
    SOULBINDS,
    SoulBind,
    SoulBindTalent,
    get_soul_bind,
)
from simc_support.game_data.WowSpec import WowSpec

logger = logging.getLogger(__name__)

MAX_SOULBINDTALENT_TIER = 11
CONDUIT_MAX_RANK = 11
CONDUIT_MIN_RANK = 9
CONDUIT_RANKS = list(range(CONDUIT_MIN_RANK, CONDUIT_MAX_RANK + 1))


def _are_all_covenants_present(profiles: dict) -> bool:
    return len(profiles.keys()) == 4


def _get_first_row_soulbindtalent(soulbind: SoulBind) -> SoulBindTalent:
    for talent in soulbind.soul_bind_talents:
        if talent.tier == 0:
            return talent
    raise ValueError("No first row soulbindtalent found.")


def _is_last_row_soulbindtalent(soulbindtalent: SoulBindTalent) -> bool:
    return soulbindtalent.tier == MAX_SOULBINDTALENT_TIER


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
        remove_legendary_bonus_ids(
            data_dict["profile"], covenant_legendary_ids + [unity.bonus_id]
        )
        inject_bonus_id(data_dict["profile"], unity.bonus_id)
        for covenant_profile in data_dict["covenant_profiles"].values():
            remove_legendary_bonus_ids(
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
                    remove_legendary_bonus_ids(
                        covenant_profile, non_covenant_legendary_ids
                    )
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

        # baseline profiles
        covenant_simulations = self._create_covenant_simulations(
            profile, additional_profiles
        )

        node_simulations = self._create_node_simulations(profile, additional_profiles)

        conduit_simulations = self._create_conduit_simulations(
            profile, additional_profiles
        )

        for simulation in covenant_simulations + node_simulations + conduit_simulations:
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

        logger.debug("Setting paths")
        data_dict["paths"] = {}
        for soulbind in SOULBINDS:
            data_dict["paths"][soulbind.full_name] = [
                [
                    # setting our own name because Emenis Potency Conduit has a different name
                    "Potency Conduit" if talent.is_potency else talent.full_name
                    for talent in path
                ]
                for path in soulbind.talent_paths
            ]

        logger.debug("Setting renowns")
        data_dict["renowns"] = {}
        for soulbind in SOULBINDS:
            path = soulbind.talent_paths[0]
            renowns = list([node.renown for node in path])
            data_dict["renowns"][soulbind.full_name] = renowns

        logger.debug("Setting simulated_steps")
        data_dict["simulated_steps"] = sorted(CONDUIT_RANKS, reverse=True)

        logger.debug("Removing first row dps values from last row dps values")
        for node in self.nodes:
            if _is_last_row_soulbindtalent(node):
                soulbind = get_soul_bind(id=node.soulbind_id)
                covenant = soulbind.covenant

                baseline_dps = data_dict["data"]["baseline"][covenant.full_name]
                first_row_dps = data_dict["data"].get(
                    _get_first_row_soulbindtalent(soulbind).full_name,
                    {covenant.full_name: baseline_dps},
                )[covenant.full_name]
                last_row_dps = data_dict["data"][node.full_name][covenant.full_name]
                actual_dps = max(last_row_dps - first_row_dps, 0) + baseline_dps
                data_dict["data"][node.full_name][covenant.full_name] = actual_dps

        logger.debug("Finding best paths")
        data_dict["soul_bind_paths"] = {}
        data_dict["sorted_data_keys"] = {}

        for rank in CONDUIT_RANKS:
            data_dict["soul_bind_paths"][str(rank)] = {}
            soul_bind_dps: typing.List[typing.Tuple[str, int]] = []
            for soul_bind in SOULBINDS:
                dps_paths: typing.List[
                    typing.Tuple[typing.List[SoulBindTalent], int, typing.List[str]]
                ] = []
                for path in soul_bind.talent_paths:
                    filtered_path = [
                        talent for talent in path if talent.is_dps_increase
                    ]
                    purged_path = []
                    dps_values: typing.List[int] = []
                    cnt_potency = 0
                    for soulbind_talent in filtered_path:
                        if soulbind_talent.is_potency:
                            # search through all double-potency conduits, if it's available twice
                            # search through all potency conduits
                            # add dps
                            cnt_potency += 1
                        elif not (
                            soulbind_talent.is_potency
                            or soulbind_talent.is_finesse
                            or soulbind_talent.is_endurance
                        ):
                            dps_values.append(
                                data_dict["data"][soulbind_talent.full_name][
                                    soul_bind.covenant.full_name
                                ]
                            )
                            purged_path.append(soulbind_talent.full_name)
                    # add potency dps values
                    if cnt_potency == 2:
                        double_potencies: typing.List[typing.Tuple[str, int]] = [
                            (
                                name,
                                data_dict["data"][name][soul_bind.covenant.full_name][
                                    str(rank)
                                ],
                            )
                            for name in data_dict["data"].keys()
                            if "+" in name
                            and soul_bind.covenant.full_name in data_dict["data"][name]
                        ]
                        winner_2 = max(
                            double_potencies, key=lambda key_value: key_value[1]
                        )
                        dps_values.append(
                            data_dict["data"][winner_2[0]][
                                soul_bind.covenant.full_name
                            ][str(rank)]
                        )
                        purged_path += winner_2[0].split("+")
                    elif cnt_potency == 1:
                        potencies: typing.List[typing.Tuple[Conduit, int]] = [
                            (
                                conduit,
                                data_dict["data"][conduit.full_name][
                                    soul_bind.covenant.full_name
                                ][str(rank)],
                            )
                            for conduit in self.conduits
                            if conduit.is_potency
                            and soul_bind.covenant in conduit.covenants
                        ]
                        winner_1 = max(potencies, key=lambda key_value: key_value[1])
                        dps_values.append(
                            data_dict["data"][winner_1[0].full_name][
                                soul_bind.covenant.full_name
                            ][str(rank)]
                        )
                        purged_path.append(winner_1[0].full_name)

                    def get_path_sum(
                        soulbind: SoulBind, dps_values: typing.List[int]
                    ) -> int:
                        result = 0
                        covenant_name: str = soulbind.covenant.full_name
                        for value in dps_values:
                            result += max(
                                value - data_dict["data"]["baseline"][covenant_name],
                                0,
                            )
                        return result

                    # compare only dps gains, without baseline dps
                    dps_paths.append(
                        (
                            path,
                            get_path_sum(soul_bind, dps_values),
                            purged_path,
                        )
                    )

                winner = max(dps_paths, key=lambda key_value: key_value[1])

                data_dict["soul_bind_paths"][str(rank)][soul_bind.full_name] = winner[2]
                # add soul bind dps to "data"
                if soul_bind.full_name not in data_dict["data"]:
                    data_dict["data"][soul_bind.full_name] = {}
                data_dict["data"][soul_bind.full_name][str(rank)] = (
                    winner[1]
                    + data_dict["data"]["baseline"][soul_bind.covenant.full_name]
                )

                soul_bind_dps.append(
                    (
                        soul_bind.full_name,
                        data_dict["data"][soul_bind.full_name][str(rank)],
                    )
                )
            ordered_soul_binds = sorted(soul_bind_dps, key=lambda e: e[1], reverse=True)

            data_dict["sorted_data_keys"][str(rank)] = [
                soul_bind[0] for soul_bind in ordered_soul_binds
            ]

        logger.debug("Finding best paths for each covenant per rank")
        # create ordered soul bind name list
        for rank in CONDUIT_RANKS:
            for covenant in COVENANTS:

                tmp_list: typing.List[typing.Tuple[str, int]] = []
                for talent in data_dict["data"]:
                    if "baseline" in talent:
                        continue

                    if "+" in talent:
                        continue

                    try:
                        tmp_list.append(
                            (
                                talent,
                                data_dict["data"][talent][covenant.full_name][str(rank)]
                                - data_dict["data"]["baseline"][covenant.full_name],
                            )
                        )
                    except TypeError:
                        tmp_list.append(
                            (
                                talent,
                                data_dict["data"][talent][covenant.full_name]
                                - data_dict["data"][f"baseline"][covenant.full_name],
                            )
                        )
                    except KeyError:
                        continue
                logger.debug(
                    "tmp_list for covenant {}: {}".format(covenant.full_name, tmp_list)
                )

                tmp_list = sorted(tmp_list, key=lambda item: item[1], reverse=True)
                logger.debug("Sorted tmp_list: {}".format(tmp_list))
                logger.debug(
                    "Soul Bind Talent '{}' ({}) won with {} dps.".format(
                        tmp_list[0][0], covenant.full_name, tmp_list[0][1]
                    )
                )

                data_dict[f"sorted_data_keys_{covenant.simc_name}_{rank}"] = [
                    soul_bind for soul_bind, _ in tmp_list
                ]

        return data_dict

    def _get_covenant_profile(
        self, profile: dict, additional_profiles: dict, covenant: Covenant
    ) -> dict:
        if _are_all_covenants_present(additional_profiles):
            return additional_profiles.get(covenant.simc_name, profile)
        return profile

    def _create_covenant_simulations(
        self, profile: dict, additional_profiles: dict
    ) -> typing.List[Simulation_Data]:
        simulations: typing.List[Simulation_Data] = []

        for covenant in COVENANTS:

            covenant_profile = self._get_covenant_profile(
                profile=profile,
                additional_profiles=additional_profiles,
                covenant=covenant,
            )

            simulation_data = Simulation_Data(
                name=self.profile_split_character().join(
                    ["baseline", covenant.full_name]
                ),
                fight_style=self.fight_style,
                profile=covenant_profile,
                simc_arguments=[
                    f"covenant={covenant.simc_name}",
                    "soulbind=",
                ],
                target_error=self.settings.target_error.get(self.fight_style, "0.1"),
                ptr=self.settings.ptr,
                default_actions=self.settings.default_actions,
                executable=self.settings.executable,
                iterations=self.settings.iterations,
            )

            if covenant == COVENANTS[0]:
                custom_apl = None
                if self.settings.custom_apl:
                    with open("custom_apl.txt") as f:
                        custom_apl = f.read()
                if custom_apl:
                    simulation_data.simc_arguments.append("# custom_apl")
                    simulation_data.simc_arguments.append(custom_apl)

                custom_fight_style = None
                if self.settings.custom_fight_style:
                    with open("custom_fight_style.txt") as f:
                        custom_fight_style = f.read()
                if custom_fight_style:
                    simulation_data.simc_arguments.append("# custom_fight_style")
                    simulation_data.simc_arguments.append(custom_fight_style)

            simulations.append(simulation_data)
            logger.debug(
                (
                    "Created covenant base profile '{}' in profile '{}'.".format(
                        covenant.full_name, simulation_data.name
                    )
                )
            )

        return simulations

    def _create_node_simulations(
        self, profile: dict, additional_profiles: dict
    ) -> typing.List[Simulation_Data]:
        simulations: typing.List[Simulation_Data] = []

        for node in self.nodes:
            soulbind = get_soul_bind(id=node.soulbind_id)

            covenant_profile = self._get_covenant_profile(
                profile=profile,
                additional_profiles=additional_profiles,
                covenant=soulbind.covenant,
            )

            # last row nodes ususally need their first row to function properly
            soulbind_string = str(node.spell_id)
            if _is_last_row_soulbindtalent(node):
                soulbind_string += "/" + str(
                    _get_first_row_soulbindtalent(soulbind).spell_id
                )

            simulation_data = Simulation_Data(
                name=self.profile_split_character().join(
                    [node.full_name, soulbind.covenant.full_name]
                ),
                fight_style=self.fight_style,
                profile=covenant_profile,
                simc_arguments=[
                    f"covenant={soulbind.covenant.simc_name}",
                    f"soulbind={soulbind_string}",
                ],
                target_error=self.settings.target_error.get(self.fight_style, "0.1"),
                ptr=self.settings.ptr,
                default_actions=self.settings.default_actions,
                executable=self.settings.executable,
                iterations=self.settings.iterations,
            )

            if node.full_name == "Party Favors":
                simulation_data.simc_arguments += [
                    "shadowlands.party_favor_type=random"
                ]

            simulations.append(simulation_data)
            logger.debug(
                (
                    "Created soulbind node '{}' in profile '{}'.".format(
                        node.full_name, simulation_data.name
                    )
                )
            )

        return simulations

    def _create_conduit_simulations(
        self, profile: dict, additional_profiles: dict
    ) -> typing.List[Simulation_Data]:
        simulations: typing.List[Simulation_Data] = []

        # single conduits
        single_conduits_product = itertools.product(
            CONDUIT_RANKS, COVENANTS, self.conduits
        )
        single_conduits = filter(
            lambda rank_cov_con: rank_cov_con[1] in rank_cov_con[2].covenants,
            single_conduits_product,
        )
        for rank, covenant, conduit in single_conduits:
            covenant_profile = self._get_covenant_profile(
                profile=profile,
                additional_profiles=additional_profiles,
                covenant=covenant,
            )

            simulation = Simulation_Data(
                name=self.profile_split_character().join(
                    [conduit.full_name, covenant.full_name, str(rank)]
                ),
                fight_style=self.fight_style,
                profile=covenant_profile,
                simc_arguments=[
                    f"covenant={covenant.simc_name}",
                    f"soulbind={conduit.id}:{rank}",
                ],
                target_error=self.settings.target_error.get(self.fight_style, "0.1"),
                ptr=self.settings.ptr,
                default_actions=self.settings.default_actions,
                executable=self.settings.executable,
                iterations=self.settings.iterations,
            )

            simulations.append(simulation)

        # double conduits
        def is_valid_combination(
            rank: int, covenant: Covenant, conduit1: Conduit, conduit2: Conduit
        ) -> bool:
            def are_generic_conduits(conduit1: Conduit, conduit2: Conduit) -> bool:
                len1 = len(conduit1.covenants)
                len2 = len(conduit2.covenants)
                return len1 == len2 and len1 + len2 > 2

            def covenant_specific_conduit_matches_covenant(
                conduit: Conduit, covenant: Covenant
            ) -> bool:
                return len(conduit.covenants) == 1 and covenant in conduit.covenants

            def max_one_covenant_conduit(conduit1: Conduit, conduit2: Conduit) -> bool:
                len1 = len(conduit1.covenants)
                len2 = len(conduit2.covenants)
                return len1 + len2 > 2

            return (
                (
                    are_generic_conduits(conduit1, conduit2)
                    or covenant_specific_conduit_matches_covenant(conduit1, covenant)
                    or covenant_specific_conduit_matches_covenant(conduit2, covenant)
                )
                and max_one_covenant_conduit(conduit1, conduit2)
                and conduit1 != conduit2
                and conduit1.spell_id < conduit2.spell_id
            )

        double_conduits_product = itertools.product(
            CONDUIT_RANKS, COVENANTS, self.conduits, self.conduits
        )
        double_conduits = filter(
            lambda combination: is_valid_combination(*combination),
            double_conduits_product,
        )

        for rank, covenant, conduit1, conduit2 in double_conduits:
            covenant_profile = self._get_covenant_profile(
                profile=profile,
                additional_profiles=additional_profiles,
                covenant=covenant,
            )

            simulation = Simulation_Data(
                name=self.profile_split_character().join(
                    [
                        f"{conduit1.full_name}+{conduit2.full_name}",
                        covenant.full_name,
                        str(rank),
                    ]
                ),
                fight_style=self.fight_style,
                profile=covenant_profile,
                simc_arguments=[
                    f"covenant={covenant.simc_name}",
                    f"soulbind={conduit1.id}:{rank}/{conduit2.id}:{rank}",
                ],
                target_error=self.settings.target_error.get(self.fight_style, "0.1"),
                ptr=self.settings.ptr,
                default_actions=self.settings.default_actions,
                executable=self.settings.executable,
                iterations=self.settings.iterations,
            )

            simulations.append(simulation)

        logger.debug(f"Created {len(simulations)} Simulations.")
        return simulations

    def _adjust_covenant_profiles_itemlevels(
        self, profile: dict, covenant_profiles: dict
    ) -> dict:

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

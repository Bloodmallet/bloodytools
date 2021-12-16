import dataclasses
import itertools
import logging
import typing

from bloodytools.simulations.legendary_simulations import (
    find_legendary_bonus_id,
    remove_legendary_bonus_ids,
)
from bloodytools.simulations.simulator import Simulator
from bloodytools.utils.simulation_objects import Simulation_Data, Simulation_Group
from simc_support.game_data.Conduit import Conduit, get_conduits_for_spec
from simc_support.game_data.Covenant import COVENANTS, Covenant
from simc_support.game_data.Legendary import get_legendaries_for_spec
from simc_support.game_data.SoulBind import (
    SOULBINDS,
    SoulBind,
    SoulBindTalent,
    get_soul_bind,
)

logger = logging.getLogger(__name__)

MAX_SOULBINDTALENT_TIER = 11
CONDUIT_MAX_RANK = 11
CONDUIT_MIN_RANK = 5
CONDUIT_RANKS = list(range(CONDUIT_MIN_RANK, CONDUIT_MAX_RANK + 1))


def _are_all_covenants_present(profiles: dict) -> bool:
    return len(profiles.keys()) == 4


def _get_first_row_soulbindtalent(soulbind: SoulBind) -> SoulBindTalent:
    for talent in soulbind.soul_bind_talents:
        if talent.tier == 0:
            return talent


def _is_last_row_soulbindtalent(soulbindtalent: SoulBindTalent) -> bool:
    return soulbindtalent.tier == MAX_SOULBINDTALENT_TIER


def _is_dps_node(talent: SoulBindTalent) -> bool:
    return (
        talent.is_dps_increase
        and not (talent.is_endurance or talent.is_finesse or talent.is_potency)
        or talent.full_name == "Party Favors"
    )


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
    @property
    def name(cls) -> str:
        return "Soulbinds"

    def pre_processing(self, data_dict: dict) -> dict:
        data_dict = super().pre_processing(data_dict)
        if not _are_all_covenants_present(data_dict["covenant_profiles"]):
            logger.debug("Purging spec legendaries from base profile")
            covenant_legendary_ids = [
                legendary.bonus_id
                for legendary in get_legendaries_for_spec(self.wow_spec)
                if len(legendary.covenants) == 1
            ]
            data_dict["profile"] = remove_legendary_bonus_ids(
                data_dict["profile"], covenant_legendary_ids
            )

        if self.settings.custom_profile:
            # replace legendaries if custom profile contained a non-covenant one
            legendaries = [
                legendary for legendary in get_legendaries_for_spec(self.wow_spec)
            ]
            all_legendary_ids = [legendary.bonus_id for legendary in legendaries]
            non_covenant_legendary_ids = [
                legendary.bonus_id
                for legendary in legendaries
                if len(legendary.covenants) > 1
            ]
            legendary_id: int = find_legendary_bonus_id(
                data_dict["profile"], all_legendary_ids
            )
            if legendary_id:
                is_non_covenant_legendary = legendary_id in non_covenant_legendary_ids
                if is_non_covenant_legendary:
                    for covenant_profile in data_dict["covenant_profiles"].values():
                        remove_legendary_bonus_ids(covenant_profile, all_legendary_ids)
                        if "bonus_id" in covenant_profile["items"]["head"]:
                            covenant_profile["items"]["head"]["bonus_id"] = "/".join(
                                [
                                    covenant_profile["items"]["head"]["bonus_id"],
                                    str(legendary_id),
                                ]
                            )
                        else:
                            covenant_profile["items"]["head"]["bonus_id"] = str(
                                legendary_id
                            )

        if self.settings.custom_profile:
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
            soul_bind_dps: typing.List[SoulBind] = []
            for soul_bind in SOULBINDS:
                dps_paths: typing.List[
                    typing.Tuple[typing.List[SoulBindTalent], float, typing.List[str]]
                ] = []
                for path in soul_bind.talent_paths:
                    filtered_path = [
                        talent for talent in path if talent.is_dps_increase
                    ]
                    purged_path = []
                    dps_values = []
                    cnt_potency = 0
                    for talent in filtered_path:
                        if talent.is_potency:
                            # search through all double-potency conduits, if it's available twice
                            # search through all potency conduits
                            # add dps
                            cnt_potency += 1
                        elif not (
                            talent.is_potency
                            or talent.is_finesse
                            or talent.is_endurance
                        ):
                            dps_values.append(
                                data_dict["data"][talent.full_name][
                                    soul_bind.covenant.full_name
                                ]
                            )
                            purged_path.append(talent.full_name)
                    # add potency dps values
                    if cnt_potency == 2:
                        double_potencies = [
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
                        winner = max(
                            double_potencies, key=lambda key_value: key_value[1]
                        )
                        dps_values.append(
                            data_dict["data"][winner[0]][soul_bind.covenant.full_name][
                                str(rank)
                            ]
                        )
                        purged_path += winner[0].split("+")
                    elif cnt_potency == 1:
                        potencies = [
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
                        winner = max(potencies, key=lambda key_value: key_value[1])
                        dps_values.append(
                            data_dict["data"][winner[0].full_name][
                                soul_bind.covenant.full_name
                            ][str(rank)]
                        )
                        purged_path.append(winner[0].full_name)

                    # compare only dps gains, without baseline dps
                    dps_paths.append(
                        (
                            path,
                            sum(
                                map(
                                    lambda value: value
                                    - data_dict["data"]["baseline"][
                                        soul_bind.covenant.full_name
                                    ],
                                    dps_values,
                                )
                            ),
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

                tmp_list = []
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
                name=f"baseline_{covenant.full_name}",
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
                name=f"{node.full_name}_{soulbind.covenant.full_name}",
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
        combinations = []
        for conduit in self.conduits:
            for covenant in conduit.covenants:
                for rank in CONDUIT_RANKS:
                    combinations.append((rank, covenant, conduit))
        for rank, covenant, conduit in combinations:
            covenant_profile = self._get_covenant_profile(
                profile=profile,
                additional_profiles=additional_profiles,
                covenant=covenant,
            )

            simulation = Simulation_Data(
                name=f"{conduit.full_name}_{covenant.full_name}_{rank}",
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
        conduit_combinations: typing.Iterable[
            typing.Tuple[Conduit, Conduit]
        ] = itertools.combinations(self.conduits, 2)
        conduit_combinations = filter(
            lambda c: len(c[0].covenants) + len(c[1].covenants) > 2,
            conduit_combinations,
        )

        covenant_combinations = itertools.product(
            COVENANTS, conduit_combinations, repeat=1
        )
        covenant_combinations = [
            (combination[0], *combination[1])
            for combination in covenant_combinations
            if len(combination[1][0].covenants) == len(combination[1][1].covenants)
            or len(combination[1][0].covenants) == 1
            and combination[1][0].covenants[0] == combination[0]
            or len(combination[1][1].covenants) == 1
            and combination[1][1].covenants[0] == combination[0]
        ]

        combinations = itertools.product(CONDUIT_RANKS, covenant_combinations)
        combinations = [
            (combination[0], *combination[1]) for combination in combinations
        ]

        for rank, covenant, conduit1, conduit2 in combinations:
            covenant_profile = self._get_covenant_profile(
                profile=profile,
                additional_profiles=additional_profiles,
                covenant=covenant,
            )

            simulation = Simulation_Data(
                name=f"{conduit1.full_name}+{conduit2.full_name}_{covenant.full_name}_{rank}",
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

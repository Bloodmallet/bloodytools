import json
import logging
import os

from bloodytools.utils.utils import create_base_json_dict
from bloodytools.utils.simulation_objects import Simulation_Group, Simulation_Data

from simc_support.game_data.Conduit import get_conduits_for_spec
from simc_support.game_data.Covenant import COVENANTS, get_covenant
from simc_support.game_data.SoulBind import SOULBINDS, SoulBindTalent

from simc_support.game_data.WowSpec import WowSpec
from typing import List

logger = logging.getLogger(__name__)

CONDUITMAXRANK = 11
ranks = list(range(5, CONDUITMAXRANK + 1))


def soul_bind_simulation(settings: object) -> None:
    """Simulates all options (nodes and conduits) of all soul binds.

    Arguments:
        settings {object} -- settings object

    Returns:
        None --
    """
    logger.debug("soul_bind_simulation start")

    specs: List[WowSpec] = settings.wow_class_spec_list

    # prepare nodes
    nodes = []
    for soul_bind in SOULBINDS:
        for talent in soul_bind.soul_bind_talents:
            talent.soul_bind = soul_bind
            nodes.append(talent)

    # filter conduits and non-dps nodes
    def is_relevant_node(talent: SoulBindTalent) -> bool:
        return talent.is_dps_increase and not (
            talent.is_endurance or talent.is_finesse or talent.is_potency
        )

    nodes = list(filter(is_relevant_node, nodes))

    for fight_style in settings.fight_styles:
        for wow_spec in specs:

            # prepare result json
            wanted_data = create_base_json_dict(
                "Soulbinds",
                wow_spec,
                fight_style,
                settings,
            )

            wanted_data["covenant_ids"] = {}
            for covenant in COVENANTS:
                wanted_data["covenant_ids"][covenant.full_name] = covenant.id
                wanted_data["translations"][
                    covenant.full_name
                ] = covenant.translations.get_dict()

            wanted_data["covenant_mapping"] = {}
            for soul_bind in SOULBINDS:
                wanted_data["translations"][
                    soul_bind.full_name
                ] = soul_bind.translations.get_dict()
                wanted_data["covenant_mapping"][soul_bind.full_name] = [
                    soul_bind.covenant.id
                ]

            wanted_data["spell_ids"] = {}
            for node in nodes:
                wanted_data["translations"][
                    node.full_name
                ] = node.translations.get_dict()
                wanted_data["spell_ids"][node.full_name] = node.spell_id
                wanted_data["covenant_mapping"][node.full_name] = [
                    node.soul_bind.covenant.id
                ]

            wanted_data["conduits"] = []
            conduits = get_conduits_for_spec(wow_spec)
            for conduit in conduits:
                wanted_data["translations"][
                    conduit.full_name
                ] = conduit.translations.get_dict()
                wanted_data["spell_ids"][conduit.full_name] = conduit.spell_id
                wanted_data["covenant_mapping"][conduit.full_name] = list(
                    [conduit.id for conduit in conduit.covenants]
                )
                wanted_data["conduits"].append(conduit.full_name)

            wanted_data["paths"] = {}
            for soulbind in SOULBINDS:
                wanted_data["paths"][soulbind.full_name] = [
                    [
                        # setting our own name because Emenis Potency Conduit has a different name
                        "Potency Conduit" if talent.is_potency else talent.full_name
                        for talent in path
                    ]
                    for path in soulbind.talent_paths
                ]

            wanted_data["renowns"] = {}
            for soulbind in SOULBINDS:
                path = soulbind.talent_paths[0]
                renowns = list([node.renown for node in path])
                wanted_data["renowns"][soulbind.full_name] = renowns

            simulation_group = Simulation_Group(
                name="soul_bind_simulation",
                threads=settings.threads,
                profileset_work_threads=settings.profileset_work_threads,
                executable=settings.executable,
                remove_files=not settings.keep_files,
            )

            for covenant in COVENANTS:
                simulation_data = None

                profile = wanted_data["covenant_profiles"].get(
                    covenant.simc_name, wanted_data["profile"]
                )

                simulation_data = Simulation_Data(
                    name=f"baseline_{covenant.id}",
                    fight_style=fight_style,
                    profile=profile,
                    simc_arguments=[
                        f"covenant={covenant.simc_name}",
                        "soulbind=",
                    ],
                    target_error=settings.target_error.get(fight_style, "0.1"),
                    ptr=settings.ptr,
                    default_actions=settings.default_actions,
                    executable=settings.executable,
                    iterations=settings.iterations,
                )

                if covenant == COVENANTS[0]:
                    custom_apl = None
                    if settings.custom_apl:
                        with open("custom_apl.txt") as f:
                            custom_apl = f.read()
                    if custom_apl:
                        simulation_data.simc_arguments.append("# custom_apl")
                        simulation_data.simc_arguments.append(custom_apl)

                    custom_fight_style = None
                    if settings.custom_fight_style:
                        with open("custom_fight_style.txt") as f:
                            custom_fight_style = f.read()
                    if custom_fight_style:
                        simulation_data.simc_arguments.append("# custom_fight_style")
                        simulation_data.simc_arguments.append(custom_fight_style)

                simulation_group.add(simulation_data)
                logger.debug(
                    (
                        "Added covenant base profile '{}' in profile '{}' to simulation_group.".format(
                            covenant.full_name, simulation_data.name
                        )
                    )
                )

            for node in nodes:

                simulation_data = None

                simulation_data = Simulation_Data(
                    name=f"{node.full_name}_{node.soul_bind.covenant.id}",
                    fight_style=fight_style,
                    simc_arguments=[
                        f"covenant={node.soul_bind.covenant.simc_name}",
                        f"soulbind={node.spell_id}",
                    ],
                    target_error=settings.target_error.get(fight_style, "0.1"),
                    ptr=settings.ptr,
                    default_actions=settings.default_actions,
                    executable=settings.executable,
                    iterations=settings.iterations,
                )

                simulation_group.add(simulation_data)
                logger.debug(
                    (
                        "Added soul bind node '{}' in profile '{}' to simulation_group.".format(
                            node.full_name, simulation_data.name
                        )
                    )
                )

            wanted_data["simulated_steps"] = []
            for rank in ranks:
                if rank not in wanted_data["simulated_steps"]:
                    wanted_data["simulated_steps"] = [rank] + wanted_data[
                        "simulated_steps"
                    ]

                # track which conduit combinations are already being simulated
                combos = []
                for conduit in conduits:
                    combos.append(conduit.id)

                    for covenant in conduit.covenants:

                        simulation_data = None

                        simulation_data = Simulation_Data(
                            name=f"{conduit.full_name}_{covenant.id}_{rank}",
                            fight_style=fight_style,
                            simc_arguments=[
                                f"covenant={covenant.simc_name}",
                                f"soulbind={conduit.id}:{rank}",
                            ],
                            target_error=settings.target_error.get(fight_style, "0.1"),
                            ptr=settings.ptr,
                            default_actions=settings.default_actions,
                            executable=settings.executable,
                            iterations=settings.iterations,
                        )

                        simulation_group.add(simulation_data)
                        logger.debug(
                            (
                                "Added conduit '{}' for '{}' at rank {} in profile '{}' to simulation_group.".format(
                                    conduit.full_name,
                                    covenant.full_name,
                                    rank,
                                    simulation_data.name,
                                )
                            )
                        )

                        secondary_conduits = [
                            c
                            for c in conduits
                            if c.id not in combos and covenant in c.covenants
                        ]

                        for secondary_conduit in secondary_conduits:
                            simulation_data = None

                            simulation_data = Simulation_Data(
                                name=f"{conduit.full_name}+{secondary_conduit.full_name}_{covenant.id}_{rank}",
                                fight_style=fight_style,
                                simc_arguments=[
                                    f"covenant={covenant.simc_name}",
                                    f"soulbind={conduit.id}:{rank}/{secondary_conduit.id}:{rank}",
                                ],
                                target_error=settings.target_error.get(
                                    fight_style, "0.1"
                                ),
                                ptr=settings.ptr,
                                default_actions=settings.default_actions,
                                executable=settings.executable,
                                iterations=settings.iterations,
                            )

                            simulation_group.add(simulation_data)
                            logger.debug(
                                (
                                    "Added conduit '{}' and secondary condui '{}' for '{}' at rank {} in profile '{}' to simulation_group.".format(
                                        conduit.full_name,
                                        secondary_conduit.full_name,
                                        covenant.full_name,
                                        rank,
                                        simulation_data.name,
                                    )
                                )
                            )
            logger.info(
                "Start {} soul_binds simulation for {}.".format(fight_style, wow_spec)
            )
            try:
                if settings.use_raidbots and settings.apikey:
                    settings.simc_hash = simulation_group.simulate_with_raidbots(
                        settings.apikey
                    )
                else:
                    simulation_group.simulate()
            except Exception as e:
                logger.error(
                    "{} soul_binds simulation for {} failed. {}".format(
                        fight_style.title(), wow_spec, e
                    )
                )
                continue
            else:
                logger.info(
                    "{} soul_binds simulation for {} ended successfully. Cleaning up.".format(
                        fight_style.title(), wow_spec
                    )
                )

            # collect dps
            for profile in simulation_group.profiles:
                logger.debug(f"Profile '{profile.name}' DPS: {profile.get_dps()}")

                name = profile.name.split("_")[0]
                covenant_id = int(profile.name.split("_")[1])
                covenant = get_covenant(id=covenant_id).full_name
                try:
                    rank = int(profile.name.split("_")[2])
                except IndexError:
                    rank = None

                if name not in wanted_data["data"]:
                    wanted_data["data"][name] = {}

                if isinstance(rank, int):
                    if covenant not in wanted_data["data"][name]:
                        wanted_data["data"][name][covenant] = {}
                    wanted_data["data"][name][covenant][rank] = profile.get_dps()
                else:
                    wanted_data["data"][name][covenant] = profile.get_dps()

                logger.debug(
                    "Added '{}' with {} dps to json.".format(
                        profile.name, profile.get_dps()
                    )
                )

            logger.debug(wanted_data)

            # finding the best paths:
            wanted_data["soul_bind_paths"] = {}
            wanted_data["sorted_data_keys"] = {}
            for rank in ranks:
                wanted_data["soul_bind_paths"][rank] = {}
                soul_bind_dps = []
                for soul_bind in SOULBINDS:
                    dps_paths = []
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
                                    wanted_data["data"][talent.full_name][
                                        soul_bind.covenant.full_name
                                    ]
                                )
                                purged_path.append(talent.full_name)
                        # add potency dps values
                        if cnt_potency == 2:
                            double_potencies = [
                                (
                                    name,
                                    wanted_data["data"][name][
                                        soul_bind.covenant.full_name
                                    ][rank],
                                )
                                for name in wanted_data["data"].keys()
                                if "+" in name
                                and soul_bind.covenant.full_name
                                in wanted_data["data"][name]
                            ]
                            winner = max(
                                double_potencies, key=lambda key_value: key_value[1]
                            )
                            dps_values.append(
                                wanted_data["data"][winner[0]][
                                    soul_bind.covenant.full_name
                                ][rank]
                            )
                            purged_path += winner[0].split("+")
                        elif cnt_potency == 1:
                            potencies = [
                                (
                                    conduit,
                                    wanted_data["data"][conduit.full_name][
                                        soul_bind.covenant.full_name
                                    ][rank],
                                )
                                for conduit in conduits
                                if conduit.is_potency
                                and soul_bind.covenant in conduit.covenants
                            ]
                            winner = max(potencies, key=lambda key_value: key_value[1])
                            dps_values.append(
                                wanted_data["data"][winner[0].full_name][
                                    soul_bind.covenant.full_name
                                ][rank]
                            )
                            purged_path.append(winner[0].full_name)

                        # compare only dps gains, without baseline dps
                        dps_paths.append(
                            (
                                path,
                                sum(
                                    map(
                                        lambda value: value
                                        - wanted_data["data"]["baseline"][
                                            soul_bind.covenant.full_name
                                        ],
                                        dps_values,
                                    )
                                ),
                                purged_path,
                            )
                        )

                    winner = max(dps_paths, key=lambda key_value: key_value[1])

                    wanted_data["soul_bind_paths"][rank][soul_bind.full_name] = winner[
                        2
                    ]
                    # add soul bind dps to "data"
                    if soul_bind.full_name not in wanted_data["data"]:
                        wanted_data["data"][soul_bind.full_name] = {}
                    wanted_data["data"][soul_bind.full_name][rank] = (
                        winner[1]
                        + wanted_data["data"]["baseline"][soul_bind.covenant.full_name]
                    )

                    soul_bind_dps.append(
                        (
                            soul_bind.full_name,
                            wanted_data["data"][soul_bind.full_name][rank],
                        )
                    )
                ordered_soul_binds = sorted(
                    soul_bind_dps, key=lambda e: e[1], reverse=True
                )
                wanted_data["sorted_data_keys"][rank] = [
                    soul_bind[0] for soul_bind in ordered_soul_binds
                ]

            # create ordered soul bind name list
            for rank in ranks:
                for covenant in COVENANTS:

                    tmp_list = []
                    for talent in wanted_data["data"]:
                        if "baseline" in talent:
                            continue

                        if "+" in talent:
                            continue

                        try:
                            tmp_list.append(
                                (
                                    talent,
                                    wanted_data["data"][talent][covenant.full_name][
                                        rank
                                    ]
                                    - wanted_data["data"]["baseline"][
                                        covenant.full_name
                                    ],
                                )
                            )
                        except TypeError:
                            tmp_list.append(
                                (
                                    talent,
                                    wanted_data["data"][talent][covenant.full_name]
                                    - wanted_data["data"][f"baseline"][
                                        covenant.full_name
                                    ],
                                )
                            )
                        except KeyError:
                            continue
                    logger.debug(
                        "tmp_list for covenant {}: {}".format(
                            covenant.full_name, tmp_list
                        )
                    )

                    tmp_list = sorted(tmp_list, key=lambda item: item[1], reverse=True)
                    logger.debug("Sorted tmp_list: {}".format(tmp_list))
                    logger.info(
                        "Soul Bind Talent '{}' ({}) won with {} dps.".format(
                            tmp_list[0][0], covenant.full_name, tmp_list[0][1]
                        )
                    )

                    wanted_data[f"sorted_data_keys_{covenant.simc_name}_{rank}"] = [
                        soul_bind for soul_bind, _ in tmp_list
                    ]

            logger.debug("Final json: {}".format(wanted_data))

            path = "results/soul_binds/"
            if not os.path.isdir(path):
                os.makedirs(path)

            # write json to file
            with open(
                "{}{}_{}_{}.json".format(
                    path,
                    wow_spec.wow_class.simc_name,
                    wow_spec.simc_name,
                    fight_style.lower(),
                ),
                "w",
                encoding="utf-8",
            ) as f:
                logger.debug("Print soul bind json.")
                f.write(
                    json.dumps(
                        wanted_data,
                        sort_keys=True,
                        indent=4 if settings.pretty else None,
                        ensure_ascii=False,
                    )
                )
                logger.debug("Printed soul bind json.")

    logger.debug("soul_bind_simulations ended")

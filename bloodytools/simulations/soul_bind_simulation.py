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

CONDUITMAXRANK = 7
ranks = [
    7,
]  # list(range(1, CONDUITMAXRANK + 1))


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
                "Soul Binds",
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

            wanted_data["soul_bind_paths"] = {}
            for soul_bind in SOULBINDS:
                wanted_data["soul_bind_paths"][soul_bind.full_name] = [
                    [talent.full_name for talent in path]
                    for path in soul_bind.talent_paths
                ]
                wanted_data["translations"][
                    soul_bind.full_name
                ] = soul_bind.translations.get_dict()

            wanted_data["covenant_mapping"] = {}
            wanted_data["spell_ids"] = {}
            for node in nodes:
                wanted_data["translations"][
                    node.full_name
                ] = node.translations.get_dict()
                wanted_data["spell_ids"][node.full_name] = node.spell_id
                wanted_data["covenant_mapping"][node.full_name] = [
                    node.soul_bind.covenant.id
                ]

            conduits = get_conduits_for_spec(wow_spec)
            for conduit in conduits:
                wanted_data["translations"][
                    conduit.full_name
                ] = conduit.translations.get_dict()
                wanted_data["spell_ids"][conduit.full_name] = conduit.spell_id
                wanted_data["covenant_mapping"][conduit.full_name] = list(
                    [conduit.id for conduit in conduit.covenants]
                )

            simulation_group = Simulation_Group(
                name="soul_bind_simulation",
                threads=settings.threads,
                profileset_work_threads=settings.profileset_work_threads,
                executable=settings.executable,
            )

            for covenant in COVENANTS:
                simulation_data = None

                simulation_data = Simulation_Data(
                    name=f"baseline_{covenant.id}",
                    fight_style=fight_style,
                    profile=wanted_data["profile"],
                    simc_arguments=[
                        f"covenant={covenant.simc_name}",
                        "soulbind=",
                    ],
                    target_error=settings.target_error[fight_style],
                    ptr=settings.ptr,
                    default_actions=settings.default_actions,
                    executable=settings.executable,
                    iterations=settings.iterations,
                )

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
                    target_error=settings.target_error[fight_style],
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
                            target_error=settings.target_error[fight_style],
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
                                target_error=settings.target_error[fight_style],
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
                "Start {} soul bind node simulation for {}.".format(
                    fight_style, wow_spec
                )
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
                    "{} soul bind node simulation for {} failed. {}".format(
                        fight_style.title(), wow_spec, e
                    )
                )
                continue
            else:
                logger.info(
                    "{} soul bind node simulation for {} ended successfully. Cleaning up.".format(
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
                        indent=4,
                        ensure_ascii=False,
                    )
                )
                logger.debug("Printed soul bind json.")

    logger.debug("soul_bind_simulations ended")

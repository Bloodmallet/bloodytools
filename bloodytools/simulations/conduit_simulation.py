import json
import logging
import os

from bloodytools.utils.utils import create_basic_profile_string, create_base_json_dict
from bloodytools.utils.simulation_objects import Simulation_Group, Simulation_Data

from simc_support.game_data.Covenant import COVENANTS
from simc_support.game_data.Conduit import get_conduits_for_spec
from simc_support.game_data.WowSpec import WowSpec
from typing import List

logger = logging.getLogger(__name__)


def conduit_simulation(settings: object) -> None:
    """Simulates dps nodes of all dps conduits.

    Arguments:
        specs {List[Tuple[str, str]]} -- List of all wanted wow_specs

    Returns:
        None --
    """
    logger.debug("conduit_simulation start")

    specs: List[WowSpec] = settings.wow_class_spec_list

    for fight_style in settings.fight_styles:
        for wow_spec in specs:

            CONDUITS = get_conduits_for_spec(wow_spec)

            # prepare result json
            wanted_data = create_base_json_dict(
                "Conduits",
                wow_spec,
                fight_style,
                settings,
            )

            wanted_data["spell_ids"] = {}
            wanted_data["covenant_mapping"] = {}
            for conduit in CONDUITS:
                wanted_data["translations"][
                    conduit.full_name
                ] = conduit.translations.get_dict()
                wanted_data["spell_ids"][conduit.full_name] = conduit.spell_id
                if len(conduit.covenants) == 1:
                    wanted_data["covenant_mapping"][
                        conduit.full_name
                    ] = conduit.covenants[0].id
                else:
                    wanted_data["covenant_mapping"][conduit.full_name] = 0

            simulation_group = Simulation_Group(
                name="conduit_simulation",
                threads=settings.threads,
                profileset_work_threads=settings.profileset_work_threads,
                executable=settings.executable,
            )

            simulation_data = Simulation_Data(
                name="baseline_0",
                fight_style=fight_style,
                profile=wanted_data["profile"],
                simc_arguments=["covenant=none", "soulbind="],
                target_error=settings.target_error.get(fight_style, "0.1"),
                ptr=settings.ptr,
                default_actions=settings.default_actions,
                executable=settings.executable,
                iterations=settings.iterations,
            )
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

            for covenant in COVENANTS:
                simulation_data = None

                simulation_data = Simulation_Data(
                    name=f"baseline_{covenant.id}",
                    fight_style=fight_style,
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

                simulation_group.add(simulation_data)
                logger.debug(
                    (
                        "Added covenant base profile '{}' in profile '{}' to simulation_group.".format(
                            covenant.full_name, simulation_data.name
                        )
                    )
                )

            wanted_data["simulated_steps"] = []
            for conduit in CONDUITS:
                for rank in conduit.ranks:

                    if rank not in wanted_data["simulated_steps"]:
                        wanted_data["simulated_steps"] = [rank] + wanted_data[
                            "simulated_steps"
                        ]

                    simulation_data = None

                    covenant_name = (
                        "none"
                        if len(conduit.covenants) > 1
                        else conduit.covenants[0].simc_name
                    )

                    simulation_data = Simulation_Data(
                        name=f"{conduit.full_name}_{rank}",
                        fight_style=fight_style,
                        simc_arguments=[
                            f"covenant={covenant_name}",
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
                            "Added conduit '{}' in profile '{}' to simulation_group.".format(
                                conduit.full_name, simulation_data.name
                            )
                        )
                    )

            logger.info(
                "Start {} conduit simulation for {}.".format(fight_style, wow_spec)
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
                    "{} conduit simulation for {} failed. {}".format(
                        fight_style.title(), wow_spec, e
                    )
                )
                continue
            else:
                logger.info(
                    "{} conduit simulation for {} ended successfully. Cleaning up.".format(
                        fight_style.title(), wow_spec
                    )
                )

            for profile in simulation_group.profiles:
                logger.debug(f"Profile '{profile.name}' DPS: {profile.get_dps()}")
                name = profile.name.split("_")[0]
                rank = int(profile.name.split("_")[1])
                if not name in wanted_data["data"]:
                    wanted_data["data"][name] = {}
                wanted_data["data"][name][rank] = profile.get_dps()

            logger.debug("Created base dict for json export. {}".format(wanted_data))

            # create ordered conduit name list
            tmp_list = []
            for conduit in wanted_data["data"]:
                if "baseline" in conduit:
                    continue
                tmp_list.append(
                    (
                        conduit,
                        wanted_data["data"][conduit][
                            max(wanted_data["data"][conduit].keys())
                        ],
                    )
                )
            logger.debug("tmp_list: {}".format(tmp_list))

            tmp_list = sorted(tmp_list, key=lambda item: item[1], reverse=True)
            logger.debug("Sorted tmp_list: {}".format(tmp_list))
            logger.info(
                "Conduit '{}' won with {} dps.".format(tmp_list[0][0], tmp_list[0][1])
            )

            wanted_data["sorted_data_keys"] = [conduit for conduit, _ in tmp_list]

            logger.debug("Final json: {}".format(wanted_data))

            path = "results/conduits/"
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
                logger.debug("Print conduit json.")
                f.write(
                    json.dumps(
                        wanted_data,
                        sort_keys=True,
                        indent=4 if settings.pretty else None,
                        ensure_ascii=False,
                    )
                )
                logger.debug("Printed conduit json.")

    logger.debug("conduit_simulation ended")

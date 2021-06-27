import json
import logging
import os
import typing

from bloodytools.utils.utils import create_base_json_dict
from bloodytools.utils.simulation_objects import Simulation_Group, Simulation_Data

from simc_support.game_data.Covenant import COVENANTS, Covenant
from simc_support.game_data.Conduit import Conduit, get_conduits_for_spec
from simc_support.game_data.WowSpec import WowSpec
from typing import List

logger = logging.getLogger(__name__)


def _get_covenant_specific_conduits(
    covenant: Covenant, wow_spec: WowSpec
) -> typing.List[Conduit]:
    conduits = []
    for conduit in get_conduits_for_spec(wow_spec):
        if covenant in conduit.covenants and len(conduit.covenants) == 1:
            conduits.append(conduit)
    return conduits


def covenant_simulation(settings: object) -> None:
    """Simulates dps nodes of all covenant abilities and their specific conduits.

    Arguments:
        settings {object} --

    Returns:
        None --
    """
    logger.debug("covenant_simulation start")

    specs: List[WowSpec] = settings.wow_class_spec_list

    for fight_style in settings.fight_styles:
        for wow_spec in specs:

            # prepare result json
            wanted_data = create_base_json_dict(
                "Covenants",
                wow_spec,
                fight_style,
                settings,
            )

            wanted_data["profile"]["character"].pop("covenant", None)
            wanted_data["profile"]["character"].pop("soulbind", None)

            for covenant in COVENANTS:
                wanted_data["translations"][
                    covenant.full_name
                ] = covenant.translations.get_dict()

            simulation_group = Simulation_Group(
                name="covenants_simulation",
                threads=settings.threads,
                profileset_work_threads=settings.profileset_work_threads,
                executable=settings.executable,
            )

            simulation_data = Simulation_Data(
                name="baseline",
                fight_style=fight_style,
                profile=wanted_data["profile"],
                simc_arguments=[
                    "covenant=none",
                    "soulbind=",
                ],
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
                    name=covenant.full_name,
                    fight_style=fight_style,
                    simc_arguments=[
                        f"covenant={covenant.simc_name}",
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
                        "Added covenant '{}' in profile '{}' to simulation_group.".format(
                            covenant.full_name, simulation_data.name
                        )
                    )
                )

                for conduit in _get_covenant_specific_conduits(covenant, wow_spec):
                    # covenant conduit
                    simulation_data = Simulation_Data(
                        name=f"{covenant.full_name} +{conduit.full_name}",
                        fight_style=fight_style,
                        simc_arguments=[
                            f"covenant={covenant.simc_name}",
                            f"soulbind={conduit.id}:6",
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
                            "Added covenant '{}' in profile '{}' to simulation_group.".format(
                                covenant.full_name, simulation_data.name
                            )
                        )
                    )

            logger.info(
                "Start {} covenant simulation for {}.".format(fight_style, wow_spec)
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
                    "{} covenant simulation for {} failed. {}".format(
                        fight_style.title(), wow_spec, e
                    )
                )
                continue
            else:
                logger.info(
                    "{} covenant simulation for {} ended successfully. Cleaning up.".format(
                        fight_style.title(), wow_spec
                    )
                )

            for profile in simulation_group.profiles:
                logger.debug(f"Profile '{profile.name}' DPS: {profile.get_dps()}")

            logger.debug("Created base dict for json export. {}".format(wanted_data))

            # add dps values to json
            for profile in simulation_group.profiles:
                wanted_data["data"][profile.name] = profile.get_dps()
                logger.debug(
                    "Added '{}' with {} dps to json.".format(
                        profile.name, profile.get_dps()
                    )
                )

            # create ordered soul bind name list
            tmp_list = []
            for covenant in wanted_data["data"]:
                tmp_list.append((covenant, wanted_data["data"][covenant]))
            logger.debug("tmp_list: {}".format(tmp_list))

            filtered_tmp_list = [data for data in tmp_list if "baseline" != data[0]]

            tmp_list = sorted(filtered_tmp_list, key=lambda item: item[1], reverse=True)
            logger.debug("Sorted tmp_list: {}".format(tmp_list))
            logger.info(
                "Covenant '{}' won with {} dps.".format(tmp_list[0][0], tmp_list[0][1])
            )

            wanted_data["sorted_data_keys"] = [covenant for covenant, _ in tmp_list]

            logger.debug("Final json: {}".format(wanted_data))

            path = "results/covenants/"
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
                logger.debug("Print covenant json.")
                f.write(
                    json.dumps(
                        wanted_data,
                        sort_keys=True,
                        indent=4 if settings.pretty else None,
                        ensure_ascii=False,
                    )
                )
                logger.debug("Printed covenant json.")

    logger.debug("covenant_simulation ended")

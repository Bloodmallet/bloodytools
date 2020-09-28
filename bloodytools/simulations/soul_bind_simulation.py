import json
import logging
import os

from bloodytools.utils.utils import create_basic_profile_string, create_base_json_dict
from bloodytools.utils.simulation_objects import Simulation_Group, Simulation_Data

from simc_support.game_data.SoulBind import SOULBINDS, SoulBindTalent
from simc_support.game_data.WowSpec import WowSpec
from typing import List

logger = logging.getLogger(__name__)


def soul_bind_simulation(settings: object) -> None:
    """Simulates dps nodes of all soul binds.

    Arguments:
        specs {List[Tuple[str, str]]} -- List of all wanted wow_specs

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

            # check whether the baseline profile does exist
            try:
                with open(
                    create_basic_profile_string(wow_spec, settings.tier, settings), "r"
                ) as f:
                    pass
            except FileNotFoundError:
                logger.warning("{} base profile not found. Skipping.".format(wow_spec))
                continue

            # prepare result json
            wanted_data = create_base_json_dict(
                "Soul Binds",
                wow_spec,
                fight_style,
                settings,
            )

            simulation_group = Simulation_Group(
                name="soul_bind_simulation",
                threads=settings.threads,
                profileset_work_threads=settings.profileset_work_threads,
                executable=settings.executable,
            )

            simulation_data = Simulation_Data(
                name="baseline",
                fight_style=fight_style,
                profile=wanted_data["profile"],
                simc_arguments=["soulbind="],
                target_error=settings.target_error[fight_style],
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
                simulation_data.simc_arguments.append(custom_apl)

            custom_fight_style = None
            if settings.custom_fight_style:
                with open("custom_fight_style.txt") as f:
                    custom_fight_style = f.read()
            if custom_fight_style:
                simulation_data.simc_arguments.append(custom_fight_style)

            simulation_group.add(simulation_data)

            for node in nodes:

                simulation_data = None

                simulation_data = Simulation_Data(
                    name=node.full_name,
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

            for profile in simulation_group.profiles:
                logger.debug(f"Profile '{profile.name}' DPS: {profile.get_dps()}")

            logger.debug("Created base dict for json export. {}".format(wanted_data))

            wanted_data["spell_ids"] = {}
            # add dps values to json
            for profile in simulation_group.profiles:
                wanted_data["data"][profile.name] = profile.get_dps()
                logger.debug(
                    "Added '{}' with {} dps to json.".format(
                        profile.name, profile.get_dps()
                    )
                )

                if "baseline" in profile.name:
                    continue

                node: SoulBindTalent = None
                for element in nodes:
                    if element.full_name == profile.name:
                        node = element
                # add soul bind translations to the final json
                wanted_data["languages"][profile.name] = node.translations.get_dict()
                wanted_data["spell_ids"][profile.name] = node.spell_id

            # create ordered soul bind name list
            tmp_list = []
            for soul_bind in wanted_data["data"]:
                tmp_list.append((soul_bind, wanted_data["data"][soul_bind]))
            logger.debug("tmp_list: {}".format(tmp_list))

            tmp_list = sorted(tmp_list, key=lambda item: item[1], reverse=True)
            logger.debug("Sorted tmp_list: {}".format(tmp_list))
            logger.info(
                "Soul Bind Node '{}' won with {} dps.".format(
                    tmp_list[0][0], tmp_list[0][1]
                )
            )

            wanted_data["sorted_data_keys"] = [soul_bind for soul_bind, _ in tmp_list]

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

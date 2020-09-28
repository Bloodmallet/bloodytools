import json
import logging
import os

from simc_support.game_data.Legendary import Legendary, get_legendaries_for_spec

from bloodytools.utils.utils import create_basic_profile_string, create_base_json_dict
from bloodytools.utils.simulation_objects import Simulation_Group, Simulation_Data
from typing import List
from simc_support.game_data.WowSpec import WowSpec

logger = logging.getLogger(__name__)


def legendary_simulation(settings) -> None:
    """Simulates all available legendaries for all given specs.

    Arguments:
        settings {object} -- see settings.py

    Returns:
        None --
    """
    logger.debug("legendary_simulation start")

    specs: List[WowSpec] = settings.wow_class_spec_list

    for fight_style in settings.fight_styles:
        for wow_spec in specs:
            wow_class = wow_spec.wow_class
            # check whether the baseline profile does exist
            try:
                with open(
                    create_basic_profile_string(wow_spec, settings.tier, settings),
                    "r",
                ) as f:
                    pass
            except FileNotFoundError:
                logger.warning("{} base profile not found. Skipping.".format(wow_spec))
                continue

            # prepare result json
            wanted_data = create_base_json_dict(
                "Legendaries", wow_spec, fight_style, settings
            )

            legendaries = get_legendaries_for_spec(wow_spec=wow_spec)

            bonus_ids = list([legendary.bonus_id for legendary in legendaries])

            # remove any existing legendary effects
            for item in wanted_data["profile"]["items"]:
                item_bonus_ids: List[str] = None
                try:
                    item_bonus_ids = wanted_data["profile"]["items"][item][
                        "bonus_id"
                    ].split("/")
                except KeyError:
                    continue
                item_bonus_ids = [
                    b_id for b_id in item_bonus_ids if not int(b_id) in bonus_ids
                ]

                wanted_data["profile"]["items"][item]["bonus_id"] = "/".join(
                    item_bonus_ids
                )

            simulation_group = Simulation_Group(
                name="legendary_simulations",
                threads=settings.threads,
                profileset_work_threads=settings.profileset_work_threads,
                executable=settings.executable,
                logger=logger,
            )

            item_information = wanted_data["profile"]["items"]["head"]
            constructed_item = f"head=,id={item_information['id']}"
            if "enchant" in item_information:
                constructed_item += f",enchant={item_information['enchant']}"
            if "ilevel" in item_information:
                constructed_item += f",ilevel={item_information['ilevel']}"
            try:
                constructed_item += f",bonus_id={item_information['bonus_id']}"
            except KeyError:
                constructed_item += f",bonus_id="

            simulation_data = Simulation_Data(
                name="baseline",
                fight_style=fight_style,
                profile=wanted_data["profile"],
                simc_arguments=[f"{constructed_item}"],
                target_error=settings.target_error[fight_style],
                ptr=settings.ptr,
                default_actions=settings.default_actions,
                executable=settings.executable,
                iterations=settings.iterations,
                logger=logger,
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

            for legendary in legendaries:

                simulation_data = None

                simulation_data = Simulation_Data(
                    name=legendary.full_name,
                    fight_style=fight_style,
                    simc_arguments=[f"{constructed_item}/{legendary.bonus_id}"],
                    target_error=settings.target_error[fight_style],
                    ptr=settings.ptr,
                    default_actions=settings.default_actions,
                    executable=settings.executable,
                    iterations=settings.iterations,
                    logger=logger,
                )

                simulation_group.add(simulation_data)
                logger.debug(
                    (
                        "Added legendary '{}' in profile '{}' to simulation_group.".format(
                            legendary.full_name, simulation_data.name
                        )
                    )
                )

            logger.info(
                "Start {} legendary simulation for {}.".format(fight_style, wow_spec)
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
                    "{} legendary simulation for {} failed. {}".format(
                        fight_style.title(), wow_spec, e
                    )
                )
                continue
            else:
                logger.info(
                    "{} legendary simulation for {} ended successfully. Cleaning up.".format(
                        fight_style.title(), wow_spec
                    )
                )

            for profile in simulation_group.profiles:
                logger.debug(
                    "Profile '{}' DPS: {}".format(profile.name, profile.get_dps())
                )

            logger.debug("Created base dict for json export. {}".format(wanted_data))

            # add dps values to json
            for profile in simulation_group.profiles:
                wanted_data["data"][profile.name] = profile.get_dps()
                logger.debug(
                    "Added '{}' with {} dps to json.".format(
                        profile.name, profile.get_dps()
                    )
                )

                legendary: Legendary = None
                for element in legendaries:
                    if element.full_name == profile.name:
                        legendary = element

                # add legendary translations to the final json
                if not "baseline" in profile.name:
                    translated_name = legendary.translations.get_dict()
                    wanted_data["languages"][profile.name] = translated_name

            # create ordered legendary name list
            tmp_list = []
            for legendary in wanted_data["data"]:
                tmp_list.append((legendary, wanted_data["data"][legendary]))
            logger.debug("tmp_list: {}".format(tmp_list))

            tmp_list = sorted(tmp_list, key=lambda item: item[1], reverse=True)
            logger.debug("Sorted tmp_list: {}".format(tmp_list))
            logger.info(
                "Legendary {} won with {} dps.".format(tmp_list[0][0], tmp_list[0][1])
            )

            wanted_data["sorted_data_keys"] = []
            for legendary, _ in tmp_list:
                wanted_data["sorted_data_keys"].append(legendary)

            logger.debug("Final json: {}".format(wanted_data))

            path = "results/legendaries/"
            if not os.path.isdir(path):
                os.makedirs(path)

            # write json to file
            with open(
                "{}{}_{}_{}.json".format(
                    path, wow_class.simc_name, wow_spec.simc_name, fight_style.lower()
                ),
                "w",
                encoding="utf-8",
            ) as f:
                logger.debug("Print legendary json.")
                f.write(
                    json.dumps(
                        wanted_data, sort_keys=True, indent=4, ensure_ascii=False
                    )
                )
                logger.debug("Printed legendary json.")

    logger.debug("legendary_simulation ended")

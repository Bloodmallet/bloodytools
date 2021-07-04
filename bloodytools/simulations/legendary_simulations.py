import json
import logging
import os
import pkg_resources
import yaml


from bloodytools.utils.simulation_objects import Simulation_Group, Simulation_Data
from bloodytools.utils.utils import create_base_json_dict

from simc_support.game_data.Legendary import Legendary, get_legendaries_for_spec
from simc_support.game_data.WowSpec import get_wow_spec, WowSpec

from typing import List
import typing

logger = logging.getLogger(__name__)


def _load_special_cases():
    try:
        with pkg_resources.resource_stream(
            __name__, "/".join(("legendary_special_cases.yml",))
        ) as f:
            LOADED_SPECIAL_CASES = yaml.safe_load(f)
    except FileNotFoundError as e:
        logger.warning(e)
        LOADED_SPECIAL_CASES = {}

    SPECIAL_CASES = {}
    for wow_class in LOADED_SPECIAL_CASES.keys():
        for wow_spec in LOADED_SPECIAL_CASES[wow_class].keys():
            SPECIAL_CASES[get_wow_spec(wow_class, wow_spec)] = LOADED_SPECIAL_CASES[
                wow_class
            ][wow_spec]

    return SPECIAL_CASES


def remove_legendary_bonus_ids(
    profile: dict, unwanted_ids: typing.Iterable[int]
) -> dict:
    for item in profile["items"]:
        item_bonus_ids: List[str] = []
        try:
            tmp_item_bonus_ids = profile["items"][item]["bonus_id"].split("/")
        except KeyError:
            continue
        for element in tmp_item_bonus_ids:
            for b_id in element.split(":"):
                item_bonus_ids.append(b_id)

        filtered_item_bonus_ids = [
            b_id for b_id in item_bonus_ids if not int(b_id) in unwanted_ids
        ]

        profile["items"][item]["bonus_id"] = "/".join(filtered_item_bonus_ids)

    return profile


# spell ids
UNWANTED_LEGENDARIES = [
    339340,  # Norgannon's Sagacity
    339351,  # Stable Phantasma Lure
    338743,  # Vitality Sacrifice
]


def legendary_simulation(settings) -> None:
    """Simulates all available legendaries for all given specs.

    Arguments:
        settings {object} -- see settings.py

    Returns:
        None --
    """
    logger.debug("legendary_simulation start")

    SPECIAL_CASES = _load_special_cases()

    specs: List[WowSpec] = settings.wow_class_spec_list

    for fight_style in settings.fight_styles:
        for wow_spec in specs:
            wow_class = wow_spec.wow_class

            # prepare result json
            wanted_data = create_base_json_dict(
                "Legendaries", wow_spec, fight_style, settings
            )

            legendaries = get_legendaries_for_spec(wow_spec=wow_spec)

            legendaries = list(
                [
                    legendary
                    for legendary in legendaries
                    if legendary.spell_id not in UNWANTED_LEGENDARIES
                ]
            )

            bonus_ids = list([legendary.bonus_id for legendary in legendaries])

            wanted_data["profile"] = remove_legendary_bonus_ids(
                wanted_data["profile"], bonus_ids
            )
            for profile in wanted_data["covenant_profiles"]:
                wanted_data["covenant_profiles"][profile] = remove_legendary_bonus_ids(
                    wanted_data["covenant_profiles"][profile], bonus_ids
                )

            wanted_data["spell_ids"] = {}
            for legendary in legendaries:
                wanted_data["translations"][
                    legendary.full_name
                ] = legendary.translations.get_dict()
                wanted_data["spell_ids"][legendary.full_name] = legendary.spell_id

            simulation_group = Simulation_Group(
                name="legendary_simulations",
                threads=settings.threads,
                profileset_work_threads=settings.profileset_work_threads,
                executable=settings.executable,
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

            for covenant in wanted_data["covenant_profiles"]:
                simulation_data = Simulation_Data(
                    name=f"{{{covenant}}}",
                    fight_style=fight_style,
                    profile=wanted_data["covenant_profiles"][covenant],
                    simc_arguments=[f"{constructed_item}"],
                    target_error=settings.target_error.get(fight_style, "0.1"),
                    ptr=settings.ptr,
                    default_actions=settings.default_actions,
                    executable=settings.executable,
                    iterations=settings.iterations,
                )
                simulation_group.add(simulation_data)

            for legendary in legendaries:

                simulation_data = None

                profile = {}
                profile_name = legendary.full_name
                if (
                    len(legendary.covenants) == 1
                    and legendary.covenants[0].simc_name
                    in wanted_data["covenant_profiles"]
                ):
                    profile_name = (
                        f"{{{legendary.covenants[0].simc_name}}} {legendary.full_name}"
                    )
                    profile = wanted_data["covenant_profiles"][
                        legendary.covenants[0].simc_name
                    ]

                simulation_data = Simulation_Data(
                    name=profile_name,
                    fight_style=fight_style,
                    simc_arguments=[f"{constructed_item}/{legendary.bonus_id}"],
                    target_error=settings.target_error.get(fight_style, "0.1"),
                    ptr=settings.ptr,
                    default_actions=settings.default_actions,
                    executable=settings.executable,
                    iterations=settings.iterations,
                    profile=profile,
                )

                simulation_group.add(simulation_data)
                logger.debug(
                    (
                        "Added legendary '{}' in profile '{}' to simulation_group.".format(
                            legendary.full_name, simulation_data.name
                        )
                    )
                )

                if wow_spec in SPECIAL_CASES:
                    for special_case in SPECIAL_CASES[wow_spec]:
                        if special_case["name"] == legendary.full_name:
                            new_profile = simulation_data.copy()
                            name_addition = (
                                "[" + "+".join(special_case["name_additions"]) + "] "
                            )
                            new_name = name_addition + new_profile.name
                            new_profile.name = new_name
                            new_profile.simc_arguments += special_case["overrides"]
                            simulation_group.add(new_profile)
                            wanted_data["translations"][
                                new_name
                            ] = legendary.translations.get_dict()
                            for language in wanted_data["translations"][
                                new_name
                            ].keys():
                                wanted_data["translations"][new_name][language] = (
                                    name_addition
                                    + wanted_data["translations"][new_name][language]
                                )
                            wanted_data["spell_ids"][new_name] = legendary.spell_id

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

            # create ordered legendary name list
            tmp_list = []
            for legendary in wanted_data["data"]:
                tmp_list.append((legendary, wanted_data["data"][legendary]))
            logger.debug("tmp_list: {}".format(tmp_list))

            # remove baseline and covenant profiles
            filtered_tmp_list = [
                element
                for element in tmp_list
                if "baseline" not in element[0] and "}" != element[0][-1]
            ]

            tmp_list = sorted(filtered_tmp_list, key=lambda item: item[1], reverse=True)
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
                        wanted_data,
                        sort_keys=True,
                        indent=4 if settings.pretty else None,
                        ensure_ascii=False,
                    )
                )
                logger.debug("Printed legendary json.")

    logger.debug("legendary_simulation ended")

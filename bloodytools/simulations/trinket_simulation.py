import json
import logging
import os

from bloodytools.utils.simulation_objects import Simulation_Data, Simulation_Group
from bloodytools.utils.utils import create_base_json_dict, create_basic_profile_string
from simc_support.game_data.Trinket import (
    Trinket,
    get_trinkets_for_spec,
    get_versatility_trinket,
)
from typing import List, Tuple
from simc_support.game_data.WowSpec import WowSpec

logger = logging.getLogger(__name__)


def _get_translation(trinkets: List[Trinket], name: str) -> dict:
    for trinket in trinkets:
        if trinket.translations.US == name:
            return trinket.translations.get_dict()


def _get_trinket(trinkets: List[Trinket], name: str) -> Trinket:
    for trinket in trinkets:
        if trinket.translations.US == name:
            return trinket
    raise ValueError(f"No trinket found with name '{name}'.")


def _is_valid_itemlevel(itemlevel: int, settings: object) -> bool:
    return itemlevel >= settings.min_ilevel and itemlevel <= settings.max_ilevel


# def _export_to_lua():
#     # LUA data exporter
#     if fight_style.lower() == "patchwerk" and settings.lua_trinket_export:
#         human_readable = False
#         item_dict = {}     # intended structure: itemID -> class -> spec -> itemlevel

#         for wow_class in simulation_results:
#             wow_class_id = wow_class if human_readable else wow_lib.get_class_id(
#                 wow_class)

#             for wow_spec in simulation_results[wow_class]:
#                 wow_spec_id = wow_spec if human_readable else wow_lib.get_spec_id(
#                     wow_class, wow_spec
#                 )

#                 for profile in simulation_results[wow_class][wow_spec].profiles:
#                     if profile.name != "baseline {}".format(settings.min_ilevel):
#                         name = profile.name[:profile.name.rfind(" ")]
#                         ilevel = int(
#                             profile.name[profile.name.rfind(" ") + 1:])

#                         item_id = name if human_readable else wow_lib.get_trinket_id(
#                             name)

#                         if not item_id in item_dict:
#                             item_dict[item_id] = {}

#                         if not wow_class_id in item_dict[item_id]:
#                             item_dict[item_id][wow_class_id] = {}

#                         if not wow_spec_id in item_dict[item_id][wow_class_id]:
#                             item_dict[item_id][wow_class_id][wow_spec_id] = {}

#                         item_dict[item_id][wow_class_id][wow_spec_id][
#                             ilevel] = profile.get_dps(
#                         ) - simulation_results[wow_class][wow_spec].get_dps_of(
#                                 "baseline {}".format(settings.min_ilevel)
#                         )

#         logger.debug("item_dict: {}".format(item_dict))

#         # enhance item_dict with missing itemlevels
#         if settings.ilevel_step != 5:
#             for item in item_dict:
#                 for wow_class in item_dict[item]:
#                     for wow_spec in item_dict[item][wow_class]:

#                         trinket = item_dict[item][wow_class][wow_spec]

#                         # skip creating additions to the lua file if increase cant be calculated
#                         if len(trinket) < 2:
#                             continue

#                         # get average dps increase
#                         dps_sum = 0
#                         lower_dps = 0
#                         itemlevels_counted = 0
#                         for itemlevel in range(
#                             settings.min_ilevel, settings.max_ilevel + 1, 5
#                         ):
#                             if itemlevel in trinket:
#                                 if lower_dps:
#                                     dps_sum += trinket[itemlevel] - \
#                                         lower_dps
#                                     itemlevels_counted += 1
#                                 lower_dps = trinket[itemlevel]

#                         logger.debug(
#                             "Item: {}, dps_sum: {}, itemlevels_counted: {}, settings.ilevel_step: {}"
#                             .format(item, dps_sum, itemlevels_counted, settings.ilevel_step)
#                         )

#                         average_increase = int(
#                             dps_sum / itemlevels_counted /
#                             (settings.ilevel_step / 5)
#                         )

#                         logger.debug(
#                             "Item {} has {} counted ilevel differences. Average dps increase is {}"
#                             .format(item, itemlevels_counted, average_increase)
#                         )

#                         try:
#                             trinket_data = wow_lib.get_trinket(
#                                 item_id=item)
#                         except Exception:
#                             # failes due to the human readability check
#                             trinket_data = wow_lib.get_trinket(name=item)

#                         for itemlevel in range(settings.min_ilevel, settings.max_ilevel, 5):
#                             # if itemlevel is valid for that item
#                             if itemlevel >= trinket_data.min_itemlevel and itemlevel <= trinket_data.max_itemlevel:
#                                 # if itemlevel is missing, we add it
#                                 if not itemlevel in trinket:
#                                     # is able to catch up to +15 ilevel steps
#                                     try:
#                                         trinket[itemlevel] = trinket[itemlevel -
#                                                                      5] + average_increase
#                                     except Exception:
#                                         trinket[itemlevel] = trinket[itemlevel +
#                                                                      5] - average_increase

#         if not item_dict:
#             continue

#         with open("results/trinkets/ItemDPS.lua", "w") as f:
#             logger.debug("Print trinket lua.")
#             f.write("-- itemID -> class -> spec -> itemlevel\n")
#             f.write("MoreItemInfo.Enum.ItemDPS = {\n")

#             for trinket in item_dict:
#                 f.write("{}[{}] = {{\n".format(" " * 4, trinket))

#                 for wow_class in item_dict[trinket]:
#                     f.write("{}[{}] = {{\n".format(" " * 8, wow_class))

#                     for wow_spec in item_dict[trinket][wow_class]:
#                         f.write("{}[{}] = {{\n".format(" " * 12, wow_spec))

#                         for itemlevel in item_dict[trinket][wow_class][wow_spec]:
#                             f.write(
#                                 "{}[{}] = {}".format(
#                                     " " * 16, itemlevel,
#                                     item_dict[trinket][wow_class][wow_spec][itemlevel]
#                                 )
#                             )

#                             if itemlevel == list(
#                                 item_dict[trinket][wow_class][wow_spec].keys()
#                             )[-1]:
#                                 f.write("\n")
#                             else:
#                                 f.write(",\n")

#                         if wow_spec == list(item_dict[trinket][wow_class].keys())[-1]:
#                             f.write("{}}}\n".format(" " * 12))
#                         else:
#                             f.write("{}}},\n".format(" " * 12))

#                     if wow_class == list(item_dict[trinket].keys())[-1]:
#                         f.write("{}}}\n".format(" " * 8))
#                     else:
#                         f.write("{}}},\n".format(" " * 8))

#                 if trinket == list(item_dict.keys())[-1]:
#                     f.write("{}}}\n".format(" " * 4))
#                 else:
#                     f.write("{}}},\n".format(" " * 4))
#             f.write("}\n")
#             logger.debug("Printed trinket lua.")


def trinket_simulation(settings: object) -> None:
    """Simulates all available trinkets to all given wow_classes and wow_specs.

    Arguments:
      settings {object} - loaded settings

    Raises:
      NotImplementedError -- [description]

    Returns:
      None -- [description]
    """
    specs: List[WowSpec] = settings.wow_class_spec_list

    logger.debug("trinket_simulations start")
    for fight_style in settings.fight_styles:
        simulation_results = {}
        for wow_spec in specs:

            # json exporter
            json_export = create_base_json_dict(
                "trinkets", wow_spec, fight_style, settings
            )

            # get main-trinkets
            trinket_list = get_trinkets_for_spec(wow_spec)
            # get secondary-trinket (standard stat stick)
            second_trinket = get_versatility_trinket(wow_spec.stat)

            # fix profile for this type of simulations
            json_export["profile"]["items"].pop("trinket1")
            json_export["profile"]["items"].pop("trinket2")
            json_export["profile"]["items"]["trinket2"] = {
                "id": second_trinket.item_id,
                "bonus_id": second_trinket.bonus_ids[0],
                "ilevel": str(settings.min_ilevel),
            }

            json_export["data_active"] = {}
            json_export["data_sources"] = {}
            json_export["item_ids"] = {}
            json_export["data"]["baseline"] = {}
            for trinket in trinket_list:
                json_export["translations"][
                    trinket.name
                ] = trinket.translations.get_dict()
                json_export["data"][trinket.name] = {}
                json_export["data_active"][trinket.name] = trinket.on_use
                json_export["data_sources"][trinket.name] = trinket.source.value
                json_export["item_ids"][trinket.name] = trinket.item_id

            if not wow_spec.wow_class.simc_name in simulation_results:
                simulation_results[wow_spec.wow_class.simc_name] = {}

            simulation_group = Simulation_Group(
                name="{} {}".format(wow_spec.wow_class.simc_name, wow_spec.simc_name),
                threads=settings.threads,
                profileset_work_threads=settings.profileset_work_threads,
                executable=settings.executable,
            )

            for trinket in trinket_list:

                if trinket == trinket_list[0]:
                    simulation_data = Simulation_Data(
                        name="baseline {}".format(settings.min_ilevel),
                        fight_style=fight_style,
                        iterations=settings.iterations,
                        target_error=settings.target_error[fight_style],
                        profile=json_export["profile"],
                        simc_arguments=[
                            "trinket1=",
                        ],
                        ptr=settings.ptr,
                        default_actions=settings.default_actions,
                        executable=settings.executable,
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

                # for each available itemlevel of the trinket
                for itemlevel in filter(
                    lambda x: _is_valid_itemlevel(x, settings), trinket.itemlevels
                ):

                    simulation_data = Simulation_Data(
                        name="{} {}".format(trinket.name, itemlevel),
                        fight_style=fight_style,
                        iterations=settings.iterations,
                        target_error=settings.target_error[fight_style],
                        simc_arguments=[
                            "trinket1=,id={},ilevel={}".format(
                                trinket.item_id, itemlevel
                            )
                        ],
                        ptr=settings.ptr,
                        default_actions=settings.default_actions,
                        executable=settings.executable,
                    )
                    simulation_group.add(simulation_data)

            # create and simulate baseline profile
            logger.info(
                "Start {} trinket simulation for {}.".format(fight_style, wow_spec)
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
                    "{} trinket simulation for {} failed. {}".format(
                        fight_style.title(), wow_spec, e
                    )
                )
                continue
            else:
                logger.info(
                    "{} trinket simulation for {} ended successfully. Cleaning up.".format(
                        fight_style.title(), wow_spec
                    )
                )
                logger.info(f"Profiles: {len(simulation_group.profiles)}")

            for profile in simulation_group.profiles:
                try:
                    logger.debug(
                        "{} {} DPS, baseline + {}".format(
                            profile.name,
                            profile.get_dps(),
                            profile.get_dps()
                            - simulation_group.get_dps_of(
                                "baseline {}".format(settings.min_ilevel)
                            ),
                        )
                    )
                except Exception as e:
                    logger.error(
                        'Exception was thrown when trying to fetch the following data from simulation_group: profile.name, profile.get_dps(), profile.get_dps() - simulation_group.get_dps_of("baseline {}".format(settings.min_ilevel))'
                    )
                    logger.debug("profile.name {}".format(profile.name))
                    logger.debug("profile.get_dps() {}".format(profile.get_dps()))
                    logger.debug("settings.min_ilevel {}".format(settings.min_ilevel))
                    logger.debug(
                        'simulation_group.get_dps_of("baseline {{}}".format(settings.min_ilevel)) {}'.format(
                            simulation_group.get_dps_of(
                                "baseline {}".format(settings.min_ilevel)
                            )
                        )
                    )

            simulation_results[wow_spec.wow_class.simc_name][
                wow_spec.simc_name
            ] = simulation_group

            for profile in simulation_group.profiles:

                full_name = profile.name[: profile.name.rfind(" ")]
                name = full_name.split("+")[0]
                ilevel = profile.name[profile.name.rfind(" ") + 1 :]
                try:
                    trinket = _get_trinket(trinket_list, name)
                except ValueError:
                    trinket = None

                json_export["data"][full_name][ilevel] = profile.get_dps()

            logger.debug("Enriched json export: {}".format(json_export))

            # create ordered trinket name list
            tmp_list = []
            for trinket in json_export["data"]:
                if trinket != "baseline":
                    tmp_list.append(
                        (trinket, max(json_export["data"][trinket].values()))
                    )
            logger.debug("tmp_list: {}".format(tmp_list))

            tmp_list = sorted(tmp_list, key=lambda item: item[1], reverse=True)
            logger.debug("Sorted tmp_list: {}".format(tmp_list))

            logger.info(
                "Trinket {} won with {} dps.".format(tmp_list[0][0], tmp_list[0][1])
            )

            json_export["sorted_data_keys"] = []
            for trinket, _ in tmp_list:
                json_export["sorted_data_keys"].append(trinket)

            # add itemlevel list
            json_export["simulated_steps"] = []
            for trinket in trinket_list:
                for itemlevel in filter(
                    lambda x: _is_valid_itemlevel(x, settings), trinket.itemlevels
                ):
                    json_export["simulated_steps"].append(itemlevel)

            json_export["simulated_steps"] = sorted(
                list(set(json_export["simulated_steps"]))
            )

            # change order from ascending to descending to keep the order of previous versions
            json_export["simulated_steps"].sort(reverse=True)

            if not os.path.isdir("results/trinkets/"):
                os.makedirs("results/trinkets/")

            # write json to file
            with open(
                "results/trinkets/{}_{}_{}.json".format(
                    wow_spec.wow_class.simc_name,
                    wow_spec.simc_name,
                    fight_style.lower(),
                ),
                "w",
                encoding="utf-8",
            ) as f:
                logger.debug("Print trinket json.")
                f.write(
                    json.dumps(
                        json_export, sort_keys=True, indent=4, ensure_ascii=False
                    )
                )
                logger.debug("Printed trinket json.")

    logger.debug("trinket_simulations ended")

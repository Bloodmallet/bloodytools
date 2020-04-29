import json
import os

from bloodytools.simulation_objects.simulation_objects import Simulation_Data, Simulation_Group
from bloodytools.utils.utils import create_base_json_dict, create_basic_profile_string
from simc_support import wow_lib
from simc_support.game_data import Source
from typing import List, Tuple


def trinket_simulation(settings: object) -> None:
    """Simulates all available trinkets to all given wow_classes and wow_specs.

  Arguments:
    settings {object} - loaded settings

  Raises:
    NotImplementedError -- [description]

  Returns:
    None -- [description]
  """

    logger = settings.logger

    specs: List[Tuple[str, str]] = settings.wow_class_spec_list

    logger.debug("trinket_simulations start")
    for fight_style in settings.fight_styles:
        simulation_results = {}
        for wow_class, wow_spec in specs:

            # check whether the baseline profile does exist
            try:
                with open(
                    create_basic_profile_string(wow_class, wow_spec, settings.tier, settings), 'r'
                ) as f:
                    pass
            except FileNotFoundError:
                logger.warning(
                    "{} {} profile not found. Skipping.".format(
                        wow_spec.title(), wow_class.title()
                    )
                )
                continue

            # json exporter
            json_export = create_base_json_dict(
                "trinkets", wow_class, wow_spec, fight_style, settings
            )

            # get main-trinkets
            trinket_list = wow_lib.get_trinkets_for_spec(wow_class, wow_spec)
            # get secondary-trinket (standard stat stick)
            second_trinket = wow_lib.get_second_trinket_for_spec(wow_class, wow_spec)

            # fix profile for this type of simulations
            json_export['profile']['items'].pop('trinket1')
            json_export['profile']['items'].pop('trinket2')
            json_export['profile']['items']['trinket2'] = {
                "id": second_trinket.split(",")[1].split("=")[1],
                "bonus_id": second_trinket.split(",")[2].split("=")[1],
                "ilevel": str(settings.min_ilevel)
            }
            # TODO: remove after some time and after frontend is updated
            json_export['profile'].pop('trinket1')
            json_export['profile'].pop('trinket2')
            json_export['profile']['trinket2'] = {
                "id": second_trinket.split(",")[1].split("=")[1],
                "bonus_id": second_trinket.split(",")[2].split("=")[1],
                "ilevel": str(settings.min_ilevel)
            }

            if not wow_class in simulation_results:
                simulation_results[wow_class] = {}

            simulation_group = Simulation_Group(
                name="{} {}".format(wow_class.title(), wow_spec.title()),
                threads=settings.threads,
                profileset_work_threads=settings.profileset_work_threads,
                executable=settings.executable,
                logger=logger
            )

            for trinket in trinket_list:

                if trinket == trinket_list[0]:
                    simulation_data = Simulation_Data(
                        name="baseline {}".format(settings.min_ilevel),
                        fight_style=fight_style,
                        iterations=settings.iterations,
                        target_error=settings.target_error[fight_style],
                        profile=json_export['profile'],
                        simc_arguments=[
                            "trinket1=",
                        ],
                        ptr=settings.ptr,
                        default_actions=settings.default_actions,
                        executable=settings.executable,
                        logger=logger
                    )

                    # reduce the uptime of the trinket for tanks
                    if wow_lib.get_raid_role(wow_class, wow_spec) == 'tank':
                        simulation_data.simc_arguments.append(
                            'bfa.voidtwisted_titanshard_percent_duration=0.1'
                        )

                    custom_apl = None
                    if settings.custom_apl:
                        with open('custom_apl.txt') as f:
                            custom_apl = f.read()
                    if custom_apl:
                        simulation_data.simc_arguments.append(custom_apl)

                    custom_fight_style = None
                    if settings.custom_fight_style:
                        with open('custom_fight_style.txt') as f:
                            custom_fight_style = f.read()
                    if custom_fight_style:
                        simulation_data.simc_arguments.append(custom_fight_style)

                    simulation_group.add(simulation_data)

                # for each available itemlevel of the trinket
                for itemlevel in range(
                    settings.min_ilevel, settings.max_ilevel + 1, settings.ilevel_step
                ):

                    if itemlevel >= trinket[2] and itemlevel <= trinket[3]:

                        simulation_data = Simulation_Data(
                            name="{} {}".format(trinket[0], itemlevel),
                            fight_style=fight_style,
                            iterations=settings.iterations,
                            target_error=settings.target_error[fight_style],
                            simc_arguments=[
                                "trinket1=,id={},ilevel={}".format(trinket[1], itemlevel)
                            ],
                            ptr=settings.ptr,
                            default_actions=settings.default_actions,
                            executable=settings.executable,
                            logger=logger
                        )
                        simulation_group.add(simulation_data)

            # create and simulate baseline profile
            logger.info(
                "Start {} trinket simulation for {} {}.".format(fight_style, wow_class, wow_spec)
            )
            try:
                if settings.use_raidbots and settings.apikey:
                    settings.simc_hash = simulation_group.simulate_with_raidbots(settings.apikey)
                else:
                    simulation_group.simulate()
            except Exception as e:
                logger.error(
                    "{} trinket simulation for {} {} failed. {}".format(
                        fight_style.title(), wow_class, wow_spec, e
                    )
                )
                continue
            else:
                logger.info(
                    "{} trinket simulation for {} {} ended successfully. Cleaning up.".format(
                        fight_style.title(), wow_class, wow_spec
                    )
                )

            for profile in simulation_group.profiles:
                try:
                    logger.debug(
                        "{} {} DPS, baseline + {}".format(
                            profile.name, profile.get_dps(),
                            profile.get_dps() -
                            simulation_group.get_dps_of("baseline {}".format(settings.min_ilevel))
                        )
                    )
                except Exception as e:
                    logger.error(
                        "Exception was thrown when trying to fetch the following data from simulation_group: profile.name, profile.get_dps(), profile.get_dps() - simulation_group.get_dps_of(\"baseline {}\".format(settings.min_ilevel))"
                    )
                    logger.debug("profile.name {}".format(profile.name))
                    logger.debug("profile.get_dps() {}".format(profile.get_dps()))
                    logger.debug("settings.min_ilevel {}".format(settings.min_ilevel))
                    logger.debug(
                        "simulation_group.get_dps_of(\"baseline {{}}\".format(settings.min_ilevel)) {}"
                        .format(
                            simulation_group.get_dps_of("baseline {}".format(settings.min_ilevel))
                        )
                    )

            simulation_results[wow_class][wow_spec] = simulation_group

            json_export["data_active"] = {}
            for trinket in trinket_list:
                json_export["data_active"][trinket[0]] = trinket[5]

            for profile in simulation_group.profiles:

                full_name = profile.name[:profile.name.rfind(" ")]
                name = full_name.split('+')[0]
                ilevel = profile.name[profile.name.rfind(" ") + 1:]

                if not full_name in json_export["data"]:
                    json_export["data"][full_name] = {}

                json_export["data"][full_name][ilevel] = profile.get_dps()

                # add translation to export
                if not full_name in json_export["languages"] and not "baseline" in full_name:
                    try:
                        json_export["languages"][full_name] = wow_lib.get_trinket_translation(name)
                    except Exception as e:
                        logger.debug("No translation found for {}.".format(name))
                        logger.warning(e)

                if not "data_sources" in json_export:
                    json_export["data_sources"] = {}

                if not full_name in json_export["data_sources"] and not "baseline" in full_name:
                    try:
                        json_export["data_sources"][full_name] = wow_lib.get_trinket(name=name
                                                                                     ).get_source()
                    except:
                        pass

            # create item_id table
            json_export["item_ids"] = {}
            for trinket in json_export["data"]:
                if trinket != "baseline":
                    name = trinket.split('+')[0]
                    json_export["item_ids"][trinket] = wow_lib.get_trinket_id(name)
                    if json_export["item_ids"][trinket] == None:
                        del json_export["item_ids"][trinket]

            logger.debug("Enriched json export: {}".format(json_export))

            # create ordered trinket name list
            tmp_list = []
            for trinket in json_export["data"]:
                if trinket != "baseline":
                    tmp_list.append((trinket, max(json_export["data"][trinket].values())))
            logger.debug("tmp_list: {}".format(tmp_list))

            tmp_list = sorted(tmp_list, key=lambda item: item[1], reverse=True)
            logger.debug("Sorted tmp_list: {}".format(tmp_list))

            logger.info("Trinket {} won with {} dps.".format(tmp_list[0][0], tmp_list[0][1]))

            json_export["sorted_data_keys"] = []
            for trinket, _ in tmp_list:
                json_export["sorted_data_keys"].append(trinket)

            # add itemlevel list
            json_export["simulated_steps"] = []
            for itemlevel in range(
                settings.min_ilevel, settings.max_ilevel + 1, settings.ilevel_step
            ):
                json_export["simulated_steps"].append(itemlevel)

            # change order from ascending to descending to keep the order of previous versions
            json_export["simulated_steps"].sort(reverse=True)

            if not os.path.isdir("results/trinkets/"):
                os.makedirs("results/trinkets/")

            # write json to file
            with open(
                "results/trinkets/{}_{}_{}.json".format(
                    wow_class.lower(), wow_spec.lower(), fight_style.lower()
                ),
                "w",
                encoding="utf-8"
            ) as f:
                logger.debug("Print trinket json.")
                f.write(json.dumps(json_export, sort_keys=True, indent=4, ensure_ascii=False))
                logger.debug("Printed trinket json.")

        # LUA data exporter
        if fight_style.lower() == "patchwerk" and settings.lua_trinket_export:
            human_readable = False
            item_dict = {}     # intended structure: itemID -> class -> spec -> itemlevel

            for wow_class in simulation_results:
                wow_class_id = wow_class if human_readable else wow_lib.get_class_id(wow_class)

                for wow_spec in simulation_results[wow_class]:
                    wow_spec_id = wow_spec if human_readable else wow_lib.get_spec_id(
                        wow_class, wow_spec
                    )

                    for profile in simulation_results[wow_class][wow_spec].profiles:
                        if profile.name != "baseline {}".format(settings.min_ilevel):
                            name = profile.name[:profile.name.rfind(" ")]
                            ilevel = int(profile.name[profile.name.rfind(" ") + 1:])

                            item_id = name if human_readable else wow_lib.get_trinket_id(name)

                            if not item_id in item_dict:
                                item_dict[item_id] = {}

                            if not wow_class_id in item_dict[item_id]:
                                item_dict[item_id][wow_class_id] = {}

                            if not wow_spec_id in item_dict[item_id][wow_class_id]:
                                item_dict[item_id][wow_class_id][wow_spec_id] = {}

                            item_dict[item_id][wow_class_id][wow_spec_id][
                                ilevel] = profile.get_dps(
                                ) - simulation_results[wow_class][wow_spec].get_dps_of(
                                    "baseline {}".format(settings.min_ilevel)
                                )

            logger.debug("item_dict: {}".format(item_dict))

            # enhance item_dict with missing itemlevels
            if settings.ilevel_step != 5:
                for item in item_dict:
                    for wow_class in item_dict[item]:
                        for wow_spec in item_dict[item][wow_class]:

                            trinket = item_dict[item][wow_class][wow_spec]

                            # skip creating additions to the lua file if increase cant be calculated
                            if len(trinket) < 2:
                                continue

                            # get average dps increase
                            dps_sum = 0
                            lower_dps = 0
                            itemlevels_counted = 0
                            for itemlevel in range(
                                settings.min_ilevel, settings.max_ilevel + 1, 5
                            ):
                                if itemlevel in trinket:
                                    if lower_dps:
                                        dps_sum += trinket[itemlevel] - lower_dps
                                        itemlevels_counted += 1
                                    lower_dps = trinket[itemlevel]

                            logger.debug(
                                "Item: {}, dps_sum: {}, itemlevels_counted: {}, settings.ilevel_step: {}"
                                .format(item, dps_sum, itemlevels_counted, settings.ilevel_step)
                            )

                            average_increase = int(
                                dps_sum / itemlevels_counted / (settings.ilevel_step / 5)
                            )

                            logger.debug(
                                "Item {} has {} counted ilevel differences. Average dps increase is {}"
                                .format(item, itemlevels_counted, average_increase)
                            )

                            try:
                                trinket_data = wow_lib.get_trinket(item_id=item)
                            except Exception:
                                # failes due to the human readability check
                                trinket_data = wow_lib.get_trinket(name=item)

                            for itemlevel in range(settings.min_ilevel, settings.max_ilevel, 5):
                                # if itemlevel is valid for that item
                                if itemlevel >= trinket_data.min_itemlevel and itemlevel <= trinket_data.max_itemlevel:
                                    #if itemlevel is missing, we add it
                                    if not itemlevel in trinket:
                                        # is able to catch up to +15 ilevel steps
                                        try:
                                            trinket[itemlevel] = trinket[itemlevel -
                                                                         5] + average_increase
                                        except Exception:
                                            trinket[itemlevel] = trinket[itemlevel +
                                                                         5] - average_increase

            with open("results/trinkets/ItemDPS.lua", "w") as f:
                logger.debug("Print trinket lua.")
                f.write("-- itemID -> class -> spec -> itemlevel\n")
                f.write("MoreItemInfo.Enum.ItemDPS = {\n")

                for trinket in item_dict:
                    f.write("{}[{}] = {{\n".format(" " * 4, trinket))

                    for wow_class in item_dict[trinket]:
                        f.write("{}[{}] = {{\n".format(" " * 8, wow_class))

                        for wow_spec in item_dict[trinket][wow_class]:
                            f.write("{}[{}] = {{\n".format(" " * 12, wow_spec))

                            for itemlevel in item_dict[trinket][wow_class][wow_spec]:
                                f.write(
                                    "{}[{}] = {}".format(
                                        " " * 16, itemlevel,
                                        item_dict[trinket][wow_class][wow_spec][itemlevel]
                                    )
                                )

                                if itemlevel == list(
                                    item_dict[trinket][wow_class][wow_spec].keys()
                                )[-1]:
                                    f.write("\n")
                                else:
                                    f.write(",\n")

                            if wow_spec == list(item_dict[trinket][wow_class].keys())[-1]:
                                f.write("{}}}\n".format(" " * 12))
                            else:
                                f.write("{}}},\n".format(" " * 12))

                        if wow_class == list(item_dict[trinket].keys())[-1]:
                            f.write("{}}}\n".format(" " * 8))
                        else:
                            f.write("{}}},\n".format(" " * 8))

                    if trinket == list(item_dict.keys())[-1]:
                        f.write("{}}}\n".format(" " * 4))
                    else:
                        f.write("{}}},\n".format(" " * 4))
                f.write("}\n")
                logger.debug("Printed trinket lua.")

    logger.debug("trinket_simulations ended")

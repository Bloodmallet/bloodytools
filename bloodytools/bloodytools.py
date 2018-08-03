#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Welcome to bloodytools - a SimulationCraft automator/wrapper

  Generate your data more easily without having to create each and every needed profile to do so by hand:
    - races
    - trinkets
    - (NYI) azerite traits
    - secondary distributions

  Output is usually saved as .json. But you can add different ways to output the data yourself.

  Contact:  https://discord.gg/tFR2uvK Bloodmallet(EU)#8246
  Github:   https://github.com/Bloodmallet/bloodytools
  Support the development:
            https://www.patreon.com/bloodmallet
            https://www.paypal.me/bloodmallet

  May 2018
"""

from typing import List, Tuple

import argparse
import datetime
import json
import logging
import os
import settings
import simulation_objects.simulation_objects as simulation_objects
import time
from simc_support import wow_lib

if settings.use_own_threading:
  import threading

# activate logging to file and console
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if hasattr(settings, "debug"):
  if settings.debug:
    logger.setLevel(logging.DEBUG)
# file logger
fh = logging.FileHandler("log.txt", "w")
fh.setLevel(logging.DEBUG)
# if hasattr(settings, "debug"):
#   if settings.debug:
#     fh.setLevel(logging.DEBUG)
log_formatter = logging.Formatter(
  "%(asctime)s - %(filename)s / %(funcName)s - %(levelname)s - %(message)s"
)
live_formatter = logging.Formatter(
  "%(asctime)s - %(levelname)s - %(message)s"
)
fh.setFormatter(log_formatter)
logger.addHandler(fh)
# console logger
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
if hasattr(settings, "debug"):
  if settings.debug:
    ch.setLevel(logging.DEBUG)
ch.setFormatter(live_formatter)
logger.addHandler(ch)


def create_basic_profile_string(wow_class: str, wow_spec: str, tier: str):
  """Create basic profile string to get the standard profile of a spec. Use this function to get the necessary string for your first argument of a simulation_data object.

  Arguments:
    wow_class {str} -- wow class, e.g. shaman
    wow_spec {str} -- wow spec, e.g. elemental
    tier {str} -- profile tier, e.g. 21 or PR

  Returns:
    str -- relative link to the standard simc profile
  """

  logger.debug("create_basic_profile_string start")
  # create the basis profile string
  basis_profile_string: str = settings.executable.split("simc")[0]
  basis_profile_string += "profiles/"
  if tier == "PR":
    basis_profile_string += "PreRaids/PR_{}_{}".format(
      wow_class.title(), wow_spec.title()
    )
  else:
    basis_profile_string += "Tier{}/T{}_{}_{}".format(
      tier, tier, wow_class, wow_spec
    ).title()
  basis_profile_string += ".simc"

  logger.debug(
    "Created basis_profile_string '{}'.".format(basis_profile_string)
  )
  logger.debug("create_basic_profile_string ended")
  return basis_profile_string


def pretty_timestamp() -> str:
  """Returns a pretty time stamp "YYYY-MM-DD HH:MM"

  Returns:
    str -- timestamp
  """
  # str(datetime.datetime.utcnow())[:-10] should be the same
  return datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M")


def create_base_json_dict(
  data_type: str, wow_class: str, wow_spec: str, fight_style: str
):
  """Creates as basic json dictionary. You'll need to add your data into 'data'. Can be extended.

  Arguments:
    data_type {str} -- e.g. Races, Trinkets, Azerite Traits (str is used in the title)
    wow_class {str} -- [description]
    wow_spec {str} -- [description]
    fight_style {str} -- [description]
    simulation_group {simulation_objects.Simulation_Group} -- [description]

  Returns:
    dict -- [description]
  """

  logger.debug("create_base_json_dict start")

  timestamp = pretty_timestamp()

  return {
    "data_type":
      "{}".format(data_type.lower().replace(" ", "_")),
    "timestamp":
      timestamp,
    "title":
      "{data_type} | {wow_class} {wow_spec} | {fight_style}".format(
        data_type=data_type.title(),
        wow_class=wow_class.title(),
        wow_spec=wow_spec.title(),
        fight_style=fight_style.title()
      ),
    "subtitle":
      "UTC {timestamp} | SimC build: <a href=\"https://github.com/simulationcraft/simc/commit/{simc_hash}\" target=\"blank\">{simc_hash_short}</a>"
      .format(
        timestamp=timestamp,
        simc_hash=settings.simc_hash,
        simc_hash_short=settings.simc_hash[0:7]
      ),
    "simc_settings":
      {
        "tier": settings.tier,
        "fight_style": fight_style,
        "iterations": settings.iterations,
        "target_error": settings.target_error[fight_style],
        "ptr": settings.ptr,
        "simc_hash": settings.simc_hash,
        "class": wow_class,
        "spec": wow_spec
      },
    "data": {},
  }


def tokenize_str(string: str) -> str:
  """Return SimulationCraft appropriate name.

  Arguments:
    string {str} -- E.g. "Tawnos, Urza's Apprentice"

  Returns:
    str -- "tawnos_urzas_apprentice"
  """

  string = string.lower().split(" (")[0]
  # cleanse name
  if "__" in string or " " in string or "-" in string or "'" in string or "," in string:
    return tokenize_str(
      string.replace("'", "").replace("-", "").replace(" ", "_").replace(
        "__", "_"
      ).replace(",", "")
    )

  return string


def race_simulations(specs: List[Tuple[str, str]]) -> None:
  """Simulates all available races for all given specs.

  Arguments:
    specs {List[Tuple[str, str]]} -- List of all wanted wow_specs

  Returns:
    None --
  """

  logger.debug("race_simulations start")
  for fight_style in settings.fight_styles:
    for wow_class, wow_spec in specs:

      # check whether the baseline profile does exist
      try:
        with open(
          create_basic_profile_string(wow_class, wow_spec, settings.tier), 'r'
        ) as f:
          pass
      except Exception as e:
        logger.error(
          "Opening baseline profile {} {} failed. This spec won't be in the result. {}".
          format(wow_class, wow_spec, e)
        )
        # end this try early, no profile, no calculations
        continue

      races = wow_lib.get_races_for_class(wow_class)
      simulation_group = simulation_objects.Simulation_Group(
        name="race_simulations",
        threads=settings.threads,
        profileset_work_threads=settings.profileset_work_threads,
        executable=settings.executable,
        logger=logger
      )

      for race in races:

        simulation_data = None

        if race == races[0]:

          basic_profile_string = create_basic_profile_string(
            wow_class, wow_spec, settings.tier
          )

          simulation_data = simulation_objects.Simulation_Data(
            name=race,
            fight_style=fight_style,
            simc_arguments=[basic_profile_string, "race={}".format(race)],
            target_error=settings.target_error[fight_style],
            executable=settings.executable,
            logger=logger
          )
        else:
          simulation_data = simulation_objects.Simulation_Data(
            name=race,
            fight_style=fight_style,
            simc_arguments=["race={}".format(race)],
            target_error=settings.target_error[fight_style],
            executable=settings.executable,
            logger=logger
          )
        simulation_group.add(simulation_data)
        logger.debug(
          (
            "Added race '{}' in profile '{}' to simulation_group.".format(
              race, simulation_data.name
            )
          )
        )

      logger.info(
        "Start {} race simulation for {} {}.".format(
          fight_style, wow_class, wow_spec
        )
      )
      try:
        if settings.use_raidbots and settings.apikey:
          simulation_group.simulate_with_raidbots(settings.apikey)
        else:
          simulation_group.simulate()
      except Exception as e:
        logger.error(
          "{} race simulation for {} {} failed. {}".format(
            fight_style.title(), wow_class, wow_spec, e
          )
        )
        continue
      else:
        logger.info(
          "{} race simulation for {} {} ended successfully. Cleaning up.".
          format(fight_style.title(), wow_class, wow_spec)
        )

      for profile in simulation_group.profiles:
        logger.debug(
          "Profile '{}' DPS: {}".format(profile.name, profile.get_dps())
        )

      # save data to json
      wanted_data = create_base_json_dict(
        "Races", wow_class, wow_spec, fight_style
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

      # create ordered race name list
      tmp_list = []
      for race in wanted_data["data"]:
        tmp_list.append((race, wanted_data["data"][race]))
      logger.debug("tmp_list: {}".format(tmp_list))

      tmp_list = sorted(tmp_list, key=lambda item: item[1], reverse=True)
      logger.debug("Sorted tmp_list: {}".format(tmp_list))
      logger.info(f"Race {tmp_list[0][0]} won with {tmp_list[0][1]} dps.")

      wanted_data["sorted_data_keys"] = []
      for race, _ in tmp_list:
        wanted_data["sorted_data_keys"].append(race)

      logger.debug("Final json: {}".format(wanted_data))

      if not os.path.isdir("results/races/"):
        os.makedirs("results/races/")

      # write json to file
      with open(
        "results/races/{}_{}_{}.json".format(
          wow_class.lower(), wow_spec.lower(), fight_style.lower()
        ), "w"
      ) as f:
        logger.debug("Print race json.")
        f.write(json.dumps(wanted_data, sort_keys=True, indent=4))
        logger.debug("Printed race json.")

  logger.debug("race_simulations ended")


def trinket_simulations(specs: List[Tuple[str, str]]) -> None:
  """Simulates all available trinkets to all given wow_classes and wow_specs.

  Arguments:
    specs {List[Tuple[str, str]]} -- [description]

  Raises:
    NotImplementedError -- [description]

  Returns:
    None -- [description]
  """

  logger.debug("trinket_simulations start")
  for fight_style in settings.fight_styles:
    simulation_results = {}
    for wow_class, wow_spec in specs:

      # check whether the baseline profile does exist
      try:
        with open(
          create_basic_profile_string(wow_class, wow_spec, settings.tier), 'r'
        ) as f:
          pass
      except Exception as e:
        logger.error(
          "Opening baseline profile for {} {} failed. This spec won't be in the result. {}".
          format(wow_class, wow_spec, e)
        )
        # end this try early, no profile, no calculations
        continue

      if not wow_class in simulation_results:
        simulation_results[wow_class] = {}

      # get main-trinkets
      trinket_list = wow_lib.get_trinkets_for_spec(wow_class, wow_spec)
      # get secondary-trinket (standard stat stick)
      second_trinket = wow_lib.get_second_trinket_for_spec(wow_class, wow_spec)

      simulation_group = simulation_objects.Simulation_Group(
        name="{} {}".format(wow_class.title(), wow_spec.title()),
        threads=settings.threads,
        profileset_work_threads=settings.profileset_work_threads,
        executable=settings.executable,
        logger=logger
      )

      for trinket in trinket_list:

        if trinket == trinket_list[0]:
          simulation_data = simulation_objects.Simulation_Data(
            name="baseline {}".format(settings.min_ilevel),
            fight_style=fight_style,
            iterations=settings.iterations,
            target_error=settings.target_error[fight_style],
            simc_arguments=[
              create_basic_profile_string(wow_class, wow_spec, settings.tier),
              "trinket1=", "trinket2=" + second_trinket
            ],
            executable=settings.executable,
            logger=logger
          )
          simulation_group.add(simulation_data)

        # for each available itemlevel of the trinket
        for itemlevel in range(
          settings.min_ilevel, settings.max_ilevel + 1, settings.ilevel_step
        ):

          if itemlevel >= trinket[2] and itemlevel <= trinket[3]:

            simulation_data = simulation_objects.Simulation_Data(
              name="{} {}".format(trinket[0], itemlevel),
              fight_style=fight_style,
              iterations=settings.iterations,
              target_error=settings.target_error[fight_style],
              simc_arguments=[
                "trinket1=,id={},ilevel={}".format(trinket[1], itemlevel)
              ],
              executable=settings.executable,
              logger=logger
            )
            simulation_group.add(simulation_data)

      # create and simulate baseline profile
      logger.info(
        "Start {} trinket simulation for {} {}.".format(
          fight_style, wow_class, wow_spec
        )
      )
      try:
        if settings.use_raidbots and settings.apikey:
          simulation_group.simulate_with_raidbots(settings.apikey)
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
          "{} trinket simulation for {} {} ended successfully. Cleaning up.".
          format(fight_style.title(), wow_class, wow_spec)
        )

      for profile in simulation_group.profiles:
        logger.debug(
          "{} {} DPS, baseline +{}".format(
            profile.name, profile.get_dps(),
            profile.get_dps() - simulation_group.get_dps_of(
              "baseline {}".format(settings.min_ilevel)
            )
          )
        )

      simulation_results[wow_class][wow_spec] = simulation_group

      # json exporter
      json_export = create_base_json_dict(
        "trinkets", wow_class, wow_spec, fight_style
      )

      for profile in simulation_group.profiles:

        name = profile.name[:profile.name.rfind(" ")]
        ilevel = profile.name[profile.name.rfind(" ") + 1:]

        if not name in json_export["data"]:
          json_export["data"][name] = {}

        json_export["data"][name][ilevel] = profile.get_dps()

      # create item_id table
      json_export["item_ids"] = {}
      for trinket in json_export["data"]:
        if trinket != "baseline":
          # FIXME: delete wow_class and wow_spec from function for bfa
          json_export["item_ids"][trinket] = wow_lib.get_trinket_id(
            trinket, wow_class, wow_spec
          )

      logger.debug("Enriched json export: {}".format(json_export))

      # create ordered trinket name list
      tmp_list = []
      for trinket in json_export["data"]:
        if trinket != "baseline":
          tmp_list.append((trinket, max(json_export["data"][trinket].values())))
      logger.debug("tmp_list: {}".format(tmp_list))

      tmp_list = sorted(tmp_list, key=lambda item: item[1], reverse=True)
      logger.debug("Sorted tmp_list: {}".format(tmp_list))

      logger.info(f"Trinket {tmp_list[0][0]} won with {tmp_list[0][1]} dps.")

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
        ), "w"
      ) as f:
        logger.debug("Print trinket json.")
        f.write(json.dumps(json_export, sort_keys=True, indent=4))
        logger.debug("Printed trinket json.")

    # LUA data exporter
    if fight_style.lower() == "patchwerk" and settings.lua_trinket_export:
      human_readable = False
      item_dict = {}  # intended structure: itemID -> class -> spec -> itemlevel

      for wow_class in simulation_results:
        wow_class_id = wow_class if human_readable else wow_lib.get_class_id(
          wow_class
        )

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

              item_dict[item_id
                       ][wow_class_id][wow_spec_id][ilevel] = profile.get_dps(
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

              # get average dps increase
              dps_sum = 0
              lower_dps = 0
              itemlevels_counted = 0
              for itemlevel in range(
                settings.min_ilevel, settings.max_ilevel, 5
              ):
                if itemlevel in trinket:
                  if lower_dps:
                    dps_sum += trinket[itemlevel] - lower_dps
                    itemlevels_counted += 1
                  lower_dps = trinket[itemlevel]

              average_increase = int(
                dps_sum / itemlevels_counted / (settings.ilevel_step / 5)
              )

              logger.debug(
                "Item {} has {} counted ilevel differences. Average dps increase is {}".
                format(item, itemlevels_counted, average_increase)
              )

              try:
                trinket_data = wow_lib.get_trinket(item_id=item)
              except Exception:
                # failes due to the human readability check
                trinket_data = wow_lib.get_trinket(name=item)

              for itemlevel in range(
                settings.min_ilevel, settings.max_ilevel, 5
              ):
                # if itemlevel is valid for that item
                if itemlevel >= trinket_data.min_itemlevel and itemlevel <= trinket_data.max_itemlevel:
                  #if itemlevel is missing, we add it
                  if not itemlevel in trinket:
                    # is able to catch up to +15 ilevel steps
                    try:
                      trinket[itemlevel
                             ] = trinket[itemlevel - 5] + average_increase
                    except Exception:
                      trinket[itemlevel
                             ] = trinket[itemlevel + 5] - average_increase

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


def secondary_distribution_simulations(
  wow_class: str,
  wow_spec: str,
  talent_combinations: List[str] = [False],
) -> List[simulation_objects.Simulation_Group]:

  logger.debug("secondary_distribution_simulations start")

  distribution_multipliers = []
  step_size = settings.secondary_distributions_step_size
  lower_border = 10
  upper_border = 70
  secondary_amount = 0

  # get secondary sum from profile
  try:
    with open(
      create_basic_profile_string(wow_class, wow_spec, settings.tier), 'r'
    ) as f:
      for line in f:
        if "gear_crit_rating=" in line:
          secondary_amount += int(line.split("=")[1])
        elif "gear_haste_rating=" in line:
          secondary_amount += int(line.split("=")[1])
        elif "gear_mastery_rating=" in line:
          secondary_amount += int(line.split("=")[1])
        elif "gear_versatility_rating=" in line:
          secondary_amount += int(line.split("=")[1])
  except Exception as e:
    logger.error(
      "Scanning baseline profile {} {} failed. This spec won't be in the result. {}".
      format(wow_class, wow_spec, e)
    )
    # end this try early, no profile, no calculations
    return

  logger.debug("secondary_amount found: {}".format(secondary_amount))

  # generate all valied secondary distributions
  for c in range(lower_border, upper_border + step_size, step_size):
    for h in range(lower_border, upper_border + step_size, step_size):
      for m in range(lower_border, upper_border + step_size, step_size):
        for v in range(lower_border, upper_border + step_size, step_size):
          if c + h + m + v == 100:
            distribution_multipliers.append((c, h, m, v))

  logger.debug(
    "'{}' different distributions generated.".format(
      len(distribution_multipliers)
    )
  )

  for fight_style in settings.fight_styles:

    result_dict = create_base_json_dict(
      "secondary_distributions", wow_class, wow_spec, fight_style
    )
    result_dict["sorted_data_keys"] = {}
    result_dict["secondary_sum"] = secondary_amount

    for talent_combination in talent_combinations:
      simulation_group = simulation_objects.Simulation_Group(
        name=talent_combination,
        threads=settings.threads,
        profileset_work_threads=settings.profileset_work_threads,
        executable=settings.executable,
        logger=logger
      )

      for distribution_multiplier in distribution_multipliers:
        # if it is the first one
        if distribution_multiplier == distribution_multipliers[0]:
          simulation_group.add(
            simulation_objects.Simulation_Data(
              name="{}_{}_{}_{}".format(
                distribution_multiplier[0], distribution_multiplier[1],
                distribution_multiplier[2], distribution_multiplier[3]
              ),
              fight_style=fight_style,
              target_error=settings.target_error[fight_style],
              iterations=settings.iterations,
              logger=logger,
              simc_arguments=[
                create_basic_profile_string(wow_class, wow_spec, settings.tier),
                "gear_crit_rating={}".format(
                  int(secondary_amount * (distribution_multiplier[0] / 100))
                ),
                "gear_haste_rating={}".format(
                  int(secondary_amount * (distribution_multiplier[1] / 100))
                ),
                "gear_mastery_rating={}".format(
                  int(secondary_amount * (distribution_multiplier[2] / 100))
                ),
                "gear_versatility_rating={}".format(
                  int(secondary_amount * (distribution_multiplier[3] / 100))
                ),
              ],
              executable=settings.executable
            )
          )
          # add the talent combination to the profileset, if one was provided
          if talent_combination:
            simulation_group.profiles[-1].simc_arguments.append(
              "talents={}".format(talent_combination)
            )
        else:
          simulation_group.add(
            simulation_objects.Simulation_Data(
              name="{}_{}_{}_{}".format(
                distribution_multiplier[0], distribution_multiplier[1],
                distribution_multiplier[2], distribution_multiplier[3]
              ),
              fight_style=fight_style,
              target_error=settings.target_error[fight_style],
              iterations=settings.iterations,
              logger=logger,
              simc_arguments=[
                "gear_crit_rating={}".format(
                  int(secondary_amount * (distribution_multiplier[0] / 100))
                ),
                "gear_haste_rating={}".format(
                  int(secondary_amount * (distribution_multiplier[1] / 100))
                ),
                "gear_mastery_rating={}".format(
                  int(secondary_amount * (distribution_multiplier[2] / 100))
                ),
                "gear_versatility_rating={}".format(
                  int(secondary_amount * (distribution_multiplier[3] / 100))
                ),
              ],
              executable=settings.executable
            )
          )

      logger.info(
        "Start {} secondary distribution simulation for {} {} {}.".format(
          fight_style, wow_class, wow_spec, talent_combination
        )
      )

      try:
        simulation_group.simulate()
      except Exception as e:
        logger.error(
          "Secondary distribution simulation for {} {} {} failed. {}".format(
            wow_class, wow_spec, talent_combination, e
          )
        )
        continue
      else:
        logger.info(
          "{} secondary distribution simulation for {} {} {} ended successfully. Cleaning up.".
          format(fight_style.title(), wow_class, wow_spec, talent_combination)
        )

      if settings.debug:
        logger.debug("Talent combination: " + talent_combination)
        for profile in simulation_group.profiles:
          logger.debug("{}   {}".format(profile.name, profile.get_dps()))

      # create sorted list and add data to the result_dict
      stat_dps_list = []
      result_dict["data"][talent_combination] = {}

      for profile in simulation_group.profiles:
        stat_dps_list.append((profile.name, profile.get_dps()))
        result_dict["data"][talent_combination][profile.name
                                               ] = profile.get_dps()

      # sort list
      stat_dps_list = sorted(
        stat_dps_list, key=lambda item: item[1], reverse=True
      )
      logger.info(f"Stat distribution {stat_dps_list[0][0]} of talent combination {talent_combination} won with {stat_dps_list[0][1]} dps.")

      # add debug information which is coincidentally the same as settings.write_humanreadable_secondary_distribution_file
      logger.debug(
        "Secondary distribution list for {} (max:{}):".format(
          talent_combination, stat_dps_list[0][1]
        )
      )
      if settings.write_humanreadable_secondary_distribution_file:
        with open(
          'results/secondary_distributions/{}_{}_{}.txt'.format(
            wow_class.lower(), wow_spec.lower(), fight_style.lower()
          ), 'a'
        ) as f:
          f.write(
            "Sorted secondary distribution list for {} (max:{}):\n".format(
              talent_combination, stat_dps_list[0][1]
            )
          )
      logger.debug("c  h  m  v    dps")
      if settings.write_humanreadable_secondary_distribution_file:
        with open(
          'results/secondary_distributions/{}_{}_{}.txt'.format(
            wow_class.lower(), wow_spec.lower(), fight_style.lower()
          ), 'a'
        ) as f:
          f.write("  c  h  m  v    dps\n")
      for item in stat_dps_list:
        logger.debug(
          "{}   {}  {}%".format(
            item[0], item[1], round(item[1] * 100 / stat_dps_list[0][1], 2)
          )
        )
        if settings.write_humanreadable_secondary_distribution_file:
          with open(
            'results/secondary_distributions/{}_{}_{}.txt'.format(
              wow_class.lower(), wow_spec.lower(), fight_style.lower()
            ), 'a'
          ) as f:
            f.write(
              "  {}   {}  {}%\n".format(
                item[0], item[1], round(item[1] * 100 / stat_dps_list[0][1], 2)
              )
            )

      result_dict["sorted_data_keys"][talent_combination] = []
      for item in stat_dps_list:
        result_dict["sorted_data_keys"][talent_combination].append(item[0])

    # print file
    logger.debug(result_dict)

    if not os.path.isdir("results/secondary_distributions/"):
      os.makedirs("results/secondary_distributions/")

    with open(
      "results/secondary_distributions/{}_{}_{}.json".format(
        wow_class.lower(), wow_spec.lower(), fight_style.lower()
      ), 'w'
    ) as f:
      logger.debug("Print secondary distribution json.")
      f.write(json.dumps(result_dict, sort_keys=True, indent=4))
      logger.debug("Printed secondary distribution json.")
  logger.debug("secondary_distribution_simulations ended")


def azerite_trait_simulations(specs: List[Tuple[str, str]]) -> None:
  """Simulate all azerite traits with an adjusted head itemlevel. Create json with trait values and with all known azerite items and their sumed up trait dps values.

  Arguments:
    specs {List[Tuple[str, str]]} -- all wow_specs you want to be simulated

  Returns:
    None -- Files will be created in /results/azerite_traits/
  """

  logger.debug("azerite_trait_simulations start")
  for fight_style in settings.fight_styles:
    for wow_class, wow_spec in specs:


      basic_profile_string = create_basic_profile_string(
        wow_class, wow_spec, settings.tier
      )

      # check whether the baseline profile does exist
      try:
        with open(basic_profile_string, 'r') as f:
          for line in f:
            if "head=" in line:
              item_head = line[:-1]
      except Exception as e:
        logger.error(
          "Opening baseline profile {} {} failed. This spec won't be in the result. {}".
          format(wow_class, wow_spec, e)
        )
        # end this try early, no profile, no calculations
        continue

      azerite_traits = wow_lib.get_azerite_traits(wow_class, wow_spec)
      simulation_group = simulation_objects.Simulation_Group(
        name="azerite_trait_simulations",
        threads=settings.threads,
        profileset_work_threads=settings.profileset_work_threads,
        executable=settings.executable,
        logger=logger
      )

      reset_string = "disable_azerite=items"

      # need this special handling of the first profile or else the other baseline profiles won't simulate correctly
      simulation_data = simulation_objects.Simulation_Data(
        name="baseline 1_{}".format(settings.azerite_trait_ilevels[0]),
        fight_style=fight_style,
        simc_arguments=[basic_profile_string, reset_string, item_head + f",ilevel={settings.azerite_trait_ilevels[0]}"],
        target_error=settings.target_error[fight_style],
        executable=settings.executable,
        logger=logger
      )
      simulation_group.add(simulation_data)

      for itemlevel in settings.azerite_trait_ilevels:
        if itemlevel != settings.azerite_trait_ilevels[0]:
          simulation_data = simulation_objects.Simulation_Data(
            name="baseline 1_{}".format(itemlevel),
            fight_style=fight_style,
            simc_arguments=[item_head + f",ilevel={itemlevel}"],
            target_error=settings.target_error[fight_style],
            executable=settings.executable,
            logger=logger
          )
          simulation_group.add(simulation_data)

      azerite_trait_name_spell_id_dict = {}

      for azerite_trait_spell_id in azerite_traits:

        for itemlevel in settings.azerite_trait_ilevels:

          azerite_trait = azerite_traits[azerite_trait_spell_id]['name']

          if not azerite_trait in azerite_trait_name_spell_id_dict:
            azerite_trait_name_spell_id_dict[azerite_trait.split(" (")[0]
                                            ] = azerite_trait_spell_id

          simulation_data = None
          # azerite_override=
          trait_input = "azerite_override={}:{}".format(
            tokenize_str(azerite_trait), itemlevel
          )

          simulation_data = simulation_objects.Simulation_Data(
            name='{} 1_{}'.format(azerite_trait.split(" (")[0], itemlevel),
            fight_style=fight_style,
            simc_arguments=[trait_input, item_head + f",ilevel={itemlevel}"],
            target_error=settings.target_error[fight_style],
            executable=settings.executable,
            logger=logger
          )
          simulation_group.add(simulation_data)
          logger.debug(
            (
              "Added azerite trait '{}' at itemlevel {} in profile '{}' to simulation_group.".
              format(azerite_trait, itemlevel, simulation_data.name)
            )
          )

          # add stacked traits profiles to simulationgroup at max itemlevel
          if itemlevel == settings.azerite_trait_ilevels[-1]:
            logger.debug("Adding stacked azerite traits to highest itemlevel.")
            doublicate_text = "/" + trait_input.split("=")[1]
            simulation_data = None
            simulation_data = simulation_objects.Simulation_Data(
              name='{} 2_{}'.format(azerite_trait.split(" (")[0], itemlevel),
              fight_style=fight_style,
              simc_arguments=[trait_input + doublicate_text, item_head + f",ilevel={itemlevel}"],
              target_error=settings.target_error[fight_style],
              executable=settings.executable,
              logger=logger
            )
            simulation_group.add(simulation_data)

            simulation_data = None
            simulation_data = simulation_objects.Simulation_Data(
              name='{} 3_{}'.format(azerite_trait.split(" (")[0], itemlevel),
              fight_style=fight_style,
              simc_arguments=[trait_input + doublicate_text + doublicate_text, item_head + f",ilevel={itemlevel}"],
              target_error=settings.target_error[fight_style],
              executable=settings.executable,
              logger=logger
            )
            simulation_group.add(simulation_data)

      logger.info(
        "Start {} azerite_trait simulation for {} {}. {} profiles.".format(
          fight_style, wow_class.title(), wow_spec.title(),
          len(simulation_group.profiles)
        )
      )
      try:
        if settings.use_raidbots and settings.apikey:
          simulation_group.simulate_with_raidbots(settings.apikey)
        else:
          simulation_group.simulate()
      except Exception as e:
        logger.error(
          "{} azerite_trait simulation for {} {} failed. {}".format(
            fight_style.title(), wow_class.title(), wow_spec.title(), e
          )
        )
        continue
      else:
        logger.info(
          "{} azerite_trait simulation for {} {} ended successfully. Cleaning up.".
          format(fight_style.title(), wow_class.title(), wow_spec.title())
        )

      for profile in simulation_group.profiles:
        logger.debug(
          "Profile '{}' DPS: {}".format(profile.name, profile.get_dps())
        )

      # save data to json
      wanted_data = create_base_json_dict(
        "Azerite Traits", wow_class, wow_spec, fight_style
      )

      logger.debug("Created base dict for json export. {}".format(wanted_data))

      # update used ilevel steps to the correct keys
      # add itemlevel list
      wanted_data["simulated_steps"] = []
      for itemlevel in settings.azerite_trait_ilevels:
        wanted_data["simulated_steps"].insert(0, "1_" + itemlevel)

      # add dps values to json
      for profile in simulation_group.profiles:
        azerite_trait_name = " ".join(profile.name.split()[:-1])
        azerite_trait_ilevel = profile.name.split()[-1]

        if not azerite_trait_name in wanted_data["data"]:
          wanted_data["data"][azerite_trait_name] = {}

        wanted_data["data"][azerite_trait_name][azerite_trait_ilevel] = profile.get_dps()

        # TODO : Does this break? I don#t think special handling of baseline is required anymore
        # if azerite_trait_name == "baseline":
        #   wanted_data["data"][
        #     azerite_trait_name
        #   ]["1_" + settings.azerite_trait_ilevels[0]] = profile.get_dps()

        logger.debug(
          "Added '{}' with {} dps to json.".format(
            profile.name, profile.get_dps()
          )
        )

      # create azerite name list
      tmp_list = []
      for trait in wanted_data["data"]:
        tmp_list.append(
          (
            trait,
            wanted_data["data"][trait]["1_"
                                       + settings.azerite_trait_ilevels[-1]]
          )
        )
      logger.debug("tmp_list: {}".format(tmp_list))

      # sort
      tmp_list = sorted(tmp_list, key=lambda item: item[1], reverse=True)
      logger.debug("Sorted tmp_list: {}".format(tmp_list))
      logger.info(f"Solo Azerite Trait {tmp_list[0][0]} won with {tmp_list[0][1]} dps.")

      # sorted list of all traits (one trait at max itemlevel each)
      wanted_data["sorted_data_keys"] = []
      for azerite_trait, _ in tmp_list:
        wanted_data["sorted_data_keys"].append(azerite_trait)

      # create secondary azerite name list (tripple azerite trait at max itemlevel each)
      tmp_list = []
      for trait in wanted_data["data"]:
        if not "baseline" in trait:
          tmp_list.append(
            (
              trait,
              wanted_data["data"][trait]["3_"
                                         + settings.azerite_trait_ilevels[-1]]
            )
          )
      logger.debug("tmp_list: {}".format(tmp_list))

      # sort
      tmp_list = sorted(tmp_list, key=lambda item: item[1], reverse=True)
      logger.debug("Sorted tmp_list: {}".format(tmp_list))
      logger.info(f"Tripple stacked Azerite Trait {tmp_list[0][0]} won with {tmp_list[0][1]} dps.")

      wanted_data["sorted_data_keys_2"] = []
      for azerite_trait, _ in tmp_list:
        wanted_data["sorted_data_keys_2"].append(azerite_trait)

      # spell id dict to allow link creation
      wanted_data["spell_ids"] = azerite_trait_name_spell_id_dict

      logger.debug("Final json: {}".format(wanted_data))

      # create directory if it doesn't exist
      if not os.path.isdir("results/azerite_traits/"):
        os.makedirs("results/azerite_traits/")

      # write json to file
      with open(
        "results/azerite_traits/{}_{}_{}.json".format(
          wow_class.lower(), wow_spec.lower(), fight_style.lower()
        ), "w"
      ) as f:
        logger.debug("Print azerite_traits json.")
        f.write(json.dumps(wanted_data, sort_keys=True, indent=4))
        logger.debug("Printed azerite_traits json.")

      ##
      # item export start (Azerite Items)
      azerite_items = wow_lib.get_azerite_items(wow_class, wow_spec)

      # create an export for each slot
      for slot in azerite_items:
        slot_export = create_base_json_dict(
          "Azerite Items " + slot.title(), wow_class, wow_spec, fight_style
        )

        slot_export["simulated_steps"] = []
        for itemlevel in settings.azerite_trait_ilevels:
          slot_export["simulated_steps"].insert(0, "1_" + itemlevel)

        # add baseline dps
        slot_export["data"]["baseline"] = {}

        for itemlevel in settings.azerite_trait_ilevels:
          slot_export["data"]["baseline"]["1_" + itemlevel] = wanted_data["data"]["baseline"]["1_" + itemlevel]

        # create shorthand for later use
        baseline_dps = slot_export["data"]["baseline"]

        # create dict of which azerite traits were used on whcih item
        slot_export["used_azerite_traits_per_item"] = {}

        # add class id number
        slot_export["class_id"] = wow_lib.get_class_id(wow_class)

        # look at each item
        unsorted_item_dps_list = []
        for item in azerite_items[slot]:

          # skip item if necessary fields are missing
          if not "name" in item and not "azeriteTraits" in item:
            continue

          if item["name"] in slot_export["data"]:
            continue

          # create trait lists for each tier [(trait_name, dps)]
          trait_dict = {2: [], 3: []}
          # collect trait data like spellid and power id to allow construction of links in page
          trait_data = {}
          for trait in item["azeriteTraits"]:

            # keys in this dict are intentionally left out as those are just alliance counterparts to horde pvp traits, get values from their horde counterparts
            # this list needs to match with the faq.html page on bloodmallet.com
            trait_exclusions = {
              "Anduin's Dedication": "Sylvanas' Resolve",
              "Battlefield Precision": "Battlefield Focus",
              "Stand As One": "Collective Will",
              "Stronger Together": "Combined Might",
              "Last Gift": "Retaliatory Fury",
              "Liberator's Might": "Glory in Battle"
            }

            # if trait tier is appropriate
            if not trait["tier"] in trait_dict:
              continue

            # skip trait if no name is provided (trait is probably not yet implemented in wow anyway)
            if not "name" in trait:
              continue

            # if trait was not simmed previously, throw a warning and exclude trait
            if not trait["name"] in wanted_data["data"] and not trait["name"] in trait_exclusions:
              logger.warning(f"Trait <{trait['name']}> wasn't found in already simed data and exluded data. Item <{item['name']}> will be evaluated without that trait.")
              continue

            # name is used to determine values, trait name is used to determine the name of the trait
            name = trait_name = trait["name"]

            # update name if we're dealing with an excluded trait
            if trait_name in trait_exclusions:
              name = trait_exclusions[trait_name]

            trait_data[name] = {
              "id": trait["powerId"],
              "spell_id": trait["spellId"]
            }

            # if trait is a dps trait we simmed
            if name in wanted_data["data"]:
              # append tuple of name and max itemlevel dps
              trait_dict[trait["tier"]].append(
                (
                  name, wanted_data["data"][name]
                  ["1_" + settings.azerite_trait_ilevels[-1]] - baseline_dps["1_" + settings.azerite_trait_ilevels[-1]]
                )
              )

          # create list of traits of item
          slot_export["used_azerite_traits_per_item"][item["name"]] = []

          # complete trait list with dps was created. get max values
          for tier in trait_dict:
            if trait_dict[tier]:
              trait_dict[tier] = sorted(trait_dict[tier], key=lambda item: item[1], reverse=True)
              slot_export["used_azerite_traits_per_item"][item["name"]].append({
                "name": trait_dict[tier][0][0],
                "id": trait_data[trait_dict[tier][0][0]]["id"],
                "spell_id": trait_data[trait_dict[tier][0][0]]["spell_id"]
              })

          slot_export["data"][item["name"]] = {}
          # add values to the armor for all itemlevels
          for itemlevel in settings.azerite_trait_ilevels:

            slot_export["data"][item["name"]]["1_" + itemlevel] = baseline_dps["1_" + itemlevel]

            # sum up dps values of best dps traits
            for tier in trait_dict:
              if trait_dict[tier]:
                slot_export["data"][item["name"]]["1_" + itemlevel] += wanted_data["data"][trait_dict[tier][0][0]]["1_" + itemlevel] - baseline_dps["1_" + itemlevel]

          # add (item_name, item_dps) to unsorted_item_dps_list
          unsorted_item_dps_list.append(
            (
              item["name"],
              slot_export["data"][item["name"]]["1_" + settings.azerite_trait_ilevels[-1]]
            )
          )

          # create item_ids dict
          if not "item_ids" in slot_export:
            slot_export["item_ids"] = {}

          # add item id
          slot_export["item_ids"][item["name"]] = str(item["id"])

        # all items are done, sort unsorted_item_dps_list
        sorted_item_dps_list = sorted(unsorted_item_dps_list, key=lambda item: item[1], reverse=True)

        # add sorted list to slot_export
        slot_export["sorted_data_keys"] = []
        for item, _ in sorted_item_dps_list:
          slot_export["sorted_data_keys"].append(item)

        if not os.path.isdir("results/azerite_traits/"):
          os.makedirs("results/azerite_traits/")

        with open(
          "results/azerite_traits/{}_{}_{}_{}.json".format(
            wow_class.lower(), wow_spec.lower(), slot.lower(), fight_style.lower()
          ), "w"
        ) as f:
          logger.debug(f"Print azerite_traits {slot} json.")
          f.write(json.dumps(slot_export, sort_keys=True, indent=4))
          logger.debug(f"Printed azerite_traits {slot} json.")

  logger.debug("azerite_trait_simulations ended")

def gear_path_simulations(specs: List[Tuple[str, str]]) -> None:

  for fight_style in settings.fight_styles:
    gear_path = []
    for spec in specs:
      wow_class, wow_spec = spec

      # initial profiles and data
      secondary_sum = 0
      base_profile_string = create_basic_profile_string(wow_class, wow_spec, settings.tier)

      try:
        with open(base_profile_string, 'r') as f:
          for line in f:
            if "gear_crit_rating" in line:
              secondary_sum += int(line.split("=")[-1])
            if "gear_haste_rating" in line:
              secondary_sum += int(line.split("=")[-1])
            if "gear_mastery_rating" in line:
              secondary_sum += int(line.split("=")[-1])
            if "gear_versatility_rating" in line:
              secondary_sum += int(line.split("=")[-1])
      except Exception:
        logger.warning(f"Profile for {wow_spec} {wow_class} couldn't be found. Will be left out in Gear Path simulations.")
        continue

      crit_rating = haste_rating = mastery_rating = vers_rating = settings.start_value

      while crit_rating + haste_rating + mastery_rating + vers_rating < secondary_sum:

        simulation_group = simulation_objects.Simulation_Group(
          name=f"{fight_style} {wow_spec} {wow_class}",
          executable=settings.executable,
          threads=settings.threads,
          profileset_work_threads=settings.profileset_work_threads,
          logger=logger
        )

        crit_profile = simulation_objects.Simulation_Data(
          name="crit_profile",
          executable=settings.executable,
          fight_style=fight_style,
          target_error=settings.target_error[fight_style],
          logger=logger,
          simc_arguments=[
            base_profile_string,
            "gear_crit_rating={}".format(crit_rating + settings.step_size),
            "gear_haste_rating={}".format(haste_rating),
            "gear_mastery_rating={}".format(mastery_rating),
            "gear_versatility_rating={}".format(vers_rating)
          ]
        )
        simulation_group.add(crit_profile)

        haste_profile = simulation_objects.Simulation_Data(
          name="haste_profile",
          executable=settings.executable,
          fight_style=fight_style,
          target_error=settings.target_error[fight_style],
          logger=logger,
          simc_arguments=[
            "gear_crit_rating={}".format(crit_rating),
            "gear_haste_rating={}".format(haste_rating + settings.step_size),
            "gear_mastery_rating={}".format(mastery_rating),
            "gear_versatility_rating={}".format(vers_rating)
          ]
        )
        simulation_group.add(haste_profile)

        mastery_profile = simulation_objects.Simulation_Data(
          name="mastery_profile",
          executable=settings.executable,
          fight_style=fight_style,
          target_error=settings.target_error[fight_style],
          logger=logger,
          simc_arguments=[
            "gear_crit_rating={}".format(crit_rating),
            "gear_haste_rating={}".format(haste_rating),
            "gear_mastery_rating={}".format(mastery_rating + settings.step_size),
            "gear_versatility_rating={}".format(vers_rating)
          ]
        )
        simulation_group.add(mastery_profile)

        vers_profile = simulation_objects.Simulation_Data(
          name="vers_profile",
          executable=settings.executable,
          fight_style=fight_style,
          target_error=settings.target_error[fight_style],
          logger=logger,
          simc_arguments=[
            "gear_crit_rating={}".format(crit_rating),
            "gear_haste_rating={}".format(haste_rating),
            "gear_mastery_rating={}".format(mastery_rating),
            "gear_versatility_rating={}".format(vers_rating + settings.step_size)
          ]
        )
        simulation_group.add(vers_profile)

        simulation_group.simulate()

        # ugly
        winner_dps = 0
        if crit_profile.get_dps() >= haste_profile.get_dps() and crit_profile.get_dps() >= mastery_profile.get_dps() and crit_profile.get_dps() >= vers_profile.get_dps():

          crit_rating += settings.step_size
          winner_dps = crit_profile.get_dps()
          logger.info(f"Crit - {crit_rating}/{haste_rating}/{mastery_rating}/{vers_rating}: {winner_dps}")

        elif haste_profile.get_dps() >= crit_profile.get_dps() and haste_profile.get_dps() >= mastery_profile.get_dps() and haste_profile.get_dps() >= vers_profile.get_dps():

          haste_rating += settings.step_size
          winner_dps = haste_profile.get_dps()
          logger.info(f"Haste - {crit_rating}/{haste_rating}/{mastery_rating}/{vers_rating}: {winner_dps}")

        elif mastery_profile.get_dps() >= haste_profile.get_dps() and mastery_profile.get_dps() >= crit_profile.get_dps() and mastery_profile.get_dps() >= vers_profile.get_dps():

          mastery_rating += settings.step_size
          winner_dps = mastery_profile.get_dps()
          logger.info(f"Mastery - {crit_rating}/{haste_rating}/{mastery_rating}/{vers_rating}: {winner_dps}")

        elif vers_profile.get_dps() >= haste_profile.get_dps() and vers_profile.get_dps() >= mastery_profile.get_dps() and vers_profile.get_dps() >= crit_profile.get_dps():

          vers_rating += settings.step_size
          winner_dps = vers_profile.get_dps()
          logger.info(f"Vers - {crit_rating}/{haste_rating}/{mastery_rating}/{vers_rating}: {winner_dps}")

        gear_path.append({
          f"{crit_rating}_{haste_rating}_{mastery_rating}_{vers_rating}": winner_dps
        })

      logger.info(gear_path)

      result = create_base_json_dict("Gear Path", wow_class, wow_spec, fight_style)

      result['data'] = gear_path

      if not os.path.isdir('results/gear_path/'):
        os.makedirs('results/gear_path/')

      with open(f'results/gear_path/{wow_class}_{wow_spec}_{fight_style}.json', 'w') as f:
        json.dump(result, f, indent=4, sort_keys=True)



def main():
  logger.debug("main start")
  logger.info("Bloodytools at your service.")

  # interface parameters
  parser = argparse.ArgumentParser(
    description="Simulate different aspects of World of Warcraft data."
  )
  parser.add_argument(
    "-a",
    "--all",
    dest="sim_all",
    action="store_const",
    const=True,
    default=False,
    help=
    "Simulate races, trinkets, secondary distributions, and azerite traits for all specs and all talent combinations."
  )
  parser.add_argument(
    "--executable",
    metavar="PATH",
    type=str,
    help="Relative path to SimulationCrafts executable. Default: '{}'".format(
      settings.executable
    )
  )
  parser.add_argument(
    "--profileset_work_threads",
    metavar="NUMBER",
    type=str,
    help=
    "Number of threads used per profileset by SimulationCraft. Default: '{}'".
    format(settings.profileset_work_threads)
  )
  parser.add_argument(
    "--threads",
    metavar="NUMBER",
    type=str,
    help="Number of threads used by SimulationCraft. Default: '{}'".format(
      settings.threads
    )
  )
  parser.add_argument(
    "--debug",
    action="store_const",
    const=True,
    default=False,
    help="Enables debug modus. Default: '{}'".format(settings.debug)
  )
  args = parser.parse_args()

  # activate debug mode as early as possible
  if args.debug:
    settings.debug = args.debug
    logger.setLevel(logging.DEBUG)
    fh.setLevel(logging.DEBUG)
    logger.debug("Set debug mode to {}".format(settings.debug))

  # if argument specified to simulate all, override settings
  if args.sim_all:
    settings.enable_race_simulations = True
    settings.enable_secondary_distributions_simulations = True
    settings.enable_trinket_simulations = True
    settings.enable_azerite_trait_simulations = True
    # set talent_list to empty to ensure all talent combinations are run
    settings.talent_list = {}
    logger.debug(
      "Set enable_race_simulations, enable_secondary_distributions_simulations, enable_trinket_simulations, and enable_azerite_trait_simulations to True."
    )

  # set new executable path if provided
  if args.executable:
    settings.executable = args.executable
    logger.debug("Set executable to {}".format(settings.executable))

  # set new threads if provided
  if args.threads:
    settings.threads = args.threads
    logger.debug("Set threads to {}".format(settings.threads))

  # set new profileset_work_threads if provided
  if args.profileset_work_threads:
    settings.profileset_work_threads = args.profileset_work_threads
    logger.debug(
      "Set profileset_work_threads to {}".format(
        settings.profileset_work_threads
      )
    )

  bloodytools_start_time = datetime.datetime.utcnow()

  # empty class-spec list or argument was provided to run all? great, we'll run all classes-specs
  if not settings.wow_class_spec_list or args.sim_all:
    settings.wow_class_spec_list = wow_lib.get_classes_specs()

  # list of all active threads. when empty, terminate tool
  thread_list = []

  # trigger race simulations
  if settings.enable_race_simulations:
    if not settings.use_own_threading:
      logger.info("Starting Race simulations.")

    if settings.use_own_threading:
      race_thread = threading.Thread(
        name="Race Thread",
        target=race_simulations,
        args=(settings.wow_class_spec_list,)
      )
      thread_list.append(race_thread)
      race_thread.start()
    else:
      race_simulations(settings.wow_class_spec_list)

    if not settings.use_own_threading:
      logger.info("Race simulations finished.")

  # trigger trinket simulations
  if settings.enable_trinket_simulations:
    if not settings.use_own_threading:
      logger.info("Starting Trinket simulations.")

    if settings.use_own_threading:
      trinket_thread = threading.Thread(
        name="Trinket Thread",
        target=trinket_simulations,
        args=(settings.wow_class_spec_list,)
      )
      thread_list.append(trinket_thread)
      trinket_thread.start()
    else:
      trinket_simulations(settings.wow_class_spec_list)

    if not settings.use_own_threading:
      logger.info("Trinket simulations finished.")

  # trigger secondary distributions
  if settings.enable_secondary_distributions_simulations:
    if not settings.use_own_threading:
      logger.info("Starting Secondary Distribution simulations.")

    for wow_class, wow_spec in settings.wow_class_spec_list:

      if not settings.talent_permutations:
        # get talent string from profile to sim
        try:
          with open(create_basic_profile_string(wow_class, wow_spec, settings.tier), 'r') as f:
            for line in f:
              if "talents=" in line:
                talent_combination = line.split("talents=")[1].split()[0]
        except Exception:
          logger.warning(f"Base profile for {wow_spec} {wow_class} not found. No secondary distribution will be calculated for this spec.")
          continue

        try:
          settings.talent_list[(wow_class, wow_spec)] = [
            talent_combination
          ]
        except Exception:
          logger.warning(f"No talent combination was found in base profile of {wow_spec} {wow_class}. Secondary Distribution won't be calculated for this spec.")
          continue

      # if no talent list is provided, simulate all
      if not (wow_class, wow_spec) in settings.talent_list:
        if settings.use_own_threading:
          secondary_distribution_thread = threading.Thread(
            name="Secondary Distribution Thread All Talents {} {}".format(
              wow_class, wow_spec
            ),
            target=secondary_distribution_simulations,
            args=(
              wow_class, wow_spec,
              wow_lib.get_talent_combinations(wow_class, wow_spec)
            )
          )
          thread_list.append(secondary_distribution_thread)
          secondary_distribution_thread.start()
        else:
          secondary_distribution_simulations(
            wow_class, wow_spec,
            wow_lib.get_talent_combinations(wow_class, wow_spec)
          )
      else:
        # if talent list is provided, sim that
        if settings.use_own_threading:
          secondary_distribution_thread = threading.Thread(
            name="Secondary Distribution Thread Provided Talents {} {}".
            format(wow_class, wow_spec),
            target=secondary_distribution_simulations,
            args=(
              wow_class, wow_spec, settings.talent_list[(wow_class, wow_spec)]
            )
          )
          thread_list.append(secondary_distribution_thread)
          secondary_distribution_thread.start()
        else:
          secondary_distribution_simulations(
            wow_class, wow_spec, settings.talent_list[(wow_class, wow_spec)]
          )

    if not settings.use_own_threading:
      logger.info("Secondary Distribution simulations finished.")

  # trigger azerite trait simulations
  if settings.enable_azerite_trait_simulations:
    if not settings.use_own_threading:
      logger.info("Starting Azerite Trait simulations.")

    if settings.use_own_threading:
      azerite_trait_thread = threading.Thread(
        name="Azerite Traits Thread",
        target=azerite_trait_simulations,
        args=(settings.wow_class_spec_list,)
      )
      thread_list.append(azerite_trait_thread)
      azerite_trait_thread.start()
    else:
      azerite_trait_simulations(settings.wow_class_spec_list)

    if not settings.use_own_threading:
      logger.info("Azerite Trait simulations finished.")

  # trigger gear path simulations
  if settings.enable_gear_path:
    if not settings.use_own_threading:
      logger.info("Gear Path simulations start.")

    if settings.use_own_threading:
      gearing_path_thread = threading.Thread(
        name="Gear Path Thread",
        target=gear_path_simulations,
        args=(settings.wow_class_spec_list,)
      )
      thread_list.append(gearing_path_thread)
      gearing_path_thread.start()
    else:
      gear_path_simulations(settings.wow_class_spec_list)

    if not settings.use_own_threading:
      logger.info("Gear Path simulations end.")

  while thread_list:
    time.sleep(1)
    for thread in thread_list:
      if thread.is_alive():
        logger.debug("{} is still in progress.".format(thread.getName()))
      else:
        logger.info("{} finished.".format(thread.getName()))
        thread_list.remove(thread)

  logger.info(
    "Bloodytools took {} to finish.".
    format(datetime.datetime.utcnow() - bloodytools_start_time)
  )
  logger.debug("main ended")


if __name__ == '__main__':
  logger.debug("__main__ start")
  main()
  logger.debug("__main__ ended")

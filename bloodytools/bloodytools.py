#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Welcome to bloodytools - a SimulationCraft automator/wrapper

Generate your data more easily without having to create each and every needed profile to do so by hand:
  - races
  - trinkets
  - azerite traits
  - secondary distributions
  - gear path

Output is usually saved as .json. But you can add different ways to output the data yourself.

Contact:
  - https://discord.gg/tFR2uvK Bloodmallet(EU)#8246

Github:
  - https://github.com/Bloodmallet/bloodytools

Support the development:
  - https://www.patreon.com/bloodmallet
  - https://www.paypal.me/bloodmallet

May 2018
"""

import argparse
import datetime
import json
import logging
import os
import re
import sys
import time
from typing import List, Tuple

import settings     # settings.py file
from simc_support import wow_lib
from simulation_objects import simulation_objects as so
from simulation_objects.azerite_trait_simulation import azerite_trait_simulations
from simulation_objects.corruption_simulation import corruption_simulation
from simulation_objects.essence_combination_simulation import essence_combination_simulation
from simulation_objects.essence_simulation import essence_simulation
from simulation_objects.trinket_simulation import trinket_simulation


if settings.use_own_threading:
  import threading

# logging to file and console
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# file handler
file_handler = logging.FileHandler("log.txt", "w", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter(
  "%(asctime)s - %(filename)s / %(funcName)s / %(lineno)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
if hasattr(settings, "debug"):
  if settings.debug:
    console_handler.setLevel(logging.DEBUG)
console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)


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
  split_path: list = settings.executable.split("simc")
  if len(split_path) > 2:
    # the path contains multiple "simc"
    basis_profile_string: str = "simc".join(split_path[:-1])
  else:
    basis_profile_string: str = split_path[0]

  # fix path for linux users
  if basis_profile_string.endswith("/engine/"):
    split_path = basis_profile_string.split("/engine/")
    if len(split_path) > 2:
      basis_profile_string = "/engine/".join(split_path[:-1])
    else:
      basis_profile_string = split_path[0] + "/"

  basis_profile_string += "profiles/"
  if tier == "PR":
    basis_profile_string += "PreRaids/PR_{}_{}".format(wow_class.title(), wow_spec.title())
  else:
    basis_profile_string += "Tier{}/T{}_{}_{}".format(tier, tier, wow_class, wow_spec).title()
  basis_profile_string += ".simc"

  logger.debug("Created basis_profile_string '{}'.".format(basis_profile_string))
  logger.debug("create_basic_profile_string ended")
  return basis_profile_string


def pretty_timestamp() -> str:
  """Returns a pretty time stamp "YYYY-MM-DD HH:MM"

  Returns:
    str -- timestamp
  """
  # str(datetime.datetime.utcnow())[:-10] should be the same
  return datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M")


def extract_profile(path: str, wow_class: str, profile: dict = None) -> dict:
  """Extract all character specific data from a given file.

  Arguments:
      path {str} -- path to file, relative or absolute
      profile {dict} -- profile input that should be updated

  Returns:
      dict -- all known character data
  """

  logger.warning(
    'DEPRICATION WARNING: profile format change. Information will be stored in its own subsection. Read result file to already get the new format.'
  )

  if not profile:
    profile = {}

  if not 'character' in profile:
    profile['character'] = {}

  profile['character']['class'] = wow_class

  # prepare regex for each extractable slot
  item_slots = [
    "head",
    "neck",
    "shoulders",
    "back",
    "chest",
    "wrists",
    "hands",
    "waist",
    "legs",
    "feet",
    "finger1",
    "finger2",
    "trinket1",
    "trinket2",
    "main_hand",
    "off_hand",
  ]
  pattern_slots = {}
  for element in item_slots:
    pattern_slots[element] = re.compile('^{}=([a-z0-9_=,/:.]*)$'.format(element))

  # prepare regex for item defining attributes
  item_elements = [
    "id",
    "bonus_id",
    "azerite_powers",
    "enchant",
    "azerite_level",     # neck
    "ilevel",
  ]
  pattern_element = {}
  # don't recompile this for each slot
  for element in item_elements:
    pattern_element[element] = re.compile(',{}=([a-z0-9_/:]*)'.format(element))

  # prepare regex for character defining information. like spec
  character_specifics = [
    'level',
    'race',
    'role',
    'position',
    'talents',
    'spec',
    'azerite_essences',
  ]
  pattern_specifics = {}
  for element in character_specifics:
    pattern_specifics[element] = re.compile('^{}=([a-z0-9_./:]*)$'.format(element))

  with open(path, 'r') as f:
    for line in f:
      for specific in character_specifics:

        matches = pattern_specifics[specific].search(line)
        if matches:
          profile['character'][specific] = matches.group(1)
          # TODO: remove after some time (webfront-end needs to be updated)
          profile[specific] = matches.group(1)

      for slot in item_slots:

        if not 'items' in profile:
          profile['items'] = {}

        matches = pattern_slots[slot].search(line)
        # slot line found
        if matches:
          new_line = matches.group(1)
          if not slot in profile:
            profile['items'][slot] = {}

          # allow pre-prepared profiles to get emptied if input wants to overwrite with empty
          # 'head=' as a head example for an empty overwrite
          if not new_line:
            profile['items'].pop(slot, None)

          # check for all elements
          for element in item_elements:
            new_matches = pattern_element[element].search(new_line)
            if new_matches:
              profile['items'][slot][element] = new_matches.group(1)
              # TODO: remove after some time (webfront-end needs to be updated)
              if not slot in profile:
                profile[slot] = {}
              profile[slot][element] = new_matches.group(1)

  logger.debug(profile)

  return profile


def create_base_json_dict(data_type: str, wow_class: str, wow_spec: str, fight_style: str):
  """Creates as basic json dictionary. You'll need to add your data into 'data'. Can be extended.

  Arguments:
    data_type {str} -- e.g. Races, Trinkets, Azerite Traits (str is used in the title)
    wow_class {str} -- [description]
    wow_spec {str} -- [description]
    fight_style {str} -- [description]

  Returns:
    dict -- [description]
  """

  logger.debug("create_base_json_dict start")

  timestamp = pretty_timestamp()

  profile_location = create_basic_profile_string(wow_class, wow_spec, settings.tier)

  profile = extract_profile(profile_location, wow_class)

  if settings.use_custom_profile:
    profile = extract_profile('custom_profile.txt', wow_class, profile)

  # spike the export data with talent data
  talent_data = wow_lib.get_talent_dict(wow_class, wow_spec, settings.ptr == "1")

  # add class/ id number
  class_id = wow_lib.get_class_id(wow_class)
  spec_id = wow_lib.get_spec_id(wow_class, wow_spec)

  subtitle = "UTC {timestamp}".format(timestamp=timestamp)
  if settings.simc_hash:
    subtitle += " | SimC build: <a href=\"https://github.com/simulationcraft/simc/commit/{simc_hash}\" target=\"blank\">{simc_hash_short}</a>".format(
      simc_hash=settings.simc_hash, simc_hash_short=settings.simc_hash[0:7]
    )

  return {
    "data_type": "{}".format(data_type.lower().replace(" ", "_")),
    "timestamp": timestamp,
    "title":
      "{data_type} | {wow_spec} {wow_class} | {fight_style}".format(
        data_type=data_type.title(),
        wow_class=wow_class.title().replace("_", " "),
        wow_spec=wow_spec.title().replace("_", " "),
        fight_style=fight_style.title()
      ),
    "subtitle": subtitle,
    "simc_settings": {
      "tier": settings.tier,
      "fight_style": fight_style,
      "iterations": settings.iterations,
      "target_error": settings.target_error[fight_style],
      "ptr": settings.ptr,
      "simc_hash": settings.simc_hash,
     # deprecated
      "class": wow_class,
     # deprecated
      "spec": wow_spec
    },
    "data": {},
    "languages": {},
    "profile": profile,
    "talent_data": talent_data,
    "class_id": class_id,
    "spec_id": spec_id
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
    return tokenize_str(string.replace("'", "").replace("-", "").replace(" ", "_").replace("__", "_").replace(",", ""))

  return string


def get_simc_hash(path) -> str:
  """Get the FETCH_HEAD or shallow simc git hash.

  Returns:
    str -- [description]
  """

  if ".exe" in path:
    new_path = path.split("simc.exe")[0]
  else:
    new_path = path[:-5]     # cut "/simc" from unix path
    if "engine" in new_path[-6:]:
      new_path = new_path[:-6]

  # add path to file to variable
  new_path += ".git/FETCH_HEAD"

  try:
    with open(new_path, 'r', encoding='utf-8') as f:
      for line in f:
        if "'bfa-dev'" in line:
          simc_hash = line.split()[0]
  except FileNotFoundError:
    try:
      with open('../../SimulationCraft/.git/shallow', 'r', encoding='utf-8') as f:
        for line in f:
          simc_hash = line.strip()
    except FileNotFoundError:
      logger.warning("Couldn't extract SimulationCraft git hash. Result files won't contain a sane hash.")
      simc_hash = None
    except Exception as e:
      logger.error(e)
      raise e
  except Exception as e:
    logger.error(e)
    raise e

  return simc_hash


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
        with open(create_basic_profile_string(wow_class, wow_spec, settings.tier), 'r') as f:
          pass
      except FileNotFoundError:
        logger.warning("{} {} base profile not found. Skipping.".format(wow_spec.title(), wow_class.title()))
        continue

      # prepare result json
      wanted_data = create_base_json_dict("Races", wow_class, wow_spec, fight_style)

      races = wow_lib.get_races_for_class(wow_class)
      simulation_group = so.Simulation_Group(
        name="race_simulations",
        threads=settings.threads,
        profileset_work_threads=settings.profileset_work_threads,
        executable=settings.executable,
        logger=logger
      )

      for race in races:

        simulation_data = None

        if race == races[0]:

          simulation_data = so.Simulation_Data(
            name=race.title().replace("_", " "),
            fight_style=fight_style,
            profile=wanted_data['profile'],
            simc_arguments=["race={}".format(race)],
            target_error=settings.target_error[fight_style],
            ptr=settings.ptr,
            default_actions=settings.default_actions,
            executable=settings.executable,
            iterations=settings.iterations,
            logger=logger
          )
        else:
          simulation_data = so.Simulation_Data(
            name=race.title().replace("_", " "),
            fight_style=fight_style,
            simc_arguments=["race={}".format(race)],
            target_error=settings.target_error[fight_style],
            ptr=settings.ptr,
            default_actions=settings.default_actions,
            executable=settings.executable,
            iterations=settings.iterations,
            logger=logger
          )

          # adding argument for zandalari trolls
          if race == 'zandalari_troll':
            simulation_data.simc_arguments.append('zandalari_loa=kimbul')
            simulation_data.name += ' Kimbul'

        simulation_group.add(simulation_data)
        logger.debug(("Added race '{}' in profile '{}' to simulation_group.".format(race, simulation_data.name)))

        if race == 'zandalari_troll':
          # create more loa profiles and add them
          simulation_data = None
          for loa in ['bwonsamdi', 'paku']:
            simulation_data = so.Simulation_Data(
              name='{} {}'.format(race.title().replace("_", " "), loa.title()),
              fight_style=fight_style,
              simc_arguments=["race={}".format(race), 'zandalari_loa={}'.format(loa)],
              target_error=settings.target_error[fight_style],
              ptr=settings.ptr,
              default_actions=settings.default_actions,
              executable=settings.executable,
              iterations=settings.iterations,
              logger=logger
            )
            simulation_group.add(simulation_data)
            logger.debug(("Added race '{}' in profile '{}' to simulation_group.".format(race, simulation_data.name)))

      logger.info("Start {} race simulation for {} {}.".format(fight_style, wow_class, wow_spec))
      try:
        if settings.use_raidbots and settings.apikey:
          settings.simc_hash = simulation_group.simulate_with_raidbots(settings.apikey)
        else:
          simulation_group.simulate()
      except Exception as e:
        logger.error("{} race simulation for {} {} failed. {}".format(fight_style.title(), wow_class, wow_spec, e))
        continue
      else:
        logger.info(
          "{} race simulation for {} {} ended successfully. Cleaning up.".format(
            fight_style.title(), wow_class, wow_spec
          )
        )

      for profile in simulation_group.profiles:
        logger.debug("Profile '{}' DPS: {}".format(profile.name, profile.get_dps()))

      logger.debug("Created base dict for json export. {}".format(wanted_data))

      # add dps values to json
      for profile in simulation_group.profiles:
        wanted_data["data"][profile.name] = profile.get_dps()
        logger.debug("Added '{}' with {} dps to json.".format(profile.name, profile.get_dps()))
        # add race translations to the final json
        translated_name = wow_lib.get_race_translation(profile.name)
        if translated_name:
          wanted_data["languages"][profile.name] = wow_lib.get_race_translation(profile.name)
        else:
          fake_translation = profile.name.title().replace("_", " ")
          wanted_data['languages'][profile.name] = {
            'en_US': fake_translation,
            'it_IT': fake_translation,
            'de_DE': fake_translation,
            'fr_FR': fake_translation,
            'ru_RU': fake_translation,
            'es_ES': fake_translation,
            'ko_KR': fake_translation,
            'cn_CN': fake_translation
          }

      # create ordered race name list
      tmp_list = []
      for race in wanted_data["data"]:
        tmp_list.append((race, wanted_data["data"][race]))
      logger.debug("tmp_list: {}".format(tmp_list))

      tmp_list = sorted(tmp_list, key=lambda item: item[1], reverse=True)
      logger.debug("Sorted tmp_list: {}".format(tmp_list))
      logger.info("Race {} won with {} dps.".format(tmp_list[0][0], tmp_list[0][1]))

      wanted_data["sorted_data_keys"] = []
      for race, _ in tmp_list:
        wanted_data["sorted_data_keys"].append(race)

      logger.debug("Final json: {}".format(wanted_data))

      if not os.path.isdir("results/races/"):
        os.makedirs("results/races/")

      # write json to file
      with open(
        "results/races/{}_{}_{}.json".format(wow_class.lower(), wow_spec.lower(), fight_style.lower()),
        "w",
        encoding="utf-8"
      ) as f:
        logger.debug("Print race json.")
        f.write(json.dumps(wanted_data, sort_keys=True, indent=4, ensure_ascii=False))
        logger.debug("Printed race json.")

  logger.debug("race_simulations ended")

def secondary_distribution_simulations(
  wow_class: str,
  wow_spec: str,
  talent_combinations: List[str] = [False],
) -> List[so.Simulation_Group]:
  """Simulates several secondary distributions for the baseline profile.

  Arguments:
    wow_class {str} -- [description]
    wow_spec {str} -- [description]

  Keyword Arguments:
    talent_combinations {List[str]} -- [description] (default: {[False]})

  Returns:
    List[so.Simulation_Group] -- [description]
  """

  logger.debug("secondary_distribution_simulations start")

  distribution_multipliers = []
  step_size = settings.secondary_distributions_step_size
  lower_border = 10     # percent
  upper_border = 70     # percent
  secondary_amount = 0

  # get secondary sum from profile
  try:
    with open(create_basic_profile_string(wow_class, wow_spec, settings.tier), 'r') as f:
      for line in f:
        if "gear_crit_rating=" in line:
          secondary_amount += int(line.split("=")[1])
        elif "gear_haste_rating=" in line:
          secondary_amount += int(line.split("=")[1])
        elif "gear_mastery_rating=" in line:
          secondary_amount += int(line.split("=")[1])
        elif "gear_versatility_rating=" in line:
          secondary_amount += int(line.split("=")[1])
  except FileNotFoundError:
    logger.warning("{} {} profile not found. Skipping.".format(wow_spec.title(), wow_class.title()))
    # end this try early, no profile, no calculations
    return

  if settings.use_custom_profile:
    try:
      with open('custom_profile.txt', 'r') as f:
        for line in f:
          if 'secondary_sum=' in line:
            secondary_amount = int(line.split('=')[1])
    except FileNotFoundError:
      logger.warning('Custom character file not found. Can\'t simulate this profile')
      return

  logger.debug("secondary_amount found: {}".format(secondary_amount))

  # generate all valied secondary distributions
  for c in range(lower_border, upper_border + step_size, step_size):
    for h in range(lower_border, upper_border + step_size, step_size):
      for m in range(lower_border, upper_border + step_size, step_size):
        for v in range(lower_border, upper_border + step_size, step_size):
          if c + h + m + v == 100:
            distribution_multipliers.append((c, h, m, v))

  logger.debug("'{}' different distributions generated.".format(len(distribution_multipliers)))

  for fight_style in settings.fight_styles:

    result_dict = create_base_json_dict("secondary_distributions", wow_class, wow_spec, fight_style)
    result_dict["sorted_data_keys"] = {}
    result_dict["secondary_sum"] = secondary_amount

    for talent_combination in talent_combinations:
      simulation_group = so.Simulation_Group(
        name=talent_combination,
        threads=settings.threads,
        profileset_work_threads=settings.profileset_work_threads,
        executable=settings.executable,
        logger=logger
      )

      for distribution_multiplier in distribution_multipliers:
        # if it is the first one
        if distribution_multiplier == distribution_multipliers[0]:

          s_o = so.Simulation_Data(
            name="{}_{}_{}_{}".format(
              distribution_multiplier[0], distribution_multiplier[1], distribution_multiplier[2],
              distribution_multiplier[3]
            ),
            fight_style=fight_style,
            target_error=settings.target_error[fight_style],
            iterations=settings.iterations,
            logger=logger,
            profile=result_dict['profile'],
            simc_arguments=[
              "gear_crit_rating={}".format(int(secondary_amount * (distribution_multiplier[0] / 100))),
              "gear_haste_rating={}".format(int(secondary_amount * (distribution_multiplier[1] / 100))),
              "gear_mastery_rating={}".format(int(secondary_amount * (distribution_multiplier[2] / 100))),
              "gear_versatility_rating={}".format(int(secondary_amount * (distribution_multiplier[3] / 100))),
            ],
            ptr=settings.ptr,
            default_actions=settings.default_actions,
            executable=settings.executable
          )

          custom_apl = None
          if settings.use_custom_apl:
            with open('custom_apl.txt') as f:
              custom_apl = f.read()
          if custom_apl:
            s_o.simc_arguments.append(custom_apl)

          custom_fight_style = None
          if settings.use_custom_fight_style:
            with open('custom_fight_style.txt') as f:
              custom_fight_style = f.read()
          if custom_fight_style:
            s_o.simc_arguments.append(custom_fight_style)

          simulation_group.add(s_o)
          # add the talent combination to the profileset, if one was provided
          if talent_combination:
            simulation_group.profiles[-1].simc_arguments.append("talents={}".format(talent_combination))
        else:
          simulation_group.add(
            so.Simulation_Data(
              name="{}_{}_{}_{}".format(
                distribution_multiplier[0], distribution_multiplier[1], distribution_multiplier[2],
                distribution_multiplier[3]
              ),
              fight_style=fight_style,
              target_error=settings.target_error[fight_style],
              iterations=settings.iterations,
              logger=logger,
              simc_arguments=[
                "gear_crit_rating={}".format(int(secondary_amount * (distribution_multiplier[0] / 100))),
                "gear_haste_rating={}".format(int(secondary_amount * (distribution_multiplier[1] / 100))),
                "gear_mastery_rating={}".format(int(secondary_amount * (distribution_multiplier[2] / 100))),
                "gear_versatility_rating={}".format(int(secondary_amount * (distribution_multiplier[3] / 100))),
              ],
              ptr=settings.ptr,
              default_actions=settings.default_actions,
              executable=settings.executable
            )
          )

      logger.info(
        "Start {} secondary distribution simulation for {} {} {}.".format(
          fight_style, wow_class, wow_spec, talent_combination
        )
      )

      try:
        if settings.use_raidbots:
          settings.simc_hash = simulation_group.simulate_with_raidbots(settings.apikey)
        else:
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
          "{} secondary distribution simulation for {} {} {} ended successfully. Cleaning up.".format(
            fight_style.title(), wow_class, wow_spec, talent_combination
          )
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
        result_dict["data"][talent_combination][profile.name] = profile.get_dps()

      # sort list
      stat_dps_list = sorted(stat_dps_list, key=lambda item: item[1], reverse=True)
      logger.info(
        "Stat distribution {} of talent combination {} won with {} dps.".format(
          stat_dps_list[0][0], talent_combination, stat_dps_list[0][1]
        )
      )

      # add debug information which is coincidentally the same as settings.write_humanreadable_secondary_distribution_file
      logger.debug("Secondary distribution list for {} (max:{}):".format(talent_combination, stat_dps_list[0][1]))

      # create directory if it doesn't exist
      if not os.path.isdir("results/"):
        os.makedirs("results/")

      # create directory if it doesn't exist
      if not os.path.isdir("results/secondary_distributions/"):
        os.makedirs("results/secondary_distributions/")

      if settings.write_humanreadable_secondary_distribution_file:
        with open(
          'results/secondary_distributions/{}_{}_{}.txt'.format(
            wow_class.lower(), wow_spec.lower(), fight_style.lower()
          ), 'a'
        ) as f:
          f.write(
            "Sorted secondary distribution list for {} (max:{}):\n".format(talent_combination, stat_dps_list[0][1])
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
        logger.debug("{}   {}  {}%".format(item[0], item[1], round(item[1] * 100 / stat_dps_list[0][1], 2)))
        if settings.write_humanreadable_secondary_distribution_file:
          with open(
            'results/secondary_distributions/{}_{}_{}.txt'.format(
              wow_class.lower(), wow_spec.lower(), fight_style.lower()
            ), 'a'
          ) as f:
            f.write("  {}   {}  {}%\n".format(item[0], item[1], round(item[1] * 100 / stat_dps_list[0][1], 2)))

      result_dict["sorted_data_keys"][talent_combination] = []
      for item in stat_dps_list:
        result_dict["sorted_data_keys"][talent_combination].append(item[0])

    # print file
    logger.debug(result_dict)

    if not os.path.isdir("results/secondary_distributions/"):
      os.makedirs("results/secondary_distributions/")

    with open(
      "results/secondary_distributions/{}_{}_{}.json".format(wow_class.lower(), wow_spec.lower(), fight_style.lower()),
      'w'
    ) as f:
      logger.debug("Print secondary distribution json.")
      f.write(json.dumps(result_dict, sort_keys=True, indent=4))
      logger.debug("Printed secondary distribution json.")
  logger.debug("secondary_distribution_simulations ended")


def gear_path_simulations(specs: List[Tuple[str, str]]) -> None:

  for fight_style in settings.fight_styles:
    gear_path = []
    for wow_class, wow_spec in specs:

      # check whether the baseline profile does exist
      try:
        with open(create_basic_profile_string(wow_class, wow_spec, settings.tier), 'r') as f:
          pass
      except FileNotFoundError:
        logger.warning("{} {} profile not found. Skipping.".format(wow_spec.title(), wow_class.title()))
        continue

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
        logger.warning(
          "Profile for {} {} couldn't be found. Will be left out in Gear Path simulations.".format(
            wow_spec, wow_class
          )
        )
        continue

      crit_rating = haste_rating = mastery_rating = vers_rating = settings.start_value

      while crit_rating + haste_rating + mastery_rating + vers_rating < secondary_sum:

        simulation_group = so.Simulation_Group(
          name="{} {} {}".format(fight_style, wow_spec, wow_class),
          executable=settings.executable,
          threads=settings.threads,
          profileset_work_threads=settings.profileset_work_threads,
          logger=logger
        )

        crit_profile = so.Simulation_Data(
          name="crit_profile",
          executable=settings.executable,
          fight_style=fight_style,
          target_error=settings.target_error[fight_style],
          logger=logger,
          simc_arguments=[
            base_profile_string, "gear_crit_rating={}".format(crit_rating + settings.step_size),
            "gear_haste_rating={}".format(haste_rating), "gear_mastery_rating={}".format(mastery_rating),
            "gear_versatility_rating={}".format(vers_rating)
          ],
          ptr=settings.ptr,
          default_actions=settings.default_actions
        )
        simulation_group.add(crit_profile)

        haste_profile = so.Simulation_Data(
          name="haste_profile",
          executable=settings.executable,
          fight_style=fight_style,
          target_error=settings.target_error[fight_style],
          logger=logger,
          simc_arguments=[
            "gear_crit_rating={}".format(crit_rating),
            "gear_haste_rating={}".format(haste_rating + settings.step_size),
            "gear_mastery_rating={}".format(mastery_rating), "gear_versatility_rating={}".format(vers_rating)
          ],
          ptr=settings.ptr,
          default_actions=settings.default_actions
        )
        simulation_group.add(haste_profile)

        mastery_profile = so.Simulation_Data(
          name="mastery_profile",
          executable=settings.executable,
          fight_style=fight_style,
          target_error=settings.target_error[fight_style],
          logger=logger,
          simc_arguments=[
            "gear_crit_rating={}".format(crit_rating), "gear_haste_rating={}".format(haste_rating),
            "gear_mastery_rating={}".format(mastery_rating + settings.step_size),
            "gear_versatility_rating={}".format(vers_rating)
          ],
          ptr=settings.ptr,
          default_actions=settings.default_actions
        )
        simulation_group.add(mastery_profile)

        vers_profile = so.Simulation_Data(
          name="vers_profile",
          executable=settings.executable,
          fight_style=fight_style,
          target_error=settings.target_error[fight_style],
          logger=logger,
          simc_arguments=[
            "gear_crit_rating={}".format(crit_rating), "gear_haste_rating={}".format(haste_rating),
            "gear_mastery_rating={}".format(mastery_rating),
            "gear_versatility_rating={}".format(vers_rating + settings.step_size)
          ],
          ptr=settings.ptr,
          default_actions=settings.default_actions
        )
        simulation_group.add(vers_profile)

        simulation_group.simulate()

        # ugly
        winner_dps = 0
        if crit_profile.get_dps() >= haste_profile.get_dps() and crit_profile.get_dps() >= mastery_profile.get_dps(
        ) and crit_profile.get_dps() >= vers_profile.get_dps():

          crit_rating += settings.step_size
          winner_dps = crit_profile.get_dps()
          logger.info(
            "Crit - {}/{}/{}/{}: {}".format(crit_rating, haste_rating, mastery_rating, vers_rating, winner_dps)
          )

        elif haste_profile.get_dps() >= crit_profile.get_dps() and haste_profile.get_dps() >= mastery_profile.get_dps(
        ) and haste_profile.get_dps() >= vers_profile.get_dps():

          haste_rating += settings.step_size
          winner_dps = haste_profile.get_dps()
          logger.info(
            "Haste - {}/{}/{}/{}: {}".format(crit_rating, haste_rating, mastery_rating, vers_rating, winner_dps)
          )

        elif mastery_profile.get_dps() >= haste_profile.get_dps() and mastery_profile.get_dps(
        ) >= crit_profile.get_dps() and mastery_profile.get_dps() >= vers_profile.get_dps():

          mastery_rating += settings.step_size
          winner_dps = mastery_profile.get_dps()
          logger.info(
            "Mastery - {}/{}/{}/{}: {}".format(crit_rating, haste_rating, mastery_rating, vers_rating, winner_dps)
          )

        elif vers_profile.get_dps() >= haste_profile.get_dps() and vers_profile.get_dps() >= mastery_profile.get_dps(
        ) and vers_profile.get_dps() >= crit_profile.get_dps():

          vers_rating += settings.step_size
          winner_dps = vers_profile.get_dps()
          logger.info(
            "Vers - {}/{}/{}/{}: {}".format(crit_rating, haste_rating, mastery_rating, vers_rating, winner_dps)
          )

        gear_path.append({"{}_{}_{}_{}".format(crit_rating, haste_rating, mastery_rating, vers_rating): winner_dps})

      logger.info(gear_path)

      result = create_base_json_dict("Gear Path", wow_class, wow_spec, fight_style)

      result['data'] = gear_path

      if not os.path.isdir('results/gear_path/'):
        os.makedirs('results/gear_path/')

      with open('results/gear_path/{}_{}_{}.json'.format(wow_class, wow_spec, fight_style), 'w') as f:
        json.dump(result, f, indent=4, sort_keys=True)


def talent_worth_simulations(specs: List[Tuple[str, str]]) -> None:
  """Function generates all possible talent combinations for all specs. Including empty dps talent rows. This way the dps gain of each talent can be calculated.

  Arguments:
    specs {List[Tuple[str, str]]} -- wow_class, wow_spec

  Returns:
    None -- [description]
  Creates json result files.
  """

  logger.debug("talent_worth_simulations start")

  for fight_style in settings.fight_styles:
    for wow_class, wow_spec in specs:

      # check whether the baseline profile does exist
      try:
        with open(create_basic_profile_string(wow_class, wow_spec, settings.tier), 'r') as f:
          pass
      except FileNotFoundError:
        logger.warning("{} {} profile not found. Skipping.".format(wow_spec.title(), wow_class.title()))
        continue

      base_profile_string = create_basic_profile_string(wow_class, wow_spec, settings.tier)

      simulation_group = so.Simulation_Group(
        name="{} {} {}".format(fight_style, wow_spec, wow_class),
        executable=settings.executable,
        threads=settings.threads,
        profileset_work_threads=settings.profileset_work_threads,
        logger=logger
      )

      talent_blueprint = wow_lib.get_talent_blueprint(wow_class, wow_spec)

      talent_combinations = []

      # build list of all talent combinations
      for first in range(4):
        for second in range(4):
          for third in range(4):
            for forth in range(4):
              for fifth in range(4):
                for sixth in range(4):
                  for seventh in range(4):

                    talent_combination = "{}{}{}{}{}{}{}".format(first, second, third, forth, fifth, sixth, seventh)

                    abort = False

                    tmp_count = 0

                    # compare all non-dps locations, use only dps talent rows
                    location = talent_blueprint.find("0")
                    while location > -1:
                      if talent_combination[tmp_count + location] != "0":
                        abort = True
                      tmp_count += location + 1
                      location = talent_blueprint[tmp_count:].find("0")

                    # skip talent combinations with too many (more than one) not chosen dps values
                    if talent_combination.count("0") > talent_blueprint.count("0") + 1:
                      abort = True

                    if abort:
                      continue

                    talent_combinations.append(talent_combination)
      logger.debug("Creating talent combinations: Done. Created {}.".format(len(talent_combinations)))

      base_profile = so.Simulation_Data(
        name="{}".format(talent_combinations[0]),
        fight_style=fight_style,
        simc_arguments=[base_profile_string, "talents={}".format(talent_combinations[0])],
        target_error=settings.target_error[fight_style],
        ptr=settings.ptr,
        default_actions=settings.default_actions,
        executable=settings.executable,
        iterations=settings.iterations,
        logger=logger
      )
      simulation_group.add(base_profile)

      # add all talent combinations to the simulation_group
      for talent_combination in talent_combinations[1:]:
        simulation_data = so.Simulation_Data(
          name="{}".format(talent_combination),
          fight_style=fight_style,
          simc_arguments=["talents={}".format(talent_combination)],
          target_error=settings.target_error[fight_style],
          ptr=settings.ptr,
          default_actions=settings.default_actions,
          executable=settings.executable,
          iterations=settings.iterations,
          logger=logger
        )
        simulation_group.add(simulation_data)

      logger.info(
        "Talent Worth {} {} {} {} profiles.".format(wow_spec, wow_class, fight_style, len(simulation_group.profiles))
      )

      # time to sim
      if settings.use_raidbots:
        simulation_group.simulate_with_raidbots(settings.apikey)
      else:
        simulation_group.simulate()

      export_json = create_base_json_dict("Talent Worth", wow_class, wow_spec, fight_style)

      # save all generated data in "data"
      for profile in simulation_group.profiles:
        export_json["data"][profile.name] = profile.get_dps()

      tmp_1 = []
      tmp_2 = []

      for talent_combination in export_json["data"]:
        if talent_combination.count("0") == talent_blueprint.count("0"):
          tmp_1.append((talent_combination, export_json["data"][talent_combination]))
        else:
          tmp_2.append((talent_combination, export_json["data"][talent_combination]))

      tmp_1 = sorted(tmp_1, key=lambda item: item[1], reverse=True)
      tmp_2 = sorted(tmp_2, key=lambda item: item[1], reverse=True)

      # add sorted key lists
      # 1 all usual talent combinations
      # 2 all talent combinations with one empty dps row
      export_json["sorted_data_keys"] = []
      export_json["sorted_data_keys_2"] = []

      for item in tmp_1:
        export_json["sorted_data_keys"].append(item[0])
      for item in tmp_2:
        export_json["sorted_data_keys_2"].append(item[0])

      # create directory if it doesn't exist
      if not os.path.isdir("results/talent_worth/"):
        os.makedirs("results/talent_worth/")

      file_name = "results/talent_worth/{}_{}_{}".format(wow_class.lower(), wow_spec.lower(), fight_style.lower())
      if settings.ptr == "1":
        file_name += "_ptr"

      # write json to file
      with open(file_name + ".json", "w", encoding="utf-8") as f:
        logger.debug("Print talent_worth json.")
        f.write(json.dumps(export_json, sort_keys=True, indent=4, ensure_ascii=False))
        logger.debug("Printed talent_worth json.")

  logger.debug("talent_worth_simulations end")
  pass


def main():
  logger.debug("main start")
  logger.info("Bloodytools at your service.")

  settings.logger = logger

  # interface parameters
  parser = argparse.ArgumentParser(description="Simulate different aspects of World of Warcraft data.")
  parser.add_argument(
    "-a",
    "--all",
    dest="sim_all",
    action="store_const",
    const=True,
    default=False,
    help="Simulate races, trinkets, secondary distributions, and azerite traits for all specs and all talent combinations."
  )
  parser.add_argument(
    "--executable",
    metavar="PATH",
    type=str,
    help="Relative path to SimulationCrafts executable. Default: '{}'".format(settings.executable)
  )
  parser.add_argument(
    "--profileset_work_threads",
    metavar="NUMBER",
    type=str,
    help="Number of threads used per profileset by SimulationCraft. Default: '{}'".format(
      settings.profileset_work_threads
    )
  )
  parser.add_argument(
    "--threads",
    metavar="NUMBER",
    type=str,
    help="Number of threads used by SimulationCraft. Default: '{}'".format(settings.threads)
  )
  parser.add_argument(
    "--debug",
    action="store_const",
    const=True,
    default=False,
    help="Enables debug modus. Default: '{}'".format(settings.debug)
  )
  parser.add_argument("-ptr", action="store_const", const=True, default=False, help="Enables ptr.")
  # sim only one type of data generation for one spec
  parser.add_argument(
    "-s",
    "--single_sim",
    dest="single_sim",
    metavar="STRING",
    type=str,
    help="Activate a single simulation on the local machine. <simulation_types> are races, azerite_traits, secondary_distributions, talent_worth, trinkets, essences, essence_combinations. Input structure: <simulation_type>,<wow_class>,<wow_spec>,<fight_style> e.g. -s races,shaman,elemental,patchwerk"
  )
  parser.add_argument(
    "--use_custom_profile",
    action="store_const",
    const=True,
    default=False,
    help="Enables usage of 'custom_profile.txt' in addition to the base profile. Default: '{}'".format(settings.debug)
  )
  parser.add_argument("--raidbots", action="store_const", const=True, default=False, help="Don't try this at home")

  args = parser.parse_args()

  # activate debug mode as early as possible
  if args.debug:
    settings.debug = args.debug
    logger.setLevel(logging.DEBUG)
    ch.setLevel(logging.DEBUG)
    logger.debug("Set debug mode to {}".format(settings.debug))

  if args.single_sim:
    logger.debug("-s / --single_sim detected")
    try:
      simulation_type, wow_class, wow_spec, fight_style = args.single_sim.split(',')
    except Exception:
      logger.error("-s / --single_sim arg is missing parameters. Read -h.")
      sys.exit("Input error. Bloodytools terminates.")

    # single sim will always use all cores unless --threads is defined
    settings.threads = ""
    settings.wow_class_spec_list = [(wow_class.lower(), wow_spec.lower())]
    settings.fight_styles = [fight_style]
    settings.iterations = "20000"
    # disable all simulation types
    settings.enable_race_simulations = False
    settings.enable_trinket_simulations = False
    settings.enable_secondary_distributions_simulations = False
    settings.enable_azerite_trait_simulations = False
    settings.enable_gear_path = False
    settings.enable_talent_worth_simulations = False
    settings.enable_azerite_essence_simulations = False
    settings.enable_azerite_essence_combination_simulations = False
    settings.enable_corruption_simulations = False

    # set dev options
    settings.use_own_threading = False
    settings.use_raidbots = False

    if simulation_type == "races":
      settings.enable_race_simulations = True
    elif simulation_type == "trinkets":
      settings.enable_trinket_simulations = True
    elif simulation_type == "azerite_traits":
      settings.enable_azerite_trait_simulations = True
    elif simulation_type == "secondary_distributions":
      settings.enable_secondary_distributions_simulations = True
    elif simulation_type == "talent_worth":
      settings.enable_talent_worth_simulations = True
    elif simulation_type == "essences":
      settings.enable_azerite_essence_simulations = True
    elif simulation_type == "essence_combinations":
      settings.enable_azerite_essence_combination_simulations = True
    elif simulation_type == "corruptions":
      settings.enable_corruption_simulations = True

  # if argument specified to simulate all, override settings
  elif args.sim_all:
    settings.enable_race_simulations = True
    settings.enable_secondary_distributions_simulations = True
    settings.enable_trinket_simulations = True
    settings.enable_azerite_trait_simulations = True
    settings.enable_corruption_simulations = True
    # set talent_list to empty to ensure all talent combinations are run
    settings.talent_list = {}

    settings.wow_class_spec_list = wow_lib.get_classes_specs()
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
    logger.debug("Set profileset_work_threads to {}".format(settings.profileset_work_threads))

  if args.ptr:
    settings.ptr = "1"

  if args.use_custom_profile:
    settings.use_custom_profile = args.use_custom_profile

  if args.raidbots:
    settings.use_raidbots = True

  # only
  new_hash = get_simc_hash(settings.executable)
  if new_hash:
    settings.simc_hash = new_hash
  if not hasattr(settings, 'simc_hash'):
    settings.simc_hash = None

  bloodytools_start_time = datetime.datetime.utcnow()

  # empty class-spec list? great, we'll run all class-spec combinations
  if not settings.wow_class_spec_list:
    settings.wow_class_spec_list = wow_lib.get_classes_specs()

  # list of all active threads. when empty, terminate tool
  thread_list = []

  # trigger race simulations
  if settings.enable_race_simulations:
    if not settings.use_own_threading:
      logger.info("Starting Race simulations.")

    if settings.use_own_threading:
      race_thread = threading.Thread(name="Race Thread", target=race_simulations, args=(settings.wow_class_spec_list,))
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
        name="Trinket Thread", target=trinket_simulation, args=(settings,)
      )
      thread_list.append(trinket_thread)
      trinket_thread.start()
    else:
      trinket_simulation(settings)

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
              if "talents=" in line[0:8]:
                # only lines starting with talents= are looked at, only the last element of that line is used to catch armory imports just fine
                talent_combination = line.split("talents=")[-1].split()[0]
        except Exception:
          logger.warning(
            "Base profile for {} {} not found. No secondary distribution will be calculated for this spec.".format(
              wow_spec, wow_class
            )
          )
          continue

        try:
          settings.talent_list[(wow_class, wow_spec)] = [talent_combination]
        except Exception:
          logger.warning(
            "No talent combination was found in base profile of {} {}. Secondary Distribution won't be calculated for this spec."
            .format(wow_spec, wow_class)
          )
          continue

      # if no talent list is provided, simulate all
      if not (wow_class, wow_spec) in settings.talent_list:
        if settings.use_own_threading:
          secondary_distribution_thread = threading.Thread(
            name="Secondary Distribution Thread All Talents {} {}".format(wow_class, wow_spec),
            target=secondary_distribution_simulations,
            args=(wow_class, wow_spec, wow_lib.get_talent_combinations(wow_class, wow_spec))
          )
          thread_list.append(secondary_distribution_thread)
          secondary_distribution_thread.start()
        else:
          secondary_distribution_simulations(wow_class, wow_spec, wow_lib.get_talent_combinations(wow_class, wow_spec))
      else:
        # if talent list is provided, sim that
        if settings.use_own_threading:
          secondary_distribution_thread = threading.Thread(
            name="Secondary Distribution Thread Provided Talents {} {}".format(wow_class, wow_spec),
            target=secondary_distribution_simulations,
            args=(wow_class, wow_spec, settings.talent_list[(wow_class, wow_spec)])
          )
          thread_list.append(secondary_distribution_thread)
          secondary_distribution_thread.start()
        else:
          secondary_distribution_simulations(wow_class, wow_spec, settings.talent_list[(wow_class, wow_spec)])

    if not settings.use_own_threading:
      logger.info("Secondary Distribution simulations finished.")

  # trigger azerite trait simulations
  if settings.enable_azerite_trait_simulations:
    if not settings.use_own_threading:
      logger.info("Starting Azerite Trait simulations.")

    if settings.use_own_threading:
      azerite_trait_thread = threading.Thread(
        name="Azerite Traits Thread", target=azerite_trait_simulations, args=(settings,)
      )
      thread_list.append(azerite_trait_thread)
      azerite_trait_thread.start()
    else:
      azerite_trait_simulations(settings)

    if not settings.use_own_threading:
      logger.info("Azerite Trait simulations finished.")

  # trigger gear path simulations
  if settings.enable_gear_path:
    if not settings.use_own_threading:
      logger.info("Gear Path simulations start.")

    if settings.use_own_threading:
      gearing_path_thread = threading.Thread(
        name="Gear Path Thread", target=gear_path_simulations, args=(settings.wow_class_spec_list,)
      )
      thread_list.append(gearing_path_thread)
      gearing_path_thread.start()
    else:
      gear_path_simulations(settings.wow_class_spec_list)

    if not settings.use_own_threading:
      logger.info("Gear Path simulations end.")

  # trigger talent worth simulations
  if settings.enable_talent_worth_simulations:
    if not settings.use_own_threading:
      logger.info("Talent Worth simulations start.")

    if settings.use_own_threading:
      talent_worth_thread = threading.Thread(
        name="Talent Worth Thread", target=talent_worth_simulations, args=(settings.wow_class_spec_list,)
      )
      thread_list.append(talent_worth_thread)
      talent_worth_thread.start()
    else:
      talent_worth_simulations(settings.wow_class_spec_list)

    if not settings.use_own_threading:
      logger.info("Talent Worth simulations end.")

  # trigger essence simulations
  if settings.enable_azerite_essence_simulations:
    if not settings.use_own_threading:
      logger.info("Essence simulations start.")

    if settings.use_own_threading:
      essence_thread = threading.Thread(name="Essence Thread", target=essence_simulation, args=(settings,))
      thread_list.append(essence_thread)
      essence_thread.start()
    else:
      essence_simulation(settings)

    if not settings.use_own_threading:
      logger.info("Essence simulations end.")

  # trigger essence simulations
  if settings.enable_azerite_essence_combination_simulations:
    if not settings.use_own_threading:
      logger.info("Essence combination simulations start.")

    if settings.use_own_threading:
      essence_combination_thread = threading.Thread(
        name="Essence Combinations Thread", target=essence_combination_simulation, args=(settings,)
      )
      thread_list.append(essence_combination_thread)
      essence_combination_thread.start()
    else:
      essence_combination_simulation(settings)

    if not settings.use_own_threading:
      logger.info("Essence combination simulations end.")

  # trigger corruption simulations
  if settings.enable_corruption_simulations:
    if not settings.use_own_threading:
      logger.info("Corruption simulations start.")

    if settings.use_own_threading:
      corruption_thread = threading.Thread(name="Corruption Thread", target=corruption_simulation, args=(settings,))
      thread_list.append(corruption_thread)
      corruption_thread.start()
    else:
      corruption_simulation(settings)

    if not settings.use_own_threading:
      logger.info("Corruption simulations end.")

  while thread_list:
    time.sleep(1)
    for thread in thread_list:
      if thread.is_alive():
        logger.debug("{} is still in progress.".format(thread.getName()))
      else:
        logger.info("{} finished.".format(thread.getName()))
        thread_list.remove(thread)

  logger.info("Bloodytools took {} to finish.".format(datetime.datetime.utcnow() - bloodytools_start_time))
  logger.debug("main ended")


if __name__ == '__main__':
  logger.debug("__main__ start")
  main()
  logger.debug("__main__ ended")

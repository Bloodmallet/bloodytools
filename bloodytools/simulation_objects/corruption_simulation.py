import json
import os
from typing import List, Tuple

from simc_support.wow_lib import get_corruptions
from utils.utils import create_base_json_dict, create_basic_profile_string

from .simulation_objects import Simulation_Data, Simulation_Group


def corruption_simulation(settings: object) -> None:
  """Simulates all available corruptions for the given specs.

  Args:
    settings (object): [description]

  Returns:
    None --
  """

  logger = settings.logger

  logger.debug("corruption_simulation start")

  specs: List[Tuple[str, str]] = settings.wow_class_spec_list

  for fight_style in settings.fight_styles:
    for wow_class, wow_spec in specs:

      # check if the baseline profile does exist
      try:
        with open(create_basic_profile_string(wow_class, wow_spec, settings.tier, settings), 'r') as f:
          pass
      except FileNotFoundError:
        logger.warning("{} {} base profile not found. Skipping.".format(wow_spec.title(), wow_class.title()))
        continue

      # prepare result json
      wanted_data = create_base_json_dict("Corruptions", wow_class, wow_spec, fight_style, settings)

      # prepare back-string
      back_string = 'back='
      for key in wanted_data['profile']['back'].keys():
        if key == 'bonus_id':
          continue
        back_string += f',{key}={wanted_data["profile"]["back"][key]}'
      back_string += f',bonus_id={wanted_data["profile"]["back"]["bonus_id"]}'

      corruptions = get_corruptions(wow_class.title(), wow_spec.title())
      simulation_group = Simulation_Group(
        name="corruptions",
        threads=settings.threads,
        profileset_work_threads=settings.profileset_work_threads,
        executable=settings.executable,
        logger=logger
      )

      # add baseline
      simulation_data = None

      simulation_data = Simulation_Data(
        name='baseline',
        fight_style=fight_style,
        profile=wanted_data['profile'],
        simc_arguments=[
          '',
        ],     # no special input is necessary in the baseline profile
        target_error=settings.target_error[fight_style],
        ptr=settings.ptr,
        default_actions=settings.default_actions,
        executable=settings.executable,
        iterations=settings.iterations,
        logger=logger
      )
      simulation_group.add(simulation_data)

      # create profiles for all corruptions and their ranks/level
      for corruption in corruptions.keys():
        rank: int
        for rank in corruptions[corruption].keys():

          bonus_id: int = corruptions[corruption][rank]['bonus_id']
          spell_id: int = corruptions[corruption][rank]['spell_id']
          corruption_rating: int = corruptions[corruption][rank]['corruption']

          simulation_data = None

          simulation_data = Simulation_Data(
            name='{}_{}'.format(corruption, rank),
            fight_style=fight_style,
            simc_arguments=[f"{back_string}/{bonus_id}"],
            target_error=settings.target_error[fight_style],
            ptr=settings.ptr,
            default_actions=settings.default_actions,
            executable=settings.executable,
            iterations=settings.iterations,
            logger=logger
          )

          simulation_group.add(simulation_data)
          logger.debug((
            "Added Corruption '{}:{}' in profile '{}' to simulation_group.".format(
              bonus_id, rank, simulation_data.name
            )
          ))

      logger.info("Start {} corruption simulation for {} {}.".format(fight_style, wow_class, wow_spec))
      try:
        if settings.use_raidbots and settings.apikey:
          settings.simc_hash = simulation_group.simulate_with_raidbots(settings.apikey)
        else:
          simulation_group.simulate()
      except Exception as e:
        logger.error(
          "{} corruption simulation for {} {} failed. {}".format(fight_style.title(), wow_class, wow_spec, e)
        )
        continue
      else:
        logger.info(
          "{} corruption simulation for {} {} ended successfully. Cleaning up.".format(
            fight_style.title(), wow_class, wow_spec
          )
        )

      for profile in simulation_group.profiles:
        logger.debug("Profile '{}' DPS: {}".format(profile.name, profile.get_dps()))

      logger.debug("Created base dict for json export. {}".format(wanted_data))

      if not 'data' in wanted_data:
        wanted_data['data'] = {}

      # add dps values to json
      for profile in simulation_group.profiles:

        if profile.name == 'baseline':
          wanted_data['data'][profile.name] = {}
          wanted_data['data'][profile.name]["1"] = profile.get_dps()
          logger.debug("Added '{}' with {} dps to json.".format(profile.name, profile.get_dps()))
          continue

        corruption_name: str = profile.name.split('_')[0]
        corruption_rank: int = profile.name.split('_')[1]
        corruption_bonus_id: int = corruptions[corruption_name][corruption_rank]['bonus_id']
        corruption_spell_id: int = corruptions[corruption_name][corruption_rank]['spell_id']
        corruption_rating: int = corruptions[corruption_name][corruption_rank]['corruption']

        # create missing subdict for dps
        if not corruption_name in wanted_data['data']:
          wanted_data['data'][corruption_name] = {}

        wanted_data['data'][corruption_name][corruption_rank] = profile.get_dps()
        logger.debug("Added '{}' with {} dps to json.".format(corruption_name, profile.get_dps()))

        # create missing subdict for spell data
        if not 'spell_ids' in wanted_data:
          wanted_data['spell_ids'] = {}

        if not corruption_name in wanted_data['spell_ids']:
          wanted_data['spell_ids'][corruption_name] = {}

        wanted_data['spell_ids'][corruption_name][corruption_rank] = corruption_spell_id

        # create missing subdict for corruption rating
        if not 'corruption_rating' in wanted_data:
          wanted_data['corruption_rating'] = {}

        if not corruption_name in wanted_data['corruption_rating']:
          wanted_data['corruption_rating'][corruption_name] = {}

        wanted_data['corruption_rating'][corruption_name][corruption_rank] = corruption_rating

      # create ordered corruption name list
      tmp_list = []     # dps
      tmp_list_2 = []     # dps/corruption rating
      corruption_name: str
      for corruption_name in wanted_data["data"]:
        if corruption_name == 'baseline':
          continue

        # append highest rank of corruption to sortable dps list
        tmp_list.append((
          corruption_name,
          wanted_data["data"][corruption_name][sorted(wanted_data["data"][corruption_name].keys(), reverse=True)[0]]
        ))

        for rank in wanted_data["data"][corruption_name]:
          tmp_list_2.append((
            f'{corruption_name} {rank}',     # boy...this'll become a mess in the frontend...
            (wanted_data["data"][corruption_name][rank] - wanted_data["data"]["baseline"]["1"]) /
            wanted_data['corruption_rating'][corruption_name][rank]
          ))

      logger.debug("tmp_list: {}".format(tmp_list))
      logger.debug("tmp_list_2: {}".format(tmp_list_2))

      tmp_list = sorted(tmp_list, key=lambda item: item[1], reverse=True)
      logger.debug("Sorted tmp_list: {}".format(tmp_list))
      logger.info("Corruption {} won with {} dps.".format(tmp_list[0][0], tmp_list[0][1]))

      wanted_data["sorted_data_keys"] = []
      for corruption_name, _ in tmp_list:
        wanted_data["sorted_data_keys"].append(corruption_name)

      tmp_list_2 = sorted(tmp_list_2, key=lambda item: item[1], reverse=True)
      logger.debug("Sorted tmp_list_2: {}".format(tmp_list_2))
      logger.info("Corruption {} won with {} dps.".format(tmp_list_2[0][0], tmp_list_2[0][1]))

      wanted_data["sorted_data_keys_2"] = []
      for corruption_name, _ in tmp_list_2:
        wanted_data["sorted_data_keys_2"].append(corruption_name)

      # add simulated steps...err ranks
      wanted_data['simulated_steps'] = []
      for i in range(1, 4):
        wanted_data['simulated_steps'].append(str(4 - i))     # get the steps into the proper order...descending

      logger.debug("Final json: {}".format(wanted_data))

      # write json to file
      partial_path: str = "results/corruptions/"
      if not os.path.isdir(partial_path):
        os.makedirs(partial_path)

      with open(
        "{}{}_{}_{}.json".format(partial_path, wow_class.lower(), wow_spec.lower(), fight_style.lower()),
        "w",
        encoding="utf-8"
      ) as f:
        logger.debug("Print corruption json.")
        f.write(json.dumps(wanted_data, sort_keys=True, indent=4, ensure_ascii=False))
        logger.debug("Printed corruption json.")

  logger.debug("corruption_simulation ended")

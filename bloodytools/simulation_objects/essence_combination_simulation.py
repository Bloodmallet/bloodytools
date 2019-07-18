from . import simulation_objects
from utils import utils # pylint: disable=no-name-in-module
from simc_support import wow_lib
from typing import List, Tuple

import json
import os



def essence_combination_simulation(settings: object) -> None:
  """Simulates all available races for all given specs.

  Arguments:
    specs {List[Tuple[str, str]]} -- List of all wanted wow_specs

  Returns:
    None --
  """
  logger = settings.logger

  logger.debug("essence_combination_simulation start")

  specs: List[Tuple[str, str]] = settings.wow_class_spec_list

  for fight_style in settings.fight_styles:
    for wow_class, wow_spec in specs:

      # check whether the baseline profile does exist
      try:
        with open(
          utils.create_basic_profile_string(wow_class, wow_spec, settings.tier, settings), 'r'
        ) as f:
          pass
      except FileNotFoundError:
        logger.warning(
          "{} {} base profile not found. Skipping.".
          format(wow_spec.title(), wow_class.title())
        )
        continue

      # prepare result json
      wanted_data = utils.create_base_json_dict(
        "Essence Combinations", wow_class, wow_spec, fight_style, settings
      )

      essences = wow_lib.get_essences(wow_class.title(), wow_spec.title())
      simulation_group = simulation_objects.Simulation_Group(
        name="essence_combinations",
        threads=settings.threads,
        profileset_work_threads=settings.profileset_work_threads,
        executable=settings.executable,
        logger=logger
      )

      # add baseline
      simulation_data = None

      simulation_data = simulation_objects.Simulation_Data(
        name='baseline',
        fight_style=fight_style,
        profile=wanted_data['profile'],
        simc_arguments=["azerite_essences="],
        target_error=settings.target_error[fight_style],
        ptr=settings.ptr,
        default_actions=settings.default_actions,
        executable=settings.executable,
        iterations=settings.iterations,
        logger=logger
      )
      simulation_group.add(simulation_data)

      # create profiles for all essences, all ranks, all minor/major types
      for major_essence_id in essences.keys():
        rank: int = 3 # using rank 3 only for these combinations
        for minor_essence_id in essences.keys():

          # skip combinations with itself
          if major_essence_id == minor_essence_id:
            continue

          simulation_data = None

          simulation_data = simulation_objects.Simulation_Data(
              name='{}_{}'.format(major_essence_id, minor_essence_id),
              fight_style=fight_style,
              simc_arguments=["azerite_essences={}:{}:1/{}:{}:0".format(major_essence_id, rank, minor_essence_id, rank)],
              target_error=settings.target_error[fight_style],
              ptr=settings.ptr,
              default_actions=settings.default_actions,
              executable=settings.executable,
              iterations=settings.iterations,
              logger=logger
          )

          simulation_group.add(simulation_data)
          logger.debug(
              (
              "Added azerite essence '{}:{}:{}' in profile '{}' to simulation_group.".format(
                  major_essence_id, rank, minor_essence_id, simulation_data.name
              )
              )
          )

          # special case worldvein
          if major_essence_id == "4" or minor_essence_id == "4":
              special_case = None
              special_case = simulation_data.copy()
              special_case.name += "+3"
              special_case.simc_arguments.append("bfa.worldvein_allies=3")
              simulation_group.add(special_case)

      logger.info(
        "Start {} essence combintion simulation for {} {}.".format(
          fight_style, wow_class, wow_spec
        )
      )
      try:
        if settings.use_raidbots and settings.apikey:
          settings.simc_hash = simulation_group.simulate_with_raidbots(settings.apikey)
        else:
          simulation_group.simulate()
      except Exception as e:
        logger.error(
          "{} essence simulation combintion for {} {} failed. {}".format(
            fight_style.title(), wow_class, wow_spec, e
          )
        )
        continue
      else:
        logger.info(
          "{} essence combintion simulation for {} {} ended successfully. Cleaning up.".
          format(fight_style.title(), wow_class, wow_spec)
        )

      for profile in simulation_group.profiles:
        logger.debug(
          "Profile '{}' DPS: {}".format(profile.name, profile.get_dps())
        )

      logger.debug("Created base dict for json export. {}".format(wanted_data))

      if not 'data' in wanted_data:
        wanted_data['data'] = {}

      # add dps values to json
      for profile in simulation_group.profiles:

        if profile.name == 'baseline':
          wanted_data['data'][profile.name] = profile.get_dps()
          logger.debug(
            "Added '{}' with {} dps to json.".format(
              profile.name, profile.get_dps()
            )
          )
          continue

        major_essence_id: int = int(profile.name.split('_')[0])
        major_essence_name: str = essences[str(major_essence_id)]['name']
        minor_essence_id: int = int(profile.name.split('_')[1].split('+')[0])
        minor_essence_name: str = essences[str(minor_essence_id)]['name']

        full_name = major_essence_name + " +" + minor_essence_name + " minor"

        # add special cases
        if '+' in profile.name:
          for i, plus in enumerate(profile.name.split('+')):
            if i > 0:
              full_name += ' +' + plus

        wanted_data['data'][full_name] = profile.get_dps()
        logger.debug(
          "Added '{}' as '{}' with {} dps to json.".format(
            profile.name, full_name, profile.get_dps()
          )
        )
        # adding spell data to dict
        if not 'spell_ids' in wanted_data:
          wanted_data['spell_ids'] = {}

        if not major_essence_name in wanted_data['spell_ids']:
          wanted_data['spell_ids'][major_essence_name] = essences[str(major_essence_id)]['major']['spell_id']

        if not minor_essence_name in wanted_data['spell_ids']:
          wanted_data['spell_ids'][minor_essence_name + ' minor'] = essences[str(minor_essence_id)]['minor']['spell_id']

        # adding power ids to dict
        power_id_name = 'power_ids'
        if not power_id_name in wanted_data:
          wanted_data[power_id_name] = {}

        if not major_essence_name in wanted_data[power_id_name]:
          wanted_data[power_id_name][major_essence_name] = wow_lib.get_essence_power_id(major_essence_id)

        if not minor_essence_name in wanted_data[power_id_name]:
          wanted_data[power_id_name][minor_essence_name + ' minor'] = wow_lib.get_essence_power_id(minor_essence_id)

      # create ordered essence name list
      tmp_list = []
      essence_name: str
      for essence_name in wanted_data["data"]:
        if essence_name == 'baseline':
          continue
        tmp_list.append((essence_name, wanted_data["data"][essence_name]))
      logger.debug("tmp_list: {}".format(tmp_list))

      tmp_list = sorted(tmp_list, key=lambda item: item[1], reverse=True)
      logger.debug("Sorted tmp_list: {}".format(tmp_list))
      logger.info(f"Essence {tmp_list[0][0]} won with {tmp_list[0][1]} dps.")

      wanted_data["sorted_data_keys"] = []
      for essence_name, _ in tmp_list:
        wanted_data["sorted_data_keys"].append(essence_name)

      # add simulated steps...err ranks
      # wanted_data['simulated_steps'] = []

      logger.debug("Final json: {}".format(wanted_data))

      partial_path: str = "results/essence_combinations/"

      if not os.path.isdir(partial_path):
        os.makedirs(partial_path)

      # write json to file
      with open(
        "{}{}_{}_{}.json".format(
          partial_path, wow_class.lower(), wow_spec.lower(), fight_style.lower()
        ), "w", encoding="utf-8"
      ) as f:
        logger.debug("Print essence combinations json.")
        f.write(json.dumps(wanted_data, sort_keys=True, indent=4, ensure_ascii=False))
        logger.debug("Printed essence combinations json.")

  logger.debug("essence_combination_simulation ended")


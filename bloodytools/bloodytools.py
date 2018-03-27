#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import settings
import simulation_objects.simulation_objects as simulation_objects
from simc_support import wow_lib

# activate logging to file and console
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# file logger
fh = logging.FileHandler("log.txt", "w")
fh.setLevel(logging.ERROR)
if hasattr(settings, "debug"):
  if settings.debug:
    fh.setLevel(logging.DEBUG)
log_formatter = logging.Formatter(
  "%(asctime)s - %(filename)s / %(funcName)s - %(levelname)s - %(message)s"
)
fh.setFormatter(log_formatter)
logger.addHandler(fh)
# console logger
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(log_formatter)
logger.addHandler(ch)


def race_simulations(specs: [(str, str)]):
  logger.debug("Started")
  for fight_style in settings.fight_styles:
    for wow_class, wow_spec in specs:
      races = wow_lib.get_races_of_class(wow_class)
      simulation_group = simulation_objects.simulation_group(
        name="race_simulations",
        threads=settings.threads,
        profileset_work_threads=settings.profileset_work_threads,
        executable=settings.executable,
        logger=logger
      )

      for race in races:

        simulation_data = None

        if race == races[0]:
          # create the basis profile string
          basis_profile_string = settings.executable.split("simc")[0]
          basis_profile_string += "profiles/"
          if settings.tier == "PR":
            basis_profile_string += "PreRaids/"
          else:
            basis_profile_string += "Tier{}/".format(settings.tier)
          basis_profile_string += "T{}_{}_{}".format(
            settings.tier, wow_class, wow_spec
          ).title()
          basis_profile_string += ".simc"

          logger.debug(
            "Created basis_profile_string '{}'.".format(basis_profile_string)
          )

          simulation_data = simulation_objects.simulation_data(
            name=race,
            fight_style=fight_style,
            simc_arguments=[basis_profile_string, "race={}".format(race)],
            logger=logger
          )
        else:
          simulation_data = simulation_objects.simulation_data(
            name=race,
            fight_style=fight_style,
            simc_arguments=["race={}".format(race)],
            logger=logger
          )
        simulation_group.add(simulation_data)
        logger.debug((
          "Added race '{}' in profile '{}' to simulation_group.".format(
            simulation_data.name, race
          )
        ))
      logger.debug("Start simulation.")
      simulation_group.simulate()
      logger.debug("Finished simulation.")
      for profile in simulation_group.profiles:
        logger.debug(
          "Profile '{}' DPS: {}".format(profile.name, profile.get_dps())
        )

  logger.debug("Ended")
  pass


def main():
  logger.debug("Started")
  race_simulations([("shaman", "elemental")])
  logger.debug("Ended")


if __name__ == '__main__':
  logger.debug("__main__ started")
  main()
  logger.debug("__main__ ended")

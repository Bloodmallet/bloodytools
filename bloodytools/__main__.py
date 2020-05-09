import argparse
import logging

from bloodytools import settings
from bloodytools.bloodytools import main
from bloodytools.bloodytools import logger_config

if __name__ == '__main__':
    logger = logger_config()
    logger.debug("__main__ start")

    settings.logger = logger

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
        help="Simulate races, trinkets, secondary distributions, and azerite traits for all specs and all talent combinations."
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
        help="Number of threads used per profileset by SimulationCraft. Default: '{}'".format(
            settings.profileset_work_threads
        )
    )
    parser.add_argument(
        "--threads",
        metavar="NUMBER",
        type=str,
        help="Number of threads used by SimulationCraft. Default: '{}'".format(
            settings.threads)
    )
    parser.add_argument(
        "--debug",
        action="store_const",
        const=True,
        default=settings.debug,
        help="Enables debug modus. Default: '{}'".format(settings.debug)
    )
    parser.add_argument(
        "-ptr", action="store_const", const=True, default=False, help="Enables ptr."
    )
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
        "--custom_profile",
        action="store_const",
        const=True,
        default=False,
        help="Enables usage of 'custom_profile.txt' in addition to the base profile. Default: '{}'"
        .format(settings.debug)
    )
    parser.add_argument(
        "--custom_apl",
        action="store_const",
        const=True,
        default=False,
        help="Enables usage of 'custom_apl.txt' in addition to the base profile. Default: '{}'"
        .format(settings.debug)
    )
    parser.add_argument(
        "--custom_fight_style",
        action="store_const",
        const=True,
        default=False,
        help="Enables usage of 'custom_fight_style.txt' in addition to the base profile. Default: '{}'"
        .format(settings.debug)
    )
    parser.add_argument(
        "--target_error",
        metavar='STRING',
        type=str,
        help="Overwrites target_error for all simulations. Default: whatever is in setting.py"
    )
    parser.add_argument(
        "--raidbots",
        action="store_const",
        const=True,
        default=False,
        help="Don't try this at home"
    )

    args = parser.parse_args()

    main(args)
    logger.debug("__main__ ended")

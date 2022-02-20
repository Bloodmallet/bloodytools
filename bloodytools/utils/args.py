import argparse
from bloodytools.simulations import simulator_factory
from bloodytools.utils.config import Config


def arg_parse_config():
    settings = Config()
    parser = argparse.ArgumentParser(
        description="Simulate different aspects of World of Warcraft data."
    )
    parser.add_argument(
        "--executable",
        metavar="PATH",
        type=str,
        help="Relative path to SimulationCrafts executable. Default: '{}'".format(
            settings.executable
        ),
    )
    parser.add_argument(
        "--profileset_work_threads",
        metavar="NUMBER",
        type=str,
        help="Number of threads used per profileset by SimulationCraft. Default: '{}'".format(
            settings.profileset_work_threads
        ),
    )
    parser.add_argument(
        "--threads",
        metavar="NUMBER",
        type=str,
        help="Number of threads used by SimulationCraft. Empty means all available threads will be used. Default: '{}'".format(
            settings.threads
        ),
    )
    parser.add_argument(
        "--debug",
        action="store_const",
        const=True,
        default=settings.debug,
        help="Enables debug modus. Default: '{}'".format(settings.debug),
    )
    parser.add_argument(
        "-ptr",
        "--ptr",
        action="store_const",
        # TODO: switch True and False after 9.2 goes live
        const=True,
        default=True,
        help="Enables ptr.",
    )
    names = ", ".join(
        [
            simulator.snake_case_name()
            for simulator in simulator_factory.list_simulators()
        ]
    )
    # sim only one type of data generation for one spec
    parser.add_argument(
        "-s",
        "--single_sim",
        dest="single_sim",
        metavar="STRING",
        type=str,
        help=f"Activate a single simulation on the local machine. <simulation_types> are {names}. Input structure: <simulation_type>,<wow_class>,<wow_spec>,<fight_style> e.g. -s races,shaman,elemental,patchwerk",
    )
    parser.add_argument(
        "--custom_profile",
        action="store_const",
        const=True,
        default=False,
        help="Enables usage of 'custom_profile.txt' in addition to the base profile. Default: '{}'".format(
            settings.custom_profile
        ),
    )
    parser.add_argument(
        "--custom_apl",
        action="store_const",
        const=True,
        default=False,
        help="Enables usage of 'custom_apl.txt' in addition to the base profile. Default: '{}'".format(
            settings.custom_apl
        ),
    )
    parser.add_argument(
        "--custom_fight_style",
        action="store_const",
        const=True,
        default=False,
        help="Enables usage of 'custom_fight_style.txt' in addition to the base profile. Default: '{}'".format(
            settings.custom_fight_style
        ),
    )
    parser.add_argument(
        "--target_error",
        metavar="STRING",
        type=str,
        help="Overwrites target_error for all simulations. Default: whatever is in setting.py",
    )
    parser.add_argument(
        "--keep_files",
        action="store_const",
        const=True,
        default=False,
        help="Keep generated simc input and output files.",
    )
    parser.add_argument(
        "--pretty",
        action="store_const",
        const=True,
        default=False,
        help="Indent result files to make them more human readable.",
    )
    parser.add_argument(
        "--raidbots",
        action="store_const",
        const=True,
        default=False,
        help="Don't try this at home",
    )

    return parser.parse_args()

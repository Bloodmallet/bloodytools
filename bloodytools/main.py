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

import datetime
import logging
import sys
import threading
import time


from bloodytools import settings

# from bloodytools.simulations.gear_path_simulation import gear_path_simulation
# from bloodytools.simulations.race_simulation import race_simulation
# from bloodytools.simulations.secondary_distribution_simulation import secondary_distribution_simulation
from bloodytools.simulations.trinket_simulation import trinket_simulation
from bloodytools.simulations.soul_bind_simulation import soul_bind_simulation

# from bloodytools.simulations.talent_worth_simulation import talent_worth_simulation
from bloodytools.utils.utils import get_simc_hash
from bloodytools.utils.utils import arg_parse_config
from bloodytools.utils.utils import logger_config
from simc_support.game_data.WowSpec import WOWSPECS, get_wow_spec


def main():
    args = arg_parse_config()

    # activate debug mode as early as possible
    if args.debug:
        settings.debug = args.debug

    logger = logger_config()

    settings.logger = logger

    logger.debug("main start")
    logger.info("Bloodytools at your service.")

    if args.single_sim:
        logger.debug("-s / --single_sim detected")
        try:
            simulation_type, wow_class, wow_spec, fight_style = args.single_sim.split(
                ","
            )
        except Exception:
            logger.error("-s / --single_sim arg is missing parameters. Read -h.")
            sys.exit("Input error. Bloodytools terminates.")

        # single sim will always use all cores unless --threads is defined
        settings.threads = ""
        settings.wow_class_spec_list = [
            get_wow_spec(wow_class, wow_spec),
        ]
        settings.fight_styles = [
            fight_style,
        ]
        settings.iterations = "20000"
        # disable all simulation types
        settings.enable_race_simulations = False
        settings.enable_trinket_simulations = False
        settings.enable_secondary_distributions_simulations = False
        settings.enable_gear_path = False
        settings.enable_talent_worth_simulations = False
        settings.enable_soul_bind_simulations = False

        # set dev options
        settings.use_own_threading = False
        settings.use_raidbots = False

        # TODO: re-enable other simulation types
        # if simulation_type == "races":
        #     settings.enable_race_simulations = True
        if simulation_type == "trinkets":
            settings.enable_trinket_simulations = True
        elif simulation_type == "soul_binds":
            settings.enable_soul_bind_simulations = True
        # elif simulation_type == "secondary_distributions":
        #     settings.enable_secondary_distributions_simulations = True
        # elif simulation_type == "talent_worth":
        #     settings.enable_talent_worth_simulations = True

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
            "Set profileset_work_threads to {}".format(settings.profileset_work_threads)
        )

    if args.ptr:
        settings.ptr = "1"

    if args.custom_profile:
        settings.custom_profile = args.custom_profile

    if args.custom_apl:
        settings.custom_apl = args.custom_apl
        settings.default_actions = "0"

    if args.custom_fight_style:
        settings.custom_fight_style = args.custom_fight_style

    if args.target_error:
        for fight_style in settings.target_error:
            settings.target_error[fight_style] = args.target_error

    if args.raidbots:
        settings.use_raidbots = True

    # only
    new_hash = get_simc_hash(settings.executable)
    if new_hash:
        settings.simc_hash = new_hash
    if not hasattr(settings, "simc_hash"):
        settings.simc_hash = None

    bloodytools_start_time = datetime.datetime.utcnow()

    # empty class-spec list? great, we'll run all class-spec combinations
    if not settings.wow_class_spec_list:
        settings.wow_class_spec_list = WOWSPECS

    # list of all active threads. when empty, terminate tool
    thread_list = []

    # TODO: re-enable other simulation types
    # trigger race simulations
    # if settings.enable_race_simulations:
    #     if not settings.use_own_threading:
    #         logger.info("Starting Race simulations.")

    #     if settings.use_own_threading:
    #         race_thread = threading.Thread(
    #             name="Race Thread", target=race_simulation, args=(settings.wow_class_spec_list, settings)
    #         )
    #         thread_list.append(race_thread)
    #         race_thread.start()
    #     else:
    #         race_simulation(settings.wow_class_spec_list, settings)

    #     if not settings.use_own_threading:
    #         logger.info("Race simulations finished.")

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

    if settings.enable_soul_bind_simulations:
        if not settings.use_own_threading:
            logger.info("Starting Soul Bind simulations.")

        if settings.use_own_threading:
            soul_bind_thread = threading.Thread(
                name="Soul Bind Thread", target=soul_bind_simulation, args=(settings,)
            )
            thread_list.append(soul_bind_thread)
            soul_bind_thread.start()
        else:
            soul_bind_simulation(settings)

        if not settings.use_own_threading:
            logger.info("Soul Bind simulations finished.")

    # TODO: re-enable other simulation types
    # trigger secondary distributions
    # if settings.enable_secondary_distributions_simulations:

    #     if not settings.use_own_threading:
    #         logger.info("Starting Secondary Distribtion simulations.")

    #     if settings.use_own_threading:
    #         secondary_distribution_thread = threading.Thread(
    #             name="Secondary Distribution Thread",
    #             target=secondary_distribution_simulation,
    #             args=(settings,)
    #         )
    #         thread_list.append(secondary_distribution_thread)
    #         secondary_distribution_thread.start()
    #     else:
    #         secondary_distribution_simulation(settings)

    #     if not settings.use_own_threading:
    #         logger.info("Secondary Distribution simulations finished.")

    # TODO: re-enable other simulation types
    # trigger gear path simulations
    # if settings.enable_gear_path:
    #     if not settings.use_own_threading:
    #         logger.info("Gear Path simulations start.")

    #     if settings.use_own_threading:
    #         gearing_path_thread = threading.Thread(
    #             name="Gear Path Thread",
    #             target=gear_path_simulation,
    #             args=(settings.wow_class_spec_list, settings)
    #         )
    #         thread_list.append(gearing_path_thread)
    #         gearing_path_thread.start()
    #     else:
    #         gear_path_simulation(settings.wow_class_spec_list, settings)

    #     if not settings.use_own_threading:
    #         logger.info("Gear Path simulations end.")

    # TODO: re-enable other simulation types
    # trigger talent worth simulations
    # if settings.enable_talent_worth_simulations:
    #     if not settings.use_own_threading:
    #         logger.info("Talent Worth simulations start.")

    #     if settings.use_own_threading:
    #         talent_worth_thread = threading.Thread(
    #             name="Talent Worth Thread",
    #             target=talent_worth_simulation,
    #             args=(settings.wow_class_spec_list, settings)
    #         )
    #         thread_list.append(talent_worth_thread)
    #         talent_worth_thread.start()
    #     else:
    #         talent_worth_simulation(settings.wow_class_spec_list, settings)

    #     if not settings.use_own_threading:
    #         logger.info("Talent Worth simulations end.")

    while thread_list:
        time.sleep(1)
        for thread in thread_list:
            if thread.is_alive():
                logger.debug("{} is still in progress.".format(thread.getName()))
            else:
                logger.info("{} finished.".format(thread.getName()))
                thread_list.remove(thread)

    logger.info(
        "Bloodytools took {} to finish.".format(
            datetime.datetime.utcnow() - bloodytools_start_time
        )
    )
    logger.debug("main ended")


if __name__ == "__main__":
    main()

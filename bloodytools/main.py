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

from simc_support.game_data.WowSpec import WOWSPECS, get_wow_spec

from bloodytools import settings

# from bloodytools.simulations.gear_path_simulation import gear_path_simulation
from bloodytools.simulations.conduit_simulation import conduit_simulation
from bloodytools.simulations.covenant_simulation import covenant_simulation
from bloodytools.simulations.domination_shard_simulation import (
    domination_shard_simulation,
)
from bloodytools.simulations.legendary_simulations import legendary_simulation
from bloodytools.simulations import simulator_factory
from bloodytools.simulations.simulator import simulator_wrapper
from bloodytools.simulations.secondary_distribution_simulation import (
    secondary_distribution_simulation,
)
from bloodytools.simulations.soul_bind_node_simulation import soul_bind_node_simulation
from bloodytools.simulations.soul_bind_simulation import soul_bind_simulation
from bloodytools.simulations.talent_simulation import talent_simulation
from bloodytools.simulations.trinket_simulation import trinket_simulation
from bloodytools.utils.utils import get_simc_hash, arg_parse_config
from bloodytools.utils.config import Config

logger = logging.getLogger(__name__)


def _update_settings(args: object, logger: logging.Logger) -> Config:

    config = Config().update(settings)

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
        config.threads = ""
        config.wow_class_spec_list = [
            get_wow_spec(wow_class, wow_spec),
        ]
        config.fight_styles = [
            fight_style,
        ]
        if args.target_error:
            config.target_error[fight_style] = args.target_error
        config.iterations = "20000"
        # disable all simulation types
        config.enable_race_simulations = False
        config.enable_trinket_simulations = False
        config.enable_secondary_distributions_simulations = False
        config.enable_gear_path = False
        config.enable_talent_simulations = False
        config.enable_soul_bind_simulations = False
        config.enable_soul_bind_node_simulations = False
        config.enable_conduit_simulations = False
        config.enable_covenant_simulations = False
        config.enable_domination_shards = False

        # set dev options
        config.use_own_threading = False
        config.use_raidbots = False

        if simulation_type == "races":
            config.enable_race_simulations = True
        elif simulation_type == "trinkets":
            config.enable_trinket_simulations = True
        elif simulation_type == "soul_binds":
            config.enable_soul_bind_simulations = True
        elif simulation_type == "soul_bind_nodes":
            config.enable_soul_bind_node_simulations = True
        elif simulation_type == "conduits":
            config.enable_conduit_simulations = True
        elif simulation_type == "secondary_distributions":
            config.enable_secondary_distributions_simulations = True
        elif simulation_type == "legendaries":
            config.enable_legendary_simulations = True
        elif simulation_type == "talents":
            config.enable_talent_simulations = True
        elif simulation_type == "covenants":
            config.enable_covenant_simulations = True
        elif simulation_type == "domination_shards":
            config.enable_domination_shards = True
        else:
            raise ValueError("Unknown simulation type entered.")

    # set new executable path if provided
    if args.executable:
        config.executable = args.executable
        logger.debug("Set executable to {}".format(config.executable))

    # set new threads if provided
    if args.threads:
        config.threads = args.threads
        logger.debug("Set threads to {}".format(config.threads))

    # set new profileset_work_threads if provided
    if args.profileset_work_threads:
        config.profileset_work_threads = args.profileset_work_threads
        logger.debug(
            "Set profileset_work_threads to {}".format(config.profileset_work_threads)
        )

    if args.ptr:
        config.ptr = "1"

    if args.custom_profile:
        config.custom_profile = args.custom_profile

    if args.custom_apl:
        config.custom_apl = args.custom_apl
        config.default_actions = "0"

    if args.custom_fight_style:
        config.custom_fight_style = args.custom_fight_style

    if args.target_error:
        for fight_style in config.target_error:
            config.target_error[fight_style] = args.target_error

    if args.raidbots:
        config.use_raidbots = True

    config.keep_files = args.keep_files
    config.pretty = args.pretty

    return config


def main(args=None):

    logger.debug("main start")
    logger.info("Bloodytools at your service.")

    config = _update_settings(args, logger)

    # only
    new_hash = get_simc_hash(config.executable)
    if new_hash:
        config.simc_hash = new_hash
    if not hasattr(config, "simc_hash"):
        config.simc_hash = None

    bloodytools_start_time = datetime.datetime.utcnow()

    # empty class-spec list? great, we'll run all class-spec combinations
    if not hasattr(config, "wow_class_spec_list"):
        config.wow_class_spec_list = WOWSPECS

    # list of all active threads. when empty, terminate tool
    thread_list = []

    # trigger race simulations
    if config.enable_race_simulations:

        kwargs = {
            "simulation_type": "races",
            "simulator_factory": simulator_factory,
            "settings": config,
        }
        if not config.use_own_threading:
            logger.info("Starting Race simulations.")

        if config.use_own_threading:
            race_thread = threading.Thread(
                name="Race Thread",
                target=simulator_wrapper,
                kwargs=kwargs,
            )
            thread_list.append(race_thread)
            race_thread.start()
        else:
            simulator_wrapper(**kwargs)

        if not config.use_own_threading:
            logger.info("Race simulations finished.")

    # trigger trinket simulations
    if config.enable_trinket_simulations:
        if not config.use_own_threading:
            logger.info("Starting Trinket simulations.")

        if config.use_own_threading:
            trinket_thread = threading.Thread(
                name="Trinket Thread", target=trinket_simulation, args=(config,)
            )
            thread_list.append(trinket_thread)
            trinket_thread.start()
        else:
            trinket_simulation(config)

        if not config.use_own_threading:
            logger.info("Trinket simulations finished.")

    # trigger soul bind (nodes) simulations
    if config.enable_soul_bind_node_simulations:
        if not config.use_own_threading:
            logger.info("Starting Soul Bind Node simulations.")

        if config.use_own_threading:
            soul_bind_node_thread = threading.Thread(
                name="Soul Bind Node Thread",
                target=soul_bind_node_simulation,
                args=(config,),
            )
            thread_list.append(soul_bind_node_thread)
            soul_bind_node_thread.start()
        else:
            soul_bind_node_simulation(config)

        if not config.use_own_threading:
            logger.info("Soul Bind Node simulations finished.")

    # trigger soul bind (nodes+conduits) simulations
    if config.enable_soul_bind_simulations:
        if not config.use_own_threading:
            logger.info("Starting Soul Bind simulations.")

        if config.use_own_threading:
            soul_bind_thread = threading.Thread(
                name="Soul Bind Thread",
                target=soul_bind_simulation,
                args=(config,),
            )
            thread_list.append(soul_bind_thread)
            soul_bind_thread.start()
        else:
            soul_bind_simulation(config)

        if not config.use_own_threading:
            logger.info("Soul Bind simulations finished.")

    # trigger conduit simulations
    if config.enable_conduit_simulations:
        if not config.use_own_threading:
            logger.info("Starting Conduit simulations.")

        if config.use_own_threading:
            conduit_thread = threading.Thread(
                name="Conduit Thread", target=conduit_simulation, args=(config,)
            )
            thread_list.append(conduit_thread)
            conduit_thread.start()
        else:
            conduit_simulation(config)

        if not config.use_own_threading:
            logger.info("Conduit simulations finished.")

    # trigger legendary simulations
    if config.enable_legendary_simulations:
        if not config.use_own_threading:
            logger.info("Starting Legendary simulations.")

        if config.use_own_threading:
            legendary_thread = threading.Thread(
                name="Legendary Thread", target=legendary_simulation, args=(config,)
            )
            thread_list.append(legendary_thread)
            legendary_thread.start()
        else:
            legendary_simulation(config)

        if not config.use_own_threading:
            logger.info("Legendary simulations finished.")

    # trigger secondary distributions
    if config.enable_secondary_distributions_simulations:

        if not config.use_own_threading:
            logger.info("Starting Secondary Distribtion simulations.")

        if config.use_own_threading:
            secondary_distribution_thread = threading.Thread(
                name="Secondary Distribution Thread",
                target=secondary_distribution_simulation,
                args=(config,),
            )
            thread_list.append(secondary_distribution_thread)
            secondary_distribution_thread.start()
        else:
            secondary_distribution_simulation(config)

        if not config.use_own_threading:
            logger.info("Secondary Distribution simulations finished.")

    # trigger talent simulations
    if config.enable_talent_simulations:
        if not config.use_own_threading:
            logger.info("Talent simulations start.")

        if config.use_own_threading:
            talent_thread = threading.Thread(
                name="Talent Thread",
                target=talent_simulation,
                args=(config,),
            )
            thread_list.append(talent_thread)
            talent_thread.start()
        else:
            talent_simulation(config)

        if not config.use_own_threading:
            logger.info("Talent simulations end.")

    # trigger covenant simulations
    if config.enable_covenant_simulations:
        if not config.use_own_threading:
            logger.info("Covenant simulations start.")

        if config.use_own_threading:
            covenant_thread = threading.Thread(
                name="Covenant Thread",
                target=covenant_simulation,
                args=(config,),
            )
            thread_list.append(covenant_thread)
            covenant_thread.start()
        else:
            covenant_simulation(config)

        if not config.use_own_threading:
            logger.info("Covenant simulations end.")

    # trigger domination shard simulations
    if config.enable_domination_shards:
        if not config.use_own_threading:
            logger.info("Domination Shard simulations start.")

        if config.use_own_threading:
            domiation_shard_thread = threading.Thread(
                name="Domination Shard Thread",
                target=domination_shard_simulation,
                args=(config,),
            )
            thread_list.append(domiation_shard_thread)
            domiation_shard_thread.start()
        else:
            domination_shard_simulation(config)

        if not config.use_own_threading:
            logger.info("Domination Shard simulations end.")

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
    args = arg_parse_config()
    main(args)

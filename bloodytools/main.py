"""Welcome to bloodytools - a SimulationCraft automator/wrapper

Generate your data more easily without having to create each and every needed profile to do so by hand.

Output is usually saved as .json. But you can add different ways to output the data yourself.

Contact:
  - https://discord.gg/PKT2PWGB6w Bloodmallet(EU)#8246

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
        config.enable_tier_set_simulations = False

        # set dev options
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
        elif simulation_type == "tier_set":
            config.enable_tier_set_simulations = True
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

    # trigger race simulations
    if config.enable_race_simulations:
        kwargs = {
            "simulation_type": "races",
            "simulator_factory": simulator_factory,
            "settings": config,
        }
        logger.info("Starting Race simulations.")
        simulator_wrapper(**kwargs)
        logger.info("Race simulations finished.")

    # trigger trinket simulations
    if config.enable_trinket_simulations:
        logger.info("Starting Trinket simulations.")
        trinket_simulation(config)
        logger.info("Trinket simulations finished.")

    # trigger soul bind (nodes) simulations
    if config.enable_soul_bind_node_simulations:
        logger.info("Starting Soul Bind Node simulations.")
        soul_bind_node_simulation(config)
        logger.info("Soul Bind Node simulations finished.")

    # trigger soul bind (nodes+conduits) simulations
    if config.enable_soul_bind_simulations:
        kwargs = {
            "simulation_type": "soulbinds",
            "simulator_factory": simulator_factory,
            "settings": config,
        }
        logger.info("Starting Soul Bind simulations.")
        simulator_wrapper(**kwargs)
        logger.info("Soul Bind simulations finished.")

    # trigger conduit simulations
    if config.enable_conduit_simulations:
        logger.info("Starting Conduit simulations.")
        conduit_simulation(config)
        logger.info("Conduit simulations finished.")

    # trigger legendary simulations
    if config.enable_legendary_simulations:
        logger.info("Starting Legendary simulations.")
        legendary_simulation(config)
        logger.info("Legendary simulations finished.")

    # trigger secondary distributions
    if config.enable_secondary_distributions_simulations:
        logger.info("Starting Secondary Distribtion simulations.")
        secondary_distribution_simulation(config)
        logger.info("Secondary Distribution simulations finished.")

    # trigger talent simulations
    if config.enable_talent_simulations:
        logger.info("Talent simulations start.")
        talent_simulation(config)
        logger.info("Talent simulations end.")

    # trigger covenant simulations
    if config.enable_covenant_simulations:
        logger.info("Covenant simulations start.")
        covenant_simulation(config)
        logger.info("Covenant simulations end.")

    # trigger domination shard simulations
    if config.enable_domination_shards:
        logger.info("Domination Shard simulations start.")
        domination_shard_simulation(config)
        logger.info("Domination Shard simulations end.")

    # trigger tier set simulations
    if config.enable_tier_set_simulations:
        kwargs = {
            "simulation_type": "tier_set",
            "simulator_factory": simulator_factory,
            "settings": config,
        }
        logger.info("Starting Tier Set simulations.")
        simulator_wrapper(**kwargs)
        logger.info("Tier Set simulations finished.")

    logger.info(
        "Bloodytools took {} to finish.".format(
            datetime.datetime.utcnow() - bloodytools_start_time
        )
    )
    logger.debug("main ended")


if __name__ == "__main__":
    args = arg_parse_config()
    main(args)

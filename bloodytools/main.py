"""Welcome to bloodytools - a SimulationCraft automator/wrapper

Generate your data more easily without having to create each and every needed profile by hand.

Output is saved as json.

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

from simc_support.game_data.WowSpec import get_wow_spec

from bloodytools.simulations import simulator_factory
from bloodytools.utils.args import arg_parse_config
from bloodytools.utils.config import Config

logger = logging.getLogger(__name__)


def main(args=None):
    logger.debug("main start")
    logger.info("Bloodytools at your service.")

    if args:
        config = Config.create_config_from_args(args)
    else:
        config = Config()

    bloodytools_start_time = datetime.datetime.utcnow()

    for wow_spec in config.wow_specs:
        for simulator_name in config.simulator_type_names:
            simulator = simulator_factory.get_simulator(simulator_name)
            for fight_style in config.fight_styles:
                logger.info(f"Starting {simulator.name} simulations.")
                simulator(
                    wow_spec=wow_spec,
                    fight_style=fight_style,
                    settings=config,
                ).run()
                logger.info(f"{simulator.name} simulations finished.")

    logger.info(
        "Bloodytools took {} to finish.".format(
            datetime.datetime.utcnow() - bloodytools_start_time
        )
    )
    logger.debug("main ended")


if __name__ == "__main__":
    args = arg_parse_config()
    main(args)

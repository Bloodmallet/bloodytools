import logging

from bloodytools.main import main
from bloodytools.utils.utils import arg_parse_config
from bloodytools.utils.utils import logger_config

from bloodytools import settings

if __name__ == "__main__":
    args = arg_parse_config()

    # activate debug mode as early as possible
    if args.debug:
        settings.debug = args.debug

    logger = logger_config(logging.getLogger("bloodytools"), args.debug)

    main(args)

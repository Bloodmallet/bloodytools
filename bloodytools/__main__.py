import logging

from bloodytools.main import main
from bloodytools.utils.args import arg_parse_config
from bloodytools.utils.utils import logger_config

if __name__ == "__main__":
    args = arg_parse_config()

    logger_config(logging.getLogger("bloodytools"), args.debug)

    main(args)

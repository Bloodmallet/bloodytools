from bloodytools import settings
from bloodytools.utils.utils import arg_parse_config
from bloodytools.utils.utils import logger_config
from bloodytools.main import main

if __name__ == '__main__':
    logger = logger_config()
    logger.debug("__main__ start")

    settings.logger = logger

    args = arg_parse_config()

    main(args)
    logger.debug("__main__ ended")

from bloodytools import settings
from bloodytools.bloodytools import arg_parse_config
from bloodytools.bloodytools import main
from bloodytools.bloodytools import logger_config

if __name__ == '__main__':
    logger = logger_config()
    logger.debug("__main__ start")

    settings.logger = logger

    args = arg_parse_config()

    main(args)
    logger.debug("__main__ ended")

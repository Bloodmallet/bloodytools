import logging

SIMC_BRANCH = "dragonflight"

logger = logging.getLogger(__name__)


def get_simc_hash(path: str, log_warning: bool = True) -> str:
    """Get the FETCH_HEAD or shallow simc git hash.

    Returns:
      str -- [description]
    """
    if path.endswith("simc.exe"):
        new_path = path.split("simc.exe")[0]
    elif path.endswith("simc"):
        new_path = path[:-4]  # cut "simc" from unix path
        if "engine" in new_path[-7:]:
            new_path = new_path[:-7]
    elif log_warning:
        logger.warning(
            f"Strange path '{path}' to work with to find simulationcraft repository."
        )

    # add path to file to variable
    new_path += f".git/refs/heads/{SIMC_BRANCH}"
    simc_hash: str = ""
    try:
        with open(new_path, "r", encoding="utf-8") as f:
            simc_hash = f.read().strip()
    except FileNotFoundError as e:
        if log_warning:
            logger.warning(e)

    return simc_hash

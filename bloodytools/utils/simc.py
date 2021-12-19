import logging

SIMC_BRANCH = "shadowlands"

logger = logging.getLogger(__name__)


def get_simc_hash(path: str) -> str:
    """Get the FETCH_HEAD or shallow simc git hash.

    Returns:
      str -- [description]
    """
    if path.endswith(".exe"):
        new_path = path.split("simc.exe")[0]
    else:
        new_path = path[:-4]  # cut "simc" from unix path
        if "engine" in new_path[-7:]:
            new_path = new_path[:-7]

    # add path to file to variable
    new_path += f".git/refs/heads/{SIMC_BRANCH}"
    simc_hash: str = ""
    try:
        with open(new_path, "r", encoding="utf-8") as f:
            simc_hash = f.read().strip()
    except FileNotFoundError as e:
        logger.warning(e)

    return simc_hash

import re
import subprocess


def get_simc_hash(executable_path: str) -> str:
    """Get the FETCH_HEAD or shallow simc git hash.

    Returns:
      str -- [description]
    """
    # Execute simc with a fast input that does nothing put print the build information
    # simc display_build=1 spell_query=spell.id=0
    simc_output = subprocess.run(
        [str(executable_path), "display_build=1", "spell_query=spell.id=0"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    ).stdout
    # Extract git hash from build version, which looks like
    # SimulationCraft 1015-01 for World of Warcraft 10.1.7.51536 Live (hotfix 2023-09-27/51536, git build dragonflight d90d5c5)
    search = re.search(r"git build \w+ ([^\)]+)", simc_output)
    if not search:
        raise ValueError("SimulationCraft version could not get extracted")
    simc_hash = search.group(1)
    return str(simc_hash)

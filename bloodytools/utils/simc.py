import re
import subprocess


def get_simc_hash(executable_path: str) -> str:
    """Get the FETCH_HEAD or shallow simc git hash.

    Returns:
      str -- [description]
    """
    # Execute simc with a fast input that does nothing put print the build information
    # simc display_build=1 spell_query=spell.id=0
    try:
        simc_output = subprocess.run(
            [str(executable_path), "display_build=1", "spell_query=spell.id=0"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        ).stdout
    except FileNotFoundError as e:
        raise ValueError(
            f"SimulationCraft version could not get extracted from '{executable_path}'."
        ) from e
    # Extract git hash from build version, which looks like
    # SimulationCraft 1015-01 for World of Warcraft 10.1.7.51536 Live (hotfix 2023-09-27/51536, git build dragonflight d90d5c5)
    # SimulationCraft 1020-01 for World of Warcraft 10.2.0.52393 Live (hotfix 2023-12-05/52393, no-networking)\n\n
    search = re.search(r"git build \w+ ([^,\)]+)", simc_output)
    if not search:
        raise ValueError(
            f"SimulationCraft version could not get extracted from '{executable_path}'. Got '{simc_output}' instead."
        )
    simc_hash = search.group(1)
    return str(simc_hash)

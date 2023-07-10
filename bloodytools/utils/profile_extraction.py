import logging
import os
import re
import typing

from bloodytools.utils.config import Config
from simc_support.game_data.WowClass import WowClass
from simc_support.game_data.WowSpec import WowSpec

logger = logging.getLogger(__name__)


class EmptyFileError(Exception):
    pass


class IncompleteProfileError(Exception):
    pass


class SpecMismatchError(Exception):
    pass


def _get_tier_directory_name(tier: str) -> str:
    """PreRaids vs TierXX"""
    return "PreRaids" if tier == "PR" else f"Tier{tier}"


def _get_tier_file_name_part(tier: str) -> str:
    """PR vs TXX"""
    return "PR" if "PR" in str(tier) else f"T{tier}"


def _get_simc_profile_file_name(tier: str, wow_spec: WowSpec) -> str:
    """TXX_CLASS_SPEC.simc"""
    return (
        "_".join(
            [
                _get_tier_file_name_part(tier),
                wow_spec.wow_class.simc_name.title(),
                wow_spec.simc_name.title(),
            ]
        )
        + ".simc"
    )


def create_simc_profile_path(wow_spec: WowSpec, tier: str, executable_path: str) -> str:
    """Create basic profile string to get the standard profile of a spec. Use this function to get the necessary string for your first argument of a simulation_data object.

    Arguments:
      wow_spec {WowSpec} -- wow spec, e.g. elemental shaman
      tier {str} -- profile tier, e.g. 21 or PR
      settings {Config}

    Returns:
      str -- relative link to the standard simc profile. E.g. ./SimulationCraft/profiles/<tier>/<tier>_<wow_spec>.simc
    """

    # create the base profile string
    split_path: list = executable_path.split("simc")
    base_profile_string: str
    if len(split_path) > 2:
        # the path contains multiple "simc", e.g. executable and directory name
        base_profile_string = "simc".join(split_path[:-1])
    else:
        base_profile_string = split_path[0]

    # fix path for linux users
    if base_profile_string.endswith("/engine/"):
        base_profile_string = base_profile_string.rstrip("engine/")

    base_profile_string = os.path.join(
        base_profile_string,
        "profiles",
        _get_tier_directory_name(tier),
        _get_simc_profile_file_name(tier, wow_spec),
    )

    logger.debug(
        f"Created simc_profile_path for Tier {tier} of {wow_spec} is '{base_profile_string}'."
    )
    return base_profile_string


def create_fallback_profile_path(wow_spec: WowSpec, tier: str, fight_style: str) -> str:
    """e.g. ./fallback_profiles/<fight_style>/<tier>/<tier>_<wow_spec>.simc"""

    # ./bloodytools/utils
    self_file_path = os.path.dirname(os.path.abspath(__file__))
    # ./
    bloodytools_root_path = os.path.dirname(os.path.dirname(self_file_path))

    fallback_profile_path = os.path.join(
        bloodytools_root_path,
        "fallback_profiles",
        fight_style.lower(),
        _get_tier_directory_name(tier),
        _get_simc_profile_file_name(tier, wow_spec),
    )

    logger.debug(
        f"Created fall_back_profile_path for Tier {tier} of {wow_spec} is '{fallback_profile_path}'"
    )
    return fallback_profile_path


def create_custom_profiles_path(wow_spec: WowSpec) -> str:
    """e.g. ./custom_profiles/<wow_class>_<wow_spec>.simc"""

    # ./bloodytools/utils
    self_file_path = os.path.dirname(os.path.abspath(__file__))
    # ./
    bloodytools_root_path = os.path.dirname(os.path.dirname(self_file_path))

    custom_profiles_path = os.path.join(
        bloodytools_root_path,
        "custom_profiles",
        f"{wow_spec.wow_class.simc_name}_{wow_spec.simc_name}.simc",
    )

    logger.debug(
        f"Created cumstom_profiles_path for Tier of {wow_spec} is '{custom_profiles_path}'"
    )
    return custom_profiles_path


def extract_profile(path: str, wow_class: WowClass) -> dict:
    """Extract all character specific data from a given file.
    These options are expansion specific, so be careful when using this with other SimulatonCraft versions.

    Arguments:
        path {str} -- path to file, relative or absolute
        wow_class {WowClass} -- expected wow class in `path`

    Returns:
        dict -- all known character data
    """
    minimal_profile_keys: typing.Dict[
        str,
        typing.Dict[
            str,
            typing.Union[
                str, typing.Dict[str, typing.Union[str, typing.Dict[str, str]]]
            ],
        ],
    ] = {
        "character": {
            "class": "",
            "level": "",
            # "position": "",  # optional
            "race": "",
            "role": "",
            "spec": "",
        },
        "items": {
            "back": {},
            "chest": {},
            "feet": {},
            "finger1": {},
            "finger2": {},
            "hands": {},
            "head": {},
            "legs": {},
            "main_hand": {},
            "neck": {},
            "off_hand": {},
            "shoulders": {},
            "trinket1": {},
            "trinket2": {},
            "waist": {},
            "wrists": {},
        },
    }

    if os.stat(path).st_size == 0:
        raise EmptyFileError("Empty file")
    with open(path, "r") as f:
        file_content = f.read()
    if file_content.strip() == "":
        raise EmptyFileError("Empty file")

    profile: typing.Dict[
        str,
        typing.Dict[
            str,
            typing.Union[
                str,
                typing.Dict[
                    str,
                    typing.Union[
                        str,
                        typing.Dict[str, str],
                    ],
                ],
            ],
        ],
    ] = {
        "character": {"class": wow_class.simc_name},
        "items": {},
    }

    # prepare regex for each extractable item slot
    item_slots = [
        "head",
        "neck",
        "shoulders",
        "shoulder",
        "back",
        "chest",
        "wrists",
        "wrist",
        "hands",
        "waist",
        "legs",
        "feet",
        "finger1",
        "finger2",
        "trinket1",
        "trinket2",
        "main_hand",
        "off_hand",
    ]
    official_name = {
        "shoulder": "shoulders",
        "wrist": "wrists",
    }
    pattern_slots: typing.Dict[str, re.Pattern] = {}
    for element in item_slots:
        pattern_slots[element] = re.compile(
            r'^{}=["\']?(?P<information>.*)["\']?$'.format(element)
        )

    # prepare regex for item defining attributes
    item_elements = [
        "id",
        "bonus_id",
        # "azerite_powers",
        "enchant",
        # "azerite_level",  # neck
        "ilevel",
        "gem_id",
        "enchant_id",
        "crafted_stats",
        "drop_level",
    ]
    pattern_element: typing.Dict[str, re.Pattern] = {}
    # don't recompile this for each slot
    for element in item_elements:
        pattern_element[element] = re.compile(
            r',{}=["\']?(?P<information>[a-zA-Z0-9_/:]*)["\']?'.format(element)
        )

    # prepare regex for character defining information. like spec
    character_specifics = [
        "level",
        "race",
        "role",
        "position",
        "talents",
        "class_talents",
        "spec_talents",
        "spec",
        "default_pet",
        r"set_bonus=[\"']?tier28_2pc[\"']?",
        r"set_bonus=[\"']?tier28_4pc[\"']?",
        r"set_bonus=[\"']?tier29_2pc[\"']?",
        r"set_bonus=[\"']?tier29_4pc[\"']?",
        r"set_bonus=[\"']?tier30_2pc[\"']?",
        r"set_bonus=[\"']?tier30_4pc[\"']?",
        "gear_agility",
        "gear_intellect",
        "gear_strength",
        "gear_crit_rating",
        "gear_haste_rating",
        "gear_mastery_rating",
        "gear_versatility_rating",
        "deathknight.ams_absorb_percent",
        "deathknight.amz_absorb_percent",
        "dragonflight.ominous_chromatic_essence_dragonflight",
        "dragonflight.ominous_chromatic_essence_allies",
    ]
    clean_character_specifics = {
        r"set_bonus=[\"']?tier28_2pc[\"']?": "set_bonus=tier28_2pc",
        r"set_bonus=[\"']?tier28_4pc[\"']?": "set_bonus=tier28_4pc",
        r"set_bonus=[\"']?tier29_2pc[\"']?": "set_bonus=tier29_2pc",
        r"set_bonus=[\"']?tier29_4pc[\"']?": "set_bonus=tier29_4pc",
        r"set_bonus=[\"']?tier30_2pc[\"']?": "set_bonus=tier30_2pc",
        r"set_bonus=[\"']?tier30_4pc[\"']?": "set_bonus=tier30_4pc",
    }
    pattern_specifics: typing.Dict[str, re.Pattern] = {}
    for element in character_specifics:
        pattern_specifics[element] = re.compile(
            r'^{}=["\']?(?P<information>.*)["\']?'.format(element)
        )

    with open(path, "r") as f:
        for line in f:
            if line.lstrip().startswith("#"):
                continue

            if not line.strip():
                continue

            for specific in character_specifics:
                matches = pattern_specifics[specific].search(line)
                if matches:
                    profile["character"][
                        clean_character_specifics.get(specific, specific)
                    ] = (matches.group("information").replace('"', "").replace("'", ""))

            for slot in item_slots:
                matches = pattern_slots[slot].search(line)

                slot_name = official_name.get(slot, slot)

                if matches:
                    new_line = (
                        matches.group("information").replace('"', "").replace("'", "")
                    )
                    if not slot_name in profile["items"]:
                        profile["items"][slot_name] = {}

                    # check for all elements
                    for element in item_elements:
                        new_matches: typing.Union[re.Match, None] = pattern_element[
                            element
                        ].search(new_line)

                        if new_matches:
                            profile["items"][slot_name][element] = (  # type: ignore[index]
                                new_matches.group("information")
                                .replace('"', "")
                                .replace("'", "")
                            )

    logger.debug(f"extracted profile from '{path}' : {profile}")

    # validate profile
    missing_character_keys = []
    for key in minimal_profile_keys["character"].keys():
        if key not in profile["character"]:
            missing_character_keys.append(key)
    if missing_character_keys:
        raise IncompleteProfileError(
            f"'{path}' does not contain a complete profile. Missing keys: {missing_character_keys}"
        )

    logger.debug(f"extracted profile: {profile}")
    return profile


def _get_profile(
    profile_type: str,
    path: str,
    wow_class: WowClass,
    *,
    accepted_errors: typing.Tuple[typing.Type[Exception], ...] = (FileNotFoundError,),
) -> dict:
    try:
        profile = extract_profile(path, wow_class)
    except accepted_errors:
        profile = {}
        logger.debug(f"{profile_type.title()} profile not found at '{path}'. Skipping")
    if profile:
        logger.debug(f"{profile_type.title()} profile found at '{path}'.")
    return profile


def get_profile(wow_spec: WowSpec, fight_style: str, settings: Config) -> dict:
    """Get the compiled profile based on Fallback profiles, Simulationcraft, and custom input.

    Priority list of profiles. Profile with the highest priority is returned.

        1. Custom Input if enabled
        2. Fallback profile
        3. SimulationCraft profile

    Args:
        wow_spec (WowSpec): [description]
        fight_style (str): [description]
        settings (Config): [description]

    Raises:
        FileNotFoundError: [description]

    Returns:
        dict: [description]
    """

    if settings.custom_profile:
        custom_profile = _get_profile(
            "custom",
            "custom_profile.txt",
            wow_spec.wow_class,
            accepted_errors=(FileNotFoundError, EmptyFileError),
        )
        if custom_profile and custom_profile["character"]["spec"] != wow_spec.simc_name:
            logger.warning(
                f"Extracted spec '{custom_profile['character']['spec']}' from custom profile does not match expected '{wow_spec.simc_name}'."
            )
        if custom_profile:
            return custom_profile

    fallback_profile = _get_profile(
        "fallback",
        create_fallback_profile_path(wow_spec, settings.tier, fight_style),
        wow_spec.wow_class,
    )
    if fallback_profile:
        return fallback_profile

    simc_profile = _get_profile(
        "SimulationCraft",
        create_simc_profile_path(wow_spec, settings.tier, settings.executable),
        wow_spec.wow_class,
    )
    if simc_profile:
        return simc_profile

    raise FileNotFoundError(f"No profile found or provided for {wow_spec}.")

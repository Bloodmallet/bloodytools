import datetime
import logging
import os
import re
import subprocess
import typing

from bloodytools.utils.config import Config
from simc_support.game_data.WowClass import WowClass
from simc_support.game_data.WowSpec import WowSpec

logger = logging.getLogger(__name__)


class EmptyFileError(Exception):
    pass


class IncompleteProfileError(Exception):
    pass


def create_basic_profile_string(wow_spec: WowSpec, tier: str, settings: Config) -> str:
    """Create basic profile string to get the standard profile of a spec. Use this function to get the necessary string for your first argument of a simulation_data object.

    Arguments:
      wow_spec {WowSpec} -- wow spec, e.g. elemental shaman
      tier {str} -- profile tier, e.g. 21 or PR
      settings {Config}

    Returns:
      str -- relative link to the standard simc profile. E.g. ./SimulationCraft/profiles/<tier>/<tier>_<wow_spec>.simc
    """

    logger.debug("create_basic_profile_string start")
    # create the basis profile string
    split_path: list = settings.executable.split("simc")
    basis_profile_string: str
    if len(split_path) > 2:
        # the path contains multiple "simc"
        basis_profile_string = "simc".join(split_path[:-1])
    else:
        basis_profile_string = split_path[0]

    # fix path for linux users
    if basis_profile_string.endswith("/engine/"):
        split_path = basis_profile_string.split("/engine/")
        if len(split_path) > 2:
            basis_profile_string = "/engine/".join(split_path[:-1])
        else:
            basis_profile_string = split_path[0] + "/"

    basis_profile_string += "profiles/"
    if tier == "PR":
        basis_profile_string += "PreRaids/PR_{}_{}".format(
            wow_spec.wow_class.simc_name.title(), wow_spec.simc_name.title()
        )
    else:
        basis_profile_string += "Tier{}/T{}_{}_{}".format(
            tier, tier, wow_spec.wow_class.simc_name, wow_spec.simc_name
        ).title()
    basis_profile_string += ".simc"

    logger.debug("Created basis_profile_string '{}'.".format(basis_profile_string))
    logger.debug("create_basic_profile_string ended")
    return basis_profile_string


def get_fallback_profile_path(tier: str, fight_style: str) -> str:
    """e.g. ./fallback_profiles/<fight_style>/<tier>"""
    tmp_tier = "PR" if "PR" in str(tier) else f"Tier{tier}"
    self_file_path = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.dirname(os.path.dirname(self_file_path))
    fall_back_profile_path = os.path.join(
        base_path, "fallback_profiles", fight_style, tmp_tier
    )
    logger.debug(f"fall_back_profile_path for {tier} is '{fall_back_profile_path}'")
    return fall_back_profile_path


def _get_simc_spec_file_name(tier: str, wow_spec: WowSpec) -> str:
    name_start = (
        f"{tier}_{wow_spec.wow_class.simc_name.title()}_{wow_spec.simc_name.title()}"
    )
    return f"{name_start}.simc"


def _get_tier_file_name_part(tier: str) -> str:
    return "PR" if "PR" in str(tier) else f"T{tier}"


def get_fallback_profile_string(wow_spec: WowSpec, tier: str, fight_style: str) -> str:
    """e.g. ./fallback_profiles/<fight_style>/<tier>/<tier>_<wow_spec>.simc"""
    base_path = get_fallback_profile_path(tier, fight_style)
    tmp_tier = _get_tier_file_name_part(tier)
    name = _get_simc_spec_file_name(tmp_tier, wow_spec)
    return os.path.join(base_path, name)


def pretty_timestamp() -> str:
    """Returns a pretty time stamp "YYYY-MM-DD HH:MM"

    Returns:
      str -- timestamp
    """
    # str(datetime.datetime.utcnow())[:-10] should be the same
    return datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M")


def extract_profile(
    path: str, wow_class: WowClass, profile: typing.Optional[dict] = None
) -> dict:
    """Extract all character specific data from a given file.

    Arguments:
        path {str} -- path to file, relative or absolute
        profile {dict} -- profile input that should be updated

    Returns:
        dict -- all known character data
    """
    # ! expansion specific
    minimal_profile_keys: typing.Dict[
        str, typing.Dict[str, typing.Union[str, typing.Dict[str, str]]]
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

    if profile is None:
        provided_profile = {}
    else:
        provided_profile = profile

    profile = {
        "character": {"class": wow_class.simc_name},
        "items": {},
    }

    # prepare regex for each extractable slot
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
    official_name = {"shoulder": "shoulders", "wrist": "wrists"}
    pattern_slots = {}
    for element in item_slots:
        pattern_slots[element] = re.compile(
            r'^{}="?(?P<information>.*)"?$'.format(element)
        )

    # prepare regex for item defining attributes
    item_elements = [
        "id",
        "bonus_id",
        "azerite_powers",
        "enchant",
        "azerite_level",  # neck
        "ilevel",
        "gem_id",
        "enchant_id",
        "crafted_stats",
        "drop_level",
    ]
    pattern_element = {}
    # don't recompile this for each slot
    for element in item_elements:
        pattern_element[element] = re.compile(
            r',{}="?(?P<information>[a-zA-Z0-9_/:]*)"?'.format(element)
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
    ]
    clean_character_specifics = {
        r"set_bonus=[\"']?tier28_2pc[\"']?": "set_bonus=tier28_2pc",
        r"set_bonus=[\"']?tier28_4pc[\"']?": "set_bonus=tier28_4pc",
        r"set_bonus=[\"']?tier29_2pc[\"']?": "set_bonus=tier29_2pc",
        r"set_bonus=[\"']?tier29_4pc[\"']?": "set_bonus=tier29_4pc",
        r"set_bonus=[\"']?tier30_2pc[\"']?": "set_bonus=tier30_2pc",
        r"set_bonus=[\"']?tier30_4pc[\"']?": "set_bonus=tier30_4pc",
    }
    pattern_specifics = {}
    for element in character_specifics:
        pattern_specifics[element] = re.compile(
            r'^{}=["\']?(?P<information>.*)["\']?'.format(element)
        )

    with open(path, "r") as f:
        for line in f:
            if line.lstrip().startswith("#"):
                continue

            for specific in character_specifics:
                matches = pattern_specifics[specific].search(line)
                if matches:
                    profile["character"][
                        clean_character_specifics.get(specific, specific)
                    ] = matches.group("information").replace('"', "")

            for slot in item_slots:
                matches = pattern_slots[slot].search(line)
                slot_name = slot
                if slot in official_name:
                    slot_name = official_name[slot]
                if matches:
                    new_line = matches.group("information").replace('"', "")
                    if not slot_name in profile:
                        profile["items"][slot_name] = {}

                    # allow pre-prepared profiles to get emptied if input wants to overwrite with empty
                    # 'head=' as a head example for an empty overwrite
                    if not new_line:
                        profile["items"].pop(slot_name, None)
                        profile["items"].pop(slot, None)
                    else:
                        # check for all elements
                        for element in item_elements:
                            new_matches = pattern_element[element].search(new_line)
                            if new_matches:
                                profile["items"][slot_name][
                                    element
                                ] = new_matches.group("information").replace('"', "")

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

    return_profile = profile  # if profile["items"] else provided_profile
    logger.debug(f"returning profile: {return_profile}")

    return return_profile


def get_profile(wow_spec: WowSpec, fight_style: str, settings: Config) -> dict:
    """Get the compiled profile based on Fallback profiles, Simulationcraft, and custom input.

    Args:
        wow_spec (WowSpec): [description]
        fight_style (str): [description]
        settings (Config): [description]

    Raises:
        FileNotFoundError: [description]

    Returns:
        dict: [description]
    """
    # loading covenant profiles in the following order:
    # 1. fallback
    # 2. simc

    # load fallback profile
    fallback_profile_location = get_fallback_profile_string(
        wow_spec, settings.tier, fight_style
    )
    profile = {}
    try:
        profile = extract_profile(fallback_profile_location, wow_spec.wow_class)
    except FileNotFoundError as e:
        logger.debug(
            f"Fallback profile '{fallback_profile_location}' not found. Skipping"
        )

    # load base profile for patchwerk or fallback doesn't exist
    if not profile or "patchwerk" in fight_style.lower():
        profile_location = create_basic_profile_string(
            wow_spec, settings.tier, settings
        )
        if not os.path.exists(profile_location):
            profile_location = create_basic_profile_string(
                wow_spec, settings.tier.split("_")[0], settings
            )

        try:
            profile = extract_profile(profile_location, wow_spec.wow_class)
        except FileNotFoundError:
            logger.debug(f"Profile '{profile_location}' not found. Skipping")

    if settings.custom_profile:
        try:
            profile = extract_profile("custom_profile.txt", wow_spec.wow_class, profile)
        except EmptyFileError as e:
            logger.debug(e)
        else:
            logger.debug(f"custom profile was extracted: {profile}")

    if not profile:
        raise FileNotFoundError(f"No profile found or provided for {wow_spec}.")

    return profile


def create_base_json_dict(
    data_type: str, wow_spec: WowSpec, fight_style: str, settings: Config
):
    """Creates as basic json dictionary. You'll need to add your data into 'data'. Can be extended.

    Arguments:
      data_type {str} -- e.g. Races, Trinkets, Azerite Traits (str is used in the title)
      wow_spec {WowSpec} -- [description]
      fight_style {str} -- [description]
      settings {Config} -- [description]

    Returns:
      dict -- [description]
    """

    logger.debug("create_base_json_dict start")

    timestamp = pretty_timestamp()

    profile = get_profile(wow_spec=wow_spec, fight_style=fight_style, settings=settings)

    # add class/ id number
    class_id = wow_spec.wow_class.id
    spec_id = wow_spec.id

    subtitle = "UTC {timestamp}".format(timestamp=timestamp)
    if settings.simc_hash:
        subtitle += ' | SimC build: <a href="https://github.com/simulationcraft/simc/commit/{simc_hash}" target="blank">{simc_hash_short}</a>'.format(
            simc_hash=settings.simc_hash, simc_hash_short=settings.simc_hash[0:7]
        )

    try:
        bloodytools_hash = (
            subprocess.check_output(["git", "log", "-1", "--format=oneline"])
            .strip()
            .decode()
            .split(" ")[0]
        )
    except Exception:
        bloodytools_hash = None

    return {
        "data_type": "{}".format(data_type.lower().replace(" ", "_")),
        "timestamp": timestamp,
        "title": "{data_type} | {wow_spec} {wow_class} | {fight_style}".format(
            data_type=data_type.title(),
            wow_class=wow_spec.wow_class.full_name,
            wow_spec=wow_spec.full_name,
            fight_style=fight_style.title(),
        ),
        "subtitle": subtitle,
        "simc_settings": {
            "tier": settings.tier,
            "fight_style": fight_style,
            "iterations": settings.iterations,
            "target_error": settings.target_error.get(fight_style, "0.1"),
            "ptr": settings.ptr,
            "simc_hash": settings.simc_hash,
        },
        "metadata": {
            "bloodytools": bloodytools_hash,
            "SimulationCraft": settings.simc_hash,
            "timestamp": str(datetime.datetime.utcnow()),
        },
        "data": {},
        "translations": {},
        "profile": profile,
        "class_id": class_id,
        "spec_id": spec_id,
    }


def tokenize_str(string: str) -> str:
    """Return SimulationCraft appropriate name.

    Arguments:
      string {str} -- E.g. "Tawnos, Urza's Apprentice"

    Returns:
      str -- "tawnos_urzas_apprentice"
    """

    string = string.lower().split(" (")[0]
    # cleanse name
    if (
        "__" in string
        or " " in string
        or "-" in string
        or "'" in string
        or "," in string
    ):
        return tokenize_str(
            string.replace("'", "")
            .replace("-", "")
            .replace(" ", "_")
            .replace("__", "_")
            .replace(",", "")
        )

    return string


def logger_config(logger: logging.Logger, debug=False):
    # logging to file and console
    logger.setLevel(logging.DEBUG)

    # console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    if debug:
        console_handler.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # file handler
    file_handler = logging.FileHandler("debug.log", "w", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(filename)s / %(funcName)s:%(lineno)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # error file handler
    error_handler = logging.FileHandler("error.log", "w", encoding="utf-8")
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter(
        "%(asctime)s - %(filename)s / %(funcName)s:%(lineno)s - %(levelname)s - %(message)s"
    )
    error_handler.setFormatter(error_formatter)
    logger.addHandler(error_handler)

    return logger

import datetime
import logging
import subprocess

from bloodytools.utils.config import Config
from bloodytools.utils.profile_extraction import get_profile
from simc_support.game_data.WowSpec import WowSpec

logger = logging.getLogger(__name__)


def pretty_timestamp() -> str:
    """Returns a pretty time stamp "YYYY-MM-DD HH:MM"

    Returns:
      str -- timestamp
    """
    # str(datetime.datetime.utcnow())[:-10] should be the same
    return datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M")


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

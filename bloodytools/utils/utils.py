import datetime
import logging
import re
from simc_support import wow_lib

logger = logging.getLogger(__name__)


def create_basic_profile_string(wow_class: str, wow_spec: str, tier: str, settings: object):
  """Create basic profile string to get the standard profile of a spec. Use this function to get the necessary string for your first argument of a simulation_data object.

  Arguments:
    wow_class {str} -- wow class, e.g. shaman
    wow_spec {str} -- wow spec, e.g. elemental
    tier {str} -- profile tier, e.g. 21 or PR

  Returns:
    str -- relative link to the standard simc profile
  """

  logger.debug("create_basic_profile_string start")
  # create the basis profile string
  split_path: list = settings.executable.split("simc")
  if len(split_path) > 2:
    # the path contains multiple "simc"
    basis_profile_string: str = "simc".join(split_path[:-1])
  else:
    basis_profile_string: str = split_path[0]

  # fix path for linux users
  if basis_profile_string.endswith("/engine/"):
    split_path = basis_profile_string.split("/engine/")
    if len(split_path) > 2:
      basis_profile_string = "/engine/".join(split_path[:-1])
    else:
      basis_profile_string = split_path[0] + "/"

  basis_profile_string += "profiles/"
  if tier == "PR":
    basis_profile_string += "PreRaids/PR_{}_{}".format(wow_class.title(), wow_spec.title())
  else:
    basis_profile_string += "Tier{}/T{}_{}_{}".format(tier, tier, wow_class, wow_spec).title()
  basis_profile_string += ".simc"

  logger.debug("Created basis_profile_string '{}'.".format(basis_profile_string))
  logger.debug("create_basic_profile_string ended")
  return basis_profile_string


def pretty_timestamp() -> str:
  """Returns a pretty time stamp "YYYY-MM-DD HH:MM"

  Returns:
    str -- timestamp
  """
  # str(datetime.datetime.utcnow())[:-10] should be the same
  return datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M")


def extract_profile(path: str, wow_class: str, profile: dict = None) -> dict:
  """Extract all character specific data from a given file.

  Arguments:
      path {str} -- path to file, relative or absolute
      profile {dict} -- profile input that should be updated

  Returns:
      dict -- all known character data
  """

  logger.warning(
    'DEPRICATION WARNING: profile format change. Information will be stored in its own subsection. Read result file to already get the new format.'
  )

  if not profile:
    profile = {}

  if not 'character' in profile:
    profile['character'] = {}

  profile['character']['class'] = wow_class

  # prepare regex for each extractable slot
  item_slots = [
    "head",
    "neck",
    "shoulders",
    "back",
    "chest",
    "wrists",
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
  pattern_slots = {}
  for element in item_slots:
    pattern_slots[element] = re.compile('^{}=([a-z0-9_=,/:.]*)$'.format(element))

  # prepare regex for item defining attributes
  item_elements = [
    "id",
    "bonus_id",
    "azerite_powers",
    "enchant",
    "azerite_level",     # neck
    "ilevel",
  ]
  pattern_element = {}
  # don't recompile this for each slot
  for element in item_elements:
    pattern_element[element] = re.compile(',{}=([a-z0-9_/:]*)'.format(element))

  # prepare regex for character defining information. like spec
  character_specifics = [
    'level',
    'race',
    'role',
    'position',
    'talents',
    'spec',
    'azerite_essences',
  ]
  pattern_specifics = {}
  for element in character_specifics:
    pattern_specifics[element] = re.compile('^{}=([a-z0-9_./:]*)$'.format(element))

  with open(path, 'r') as f:
    for line in f:
      for specific in character_specifics:

        matches = pattern_specifics[specific].search(line)
        if matches:
          profile['character'][specific] = matches.group(1)
          # TODO: remove after some time (webfront-end needs to be updated)
          profile[specific] = matches.group(1)

      for slot in item_slots:

        if not 'items' in profile:
          profile['items'] = {}

        matches = pattern_slots[slot].search(line)
        # slot line found
        if matches:
          new_line = matches.group(1)
          if not slot in profile:
            profile['items'][slot] = {}

          # allow pre-prepared profiles to get emptied if input wants to overwrite with empty
          # 'head=' as a head example for an empty overwrite
          if not new_line:
            profile['items'].pop(slot, None)

          # check for all elements
          for element in item_elements:
            new_matches = pattern_element[element].search(new_line)
            if new_matches:
              profile['items'][slot][element] = new_matches.group(1)
              # TODO: remove after some time (webfront-end needs to be updated)
              if not slot in profile:
                profile[slot] = {}
              profile[slot][element] = new_matches.group(1)

  return profile


def create_base_json_dict(data_type: str, wow_class: str, wow_spec: str, fight_style: str, settings: object):
  """Creates as basic json dictionary. You'll need to add your data into 'data'. Can be extended.

  Arguments:
    data_type {str} -- e.g. Races, Trinkets, Azerite Traits (str is used in the title)
    wow_class {str} -- [description]
    wow_spec {str} -- [description]
    fight_style {str} -- [description]

  Returns:
    dict -- [description]
  """

  logger.debug("create_base_json_dict start")

  timestamp = pretty_timestamp()

  profile_location = create_basic_profile_string(wow_class, wow_spec, settings.tier, settings)

  profile = extract_profile(profile_location, wow_class)

  if settings.custom_profile:
    profile = extract_profile('custom_profile.txt', wow_class, profile)

  # spike the export data with talent data
  talent_data = wow_lib.get_talent_dict(wow_class, wow_spec, settings.ptr == "1")

  # add class/ id number
  class_id = wow_lib.get_class_id(wow_class)
  spec_id = wow_lib.get_spec_id(wow_class, wow_spec)

  subtitle = "UTC {timestamp}".format(timestamp=timestamp)
  if settings.simc_hash:
    subtitle += " | SimC build: <a href=\"https://github.com/simulationcraft/simc/commit/{simc_hash}\" target=\"blank\">{simc_hash_short}</a>".format(
      simc_hash=settings.simc_hash, simc_hash_short=settings.simc_hash[0:7]
    )

  return {
    "data_type": "{}".format(data_type.lower().replace(" ", "_")),
    "timestamp": timestamp,
    "title":
      "{data_type} | {wow_spec} {wow_class} | {fight_style}".format(
        data_type=data_type.title(),
        wow_class=wow_class.title().replace("_", " "),
        wow_spec=wow_spec.title().replace("_", " "),
        fight_style=fight_style.title()
      ),
    "subtitle": subtitle,
    "simc_settings": {
      "tier": settings.tier,
      "fight_style": fight_style,
      "iterations": settings.iterations,
      "target_error": settings.target_error[fight_style],
      "ptr": settings.ptr,
      "simc_hash": settings.simc_hash,
     # deprecated
      "class": wow_class,
     # deprecated
      "spec": wow_spec
    },
    "data": {},
    "languages": {},
    "profile": profile,
    "talent_data": talent_data,
    "class_id": class_id,
    "spec_id": spec_id
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
  if "__" in string or " " in string or "-" in string or "'" in string or "," in string:
    return tokenize_str(string.replace("'", "").replace("-", "").replace(" ", "_").replace("__", "_").replace(",", ""))

  return string


def get_simc_hash(path) -> str:
  """Get the FETCH_HEAD or shallow simc git hash.

  Returns:
    str -- [description]
  """

  if ".exe" in path:
    new_path = path.split("simc.exe")[0]
  else:
    new_path = path[:-5]     # cut "/simc" from unix path
    if "engine" in new_path[-6:]:
      new_path = new_path[:-6]

  # add path to file to variable
  new_path += ".git/FETCH_HEAD"

  try:
    with open(new_path, 'r', encoding='utf-8') as f:
      for line in f:
        if "'bfa-dev'" in line:
          simc_hash = line.split()[0]
  except FileNotFoundError:
    try:
      with open('../../SimulationCraft/.git/shallow', 'r', encoding='utf-8') as f:
        for line in f:
          simc_hash = line.strip()
    except FileNotFoundError:
      logger.warning("Couldn't extract SimulationCraft git hash. Result files won't contain a sane hash.")
      simc_hash = None
    except Exception as e:
      logger.error(e)
      raise e
  except Exception as e:
    logger.error(e)
    raise e

  return simc_hash

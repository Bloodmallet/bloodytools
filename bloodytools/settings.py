"""Settings for bloodytools

  Look for the matching paragraphs of what you want to do. And change settings responsibly. If anything breaks too hard, just reload the settingsfile from the repository.
"""

##
# General setttings
fight_styles = [
  "patchwerk",
  "hecticaddcleave"
  #"beastlord"
]
tier = "21"  # number or PR (PreRaid)
wow_class_spec_list = []  # leave empty to simulate all
# wow_class_spec_list = [("shaman", "elemental"), ("mage", "frost")] # example for a specific list
wow_class_spec_list = [
  ("death_knight", "blood"),
  ("death_knight", "frost"),
  ("death_knight", "unholy"),
  ("demon_hunter", "havoc"),
  ("demon_hunter", "vengeance"),
  ("druid", "balance"),
  ("druid", "feral"),
  ("druid", "guardian"),
  ("hunter", "beast_mastery"),
  ("hunter", "marksmanship"),
  ("hunter", "survival"),
  ("mage", "arcane"),
  ("mage", "fire"),
  ("mage", "frost"),
  ("monk", "brewmaster"),
  ("monk", "windwalker"),
  ("paladin", "protection"),
  ("paladin", "retribution"),
  ("priest", "shadow"),
  ("rogue", "assassination"),
  ("rogue", "outlaw"),
  ("rogue", "subtlety"),
  ("shaman", "elemental"),
  ("shaman", "enhancement"),
  ("warlock", "affliction"),
  ("warlock", "demonology"),
  ("warlock", "destruction"),
  ("warrior", "arms"),
  ("warrior", "fury"),
  ("warrior", "protection"),
]

##
# SimulationCraft
executable = "../../SimulationCraft_BfA/simc.exe"
iterations = "250000"
profileset_work_threads = "2"
ptr = "0"
simc_hash = "859a728aab39f4c82e100aadef07f3c26186f770"
target_error = "0.2"
threads = "8"

###############################################################################
# Race simulations
enable_race_simulations = True

###############################################################################
# Trinket simulations
enable_trinket_simulations = True
ilevel_step = 10  # ilevel_step is used to determine the size of each itemlevel step taken to max_ilevel
max_ilevel = 280  # max_itemlevel determines the upper border of steps taken
min_ilevel = 210  # min_ilevel is used to determine the first simulated itemlevel
# example: min 300, max 325, step 10, resulting simulated ilevels: 300, 310, 320

###############################################################################
# Secondary distributions
enable_secondary_distributions_simulations = False
talent_list = {
}  # if no list is provided for a class-spec, all dps talent combinations will be run. If you want to only sim the base profiles, set 'talent_permutations' to False
# talent_list = {
#   ("shaman", "elemental"): [
#     "2302023",
#   ],
# }  # example for a talent list for Elemental Shamans
talent_permutations = True  # set to False, to sim only the base profile talent combinations

###############################################################################
# Development setting - you usually don't want to touch these
debug = True
use_own_threading = False
use_raidbots = False
write_humanreadable_secondary_distribution_file = True
lua_trinket_export = False
try:
  from apikey import apikey
except Exception:
  pass

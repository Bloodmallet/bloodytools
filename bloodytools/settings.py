"""Settings for bloodytools

  Look for the matching paragraphs of what you want to do. And change settings responsibly. If anything breaks too hard, just reload the settingsfile from the repository.
"""

##
# General setttings
fight_styles = [
  "patchwerk",
  #"beastlord"
]
tier = "PR"  # number or PR (PreRaid)
wow_class_spec_list = []  # leave empty to simulate all
# wow_class_spec_list = [("shaman", "elemental"), ("mage", "frost")] # example for a specific list

##
# SimulationCraft
executable = "../../SimulationCraft_BfA/simc.exe"
iterations = "250000"
profileset_work_threads = "2"
ptr = "0"
simc_hash = "129d90531685e1e9388127317cabc57b0e5668d2"
target_error = "0.6"
threads = "8"

##
# Race simulations
enable_race_simulations = True

##
# Trinket simulations
enable_trinket_simulations = True
ilevel_step = 10  # ilevel_step is used to determine the size of each itemlevel step taken to max_ilevel
max_ilevel = 355  # max_itemlevel determines the upper border of steps taken
min_ilevel = 300  # min_ilevel is used to determine the first simulated itemlevel
# example: min 300, max 325, step 10, resulting simulated ilevels: 300, 310, 320

##
# Secondary distributions
enable_secondary_distributions_simulations = True
talent_list = {
}  # if no list is provided for a class-spec, all dps talent combinations will be run. If you want to only sim the base profiles, set 'talent_permutations' to False
# talent_list = {
#   ("shaman", "elemental"): ["1111111", "2222222"],
# } # example for a talent list for Elemental Shamans
talent_permutations = True  # set to False, to sim only the base profile talent combinations

##
# Developement setting - you usually don't need to touch these
debug = True

"""Settings for bloodytools

  Look for the matching paragraphs of what you want to do. Change settings responsibly. If anything breaks too hard, just reload the settings-file from the repository.
"""
from bloodytools.utils.data_type import DataType
import simc_support.game_data.WowSpec as WowSpec

##
# General setttings
tier = "27"  # number or PR (PreRaid)
wow_class_spec_list = [
    spec
    for spec in WowSpec.WOWSPECS
    if spec
    not in [
        WowSpec.DISCIPLINE,
        WowSpec.HOLY_PRIEST,
        WowSpec.RESTORATION_DRUID,
        WowSpec.RESTORATION_SHAMAN,
    ]
]
data_type = DataType.DPS

###############################################################################
# SimulationCraft
executable = "../SimulationCraft/simc.exe"
fight_styles = [
    "patchwerk",
    "hecticaddcleave",
    # "beastlord"
]
iterations = "20000"  # sane value, should be enough for 0.2
profileset_work_threads = "2"
ptr = "0"
default_actions = "1"
target_error = {
    "patchwerk": "0.1",
    "hecticaddcleave": "0.2",
    "beastlord": "0.2",
}
threads = "8"

custom_apl = False
custom_fight_style = False
# custom profile overrides standard profile, standard profile is still used as baseline
custom_profile = False

###############################################################################
# Race simulations
enable_race_simulations = False

###############################################################################
# Trinket simulations
enable_trinket_simulations = False
# max_itemlevel determines the upper border
max_ilevel = 259
# min_ilevel is used to determine the first simulated itemlevel and second trinket (vers stat stick)
min_ilevel = 210
lua_trinket_export = False

###############################################################################
# Secondary distributions
enable_secondary_distributions_simulations = False
# in percent of full available secondary sum
secondary_distributions_step_size = 10
talent_list = (
    {}
)  # if no list is provided for a class-spec, all dps talent combinations will be run. If you want to only sim the base profiles, set 'talent_permutations' to False
# talent_list = {
#   WowSpec.ELEMENTAL: [
#     "2301022",
#   ],
# }  # example for a talent list for Elemental Shamans
# set to False, to sim only the base profile talent combinations
talent_permutations = False
write_humanreadable_secondary_distribution_file = False


###############################################################################
# Gear path
enable_gear_path = False
step_size = 50
start_value = 50

###############################################################################
# Talent
enable_talent_simulations = False

###############################################################################
# Covenant
enable_covenant_simulations = False

###############################################################################
# Soul Bind
enable_soul_bind_simulations = False

###############################################################################
# Soul Bind Node
enable_soul_bind_node_simulations = False

###############################################################################
# Conduit
enable_conduit_simulations = False

###############################################################################
# Legendary simulations
enable_legendary_simulations = False

###############################################################################
# Domination Shard simulations
enable_domination_shards = False

###############################################################################
# Tier Set simulations
enable_tier_sets = False

###############################################################################
# Development setting - you usually don't want to touch these
debug = False
use_raidbots = False
remove_files = False
try:
    from bloodytools.apikey import apikey
except Exception:
    if use_raidbots:
        exit("Error: apikey required! Add your apikey to apikey.py")
    pass

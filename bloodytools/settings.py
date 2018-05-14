# Profile setttings
tier = "PR"  # number or PR (PreRaid)
fight_styles = [
  "patchwerk",
  #"beastlord"
]

# Simulation settings
executable = "../../SimulationCraft_BfA/simc.exe"
threads = "8"
profileset_work_threads = "2"
target_error = "0.6"
iterations = "250000"
ptr = "0"

# General Bloodytools Settings - you usually don't need to touch these
debug = True
simc_hash = "129d90531685e1e9388127317cabc57b0e5668d2"

# trinket settings
min_ilevel = 300  # min_ilevel is used to determine the first simulated itemlevel
max_ilevel = 355  # max_itemlevel determines the upper border of steps taken
ilevel_step = 10  # ilevel_step is used to determine the size of each itemlevel step taken to max_ilevel
# example: min 300, max 325, step 10, resulting simulated ilevels: 300, 310, 320

# Structure
#   wow-class
#       wow-spec
#           - special case 1
#           - special case 2
#
# Special case structure
#   'name' of the legendary
#   'name_additions', additional strings to be added to the name of the legendary to identifiy this special case in the chart
#   'override', alteration of the profile
#

SPECIAL_CASES = {
    "shaman": {
        "enhancement": [
            {
                "name": "Doom Winds",
                "name_additions": ["FW", "Asc"],
                "overrides": ["talents=2111133"],
            },
            {
                "name": "Witch Doctor's Wolf Bones",
                "name_additions": ["ES"],
                "overrides": ["talents=3111131"],
            },
        ]
    }
}

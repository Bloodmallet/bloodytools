#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This file contains special cases for Azerite Trait simulations. The base profiles will still be simulated. The special cases described in this file add additional simulation profiles. Please be as conservative with adding special cases as possible for now.

  Support for Trinkets and others might be added later on.
"""

# Structure:
# {
#   wow_class: {
#     wow_spec:  {
#       fight_style: {
#         data_type: {
#           hook_name: [ # list of additional profiles to the base profile
#             {
#               "suffix": "",
#               "additional_input": [ "", "" ],
#               "link_data": {
#                 "part_of_suffix": {"spell_id"/"item_id": "number"},
#               },
#               "description": ""
#             },
#           ]
#         }
#       }
#     }
#   }
# }
# wow_class - "shaman", ...
# wow_spec - "elemental", ...
# fight_style - "patchwerk", ...
# data_type - "azerite_trait_simulations"
# hook_name - e.g. "Laser Matrix" (Azerite Trait name)
# "suffix" - what you write here will be added to the name of the Trait. Make sure to use abbreviations where possible. The suffix will be added with a + to the standard name. "Laser Matrix" with the suffix "10" will become "Laser Matrix +10"
# "additional_input" - list of all necessary additional input to manipulate the standard profile e.g. "talents=2101011"
# "link_data" - contains information for additional spell or item links. This data is required to allow proper links + potential icons in the charts. To expand the Laser Matrix example: "link_data": {"10": {"spell_id": "281237"}}
# "description"  - add whatever is useful to describe the special case and why it's important. Consider that others might later need that information to determine whether this needs an update or not.
# Last but not least you can create longer suffixes consisting of multiple additional spells/items by adding + into the suffix name. E.g. "hello +world". You can then use "hello" and "world" in link_data to indicate multiple changes to the profile.

special_cases = {
  "hunter": {
    "beast_mastery": {
      "patchwerk": {
        "azerite_trait_simulations": {
          "Pack Alpha": [
            {
              "suffix": "AC",
              "additional_input": ["talents=2303011"],
              "link_data": {
                "AC": { "spell_id": "267116" }
              },
              "description": "Pack Alpha needs additional active pets to provide actual value. Animal Companion (talent) provides that."
            },
            {
              "suffix": "DB",
              "additional_input": ["talents=3303011"],
              "link_data": {
                "DB": { "spell_id": "120679" }
              },
              "description": "Pack Alpha needs additional active pets to provide actual value. Dire Beast (talent) provides that to some degree."
            },
          ]
        }
      },
      "hecticaddcleave": {
        "azerite_trait_simulations": {
          "Pack Alpha": [
            {
              "suffix": "AC",
              "additional_input": ["talents=2303011"],
              "link_data": {
                "AC": { "spell_id": "267116" }
              },
              "description": "Pack Alpha needs additional active pets to provide actual value. Animal Companion (talent) provides that."
            },
            {
              "suffix": "DB",
              "additional_input": ["talents=3303011"],
              "link_data": {
                "DB": { "spell_id": "120679" }
              },
              "description": "Pack Alpha needs additional active pets to provide actual value. Dire Beast (talent) provides that to some degree."
            },
          ]
        }
      }
    }
  },
  "shaman": {
    "elemental": {
      "patchwerk": {
        "azerite_trait_simulations": {
          "Natural Harmony": [
            {
              "suffix": "EB",
              "additional_input": ["talents=3303023"],
              "link_data": {
                "EB": { "spell_id": "117014" }
              },
              "description": "Natural Harmony buffs different secondary stats based on the used spell school. The standard patchwerk simulation doesn't use the Frost School. Switching to Elemental Blast (talent) forces this school."
            }
          ]
        }
      }
    }
  }
}

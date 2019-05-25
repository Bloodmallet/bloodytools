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
  # "druid": {
  #   "balance": {
  #     "patchwerk": {
  #       "azerite_trait_simulations": {
  #         "*": [
  #           {
  #             "suffix": "AP",
  #             "additional_input": ["azerite_override=arcanic_pulsar:<itemlevel>"],
  #             "link_data": {
  #               "AP": { "spell_id": "287773" }
  #             },
  #             "description": "All Balance azerite profiles use Arcanic Pulsar because it changes their order quite significantly.",
  #             "base_trait": "Arcanic Pulsar",
  #             "base_trait_id": "200"
  #           }
  #         ]
  #       }
  #     },
  #   },
  # },
  "rogue": {
    "assassination": {
      "patchwerk": {
        "azerite_trait_simulations": {
          "Shrouded Suffocation": [
            {
              "suffix": "Sub",
              "additional_input": ["talents=2210021"],
              "link_data": {
                "Sub": { "spell_id": "108208" }
              },
              "description": "Forcing the use of Subterfuge"
            }
          ]
        }
      },
      "hecticaddcleave": {
        "azerite_trait_simulations": {
          "Shrouded Suffocation": [
            {
              "suffix": "Sub",
              "additional_input": ["talents=2210021"],
              "link_data": {
                "Sub": { "spell_id": "108208" }
              },
              "description": "Forcing the use of Subterfuge"
            }
          ]
        }
      }
    },
    "outlaw": {
      "patchwerk": {
        "azerite_trait_simulations": {
          "Ace Up Your Sleeve": [
            {
              "suffix": "DS",
              "additional_input": ["talents=2020022"],
              "link_data": {
                "DS": { "spell_id": "193531" }
              },
              "description": "Forcing the use of Deeper Stratagem"
            }
          ]
        }
      }
    }
  },
  "shaman": {
    "enhancement": {
      "patchwerk": {
        "azerite_trait_simulations": {
          "Thunderaan's Fury": [
            {
              "suffix": "LiS+FFW+SA",
              "additional_input": ["talents=3201031"],
              "link_data": {
                "LiS": { "spell_id": "192106" },
                "FFW": { "spell_id": "262647" },
                "SA": { "spell_id": "192087" }
              },
              "description": "Classic 8.0 build"
            }
          ],
          "Natural Harmony": [
            {
              "suffix": "SA",
              "additional_input": ["talents=2301031"],
              "link_data": {
                "SA": { "spell_id": "192087" },
              },
              "description": "Natural Harmony comparison on Freezerburn build with Searing Assault"
            },
            {
              "suffix": "LiS+FFW+SA+Asc",
              "additional_input": ["talents=3201033"],
              "link_data": {
                "LiS": { "spell_id": "192106" },
                "FFW": { "spell_id": "262647" },
                "SA": { "spell_id": "192087" },
                "Asc": { "spell_id": "114051" }
              },
              "description": "Natural Harmony comparison on default build with Searing Assault"
            },
            {
              "suffix": "LiS+FFW+Asc",
              "additional_input": ["talents=3202033"],
              "link_data": {
                "LiS": { "spell_id": "192106" },
                "FFW": { "spell_id": "262647" },
                "Asc": { "spell_id": "114051" }
              },
              "description": "Natural Harmony comparison on default build with Hailstorm"
            }
          ],
        }
      },
      "hecticaddcleave": {
        "azerite_trait_simulations": {
          "Thunderaan's Fury": [
            {
              "suffix": "LiS+FFW+HS",
              "additional_input": ["talents=3201031"],
              "link_data": {
                "LiS": { "spell_id": "192106" },
                "FFW": { "spell_id": "262647" },
                "HS": { "spell_id": "210853" },
              },
              "description": "Classic 8.0 build"
            }
          ]
        }
      }
    }
  },
  "warrior": {
    "fury": {
      "patchwerk": {
        "azerite_trait_simulations": {
          "Gathering Storm": [
            {
              "suffix": "BS",
              "additional_input": ["talents=2332133"],
              "link_data": {
                "BS": { "spell_id": "46924" }
              },
              "description": "Archimtiros"
            }
          ]
        }
      },
      "hecticaddcleave": {
        "azerite_trait_simulations": {
          "Gathering Storm": [
            {
              "suffix": "BS",
              "additional_input": ["talents=2332133"],
              "link_data": {
                "BS": { "spell_id": "46924" }
              },
              "description": "Archimtiros"
            }
          ]
        }
      }
    }
  }
}

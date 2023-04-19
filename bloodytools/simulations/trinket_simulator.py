"""
https://github.com/WarcraftPriests/df-shadow-priest/blob/main/trinkets/other.simc#L40-L58
"""

import logging
import typing

from bloodytools.simulations.simulator import Simulator
from bloodytools.utils.config import Config
from bloodytools.utils.simulation_objects import Simulation_Data, Simulation_Group
from simc_support.game_data.Trinket import (
    Trinket,
    get_trinkets_for_spec,
    get_versatility_trinket,
)
from simc_support.game_data.WowSpec import WowSpec
from simc_support.game_data.Season import Season
from simc_support.game_data.Source import Source

logger = logging.getLogger(__name__)

# special cases
M0_ITEMLEVEL = 372
ALLOWED_NON_SEASONAL_DUNGEON_ITEMS = (
    193743,  # Irideus Frament
    193791,  # Time-Breaching Talon
    193773,  # Spoils of Neltharus
)
DARKMOON_DECK_BOX_BONUS_IDS: typing.Dict[str, int] = {
    "Emberscale": 8858,
    "Jetscale": 8860,
    "Sagescale": 8861,
    "Azurescale": 8859,
    "Bronzescale": 8857,
    "None": "",  # type: ignore
}

SPECIAL_CASE_BONUS_IDS: typing.Dict[int, typing.Dict[str, int]] = {
    # Mistcaller Ocarina
    178715: {
        "crit": 6920,
        "haste": 6921,
        "mastery": 6922,
        "versatility": 6923,
    },
    # Unbound Changeling
    178708: {
        "crit": 6916,
        "haste": 6917,
        "mastery": 6918,
        "all": 6915,
    },
    # Darkmoon Deck Box: Rime
    198477: DARKMOON_DECK_BOX_BONUS_IDS,
    # Darkmoon Deck Box: Inferno
    194872: DARKMOON_DECK_BOX_BONUS_IDS,
    # Darkmoon Deck Box: Dance
    198478: DARKMOON_DECK_BOX_BONUS_IDS,
}

SPECIAL_CASE_SIMC_OPTIONS = {
    194301: {  # Whispering Incarnate Icon
        "dps": "dragonflight.whispering_incarnate_icon_roles=dps",
        "dps/heal": "dragonflight.whispering_incarnate_icon_roles=dps/heal",
        "dps/tank": "dragonflight.whispering_incarnate_icon_roles=dps/tank",
        "dps/heal/tank": "dragonflight.whispering_incarnate_icon_roles=dps/heal/tank",
    },
    200563: {  # Primal Ritual Shell
        "wind": "dragonflight.primal_ritual_shell_blessing=wind",
        "flame": "dragonflight.primal_ritual_shell_blessing=flame",
    },
    193757: {  # Ruby Whelp Shell
        "ST": "dragonflight.player.ruby_whelp_shell_training=fire_shot:6",
        "AoE": "dragonflight.player.ruby_whelp_shell_training=lobbing_fire_nova:6",
        "haste": "dragonflight.player.ruby_whelp_shell_training=under_red_wings:6",
        "crit": "dragonflight.player.ruby_whelp_shell_training=sleepy_ruby_warmth:6",
    },
}

NON_DPS_TRINKET_IDS = [
    "133645",  # Naglfar Fare
    "133646",  # Mote of Sanctification
    "133766",  # Nether Anti-Toxin
    "136714",  # Amalgam's Seventh Spine
    "137315",  # Writhing Heart of Darkness
    "137344",  # Talisman of the Cragshaper
    "137362",  # Parjesh's Medallion
    "137378",  # Bottled Hurricane
    "137400",  # Coagulated Nightwell Residue
    "137430",  # Impenetrable Nerubian Husk
    "137440",  # Shivermaw's Jawbone
    "137452",  # Thrumming Gossamer
    "137462",  # Jewel of Insatiable Desire
    "137484",  # Flask of the Solemn Night
    "137538",  # Orb of Torment
    "137540",  # Concave Reflecting Lens
    "142158",  # Faith's Crucible
    "142161",  # Inescapable Dread
    "142162",  # Fluctuating Energy
    "142169",  # Raven Eidolon
    "142168",  # Majordomo's Dinner Bell
    "151340",  # Echo of L'ura
    "186434",  # Weave of Warped Fates
]


def _is_valid_itemlevel(itemlevel: int, settings: Config) -> bool:
    return itemlevel >= settings.min_ilevel and itemlevel <= settings.max_ilevel


def _get_trinkets(wow_spec: WowSpec, settings: Config) -> typing.List[Trinket]:
    # get main-trinkets
    trinket_list = list(get_trinkets_for_spec(wow_spec))

    allowed_season = [
        Season.SEASON_1,
        # Season.SEASON_2
    ]

    new_trinket_list = []
    for trinket in trinket_list:
        for season in trinket.seasons:
            if season in allowed_season and trinket not in new_trinket_list:
                logger.debug(
                    f"Adding {trinket.full_name} to the list. It's seasons: {trinket.seasons}"
                )
                new_trinket_list.append(trinket)

    # filter trinket list by available itemlevels:
    trinket_list = [
        t
        for t in new_trinket_list
        if any([_is_valid_itemlevel(ilevel, settings) for ilevel in t.itemlevels])
    ]

    trinket_list = [
        t for t in trinket_list if str(t.item_id) not in NON_DPS_TRINKET_IDS
    ]

    # remove lower pvp trinkets
    trinket_list = [t for t in trinket_list if t != Source.LOW_PVP]

    # add special case trinkets
    special_trinkets = [
        t
        for t in list(get_trinkets_for_spec(wow_spec))
        if t.item_id in ALLOWED_NON_SEASONAL_DUNGEON_ITEMS
    ]

    return trinket_list + special_trinkets


def _get_second_trinket(wow_spec: WowSpec) -> Trinket:
    return get_versatility_trinket(wow_spec.stat)


class TrinketSimulator(Simulator):
    @classmethod
    def name(cls) -> str:
        return "Trinkets"

    def pre_processing(self, data_dict: dict) -> dict:
        data_dict = super().pre_processing(data_dict)

        trinket_list = _get_trinkets(self.wow_spec, self.settings)

        # get secondary-trinket (standard stat stick)
        second_trinket = _get_second_trinket(self.wow_spec)

        # fix profile for this type of simulations
        data_dict["profile"]["items"].pop("trinket1", None)
        data_dict["profile"]["items"].pop("trinket2", None)
        data_dict["profile"]["items"]["trinket2"] = {
            "id": second_trinket.item_id,
            "bonus_id": second_trinket.bonus_ids[0],  # type: ignore
            "ilevel": str(self.settings.min_ilevel),
        }

        data_dict["data_active"] = {}
        data_dict["data_sources"] = {}
        data_dict["item_ids"] = {}
        data_dict["data"]["baseline"] = {}
        for trinket in trinket_list:
            data_dict["translations"][trinket.name] = trinket.translations.get_dict()
            data_dict["data"][trinket.name] = {}
            data_dict["data_active"][trinket.name] = trinket.on_use
            data_dict["data_sources"][trinket.name] = trinket.source.value
            data_dict["item_ids"][trinket.name] = trinket.item_id

            for stat in SPECIAL_CASE_BONUS_IDS.get(trinket.item_id, {}).keys():
                tmp_name = f"{trinket.name} [{stat.title()}]"
                data_dict["translations"][tmp_name] = trinket.translations.get_dict()
                for key in data_dict["translations"][tmp_name]:
                    data_dict["translations"][tmp_name][key] = (
                        data_dict["translations"][tmp_name][key] + f" [{stat.title()}]"
                    )
                data_dict["data"][tmp_name] = {}
                data_dict["data_active"][tmp_name] = trinket.on_use
                data_dict["data_sources"][tmp_name] = trinket.source.value
                data_dict["item_ids"][tmp_name] = trinket.item_id

            for special_option in SPECIAL_CASE_SIMC_OPTIONS.get(
                trinket.item_id, {}
            ).keys():
                tmp_name = f"{trinket.name} [{special_option.title()}]"
                data_dict["translations"][tmp_name] = trinket.translations.get_dict()
                for key in data_dict["translations"][tmp_name]:
                    data_dict["translations"][tmp_name][key] = (
                        data_dict["translations"][tmp_name][key]
                        + f" [{special_option.title()}]"
                    )
                data_dict["data"][tmp_name] = {}
                data_dict["data_active"][tmp_name] = trinket.on_use
                data_dict["data_sources"][tmp_name] = trinket.source.value
                data_dict["item_ids"][tmp_name] = trinket.item_id

        return data_dict

    def add_simulation_data(
        self, simulation_group: Simulation_Group, data_dict: dict
    ) -> None:
        all_itemlevels: typing.Set[int] = set()
        trinket_list = _get_trinkets(self.wow_spec, self.settings)
        for trinket in trinket_list:
            itemlevels = [
                i for i in trinket.itemlevels if _is_valid_itemlevel(i, self.settings)
            ]
            if not itemlevels and trinket.item_id in ALLOWED_NON_SEASONAL_DUNGEON_ITEMS:
                itemlevels.append(M0_ITEMLEVEL)
            for itemlevel in itemlevels:
                all_itemlevels.add(itemlevel)
        min_itemlevel = min(all_itemlevels)

        simulation_data = Simulation_Data(
            name=self.profile_split_character().join(["baseline", str(min_itemlevel)]),
            fight_style=self.fight_style,
            iterations=self.settings.iterations,
            target_error=self.settings.target_error.get(self.fight_style, "0.1"),
            profile=data_dict["profile"],
            simc_arguments=[
                "trinket1=",
            ],
            ptr=self.settings.ptr,
            default_actions=self.settings.default_actions,
            executable=self.settings.executable,
        )

        if self.settings.custom_apl:
            with open("custom_apl.txt") as f:
                custom_apl = f.read()
            simulation_data.simc_arguments.append("# custom_apl")
            simulation_data.simc_arguments.append(custom_apl)

        if self.settings.custom_fight_style:
            with open("custom_fight_style.txt") as f:
                custom_fight_style = f.read()
            simulation_data.simc_arguments.append("# custom_fight_style")
            simulation_data.simc_arguments.append(custom_fight_style)

        simulation_group.add(simulation_data)

        for trinket in trinket_list:
            # for each available itemlevel of the trinket
            itemlevels = [
                i for i in trinket.itemlevels if _is_valid_itemlevel(i, self.settings)
            ]
            if trinket.item_id in ALLOWED_NON_SEASONAL_DUNGEON_ITEMS:
                itemlevels = [M0_ITEMLEVEL]
            # weed out every other itemlevel, except first and last
            if len(itemlevels) > 10:
                first = itemlevels[0]
                last = itemlevels[-1]
                filtered_itemlevels = [
                    level for i, level in enumerate(itemlevels, 1) if i % 2
                ]
                if last not in filtered_itemlevels:
                    filtered_itemlevels = [first] + [
                        level for i, level in enumerate(itemlevels, 1) if (i + 1) % 2
                    ]
                if first not in filtered_itemlevels or last not in filtered_itemlevels:
                    raise ValueError(
                        "Somehow first or last valid itemlevel are missing the generated filtered_itemlevels."
                    )
            else:
                filtered_itemlevels = itemlevels

            for itemlevel in filtered_itemlevels:
                simulation_data = Simulation_Data(
                    name=self.profile_split_character().join(
                        [trinket.name, str(itemlevel)]
                    ),
                    fight_style=self.fight_style,
                    iterations=self.settings.iterations,
                    target_error=self.settings.target_error.get(
                        self.fight_style, "0.1"
                    ),
                    simc_arguments=[
                        "trinket1=,id={},ilevel={}".format(trinket.item_id, itemlevel)
                    ],
                    ptr=self.settings.ptr,
                    default_actions=self.settings.default_actions,
                    executable=self.settings.executable,
                )
                simulation_group.add(simulation_data)

                # special cases
                if trinket.item_id in SPECIAL_CASE_BONUS_IDS:
                    for stat in SPECIAL_CASE_BONUS_IDS[trinket.item_id]:
                        new_data = simulation_data.copy()
                        new_data.simc_arguments[-1] = (
                            new_data.simc_arguments[-1]
                            + f",bonus_id={SPECIAL_CASE_BONUS_IDS[trinket.item_id][stat]}"
                        )
                        new_data.name = self.get_profile_name(
                            f"{trinket.name} [{stat.title()}]", str(itemlevel)
                        )

                        simulation_group.add(new_data)

                if trinket.item_id in SPECIAL_CASE_SIMC_OPTIONS:
                    base_simulation = simulation_group.profiles[-1].copy()
                    simulation_group.profiles = simulation_group.profiles[:-1]
                    for option in SPECIAL_CASE_SIMC_OPTIONS[trinket.item_id]:
                        new_data = base_simulation.copy()
                        new_data.simc_arguments = new_data.simc_arguments + [
                            SPECIAL_CASE_SIMC_OPTIONS[trinket.item_id][option]
                        ]
                        new_data.name = self.get_profile_name(
                            f"{trinket.name} [{option.title()}]", str(itemlevel)
                        )

                        simulation_group.add(new_data)

    def post_processing(self, data_dict: dict) -> dict:
        data_dict = super().post_processing(data_dict)

        # derive itemlevel list from simulated information
        simulated_steps = set()
        for values in data_dict["data"].values():
            for step in values.keys():
                # conversion to int to keep old behavior
                simulated_steps.add(int(step))
        data_dict["simulated_steps"] = sorted(list(simulated_steps), reverse=True)

        # create ordered trinket name list
        self.create_sorted_key_key_value_data(data_dict, ignore_key="baseline")

        return data_dict

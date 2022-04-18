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
from simc_support.game_data.Stat import Stat

logger = logging.getLogger(__name__)

# special cases
SPECIAL_CASE_BONUS_IDS = {
    # Mistcaller Ocarina
    "178715": {
        "crit": 6920,
        "haste": 6921,
        "mastery": 6922,
        "versatility": 6923,
    },
    # Unbound Changeling
    "178708": {
        "crit": 6916,
        "haste": 6917,
        "mastery": 6918,
        "all": 6915,
    },
}
SOLEAHS_SPECIAL_CASES = {
    "190958": {
        "crit": "shadowlands.soleahs_secret_technique_type_override=crit",
        "haste": "shadowlands.soleahs_secret_technique_type_override=haste",
        "mastery": "shadowlands.soleahs_secret_technique_type_override=mastery",
        "versatility": "shadowlands.soleahs_secret_technique_type_override=versatility",
    }
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

LEGION_INT_TRINKET_IDS = [
    "133641",  # Eye of Skovald
    "133642",  # Horn of Valor
    # "136715",  # Spiked Counterweight
    "136716",  # Caged Horror
    "137301",  # Corrupted Starlight
    "137306",  # Oakheart's Gnarled Root
    "137329",  # Figurehead of the Naglfar
    "137349",  # Naraxas' Spiked Tongue
    # "137357",  # Mark of Dargrul
    "137367",  # Stormsinger Fulmination Charge
    # "137369",  # Giant Ornamental Pearl
    "137398",  # Portable Manacracker
    # "137406",  # Terrorbound Nexus
    "137419",  # Chrono Shard
    "137433",  # Obelisk of the Void
    # "137439",  # Tiny Oozeling in a Jar
    "137446",  # Elementium Bomb Squirrel Generator
    # "137459",  # Chaos Talisman
    "137485",  # Infernal Writ
    # "137486",  # Windscar Whetstone
    # "137539",  # Faulty Countermeasure
    "137541",  # Moonlit Prism
    "142157",  # Aran's Relaxing Ruby
    "142160",  # Mrrgria's Favor
    "142164",  # Toe Knee's Promise
    "142165",  # Deteriorated Construct Core
    "144480",  # Dreadstone of Endless Shadows
    "151310",  # Reality Breacher
    # "137312",  # Nightmare Egg Shell
]

LEGION_STR_TRINKET_IDS = [
    # "133641",  # Eye of Skovald    https://www.wowhead.com/item=133641
    "133642",  # Horn of Valor    https://www.wowhead.com/item=133642
    "136715",  # Spiked Counterweight    https://www.wowhead.com/item=136715
    # "136716",  # Caged Horror    https://www.wowhead.com/item=136716
    # "137301",  # Corrupted Starlight    https://www.wowhead.com/item=137301
    # "137306",  # Oakheart's Gnarled Root    https://www.wowhead.com/item=137306
    # "137329",  # Figurehead of the Naglfar    https://www.wowhead.com/item=137329
    # "137349",  # Naraxas' Spiked Tongue    https://www.wowhead.com/item=137349
    "137357",  # Mark of Dargrul    https://www.wowhead.com/item=137357
    # "137367",  # Stormsinger Fulmination Charge    https://www.wowhead.com/item=137367
    # "137369",  # Giant Ornamental Pearl    https://www.wowhead.com/item=137369
    "137398",  # Portable Manacracker    https://www.wowhead.com/item=137398
    "137406",  # Terrorbound Nexus    https://www.wowhead.com/item=137406
    "137419",  # Chrono Shard    https://www.wowhead.com/item=137419
    # "137433",  # Obelisk of the Void    https://www.wowhead.com/item=137433
    "137439",  # Tiny Oozeling in a Jar    https://www.wowhead.com/item=137439
    # "137446",  # Elementium Bomb Squirrel Generator    https://www.wowhead.com/item=137446
    "137459",  # Chaos Talisman    https://www.wowhead.com/item=137459
    # "137485",  # Infernal Writ    https://www.wowhead.com/item=137485
    "137486",  # Windscar Whetstone    https://www.wowhead.com/item=137486
    "137539",  # Faulty Countermeasure    https://www.wowhead.com/item=137539
    # "137541",  # Moonlit Prism    https://www.wowhead.com/item=137541
    # "142157",  # Aran's Relaxing Ruby    https://www.wowhead.com/item=142157
    "142160",  # Mrrgria's Favor    https://www.wowhead.com/item=142160
    "142164",  # Toe Knee's Promise    https://www.wowhead.com/item=142164
    # "142165",  # Deteriorated Construct Core    https://www.wowhead.com/item=142165
    # "144480",  # Dreadstone of Endless Shadows    https://www.wowhead.com/item=144480
    # "151310",  # Reality Breacher    https://www.wowhead.com/item=151310
    "137312",  # Nightmare Egg Shell
]

LEGION_AGI_TRINKET_IDS = [
    # "133641",  # Eye of Skovald    https://www.wowhead.com/item=133641
    "133642",  # Horn of Valor    https://www.wowhead.com/item=133642
    "136715",  # Spiked Counterweight    https://www.wowhead.com/item=136715
    # "136716",  # Caged Horror    https://www.wowhead.com/item=136716
    # "137301",  # Corrupted Starlight    https://www.wowhead.com/item=137301
    # "137306",  # Oakheart's Gnarled Root    https://www.wowhead.com/item=137306
    # "137329",  # Figurehead of the Naglfar    https://www.wowhead.com/item=137329
    # "137349",  # Naraxas' Spiked Tongue    https://www.wowhead.com/item=137349
    "137357",  # Mark of Dargrul    https://www.wowhead.com/item=137357
    # "137367",  # Stormsinger Fulmination Charge    https://www.wowhead.com/item=137367
    # "137369",  # Giant Ornamental Pearl    https://www.wowhead.com/item=137369
    "137398",  # Portable Manacracker    https://www.wowhead.com/item=137398
    "137406",  # Terrorbound Nexus    https://www.wowhead.com/item=137406
    "137419",  # Chrono Shard    https://www.wowhead.com/item=137419
    "137433",  # Obelisk of the Void    https://www.wowhead.com/item=137433
    "137439",  # Tiny Oozeling in a Jar    https://www.wowhead.com/item=137439
    # "137446",  # Elementium Bomb Squirrel Generator    https://www.wowhead.com/item=137446
    "137459",  # Chaos Talisman    https://www.wowhead.com/item=137459
    # "137485",  # Infernal Writ    https://www.wowhead.com/item=137485
    "137486",  # Windscar Whetstone    https://www.wowhead.com/item=137486
    "137539",  # Faulty Countermeasure    https://www.wowhead.com/item=137539
    "137541",  # Moonlit Prism    https://www.wowhead.com/item=137541
    # "142157",  # Aran's Relaxing Ruby    https://www.wowhead.com/item=142157
    "142160",  # Mrrgria's Favor    https://www.wowhead.com/item=142160
    "142164",  # Toe Knee's Promise    https://www.wowhead.com/item=142164
    "142165",  # Deteriorated Construct Core    https://www.wowhead.com/item=142165
    # "144480",  # Dreadstone of Endless Shadows    https://www.wowhead.com/item=144480
    # "151310",  # Reality Breacher    https://www.wowhead.com/item=151310
    "137537",  # Tirathon's Betrayal    https://www.wowhead.com/item=137537
    "137312",  # Nightmare Egg Shell
]

OBSOLETE = [
    "185818",  # So'leah's Secret Technique pre 9.2 version
    "178850",
    "180119",
    "178810",
    "178783",
    "184056",
    "186429",
    "186435",
    "186425",
    "186436",
    "178770",
]


def _is_valid_itemlevel(itemlevel: int, settings: Config) -> bool:
    return itemlevel >= settings.min_ilevel and itemlevel <= settings.max_ilevel


def _get_trinkets(wow_spec: WowSpec, settings: Config) -> typing.List[Trinket]:
    # get main-trinkets
    trinket_list = list(get_trinkets_for_spec(wow_spec))
    # filter trinket list by available itemlevels:
    trinket_list = list(
        filter(
            lambda trinket: any(
                map(
                    lambda ilevel: _is_valid_itemlevel(ilevel, settings),
                    trinket.itemlevels,
                )
            ),
            trinket_list,
        )
    )
    trinket_list = [
        t for t in trinket_list if str(t.item_id) not in OBSOLETE + NON_DPS_TRINKET_IDS
    ]
    if wow_spec.stat == Stat.INTELLECT:
        trinket_list = [
            t
            for t in trinket_list
            if t.expansion_id != 6 or t.item_id in LEGION_INT_TRINKET_IDS
        ]
    elif wow_spec.stat == Stat.AGILITY:
        trinket_list = [
            t
            for t in trinket_list
            if t.expansion_id != 6 or t.item_id in LEGION_AGI_TRINKET_IDS
        ]
    elif wow_spec.stat == Stat.STRENGTH:
        trinket_list = [
            t
            for t in trinket_list
            if t.expansion_id != 6 or t.item_id in LEGION_STR_TRINKET_IDS
        ]
    # print("=" * 30)
    # for trinket in trinket_list:
    #     if trinket.expansion_id == 6:
    #         print(
    #             f'"{trinket.item_id}", # {trinket.full_name}    https://www.wowhead.com/item={trinket.item_id}'
    #         )
    return trinket_list


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

            for stat in SOLEAHS_SPECIAL_CASES.get(trinket.item_id, {}).keys():
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

        return data_dict

    def add_simulation_data(
        self, simulation_group: Simulation_Group, data_dict: dict
    ) -> None:

        simulation_data = Simulation_Data(
            name=self.profile_split_character().join(
                ["baseline", str(self.settings.min_ilevel)]
            ),
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

        trinket_list = _get_trinkets(self.wow_spec, self.settings)

        for trinket in trinket_list:
            # for each available itemlevel of the trinket
            itemlevels = list(
                filter(
                    lambda x: _is_valid_itemlevel(x, self.settings), trinket.itemlevels
                )
            )
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
                        new_data.name = self.profile_split_character().join(
                            [f"{trinket.name} [{stat.title()}]", str(itemlevel)]
                        )

                        simulation_group.add(new_data)

                if trinket.item_id in SOLEAHS_SPECIAL_CASES.keys():
                    raw_profile = simulation_group.profiles.pop(-1)
                    for stat in SOLEAHS_SPECIAL_CASES[trinket.item_id]:
                        new_data = raw_profile.copy()
                        new_data.simc_arguments.append(
                            SOLEAHS_SPECIAL_CASES[trinket.item_id][stat]
                        )
                        new_data.name = self.profile_split_character().join(
                            [f"{trinket.name} [{stat.title()}]", str(itemlevel)]
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

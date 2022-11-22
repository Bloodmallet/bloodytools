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

logger = logging.getLogger(__name__)

# special cases
SPECIAL_CASE_BONUS_IDS = {
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

    trinket_list = [t for t in trinket_list if Season.SEASON_1 in t.seasons]

    # filter trinket list by available itemlevels:
    trinket_list = [
        t
        for t in trinket_list
        if any([_is_valid_itemlevel(ilevel, settings) for ilevel in t.itemlevels])
    ]

    trinket_list = [
        t for t in trinket_list if str(t.item_id) not in NON_DPS_TRINKET_IDS
    ]
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
            itemlevels = [
                i for i in trinket.itemlevels if _is_valid_itemlevel(i, self.settings)
            ]
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

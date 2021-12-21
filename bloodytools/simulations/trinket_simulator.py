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


def _is_valid_itemlevel(itemlevel: int, settings: Config) -> bool:
    return itemlevel >= settings.min_ilevel and itemlevel <= settings.max_ilevel


def _get_trinkets(wow_spec: WowSpec, settings: Config) -> typing.List[Trinket]:
    # get main-trinkets
    trinket_list = get_trinkets_for_spec(wow_spec)
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

            if trinket.item_id in SPECIAL_CASE_BONUS_IDS:
                for stat in SPECIAL_CASE_BONUS_IDS[trinket.item_id].keys():
                    tmp_name = f"{trinket.name} [{stat.title()}]"
                    data_dict["translations"][
                        tmp_name
                    ] = trinket.translations.get_dict()
                    for key in data_dict["translations"][tmp_name]:
                        data_dict["translations"][tmp_name][key] = (
                            data_dict["translations"][tmp_name][key] + f" {stat}"
                        )
                    data_dict["data"][tmp_name] = {}
                    data_dict["data_active"][tmp_name] = trinket.on_use
                    data_dict["data_sources"][tmp_name] = trinket.source.value
                    data_dict["item_ids"][tmp_name] = trinket.item_id

        # add itemlevel list
        data_dict["simulated_steps"] = []
        for trinket in trinket_list:
            for itemlevel in filter(
                lambda x: _is_valid_itemlevel(x, self.settings), trinket.itemlevels
            ):
                data_dict["simulated_steps"].append(itemlevel)

        data_dict["simulated_steps"] = sorted(list(set(data_dict["simulated_steps"])))

        # change order from ascending to descending to keep the order of previous versions
        data_dict["simulated_steps"].sort(reverse=True)

        return data_dict

    def add_simulation_data(
        self, simulation_group: Simulation_Group, data_dict: dict
    ) -> None:

        simulation_data = Simulation_Data(
            name="baseline_{}".format(self.settings.min_ilevel),
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
            for itemlevel in filter(
                lambda x: _is_valid_itemlevel(x, self.settings), trinket.itemlevels
            ):
                simulation_data = Simulation_Data(
                    name="{}_{}".format(trinket.name, itemlevel),
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
                        new_data.name = f"{trinket.name} [{stat.title()}] {itemlevel}"

                        simulation_group.add(new_data)

    def post_processing(self, data_dict: dict) -> dict:
        data_dict = super().post_processing(data_dict)

        # create ordered trinket name list
        tmp_list = []
        for trinket in data_dict["data"]:
            if trinket != "baseline":
                tmp_list.append((trinket, max(data_dict["data"][trinket].values())))
        logger.debug("tmp_list: {}".format(tmp_list))

        tmp_list = sorted(tmp_list, key=lambda item: item[1], reverse=True)
        logger.debug("Sorted tmp_list: {}".format(tmp_list))

        logger.info(
            "Trinket {} won with {} dps.".format(tmp_list[0][0], tmp_list[0][1])
        )

        data_dict["sorted_data_keys"] = [trinket for trinket, _ in tmp_list]

        return data_dict

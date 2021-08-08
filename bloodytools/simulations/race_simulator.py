import logging
import typing

from bloodytools.simulations.simulator import Simulator
from bloodytools.utils.simulation_objects import Simulation_Data, Simulation_Group
from bloodytools.utils.config import Config
from simc_support.game_data.WowSpec import WowSpec

logger = logging.getLogger(__name__)


class RaceSimulator(Simulator):
    def __init__(self, wow_spec: WowSpec, fight_style: str, settings: Config) -> None:
        super().__init__(
            name="Races",
            snake_case_name="races",
            wow_spec=wow_spec,
            fight_style=fight_style,
            settings=settings,
        )

    def add_simulation_data(
        self,
        simulation_group: Simulation_Group,
        profile: dict,
        additional_profiles: typing.Optional[dict],
    ) -> None:

        for race in self.wow_spec.wow_class.races:
            simulation_data = Simulation_Data(
                name=race.full_name,
                fight_style=self.fight_style,
                profile=profile,
                simc_arguments=["race={}".format(race.simc_name)],
                target_error=self.settings.target_error.get(self.fight_style, "0.1"),
                ptr=self.settings.ptr,
                default_actions=self.settings.default_actions,
                executable=self.settings.executable,
                iterations=self.settings.iterations,
                remove_files=not self.settings.keep_files,
            )

            if race == self.wow_spec.wow_class.races[0]:
                custom_apl = None
                if self.settings.custom_apl:
                    with open("custom_apl.txt") as f:
                        custom_apl = f.read()
                if custom_apl:
                    simulation_data.simc_arguments.append("# custom_apl")
                    simulation_data.simc_arguments.append(custom_apl)

                custom_fight_style = None
                if self.settings.custom_fight_style:
                    with open("custom_fight_style.txt") as f:
                        custom_fight_style = f.read()
                if custom_fight_style:
                    simulation_data.simc_arguments.append("# custom_fight_style")
                    simulation_data.simc_arguments.append(custom_fight_style)

            if race.simc_name == "zandalari_troll":
                simulation_data.simc_arguments.append("zandalari_loa=kimbul")
                simulation_data.name += " Kimbul"

                # add additional zandalari profiles
                for loa in ["bwonsamdi", "paku"]:
                    tmp_data = simulation_data.copy()
                    tmp_data.name = f"{race.full_name} {loa.title()}"
                    tmp_data.simc_arguments += [f"zandalari_loa={loa}"]

                    simulation_group.add(tmp_data)

            simulation_group.add(simulation_data)

    def post_processing(self, data_dict: dict) -> dict:
        data = super().post_processing(data_dict)

        # add translations
        for race in self.wow_spec.wow_class.races:
            data["translations"][race.full_name] = race.translations.get_dict()

            if "Zandalari" in race.full_name:

                loas = filter(lambda name: race.full_name in name, data["data"].keys())

                for full_name in loas:
                    loa = full_name.split(" ")[-1]
                    data["translations"][full_name] = race.translations.get_dict()
                    for lang in data["translations"][full_name]:
                        data["translations"][full_name][lang] = " ".join(
                            [
                                data["translations"][full_name][lang],
                                loa,
                            ]
                        )

        # create sorted list
        tmp_list = [(race, data["data"][race]) for race in data["data"]]
        logger.debug("tmp_list: {}".format(tmp_list))

        tmp_list = sorted(tmp_list, key=lambda item: item[1], reverse=True)
        logger.debug("Sorted tmp_list: {}".format(tmp_list))
        logger.info("Race {} won with {} dps.".format(tmp_list[0][0], tmp_list[0][1]))

        data["sorted_data_keys"] = [race for race, _ in tmp_list]

        return data

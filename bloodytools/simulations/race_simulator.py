import logging

from bloodytools.simulations.simulator import Simulator
from bloodytools.utils.simulation_objects import Simulation_Data, Simulation_Group

logger = logging.getLogger(__name__)


class RaceSimulator(Simulator):
    @classmethod
    def name(cls) -> str:
        return "Races"

    def add_simulation_data(
        self,
        simulation_group: Simulation_Group,
        data_dict: dict,
    ) -> None:
        profile = data_dict["profile"]

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
        data_dict = super().post_processing(data_dict)

        # add translations
        for race in self.wow_spec.wow_class.races:
            data_dict["translations"][race.full_name] = race.translations.get_dict()

            if "Zandalari" in race.full_name:
                loas = filter(
                    lambda name: race.full_name in name, data_dict["data"].keys()
                )

                for full_name in loas:
                    loa = full_name.split(" ")[-1]
                    data_dict["translations"][full_name] = race.translations.get_dict()
                    for lang in data_dict["translations"][full_name]:
                        data_dict["translations"][full_name][lang] = " ".join(
                            [
                                data_dict["translations"][full_name][lang],
                                loa,
                            ]
                        )

        data_dict = self.create_sorted_key_value_data(data_dict)

        return data_dict

import logging
import typing

from bloodytools.simulations.simulator import Simulator
from bloodytools.utils.simulation_objects import Simulation_Data, Simulation_Group


logger = logging.getLogger(__name__)

pots: typing.Dict[str, str] = {
    # pots
    "Potion of Frozen Fatality": "",
    "Bottled Putrescence": "",
    "Residual Neural Channeling Agent": "",
    "Elemental Potion of Ultimate Power": "",
    "Elemental Potion of Power": "",
    "Potion of Shocking Disclosure": "",
}

phials: typing.Dict[str, str] = {
    # phials
    # "Phial of the Eye in the Storm": "",
    # "Iced Phial of Corrupting Rage": "",
    # "Phial of Charged Isolation": "",
    # "Phial of Glacial Fury": "",
    # "Phial of Static Empowerment": "",
    # "Phial of Tepid Versatility": "",
    # "Charged Phial of Alacrity": "",
    # "Phial of Elemental Chaos": "",
}


class ConsumableSimulator(Simulator):
    @classmethod
    def name(cls) -> str:
        return "Consumables"

    def add_simulation_data(
        self,
        simulation_group: Simulation_Group,
        data_dict: dict,
    ) -> None:
        profile = data_dict["profile"]

        # potion=elemental_potion_of_ultimate_power_3
        # flask=phial_of_static_empowerment_3

        consumables = {**pots, **phials}

        for name, simc_string in consumables.items():
            if not simc_string:
                simc_string = "potion=" if name in pots else "flask="
                simc_string += name.lower().replace(" ", "_")

                simc_string += "_3"

            simulation_data = Simulation_Data(
                name=name,
                fight_style=self.fight_style,
                profile=profile,
                simc_arguments=[simc_string],
                target_error=self.settings.target_error.get(self.fight_style, "0.1"),
                ptr=self.settings.ptr,
                default_actions=self.settings.default_actions,
                executable=self.settings.executable,
                iterations=self.settings.iterations,
                remove_files=not self.settings.keep_files,
            )

            if (name, simc_string) == list(consumables.items())[0]:
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

            simulation_group.add(simulation_data)

    def post_processing(self, data_dict: dict) -> dict:
        data_dict = super().post_processing(data_dict)

        data_dict = self.create_sorted_key_value_data(data_dict)

        return data_dict

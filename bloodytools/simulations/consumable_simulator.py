import abc
import dataclasses
import logging
import typing

from bloodytools.simulations.simulator import Simulator
from bloodytools.utils.simulation_objects import Simulation_Data, Simulation_Group


logger = logging.getLogger(__name__)


class ConsumableSimulator(Simulator, abc.ABC):
    """Abstract base simulator for consumables."""

    @abc.abstractmethod
    def consumables(self) -> typing.Dict[str, str]:
        """Dictionary of all consumables to be simmed this way.

        Returns:
            typing.Dict[str, str]: human-readable name: simc-arg
        """
        ...

    @abc.abstractmethod
    def item_ids(self) -> typing.Dict[str, str]:
        """Dictionary of all consumables to be simmed this way. Contains item ids

        Returns:
            typing.Dict[str, int]: human-readable name: item-id
        """
        ...

    @abc.abstractmethod
    def simc_key(self) -> str:
        """Key describing the thing in simc. E.g. "head=" for a head piece."""
        ...

    @property
    def max_rank(self) -> int:
        return 3

    def get_simulation_steps(self) -> typing.List[int]:
        return list(range(1, self.max_rank + 1))

    def add_simulation_data(
        self,
        simulation_group: Simulation_Group,
        data_dict: dict,
    ) -> None:
        profile = data_dict["profile"]

        simulation_data = Simulation_Data(
            name=self.get_profile_name("baseline", str(1)),
            fight_style=self.fight_style,
            profile=profile,
            simc_arguments=[self.simc_key() + "disabled"],
            target_error=self.settings.target_error.get(self.fight_style, "0.1"),
            ptr=self.settings.ptr,
            default_actions=self.settings.default_actions,
            executable=self.settings.executable,
            iterations=self.settings.iterations,
            remove_files=not self.settings.keep_files,
        )

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

        # potion=elemental_potion_of_ultimate_power_3
        # flask=phial_of_static_empowerment_3

        for name, simc_string in self.consumables().items():
            # if simc_arg is not provided, create it
            if not simc_string:
                simc_string = self.simc_key()
                simc_string += name.lower().replace(" ", "_")

            for rank in self.get_simulation_steps():
                scaled_name = self.get_profile_name(name, str(rank))
                scaled_simc_string = f"{simc_string}_{rank}"

                simulation_data = Simulation_Data(
                    name=scaled_name,
                    fight_style=self.fight_style,
                    profile=profile,
                    simc_arguments=[scaled_simc_string],
                    target_error=self.settings.target_error.get(
                        self.fight_style, "0.1"
                    ),
                    ptr=self.settings.ptr,
                    default_actions=self.settings.default_actions,
                    executable=self.settings.executable,
                    iterations=self.settings.iterations,
                    remove_files=not self.settings.keep_files,
                )

                simulation_group.add(simulation_data)

    def post_processing(self, data_dict: dict) -> dict:
        data_dict = super().post_processing(data_dict)

        data_dict["simulated_steps"] = sorted(self.get_simulation_steps(), reverse=True)

        data_dict = self.create_sorted_key_key_value_data(data_dict)

        data_dict["item_ids"] = self.item_ids()

        return data_dict


class PotionSimulator(ConsumableSimulator):
    @classmethod
    def name(cls) -> str:
        return "Potions"

    def simc_key(self) -> str:
        return "potion="

    def consumables(self) -> typing.Dict[str, str]:
        return {
            # breaks simc
            # Unable to initialize consumable 'potion' from 'potion_of_frozen_fatality_3': Unable to find consumable.
            # "Potion of Frozen Fatality": "",
            "Bottled Putrescence": "",
            # Unable to initialize consumable 'potion' from 'residual_neural_channeling_agent_3': Unable to find consumable.
            # "Residual Neural Channeling Agent": "",
            "Elemental Potion of Ultimate Power": "",
            "Elemental Potion of Power": "",
            "Potion of Shocking Disclosure": "",
        }

    def item_ids(self) -> typing.Dict[str, str]:
        return {
            # breaks simc
            # Unable to initialize consumable 'potion' from 'potion_of_frozen_fatality_3': Unable to find consumable.
            # "Potion of Frozen Fatality": "",
            "Bottled Putrescence": "191360",
            # Unable to initialize consumable 'potion' from 'residual_neural_channeling_agent_3': Unable to find consumable.
            # "Residual Neural Channeling Agent": "",
            "Elemental Potion of Ultimate Power": "191381",
            "Elemental Potion of Power": "191387",
            "Potion of Shocking Disclosure": "191399",
        }


class PhialSimulator(ConsumableSimulator):
    @classmethod
    def name(cls) -> str:
        return "Phials"

    def simc_key(self) -> str:
        return "flask="

    def consumables(self) -> typing.Dict[str, str]:
        return {
            # Unable to initialize consumable 'flask' from 'phial_of_the_eye_in_the_storm_3': First special effect initialization phase could not deduce a proper consumable to create.
            # "Phial of the Eye in the Storm": "",
            "Iced Phial of Corrupting Rage": "",
            "Phial of Charged Isolation": "",
            "Phial of Glacial Fury": "",
            "Phial of Static Empowerment": "",
            "Phial of Tepid Versatility": "",
            # "Charged Phial of Alacrity": "",
            "Phial of Elemental Chaos": "",
        }

    def item_ids(self) -> typing.Dict[str, str]:
        return {
            # Unable to initialize consumable 'flask' from 'phial_of_the_eye_in_the_storm_3': First special effect initialization phase could not deduce a proper consumable to create.
            # "Phial of the Eye in the Storm": "",
            "Iced Phial of Corrupting Rage": "191327",
            "Phial of Charged Isolation": "191330",
            "Phial of Glacial Fury": "191333",
            "Phial of Static Empowerment": "191336",
            "Phial of Tepid Versatility": "191339",
            # "Charged Phial of Alacrity": "191348",
            "Phial of Elemental Chaos": "191357",
        }

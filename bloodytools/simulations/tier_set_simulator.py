from bloodytools.utils.simulation_objects import Simulation_Data, Simulation_Group
from .simulator import Simulator


class TierSetSimulator(Simulator):
    @classmethod
    @property
    def name(cls) -> str:
        return "Tier Set"

    def add_simulation_data(
        self, simulation_group: Simulation_Group, data_dict: dict
    ) -> None:
        tier_mapping = {
            "no tier": [
                "set_bonus=tier28_2pc=0",
                "set_bonus=tier28_4pc=0",
            ],
            "2p": [
                "set_bonus=tier28_2pc=1",
                "set_bonus=tier28_4pc=0",
            ],
            "4p": [
                "set_bonus=tier28_2pc=1",
                "set_bonus=tier28_4pc=1",
            ],
        }

        for tier, simc_input in tier_mapping.items():
            spec = str(self.wow_spec).replace("_", " ")
            data = Simulation_Data(
                name=f"{spec}_{tier}",
                simc_arguments=simc_input,
                fight_style=self.fight_style,
                profile=data_dict["profile"],
                target_error=self.settings.target_error.get(self.fight_style, "0.1"),
                ptr=self.settings.ptr,
                default_actions=self.settings.default_actions,
                executable=self.settings.executable,
                iterations=self.settings.iterations,
            )

            simulation_group.add(data)

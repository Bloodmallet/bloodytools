from bloodytools.utils.simulation_objects import Simulation_Data, Simulation_Group
from .simulator import Simulator


class TierSetSimulator(Simulator):
    @classmethod
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
                name=self.profile_split_character().join([spec, tier]),
                simc_arguments=simc_input,
                fight_style=self.fight_style,
                profile=data_dict["profile"],
                target_error=self.settings.target_error.get(self.fight_style, "0.1"),
                ptr=self.settings.ptr,
                default_actions=self.settings.default_actions,
                executable=self.settings.executable,
                iterations=self.settings.iterations,
            )

            if tier == "no tier":
                custom_apl = None
                if self.settings.custom_apl:
                    with open("custom_apl.txt") as f:
                        custom_apl = f.read()
                if custom_apl:
                    data.simc_arguments.append("# custom_apl")
                    data.simc_arguments.append(custom_apl)

                custom_fight_style = None
                if self.settings.custom_fight_style:
                    with open("custom_fight_style.txt") as f:
                        custom_fight_style = f.read()
                if custom_fight_style:
                    data.simc_arguments.append("# custom_fight_style")
                    data.simc_arguments.append(custom_fight_style)

            simulation_group.add(data)

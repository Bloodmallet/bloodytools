from bloodytools.utils.simulation_objects import Simulation_Data, Simulation_Group
from .simulator import Simulator
from simc_support.game_data.Covenant import get_covenant


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
            for covenant_name, covenant_profile in data_dict[
                "covenant_profiles"
            ].items():
                covenant = get_covenant(name=covenant_name)
                data = Simulation_Data(
                    name=self.profile_split_character().join(
                        [covenant.full_name, tier]
                    ),
                    simc_arguments=simc_input,
                    fight_style=self.fight_style,
                    profile=covenant_profile,
                    target_error=self.settings.target_error.get(
                        self.fight_style, "0.1"
                    ),
                    ptr=self.settings.ptr,
                    default_actions=self.settings.default_actions,
                    executable=self.settings.executable,
                    iterations=self.settings.iterations,
                )

                if len(simulation_group.profiles) == 0:
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

    def post_processing(self, data_dict: dict) -> dict:
        data_dict = super().post_processing(data_dict)

        self.create_sorted_key_key_value_data(data_dict)

        return data_dict

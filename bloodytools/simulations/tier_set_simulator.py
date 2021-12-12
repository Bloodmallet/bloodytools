import typing
from simc_support.game_data.WowSpec import WowSpec
from simc_support.game_data.WowSpec import WOWSPECS
from bloodytools.utils.config import Config

from bloodytools.utils.simulation_objects import Simulation_Data, Simulation_Group
from .simulator import Simulator
from bloodytools.utils.utils import get_profile


class TierSetSimulator(Simulator):
    def __init__(self, wow_spec: WowSpec, fight_style: str, settings: Config) -> None:
        super().__init__(
            name="Tier Set",
            snake_case_name="tier_set",
            wow_spec=wow_spec,
            fight_style=fight_style,
            settings=settings,
        )

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

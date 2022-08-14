import json
import logging
import os
import typing
import pkg_resources
import yaml

from bloodytools.utils.simulation_objects import Simulation_Data, Simulation_Group
from bloodytools.utils.utils import create_base_json_dict
from simc_support.game_data.Talent import get_talents_for_spec
from simc_support.game_data.WowSpec import WowSpec, get_wow_spec
from bloodytools.simulations.simulator import Simulator

logger = logging.getLogger(__name__)


class TalentSimulator(Simulator):
    @classmethod
    def name(cls) -> str:
        return "Talents"

    def pre_processing(self, data_dict: dict) -> dict:
        data_dict = super().pre_processing(data_dict)

        # load predefined talent paths from file
        file_path = os.path.join(
            "talent_tree_paths",
            f"{self.wow_spec.wow_class.simc_name}_{self.wow_spec.simc_name}.yaml",
        )
        try:
            with pkg_resources.resource_stream(__name__, file_path) as f:
                data_dict["data_profile_overrides"] = yaml.safe_load(f)
        except FileNotFoundError as e:
            logger.warning(e)
            data_dict["data_profile_overrides"] = {}

        return data_dict

    def add_simulation_data(
        self, simulation_group: Simulation_Group, data_dict: dict
    ) -> None:
        logger.debug("talent_simulations start")

        for i, k_v in enumerate(data_dict["data_profile_overrides"].items()):
            human_name, simc_args = k_v

            if i == 0:
                profile = data_dict["profile"]
            else:
                profile = {}

            profile = Simulation_Data(
                name=human_name,
                fight_style=self.fight_style,
                profile=profile,
                simc_arguments=simc_args,
                target_error=self.settings.target_error.get(self.fight_style, "0.1"),
                ptr=self.settings.ptr,
                default_actions=self.settings.default_actions,
                executable=self.settings.executable,
                iterations=self.settings.iterations,
            )

            if i == 0:
                if self.settings.custom_apl:
                    with open("custom_apl.txt") as f:
                        custom_apl = f.read()
                    profile.simc_arguments.append("# custom_apl")
                    profile.simc_arguments.append(custom_apl)

                if self.settings.custom_fight_style:
                    with open("custom_fight_style.txt") as f:
                        custom_fight_style = f.read()
                    profile.simc_arguments.append("# custom_fight_style")
                    profile.simc_arguments.append(custom_fight_style)

            simulation_group.add(profile)

    def post_processing(self, data_dict: dict) -> dict:
        data_dict = super().post_processing(data_dict)

        data_dict = self.create_sorted_key_value_data(data_dict)

        logger.debug("talent_simulations end")
        return data_dict

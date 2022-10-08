import logging
import os
import pkg_resources
import typing
import yaml

from bloodytools.utils.simulation_objects import Simulation_Data, Simulation_Group
from bloodytools.simulations.simulator import Simulator
from bloodytools.utils.utils import create_base_json_dict


logger = logging.getLogger(__name__)


class MissingTalentTreePathFileError(Exception):
    pass


KeyType = typing.TypeVar("KeyType")


def _deep_update(
    mapping: typing.Dict[KeyType, typing.Any],
    *updating_mappings: typing.Dict[KeyType, typing.Any],
) -> typing.Dict[KeyType, typing.Any]:
    updated_mapping = mapping.copy()
    for updating_mapping in updating_mappings:
        for k, v in updating_mapping.items():
            if (
                k in updated_mapping
                and isinstance(updated_mapping[k], dict)
                and isinstance(v, dict)
            ):
                updated_mapping[k] = _deep_update(updated_mapping[k], v)
            else:
                updated_mapping[k] = v
    return updated_mapping


class TalentTargetScalingSimulator(Simulator):
    @classmethod
    def name(cls) -> str:
        return "Talent Target Scaling"

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
            raise MissingTalentTreePathFileError() from e

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

                # need to disable this to not accidentally override desired target count
                # if self.settings.custom_fight_style:
                #     with open("custom_fight_style.txt") as f:
                #         custom_fight_style = f.read()
                #     profile.simc_arguments.append("# custom_fight_style")
                #     profile.simc_arguments.append(custom_fight_style)

            simulation_group.add(profile)

    def post_processing(self, data_dict: dict) -> dict:
        data_dict = super().post_processing(data_dict)

        data_dict = self.create_sorted_key_key_value_data(data_dict)

        logger.debug("talent_simulations end")
        return data_dict

    def run(self) -> None:
        """Manages the simulation flow. You can adjust by overwriting the provided methods."""
        logger.debug(f"Start pipeline for {self.name()} of {self.wow_spec}")
        data_dict = create_base_json_dict(
            self.name(), self.wow_spec, self.fight_style, self.settings
        )

        logger.debug("Starting pre processing")
        data_dict = self.pre_processing(data_dict)

        for target_count in [1, 2, 3, 4, 5, 6, 7, 10, 15]:
            simulation_group = Simulation_Group(
                name="simulation_group",
                threads=self.settings.threads,
                profileset_work_threads=self.settings.profileset_work_threads,
                executable=self.settings.executable,
                remove_files=not self.settings.keep_files,
            )
            self.add_simulation_data(
                simulation_group,
                data_dict,
            )

            for profile in simulation_group.profiles:
                profile.name = self.get_profile_name(profile.name, str(target_count))
                profile.simc_arguments.append(f"desired_targets={target_count}")

            logger.info(f"Simulating {target_count} targets.")
            self._simulate(simulation_group)

            if "data" not in data_dict:
                data_dict["data"] = {}

            data_dict["data"] = _deep_update(
                data_dict["data"],
                self._collect_data(simulation_group, self.settings.data_type),
            )

        logger.debug("Starting post processing")
        data_dict = self.post_processing(data_dict)

        self._write(data_dict)

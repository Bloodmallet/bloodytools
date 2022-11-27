import logging
import typing

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

        data_dict = self.get_additional_talent_paths(data_dict)

        return data_dict

    def add_simulation_data(
        self, simulation_group: Simulation_Group, data_dict: dict
    ) -> None:
        logger.debug("talent_simulations start")

        clear_talents = [
            "talents=",
            "spec_talents=",
            "class_talents=",
        ]

        for i, k_v in enumerate(data_dict["data_profile_overrides"].items()):
            human_name, simc_args = k_v

            if i == 0:
                profile = data_dict["profile"]
            else:
                profile = {}

            simulation_data = Simulation_Data(
                name=human_name,
                fight_style=self.fight_style,
                profile=profile,
                simc_arguments=clear_talents + simc_args,
                target_error=self.settings.target_error.get(self.fight_style, "0.1"),
                ptr=self.settings.ptr,
                default_actions=self.settings.default_actions,
                executable=self.settings.executable,
                iterations=self.settings.iterations,
            )

            # get talent string
            data_copy = simulation_data.copy()
            data_copy.iterations = "1"
            data_copy.simc_arguments = (
                data_copy.get_simc_arguments_from_profile(data_dict["profile"])
                + data_copy.simc_arguments
            )
            tmp_group = Simulation_Group(data_copy, name="extract_talents")
            tmp_group.simulate()
            if tmp_group.profiles[0].json_data:
                talents = "talents=" + self._get_talents(
                    tmp_group.profiles[0].json_data
                )
                if talents not in data_dict["data_profile_overrides"][human_name]:
                    data_dict["data_profile_overrides"][human_name].append(talents)

            if i == 0:
                if self.settings.custom_apl:
                    with open("custom_apl.txt") as f:
                        custom_apl = f.read()
                    simulation_data.simc_arguments.append("# custom_apl")
                    simulation_data.simc_arguments.append(custom_apl)

                # need to disable this to not accidentally override desired target count
                # if self.settings.custom_fight_style:
                #     with open("custom_fight_style.txt") as f:
                #         custom_fight_style = f.read()
                #     simulation_data.simc_arguments.append("# custom_fight_style")
                #     simulation_data.simc_arguments.append(custom_fight_style)

            simulation_group.add(simulation_data)

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

        for target_count in [1, 2, 3, 4, 5, 6, 8, 9, 15]:
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
                if profile == simulation_group.profiles[0]:
                    profile.simc_arguments.append(f"desired_targets={target_count}")

            logger.info(f"Simulating {target_count} targets.")
            self._simulate(simulation_group)

            if "data" not in data_dict:
                data_dict["data"] = {}

            data_dict["data"] = _deep_update(
                data_dict["data"],
                self._collect_data(simulation_group, self.settings.data_type),
            )

            if simulation_group.json_data:
                data_dict["profile"]["character"][
                    "talents"
                ] = simulation_group.json_data["sim"]["players"][0]["talents"]

        logger.debug("Starting post processing")
        data_dict = self.post_processing(data_dict)

        self._write(data_dict)

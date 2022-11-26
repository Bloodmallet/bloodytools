import logging
import os
import pkg_resources
import yaml

from bloodytools.utils.simulation_objects import Simulation_Data, Simulation_Group
from bloodytools.simulations.simulator import Simulator

logger = logging.getLogger(__name__)


class MissingTalentTreePathFileError(Exception):
    pass


class TalentRemovalSimulator(Simulator):
    @classmethod
    def name(cls) -> str:
        return "Talent Removal"

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

        if data_dict["data_profile_overrides"] is None:
            data_dict["data_profile_overrides"] = {}

        if "profile" in data_dict and "character" in data_dict["profile"]:
            if "talents" in data_dict["profile"]["character"]:
                data_dict["data_profile_overrides"]["custom_profile"] = [  # type: ignore
                    "talents=" + data_dict["profile"]["character"]["talents"]
                ]
            elif (
                "class_talents" in data_dict["profile"]["character"]
                and "spec_talents" in data_dict["profile"]["character"]
            ):
                data_dict["data_profile_overrides"]["custom_profile"] = [  # type: ignore
                    "class_talents="
                    + data_dict["profile"]["character"]["class_talents"],
                    "spec_talents=" + data_dict["profile"]["character"]["spec_talents"],
                ]

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

            simulation = Simulation_Data(
                name=self.get_profile_name(human_name, "baseline"),
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
                    simulation.simc_arguments.append("# custom_apl")
                    simulation.simc_arguments.append(custom_apl)

                if self.settings.custom_fight_style:
                    with open("custom_fight_style.txt") as f:
                        custom_fight_style = f.read()
                    simulation.simc_arguments.append("# custom_fight_style")
                    simulation.simc_arguments.append(custom_fight_style)

            simulation_group.add(simulation)

            # create simulations for each missing talent
            talent_strings = [
                args
                for args in simc_args
                if args.startswith("talents=")
                or args.startswith("class_talents=")
                or args.startswith("spec_talents=")
            ]
            other_args = [arg for arg in simc_args if arg not in talent_strings]
            for talent_string in talent_strings:
                other_talent_strings = [s for s in talent_strings if s != talent_string]
                prefix = talent_string.split("=")[0]
                cleaned_talents = talent_string.split("=")[1].split("#")[0].strip()
                talents = cleaned_talents.split("/")
                for talent in talents:
                    talent_id, invested_points = talent.split(":")
                    if int(invested_points) < 1:
                        continue

                    other_talents = [
                        t for t in talents if t != talent and int(t.split(":")[-1]) > 0
                    ]

                    active_talents = "=".join(
                        [
                            prefix,
                            "/".join(
                                other_talents
                                + [talent_id + ":" + str(int(invested_points) - 1)]
                            ),
                        ]
                    )
                    logger.debug(f"{active_talents=}")

                    # TODO: continue here. rebuild the current talent string, add other simc_args too
                    simulation = Simulation_Data(
                        name=self.get_profile_name(human_name, talent_id),
                        fight_style=self.fight_style,
                        profile=profile,
                        simc_arguments=other_talent_strings
                        + other_args
                        + [active_talents],
                        target_error=self.settings.target_error.get(
                            self.fight_style, "0.1"
                        ),
                        ptr=self.settings.ptr,
                        default_actions=self.settings.default_actions,
                        executable=self.settings.executable,
                        iterations=self.settings.iterations,
                    )
                    simulation_group.add(simulation)

    def post_processing(self, data_dict: dict) -> dict:
        data_dict = super().post_processing(data_dict)

        data_dict = self.create_sorted_key_key_value_data(data_dict)

        logger.debug("talent_simulations end")
        return data_dict

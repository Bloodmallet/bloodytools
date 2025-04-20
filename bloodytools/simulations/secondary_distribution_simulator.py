import itertools
import logging
import os
import typing

from bloodytools.simulations.simulator import Simulator
from bloodytools.utils.simulation_objects import (
    Simulation_Data,
    Simulation_Group,
    SimulationError,
)
from bloodytools.utils.profile_extraction import create_simc_profile_path

logger = logging.getLogger(__name__)


class TalentString:
    def __init__(self, string: str) -> None:
        self.string = string


class PlainTalentString(TalentString):
    def __str__(self) -> str:
        return f"talents={self.string}"


class ClassTalentString(TalentString):
    def __str__(self) -> str:
        return f"class_talents={self.string}"


class SpecTalentString(TalentString):
    def __str__(self) -> str:
        return f"spec_talents={self.string}"


class HeroTalentString(TalentString):
    def __str__(self) -> str:
        return f"hero_talents={self.string}"


class SecondaryDistributionSimulator(Simulator):
    @classmethod
    def name(cls) -> str:
        return "Secondary Distributions"

    def get_available_secondary_stats(self, data_dict: dict) -> int:
        secondary_amount = 0

        rating_names = [
            "crit_rating",
            "haste_rating",
            "mastery_rating",
            "versatility_rating",
        ]

        simulation = Simulation_Data(
            name="Grab dem secondary values",
            fight_style=self.fight_style,
            target_error=self.settings.target_error.get(self.fight_style, "0.1"),
            iterations="1",
            profile=data_dict["profile"],
            ptr=self.settings.ptr,
            default_actions=self.settings.default_actions,
            executable=self.settings.executable,
            generate_html=self.settings.html,
        )
        simulation.simc_arguments.append("# not-a-real-apl")
        # actions=auto_attack
        simulation.simc_arguments.append("actions=auto_attack")

        try:
            simulation.simulate()
        except SimulationError as e:
            if "unable to create action: auto_attack" in str(e.message):
                simulation.simc_arguments.pop()
                simulation.simc_arguments.pop()
                simulation.simulate()
            else:
                raise e

        stats = 0
        for stat in rating_names:
            if simulation.json_data:
                try:
                    stats += simulation.json_data["sim"]["players"][0][
                        "collected_data"
                    ]["buffed_stats"]["stats"][stat]
                except KeyError:
                    logger.warning(
                        f"Stat '{stat}' not found in single iteration simulation data while extracting secondary stats. Assuming 0."
                    )

        secondary_amount = int(stats)

        logger.debug("Extracted secondary_amount: {}".format(secondary_amount))

        return secondary_amount

    def pre_processing(self, data_dict: dict) -> dict:
        data_dict = super().pre_processing(data_dict)
        data_dict["secondary_sum"] = self.get_available_secondary_stats(data_dict)

        data_dict = self.get_additional_talent_paths(data_dict)

        return data_dict

    def add_simulation_data(
        self, simulation_group: Simulation_Group, data_dict: dict
    ) -> None:
        step_size = self.settings.secondary_distributions_step_size
        lower_threshold = 10  # percent
        upper_threshold = 70  # percent
        possible_steps = list(range(lower_threshold, upper_threshold + 1, step_size))
        step_combinations = itertools.product(possible_steps, repeat=4)
        distribution_multipliers = [
            combination for combination in step_combinations if sum(combination) == 100
        ]

        logger.debug(
            "'{}' different distributions generated.".format(
                len(distribution_multipliers)
            )
        )

        talent_combinations: typing.Dict[str, typing.Tuple[TalentString, ...]] = {}
        if "talents" in data_dict["profile"]["character"]:
            talent_combinations["baseline"] = (
                "talents=" + data_dict["profile"]["character"]["talents"],
            )
        else:
            combinations: typing.List[TalentString] = []
            if "class_talents" in data_dict["profile"]["character"]:
                combinations.append(
                    ClassTalentString(
                        data_dict["profile"]["character"]["class_talents"]
                    )
                )
            if "hero_talents" in data_dict["profile"]["character"]:
                combinations.append(
                    SpecTalentString(data_dict["profile"]["character"]["hero_talents"])
                )
            if "hero_talents" in data_dict["profile"]["character"]:
                combinations.append(
                    HeroTalentString(data_dict["profile"]["character"]["hero_talents"])
                )

            talent_combinations["baseline"] = tuple(combinations)

        if data_dict["data_profile_overrides"]:
            talent_combinations = {}

        for i, k_v in enumerate(data_dict["data_profile_overrides"].items()):
            human_name, simc_args = k_v
            if len(human_name) == 3 and human_name.startswith("T"):
                try:
                    int(human_name[1:])
                except ValueError:
                    pass
                else:
                    continue
            talent_combinations[human_name] = simc_args

        secondaries = data_dict["secondary_sum"]

        clear_talents = [
            "talents=",
            "spec_talents=",
            "class_talents=",
            "hero_talents=",
        ]

        for human_name, talent_combination in talent_combinations.items():
            for crit, haste, mastery, vers in distribution_multipliers:
                s_o = Simulation_Data(
                    name="{}{}{}_{}_{}_{}".format(
                        human_name,
                        self.profile_split_character(),
                        crit,
                        haste,
                        mastery,
                        vers,
                    ),
                    fight_style=self.fight_style,
                    target_error=self.settings.target_error.get(
                        self.fight_style, "0.1"
                    ),
                    iterations=self.settings.iterations,
                    profile=data_dict["profile"],
                    simc_arguments=[
                        *clear_talents,
                        *[str(part) for part in talent_combination],
                        "gear_crit_rating={}".format(int(secondaries * (crit / 100))),
                        "gear_haste_rating={}".format(int(secondaries * (haste / 100))),
                        "gear_mastery_rating={}".format(
                            int(secondaries * (mastery / 100))
                        ),
                        "gear_versatility_rating={}".format(
                            int(secondaries * (vers / 100))
                        ),
                    ],
                    ptr=self.settings.ptr,
                    default_actions=self.settings.default_actions,
                    executable=self.settings.executable,
                    generate_html=self.settings.html,
                )

                if (crit, haste, mastery, vers) == distribution_multipliers[0] and (
                    human_name,
                    talent_combination,
                ) == list(talent_combinations.items())[0]:
                    custom_apl = None
                    if self.settings.custom_apl:
                        with open("custom_apl.txt") as f:
                            custom_apl = f.readlines()
                    if custom_apl:
                        s_o.simc_arguments += ["# custom_apl"]
                        s_o.simc_arguments += custom_apl

                    custom_fight_style = None
                    if self.settings.custom_fight_style:
                        with open("custom_fight_style.txt") as f:
                            custom_fight_style = f.readlines()
                    if custom_fight_style:
                        s_o.simc_arguments += ["# custom_fight_style"]
                        s_o.simc_arguments += custom_fight_style

                simulation_group.add(s_o)

    def post_processing(self, data_dict: dict) -> dict:
        data_dict = super().post_processing(data_dict)

        data_dict.pop("covenant_profiles", None)

        # create ordered name list
        data_dict["sorted_data_keys"] = {}
        for talent_combination in data_dict["data"].keys():
            tmp_list: typing.List[typing.Tuple[str, int]] = []
            for distribution in data_dict["data"][talent_combination]:
                tmp_list.append(
                    (
                        distribution,
                        data_dict["data"][talent_combination][distribution],
                    )
                )
            logger.debug("tmp_list: {}".format(tmp_list))
            tmp_list = sorted(tmp_list, key=lambda item: item[1], reverse=True)
            logger.debug("Sorted tmp_list: {}".format(tmp_list))
            data_dict["sorted_data_keys"][talent_combination] = [
                distribution for distribution, _ in tmp_list
            ]

        if self.settings.write_humanreadable_secondary_distribution_file:
            human_text: typing.List[str] = []
            for talent_combination in data_dict["data"]:
                dps_dict = data_dict["data"][talent_combination]
                ordered_dps: typing.List[typing.Tuple[str, int]] = sorted(
                    list(dps_dict.items()), key=lambda pair: pair[1], reverse=True
                )
                human_text += [
                    f"Sorted secondary distribution list for {talent_combination} (max:{ordered_dps[0][1]}):",
                    "  c  h  m  v    dps",
                ]

                for pair in ordered_dps:
                    # c_h_m_v dps dps%
                    human_text += [
                        "  {}   {:>5}  {:>6.2f}%".format(
                            pair[0],
                            pair[1],
                            round(pair[1] * 100 / ordered_dps[0][1], 2),
                        )
                    ]

            # create directory if it doesn't exist
            path = "results/secondary_distributions/"
            if not os.path.isdir(path):
                os.makedirs(path)

            with open(
                "results/secondary_distributions/{}_{}_{}.txt".format(
                    self.wow_spec.wow_class.simc_name,
                    self.wow_spec.simc_name,
                    self.fight_style.lower(),
                ),
                "w",
            ) as f:
                f.write("\n".join(human_text))

        return data_dict

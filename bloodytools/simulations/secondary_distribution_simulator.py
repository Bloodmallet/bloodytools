from bloodytools.utils.config import Config
import itertools
import json
import logging
import os
from typing import List
from simc_support.game_data.WowSpec import WowSpec

from bloodytools.utils.simulation_objects import Simulation_Data
from bloodytools.utils.simulation_objects import Simulation_Group
from bloodytools.utils.utils import create_base_json_dict
from bloodytools.utils.utils import create_basic_profile_string
from bloodytools.simulations.simulator import Simulator

logger = logging.getLogger(__name__)


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

        # get secondary sum from profile
        lines = None
        try:
            with open(
                create_basic_profile_string(
                    self.wow_spec, self.settings.tier, self.settings
                ),
                "r",
            ) as f:
                lines = f.readlines()
        except FileNotFoundError:
            logger.warning(f"{self.wow_spec} profile not found. Skipping.")

        if lines:
            for line in lines:
                for rating_name in rating_names:
                    combined_rating_name = f"gear_{rating_name}="
                    if combined_rating_name in line:
                        secondary_amount += int(
                            line.split(combined_rating_name)[1].strip()
                        )

        if self.settings.custom_profile:
            simulation = Simulation_Data(
                name="Grab dem secondary values",
                fight_style=self.fight_style,
                target_error=self.settings.target_error.get(self.fight_style, "0.1"),
                iterations="1",
                profile=data_dict["profile"],
                ptr=self.settings.ptr,
                default_actions=self.settings.default_actions,
                executable=self.settings.executable,
            )
            simulation.simulate()

            stats = 0
            for stat in rating_names:
                try:
                    stats += simulation.json_data["sim"]["players"][0][
                        "collected_data"
                    ]["buffed_stats"]["stats"][stat]
                except KeyError:
                    logger.warning(
                        f"Stat '{stat}' not found in single iteration simulation data while extracting secondary stats."
                    )

            secondary_amount = int(stats)

        logger.debug("Extracted secondary_amount: {}".format(secondary_amount))

        return secondary_amount

    def pre_processing(self, data_dict: dict) -> dict:
        data_dict = super().pre_processing(data_dict)
        data_dict["secondary_sum"] = self.get_available_secondary_stats(data_dict)

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

        talent_combinations = None
        if self.settings.talent_permutations:
            talent_combinations = self.settings.talent_list.get(
                self.wow_spec, self.wow_spec.get_talent_combinations()
            )
        else:
            talent_combinations = [data_dict["profile"]["character"]["talents"]]

        secondaries = data_dict["secondary_sum"]

        for talent_combination in talent_combinations:
            for crit, haste, mastery, vers in distribution_multipliers:

                s_o = Simulation_Data(
                    name="{}_{}-{}-{}-{}".format(
                        talent_combination,
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
                        "talents={}".format(talent_combination),
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
                )

                if (crit, haste, mastery, vers) == distribution_multipliers[0]:
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

        data_dict.pop("covenant_profiles")

        # fix spelling
        for talent_combination in data_dict["data"]:
            for secondaries in list(data_dict["data"][talent_combination].keys()):
                data_dict["data"][talent_combination][
                    secondaries.replace("-", "_")
                ] = data_dict["data"][talent_combination].pop(secondaries)

        # create ordered name list
        data_dict["sorted_data_keys"] = {}
        for talent_combination in data_dict["data"].keys():
            tmp_list = []
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
            human_text = []
            for talent_combination in data_dict["data"]:
                dps_dict = data_dict["data"][talent_combination]
                ordered_dps = sorted(
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

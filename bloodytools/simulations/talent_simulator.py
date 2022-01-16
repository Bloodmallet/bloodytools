import json
import logging
import os
import typing

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
        data_dict["profile"]["character"]["talents"] = "0000000"
        for talent in get_talents_for_spec(self.wow_spec):
            data_dict["translations"][talent.name] = talent.translations.get_dict()

        return data_dict

    def add_simulation_data(
        self, simulation_group: Simulation_Group, data_dict: dict
    ) -> None:
        pass

        logger.debug("talent_simulations start")

        talent_blueprint = self.wow_spec.talents_blueprint

        talent_combinations: typing.List[str] = []

        # build list of all talent combinations
        for first in range(4):
            for second in range(4):
                for third in range(4):
                    for forth in range(4):
                        for fifth in range(4):
                            for sixth in range(4):
                                for seventh in range(4):

                                    talent_combination = "{}{}{}{}{}{}{}".format(
                                        first,
                                        second,
                                        third,
                                        forth,
                                        fifth,
                                        sixth,
                                        seventh,
                                    )

                                    abort = False

                                    tmp_count = 0

                                    # compare all non-dps locations, use only dps talent rows
                                    location = talent_blueprint.find("0")
                                    while location > -1:
                                        if (
                                            talent_combination[tmp_count + location]
                                            != "0"
                                        ):
                                            abort = True
                                        tmp_count += location + 1
                                        location = talent_blueprint[tmp_count:].find(
                                            "0"
                                        )

                                    # skip talent combinations with too many (more than one) not chosen dps values
                                    if (
                                        talent_combination.count("0")
                                        > talent_blueprint.count("0") + 1
                                    ):
                                        abort = True

                                    if abort:
                                        continue

                                    talent_combinations.append(talent_combination)

        # filter talent combinations from non-dps talents
        if self.wow_spec == get_wow_spec("demon_hunter", "vengeance"):

            def _is_not_dps_neutral_talent(talent_combination: str) -> bool:
                position_denied_talent = (
                    (1, 1),
                    (3, 1),
                    (3, 2),
                    (4, 3),
                    (5, 1),
                    (5, 3),
                    (6, 1),
                    (6, 2),
                )
                return not any(
                    [
                        True if (row, int(column)) in position_denied_talent else False
                        for row, column in enumerate(talent_combination)
                    ]
                )

            talent_combinations = list(
                [
                    talent_combination
                    for talent_combination in talent_combinations
                    if _is_not_dps_neutral_talent(talent_combination)
                ]
            )

        logger.debug(
            "Creating talent combinations: Done. Created {}.".format(
                len(talent_combinations)
            )
        )

        # no talents profile
        base_profile = Simulation_Data(
            name=talent_combinations[0],
            fight_style=self.fight_style,
            profile=data_dict["profile"],
            simc_arguments=[
                "talents={}".format(talent_combinations[0]),
            ],
            target_error=self.settings.target_error.get(self.fight_style, "0.1"),
            ptr=self.settings.ptr,
            default_actions=self.settings.default_actions,
            executable=self.settings.executable,
            iterations=self.settings.iterations,
        )

        if self.settings.custom_apl:
            with open("custom_apl.txt") as f:
                custom_apl = f.read()
            base_profile.simc_arguments.append("# custom_apl")
            base_profile.simc_arguments.append(custom_apl)

        if self.settings.custom_fight_style:
            with open("custom_fight_style.txt") as f:
                custom_fight_style = f.read()
            base_profile.simc_arguments.append("# custom_fight_style")
            base_profile.simc_arguments.append(custom_fight_style)

        simulation_group.add(base_profile)

        # add all talent combinations to the simulation_group
        for talent_combination in talent_combinations[1:]:
            simulation_data = Simulation_Data(
                name=talent_combination,
                fight_style=self.fight_style,
                simc_arguments=["talents={}".format(talent_combination)],
                target_error=self.settings.target_error.get(self.fight_style, "0.1"),
                ptr=self.settings.ptr,
                default_actions=self.settings.default_actions,
                executable=self.settings.executable,
                iterations=self.settings.iterations,
            )
            simulation_group.add(simulation_data)

    def post_processing(self, data_dict: dict) -> dict:
        data_dict = super().post_processing(data_dict)

        tmp_1 = []
        tmp_2 = []

        for talent_combination in data_dict["data"]:
            if talent_combination.count("0") == self.wow_spec.talents_blueprint.count(
                "0"
            ):
                tmp_1.append(talent_combination)
            else:
                tmp_2.append(talent_combination)

        def get_value(data, key: str) -> int:
            """This function exists to make mypy happy."""
            value: int = data[key]
            return value

        tmp_1 = sorted(
            tmp_1,
            key=lambda name: get_value(data_dict["data"], name),
            # key=lambda name: max(data_dict["data"][name].values()),
            reverse=True,
        )
        tmp_2 = sorted(
            tmp_2,
            key=lambda name: get_value(data_dict["data"], name),
            # key=lambda name: max(data_dict["data"][name].values()),
            reverse=True,
        )

        # add sorted key lists
        # 1 all usual talent combinations
        # 2 all talent combinations with one empty dps row
        data_dict["sorted_data_keys"] = []
        data_dict["sorted_data_keys_2"] = []

        for item in tmp_1:
            data_dict["sorted_data_keys"].append(item[0])
        for item in tmp_2:
            data_dict["sorted_data_keys_2"].append(item[0])

        logger.debug("talent_simulations end")
        return data_dict

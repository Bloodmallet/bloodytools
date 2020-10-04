import json
import logging
import os

from bloodytools.utils.utils import create_basic_profile_string, create_base_json_dict
from bloodytools.utils.simulation_objects import Simulation_Group, Simulation_Data
from simc_support.game_data.WowSpec import WowSpec
from typing import List, Tuple

logger = logging.getLogger(__name__)


def talent_worth_simulation(settings) -> None:
    """Function generates all possible talent combinations for all specs. Including empty dps talent rows. This way the dps gain of each talent can be calculated.

    Arguments:
        settings {object} -- bloodytools/settings.py

    Returns:
        None -- [description]
    Creates json result files.
    """
    logger.debug("talent_worth_simulations start")

    specs: List[WowSpec] = settings.wow_class_spec_list

    for fight_style in settings.fight_styles:
        for wow_spec in specs:
            wow_class = wow_spec.wow_class
            # check whether the baseline profile does exist
            try:
                with open(
                    create_basic_profile_string(wow_spec, settings.tier, settings),
                    "r",
                ) as f:
                    pass
            except FileNotFoundError:
                logger.warning(
                    "{} {} profile not found. Skipping.".format(
                        wow_spec.title(), wow_class.title()
                    )
                )
                continue

            base_profile_string = create_basic_profile_string(
                wow_spec, settings.tier, settings
            )

            simulation_group = Simulation_Group(
                name="{} {} {}".format(fight_style, wow_spec, wow_class),
                executable=settings.executable,
                threads=settings.threads,
                profileset_work_threads=settings.profileset_work_threads,
            )

            talent_blueprint = wow_spec.talents_blueprint

            talent_combinations = []

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
                                            location = talent_blueprint[
                                                tmp_count:
                                            ].find("0")

                                        # skip talent combinations with too many (more than one) not chosen dps values
                                        if (
                                            talent_combination.count("0")
                                            > talent_blueprint.count("0") + 1
                                        ):
                                            abort = True

                                        if abort:
                                            continue

                                        talent_combinations.append(talent_combination)
            logger.debug(
                "Creating talent combinations: Done. Created {}.".format(
                    len(talent_combinations)
                )
            )

            # no talents profile
            base_profile = Simulation_Data(
                name="{}".format(talent_combinations[0]),
                fight_style=fight_style,
                simc_arguments=[
                    base_profile_string,
                    "talents={}".format(talent_combinations[0]),
                ],
                target_error=settings.target_error[fight_style],
                ptr=settings.ptr,
                default_actions=settings.default_actions,
                executable=settings.executable,
                iterations=settings.iterations,
            )

            custom_apl = None
            if settings.custom_apl:
                with open("custom_apl.txt") as f:
                    custom_apl = f.read()
            if custom_apl:
                base_profile.simc_arguments.append(custom_apl)

            custom_fight_style = None
            if settings.custom_fight_style:
                with open("custom_fight_style.txt") as f:
                    custom_fight_style = f.read()
            if custom_fight_style:
                base_profile.simc_arguments.append(custom_fight_style)

            simulation_group.add(base_profile)

            # add all talent combinations to the simulation_group
            for talent_combination in talent_combinations[1:]:
                simulation_data = Simulation_Data(
                    name="{}".format(talent_combination),
                    fight_style=fight_style,
                    simc_arguments=["talents={}".format(talent_combination)],
                    target_error=settings.target_error[fight_style],
                    ptr=settings.ptr,
                    default_actions=settings.default_actions,
                    executable=settings.executable,
                    iterations=settings.iterations,
                )
                simulation_group.add(simulation_data)

            logger.info(
                "Talent Worth {} {} {} {} profiles.".format(
                    wow_spec, wow_class, fight_style, len(simulation_group.profiles)
                )
            )

            # time to sim
            if settings.use_raidbots:
                simulation_group.simulate_with_raidbots(settings.apikey)
            else:
                simulation_group.simulate()

            export_json = create_base_json_dict(
                "Talent Worth", wow_spec, fight_style, settings
            )

            # save all generated data in "data"
            for profile in simulation_group.profiles:
                export_json["data"][profile.name] = profile.get_dps()

            tmp_1 = []
            tmp_2 = []

            for talent_combination in export_json["data"]:
                if talent_combination.count("0") == talent_blueprint.count("0"):
                    tmp_1.append(
                        (talent_combination, export_json["data"][talent_combination])
                    )
                else:
                    tmp_2.append(
                        (talent_combination, export_json["data"][talent_combination])
                    )

            tmp_1 = sorted(tmp_1, key=lambda item: item[1], reverse=True)
            tmp_2 = sorted(tmp_2, key=lambda item: item[1], reverse=True)

            # add sorted key lists
            # 1 all usual talent combinations
            # 2 all talent combinations with one empty dps row
            export_json["sorted_data_keys"] = []
            export_json["sorted_data_keys_2"] = []

            for item in tmp_1:
                export_json["sorted_data_keys"].append(item[0])
            for item in tmp_2:
                export_json["sorted_data_keys_2"].append(item[0])

            path = "results/talent_worth/"
            # create directory if it doesn't exist
            if not os.path.isdir(path):
                os.makedirs(path)

            file_name = f"{path}{wow_class.simc_name}_{wow_spec.simc_name}_{fight_style.lower()}"
            if settings.ptr == "1":
                file_name += "_ptr"

            # write json to file
            with open(file_name + ".json", "w", encoding="utf-8") as f:
                logger.debug("Print talent_worth json.")
                f.write(
                    json.dumps(
                        export_json, sort_keys=True, indent=4, ensure_ascii=False
                    )
                )
                logger.debug("Printed talent_worth json.")

    logger.debug("talent_worth_simulations end")

import json
import logging
import os

from bloodytools.utils.utils import create_basic_profile_string, create_base_json_dict
from bloodytools.utils.simulation_objects import Simulation_Group, Simulation_Data
from simc_support.game_data.WowSpec import WowSpec, get_wow_spec
from simc_support.game_data.Talent import get_talents_for_spec
from typing import List, Tuple

logger = logging.getLogger(__name__)


def talent_simulation(settings) -> None:
    """Function generates all possible talent combinations for all specs. Including empty dps talent rows. This way the dps gain of each talent can be calculated.

    Arguments:
        settings {object} -- bloodytools/settings.py

    Returns:
        None -- [description]
    Creates json result files.
    """
    logger.debug("talent_simulations start")

    specs: List[WowSpec] = settings.wow_class_spec_list

    for fight_style in settings.fight_styles:
        for wow_spec in specs:
            wow_class = wow_spec.wow_class

            export_json = create_base_json_dict(
                "Talents", wow_spec, fight_style, settings
            )

            export_json["profile"]["character"]["talents"] = "0000000"

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

            # filter talent combinations from non-dps talents
            if wow_spec == get_wow_spec("demon_hunter", "vengeance"):

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
                            True
                            if (row, int(column)) in position_denied_talent
                            else False
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

            for talent in get_talents_for_spec(wow_spec):
                export_json["translations"][
                    talent.name
                ] = talent.translations.get_dict()

            # no talents profile
            base_profile = Simulation_Data(
                name="{}".format(talent_combinations[0]),
                fight_style=fight_style,
                profile=export_json["profile"],
                simc_arguments=[
                    "talents={}".format(talent_combinations[0]),
                ],
                target_error=settings.target_error.get(fight_style, "0.1"),
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
                base_profile.simc_arguments.append("# custom_apl")
                base_profile.simc_arguments.append(custom_apl)

            custom_fight_style = None
            if settings.custom_fight_style:
                with open("custom_fight_style.txt") as f:
                    custom_fight_style = f.read()
            if custom_fight_style:
                base_profile.simc_arguments.append("# custom_fight_style")
                base_profile.simc_arguments.append(custom_fight_style)

            simulation_group.add(base_profile)

            # add all talent combinations to the simulation_group
            for talent_combination in talent_combinations[1:]:
                simulation_data = Simulation_Data(
                    name="{}".format(talent_combination),
                    fight_style=fight_style,
                    simc_arguments=["talents={}".format(talent_combination)],
                    target_error=settings.target_error.get(fight_style, "0.1"),
                    ptr=settings.ptr,
                    default_actions=settings.default_actions,
                    executable=settings.executable,
                    iterations=settings.iterations,
                )
                simulation_group.add(simulation_data)

            logger.info(
                "Talent {} {} {} {} profiles.".format(
                    wow_spec, wow_class, fight_style, len(simulation_group.profiles)
                )
            )

            # time to sim
            if settings.use_raidbots:
                simulation_group.simulate_with_raidbots(settings.apikey)
            else:
                simulation_group.simulate()

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

            path = "results/talents/"
            # create directory if it doesn't exist
            if not os.path.isdir(path):
                os.makedirs(path)

            file_name = f"{path}{wow_class.simc_name}_{wow_spec.simc_name}_{fight_style.lower()}"
            if settings.ptr == "1":
                file_name += "_ptr"

            # write json to file
            with open(file_name + ".json", "w", encoding="utf-8") as f:
                logger.debug("Print talents json.")
                f.write(
                    json.dumps(
                        export_json,
                        sort_keys=True,
                        indent=4 if settings.pretty else None,
                        ensure_ascii=False,
                    )
                )
                logger.debug("Printed talents json.")

    logger.debug("talent_simulations end")

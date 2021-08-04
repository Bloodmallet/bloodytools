import json
import logging
import os

from bloodytools.utils.config import Config
from bloodytools.utils.utils import create_basic_profile_string, create_base_json_dict
from bloodytools.utils.simulation_objects import Simulation_Group, Simulation_Data
from typing import List, Tuple

logger = logging.getLogger(__name__)


def gear_path_simulation(specs: List[Tuple[str, str]], settings: Config) -> None:

    logger.debug("race_simulations start")

    for fight_style in settings.fight_styles:
        gear_path = []
        for wow_class, wow_spec in specs:

            # initial profiles and data
            secondary_sum = 0
            base_profile_string = create_basic_profile_string(
                wow_class, wow_spec, settings.tier, settings
            )

            try:
                with open(base_profile_string, "r") as f:
                    for line in f:
                        if "gear_crit_rating" in line:
                            secondary_sum += int(line.split("=")[-1])
                        if "gear_haste_rating" in line:
                            secondary_sum += int(line.split("=")[-1])
                        if "gear_mastery_rating" in line:
                            secondary_sum += int(line.split("=")[-1])
                        if "gear_versatility_rating" in line:
                            secondary_sum += int(line.split("=")[-1])
            except Exception:
                logger.warning(
                    "Profile for {} {} couldn't be found. Will be left out in Gear Path simulations.".format(
                        wow_spec, wow_class
                    )
                )
                continue

            crit_rating = (
                haste_rating
            ) = mastery_rating = vers_rating = settings.start_value

            while (
                crit_rating + haste_rating + mastery_rating + vers_rating
                < secondary_sum
            ):

                simulation_group = Simulation_Group(
                    name="{} {} {}".format(fight_style, wow_spec, wow_class),
                    executable=settings.executable,
                    threads=settings.threads,
                    profileset_work_threads=settings.profileset_work_threads,
                )

                crit_profile = Simulation_Data(
                    name="crit_profile",
                    executable=settings.executable,
                    fight_style=fight_style,
                    target_error=settings.target_error.get(fight_style, "0.1"),
                    simc_arguments=[
                        base_profile_string,
                        "gear_crit_rating={}".format(crit_rating + settings.step_size),
                        "gear_haste_rating={}".format(haste_rating),
                        "gear_mastery_rating={}".format(mastery_rating),
                        "gear_versatility_rating={}".format(vers_rating),
                    ],
                    ptr=settings.ptr,
                    default_actions=settings.default_actions,
                )
                simulation_group.add(crit_profile)

                haste_profile = Simulation_Data(
                    name="haste_profile",
                    executable=settings.executable,
                    fight_style=fight_style,
                    target_error=settings.target_error.get(fight_style, "0.1"),
                    simc_arguments=[
                        "gear_crit_rating={}".format(crit_rating),
                        "gear_haste_rating={}".format(
                            haste_rating + settings.step_size
                        ),
                        "gear_mastery_rating={}".format(mastery_rating),
                        "gear_versatility_rating={}".format(vers_rating),
                    ],
                    ptr=settings.ptr,
                    default_actions=settings.default_actions,
                )
                simulation_group.add(haste_profile)

                mastery_profile = Simulation_Data(
                    name="mastery_profile",
                    executable=settings.executable,
                    fight_style=fight_style,
                    target_error=settings.target_error.get(fight_style, "0.1"),
                    simc_arguments=[
                        "gear_crit_rating={}".format(crit_rating),
                        "gear_haste_rating={}".format(haste_rating),
                        "gear_mastery_rating={}".format(
                            mastery_rating + settings.step_size
                        ),
                        "gear_versatility_rating={}".format(vers_rating),
                    ],
                    ptr=settings.ptr,
                    default_actions=settings.default_actions,
                )
                simulation_group.add(mastery_profile)

                vers_profile = Simulation_Data(
                    name="vers_profile",
                    executable=settings.executable,
                    fight_style=fight_style,
                    target_error=settings.target_error.get(fight_style, "0.1"),
                    simc_arguments=[
                        "gear_crit_rating={}".format(crit_rating),
                        "gear_haste_rating={}".format(haste_rating),
                        "gear_mastery_rating={}".format(mastery_rating),
                        "gear_versatility_rating={}".format(
                            vers_rating + settings.step_size
                        ),
                    ],
                    ptr=settings.ptr,
                    default_actions=settings.default_actions,
                )
                simulation_group.add(vers_profile)

                simulation_group.simulate()

                # ugly
                winner_dps = 0
                if (
                    crit_profile.get_dps() >= haste_profile.get_dps()
                    and crit_profile.get_dps() >= mastery_profile.get_dps()
                    and crit_profile.get_dps() >= vers_profile.get_dps()
                ):

                    crit_rating += settings.step_size
                    winner_dps = crit_profile.get_dps()
                    logger.info(
                        "Crit - {}/{}/{}/{}: {}".format(
                            crit_rating,
                            haste_rating,
                            mastery_rating,
                            vers_rating,
                            winner_dps,
                        )
                    )

                elif (
                    haste_profile.get_dps() >= crit_profile.get_dps()
                    and haste_profile.get_dps() >= mastery_profile.get_dps()
                    and haste_profile.get_dps() >= vers_profile.get_dps()
                ):

                    haste_rating += settings.step_size
                    winner_dps = haste_profile.get_dps()
                    logger.info(
                        "Haste - {}/{}/{}/{}: {}".format(
                            crit_rating,
                            haste_rating,
                            mastery_rating,
                            vers_rating,
                            winner_dps,
                        )
                    )

                elif (
                    mastery_profile.get_dps() >= haste_profile.get_dps()
                    and mastery_profile.get_dps() >= crit_profile.get_dps()
                    and mastery_profile.get_dps() >= vers_profile.get_dps()
                ):

                    mastery_rating += settings.step_size
                    winner_dps = mastery_profile.get_dps()
                    logger.info(
                        "Mastery - {}/{}/{}/{}: {}".format(
                            crit_rating,
                            haste_rating,
                            mastery_rating,
                            vers_rating,
                            winner_dps,
                        )
                    )

                elif (
                    vers_profile.get_dps() >= haste_profile.get_dps()
                    and vers_profile.get_dps() >= mastery_profile.get_dps()
                    and vers_profile.get_dps() >= crit_profile.get_dps()
                ):

                    vers_rating += settings.step_size
                    winner_dps = vers_profile.get_dps()
                    logger.info(
                        "Vers - {}/{}/{}/{}: {}".format(
                            crit_rating,
                            haste_rating,
                            mastery_rating,
                            vers_rating,
                            winner_dps,
                        )
                    )

                gear_path.append(
                    {
                        "{}_{}_{}_{}".format(
                            crit_rating, haste_rating, mastery_rating, vers_rating
                        ): winner_dps
                    }
                )

            logger.info(gear_path)

            result = create_base_json_dict(
                "Gear Path", wow_class, wow_spec, fight_style, settings
            )

            result["data"] = gear_path

            if not os.path.isdir("results/gear_path/"):
                os.makedirs("results/gear_path/")

            with open(
                "results/gear_path/{}_{}_{}.json".format(
                    wow_class, wow_spec, fight_style
                ),
                "w",
            ) as f:
                json.dump(
                    result, f, indent=4 if settings.pretty else None, sort_keys=True
                )

    logger.debug("race_simulations ended")

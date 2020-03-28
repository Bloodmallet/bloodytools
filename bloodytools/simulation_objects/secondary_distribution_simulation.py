import json
import os

from utils.utils import create_base_json_dict
from utils.utils import create_basic_profile_string
from simc_support.wow_lib import get_talent_combinations
from simulation_objects.simulation_objects import Simulation_Data
from simulation_objects.simulation_objects import Simulation_Group


def secondary_distribution_simulation(settings: object) -> None:
    """Simulates several secondary distributions for the baseline profile.

  Arguments:
    wow_class {str} -- [description]
    wow_spec {str} -- [description]

  Keyword Arguments:
    talent_combinations {List[str]} -- [description] (default: {[False]})

  Returns:
    List[so.Simulation_Group] -- [description]
  """

    logger = settings.logger

    logger.debug("secondary_distribution_simulations start")

    for fight_style in settings.fight_styles:
        for wow_class, wow_spec in settings.wow_class_spec_list:
            result_dict = create_base_json_dict(
                "secondary_distributions", wow_class, wow_spec, fight_style, settings
            )

            talent_combinations = None
            if not settings.talent_permutations:
                talent_combinations = [result_dict['profile']['talents']]
            # if no talent list is provided, simulate all
            elif (wow_class, wow_spec) not in settings.talent_list:
                talent_combinations = get_talent_combinations(wow_class, wow_spec)
            else:
                # if talent list is provided, sim that
                talent_combinations = settings.talent_list[(wow_class, wow_spec)]

            secondary_amount = 0

            # get secondary sum from profile
            try:
                with open(
                    create_basic_profile_string(wow_class, wow_spec, settings.tier, settings), 'r'
                ) as f:
                    for line in f:
                        if "gear_crit_rating=" in line:
                            secondary_amount += int(line.split("=")[1].split()[0])
                        elif "gear_haste_rating=" in line:
                            secondary_amount += int(line.split("=")[1].split()[0])
                        elif "gear_mastery_rating=" in line:
                            secondary_amount += int(line.split("=")[1].split()[0])
                        elif "gear_versatility_rating=" in line:
                            secondary_amount += int(line.split("=")[1].split()[0])
            except FileNotFoundError:
                logger.warning(
                    "{} {} profile not found. Skipping.".format(
                        wow_spec.title(), wow_class.title()
                    )
                )
            if settings.custom_profile:
                c_secondary_amount = 0
                try:
                    with open('custom_profile', 'r') as f:
                        for line in f:
                            if "gear_crit_rating=" in line:
                                c_secondary_amount += int(line.split("=")[1].split()[0])
                            elif "gear_haste_rating=" in line:
                                c_secondary_amount += int(line.split("=")[1].split()[0])
                            elif "gear_mastery_rating=" in line:
                                c_secondary_amount += int(line.split("=")[1].split()[0])
                            elif "gear_versatility_rating=" in line:
                                c_secondary_amount += int(line.split("=")[1].split()[0])
                            elif 'secondary_sum=' in line:
                                c_secondary_amount = int(line.split("=")[1].split()[0])
                                logger.debug(
                                    "Found 'secondary_sum= in custom_profile. Using that value."
                                )
                                break
                except FileNotFoundError:
                    logger.warning("Custom profile not found. Using base profile.")
                if c_secondary_amount > 0:
                    secondary_amount = c_secondary_amount

            logger.debug("Extracted secondary_amount: {}".format(secondary_amount))

            # input generation
            distribution_multipliers = []
            step_size = settings.secondary_distributions_step_size
            lower_border = 10     # percent
            upper_border = 70     # percent

            # generate all valid secondary distributions
            for c in range(lower_border, upper_border + step_size, step_size):
                for h in range(lower_border, upper_border + step_size, step_size):
                    for m in range(lower_border, upper_border + step_size, step_size):
                        for v in range(lower_border, upper_border + step_size, step_size):
                            if c + h + m + v == 100:
                                distribution_multipliers.append((c, h, m, v))

            logger.debug(
                "'{}' different distributions generated.".format(len(distribution_multipliers))
            )

            result_dict["sorted_data_keys"] = {}
            result_dict["secondary_sum"] = secondary_amount

            for talent_combination in talent_combinations:
                simulation_group = Simulation_Group(
                    name=talent_combination,
                    threads=settings.threads,
                    profileset_work_threads=settings.profileset_work_threads,
                    executable=settings.executable,
                    logger=logger
                )

                for distribution_multiplier in distribution_multipliers:
                    # if it is the first one
                    if distribution_multiplier == distribution_multipliers[0]:

                        s_o = Simulation_Data(
                            name="{}_{}_{}_{}".format(
                                distribution_multiplier[0], distribution_multiplier[1],
                                distribution_multiplier[2], distribution_multiplier[3]
                            ),
                            fight_style=fight_style,
                            target_error=settings.target_error[fight_style],
                            iterations=settings.iterations,
                            logger=logger,
                            profile=result_dict['profile'],
                            simc_arguments=[
                                "gear_crit_rating={}".format(
                                    int(secondary_amount * (distribution_multiplier[0] / 100))
                                ),
                                "gear_haste_rating={}".format(
                                    int(secondary_amount * (distribution_multiplier[1] / 100))
                                ),
                                "gear_mastery_rating={}".format(
                                    int(secondary_amount * (distribution_multiplier[2] / 100))
                                ),
                                "gear_versatility_rating={}".format(
                                    int(secondary_amount * (distribution_multiplier[3] / 100))
                                ),
                            ],
                            ptr=settings.ptr,
                            default_actions=settings.default_actions,
                            executable=settings.executable
                        )

                        custom_apl = None
                        if settings.custom_apl:
                            with open('custom_apl.txt') as f:
                                custom_apl = f.read()
                        if custom_apl:
                            s_o.simc_arguments.append(custom_apl)

                        custom_fight_style = None
                        if settings.custom_fight_style:
                            with open('custom_fight_style.txt') as f:
                                custom_fight_style = f.read()
                        if custom_fight_style:
                            s_o.simc_arguments.append(custom_fight_style)

                        simulation_group.add(s_o)
                        # add the talent combination to the profileset, if one was provided
                        if talent_combination:
                            simulation_group.profiles[-1].simc_arguments.append(
                                "talents={}".format(talent_combination)
                            )
                    else:
                        simulation_group.add(
                            Simulation_Data(
                                name="{}_{}_{}_{}".format(
                                    distribution_multiplier[0], distribution_multiplier[1],
                                    distribution_multiplier[2], distribution_multiplier[3]
                                ),
                                fight_style=fight_style,
                                target_error=settings.target_error[fight_style],
                                iterations=settings.iterations,
                                logger=logger,
                                simc_arguments=[
                                    "gear_crit_rating={}".format(
                                        int(secondary_amount * (distribution_multiplier[0] / 100))
                                    ),
                                    "gear_haste_rating={}".format(
                                        int(secondary_amount * (distribution_multiplier[1] / 100))
                                    ),
                                    "gear_mastery_rating={}".format(
                                        int(secondary_amount * (distribution_multiplier[2] / 100))
                                    ),
                                    "gear_versatility_rating={}".format(
                                        int(secondary_amount * (distribution_multiplier[3] / 100))
                                    ),
                                ],
                                ptr=settings.ptr,
                                default_actions=settings.default_actions,
                                executable=settings.executable
                            )
                        )

                logger.info(
                    "Start {} secondary distribution simulation for {} {} {}.".format(
                        fight_style, wow_class, wow_spec, talent_combination
                    )
                )

                try:
                    if settings.use_raidbots:
                        settings.simc_hash = simulation_group.simulate_with_raidbots(
                            settings.apikey
                        )
                    else:
                        simulation_group.simulate()
                except Exception as e:
                    logger.error(
                        "Secondary distribution simulation for {} {} {} failed. {}".format(
                            wow_class, wow_spec, talent_combination, e
                        )
                    )
                    continue
                else:
                    logger.info(
                        "{} secondary distribution simulation for {} {} {} ended successfully. Cleaning up."
                        .format(fight_style.title(), wow_class, wow_spec, talent_combination)
                    )

                if settings.debug:
                    logger.debug("Talent combination: " + talent_combination)
                    for profile in simulation_group.profiles:
                        logger.debug("  {}   {}".format(profile.name, profile.get_dps()))

                # create sorted list and add data to the result_dict
                stat_dps_list = []
                result_dict["data"][talent_combination] = {}

                for profile in simulation_group.profiles:
                    stat_dps_list.append((profile.name, profile.get_dps()))
                    result_dict["data"][talent_combination][profile.name] = profile.get_dps()

                # sort list
                stat_dps_list = sorted(stat_dps_list, key=lambda item: item[1], reverse=True)
                logger.info(
                    "Stat distribution {} of talent combination {} won with {} dps.".format(
                        stat_dps_list[0][0], talent_combination, stat_dps_list[0][1]
                    )
                )

                logger.debug(
                    "Secondary distribution list for {} (max:{}):".format(
                        talent_combination, stat_dps_list[0][1]
                    )
                )

                # create directory if it doesn't exist
                if not os.path.isdir("results/"):
                    os.makedirs("results/")
                if not os.path.isdir("results/secondary_distributions/"):
                    os.makedirs("results/secondary_distributions/")

                if settings.write_humanreadable_secondary_distribution_file:
                    with open(
                        'results/secondary_distributions/{}_{}_{}.txt'.format(
                            wow_class.lower(), wow_spec.lower(), fight_style.lower()
                        ), 'a'
                    ) as f:
                        f.write(
                            "Sorted secondary distribution list for {} (max:{}):\n".format(
                                talent_combination, stat_dps_list[0][1]
                            )
                        )

                # open human readable file only once
                with open(
                    'results/secondary_distributions/{}_{}_{}.txt'.format(
                        wow_class.lower(), wow_spec.lower(), fight_style.lower()
                    ), 'a'
                ) as f:
                    for item in stat_dps_list:
                        if item == stat_dps_list[0]:
                            logger.debug("c  h  m  v    dps")
                            if settings.write_humanreadable_secondary_distribution_file:
                                f.write("  c  h  m  v    dps\n")

                        # c_h_m_v dps dps%
                        logger.debug(
                            "{}   {}  {}%".format(
                                item[0], item[1], round(item[1] * 100 / stat_dps_list[0][1], 2)
                            )
                        )
                        if settings.write_humanreadable_secondary_distribution_file:
                            f.write(
                                "  {}   {}  {}%\n".format(
                                    item[0], item[1],
                                    round(item[1] * 100 / stat_dps_list[0][1], 2)
                                )
                            )

                result_dict["sorted_data_keys"][talent_combination] = [
                    item[0] for item in stat_dps_list
                ]

            logger.debug(result_dict)
            if not os.path.isdir("results/"):
                os.makedirs("results/")
            if not os.path.isdir("results/secondary_distributions/"):
                os.makedirs("results/secondary_distributions/")

            # write result file
            with open(
                "results/secondary_distributions/{}_{}_{}.json".format(
                    wow_class.lower(), wow_spec.lower(), fight_style.lower()
                ), 'w'
            ) as f:
                logger.debug("Print secondary distribution json.")
                f.write(json.dumps(result_dict, sort_keys=True, indent=4))
                logger.debug("Printed secondary distribution json.")

    logger.debug("secondary_distribution_simulations ended")

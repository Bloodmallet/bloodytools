import os
import json

from bloodytools.utils.utils import create_basic_profile_string, create_base_json_dict
from bloodytools.utils.simulation_objects import Simulation_Group, Simulation_Data
from simc_support import wow_lib
from typing import List, Tuple


def race_simulation(specs: List[Tuple[str, str]], settings) -> None:
    """Simulates all available races for all given specs.

    Arguments:
        specs {List[Tuple[str, str]]} -- List of all wanted wow_specs

    Returns:
        None --
    """
    logger = settings.logger
    logger.debug("race_simulations start")
    for fight_style in settings.fight_styles:
        for wow_class, wow_spec in specs:

            # check whether the baseline profile does exist
            try:
                with open(
                    create_basic_profile_string(
                        wow_class, wow_spec, settings.tier, settings), 'r'
                ) as f:
                    pass
            except FileNotFoundError:
                logger.warning(
                    "{} {} base profile not found. Skipping.".format(
                        wow_spec.title(), wow_class.title()
                    )
                )
                continue

            # prepare result json
            wanted_data = create_base_json_dict(
                "Races", wow_class, wow_spec, fight_style, settings)

            races = wow_lib.get_races_for_class(wow_class)
            simulation_group = Simulation_Group(
                name="race_simulations",
                threads=settings.threads,
                profileset_work_threads=settings.profileset_work_threads,
                executable=settings.executable,
                logger=logger
            )

            for race in races:

                simulation_data = None

                if race == races[0]:

                    simulation_data = Simulation_Data(
                        name=race.title().replace("_", " "),
                        fight_style=fight_style,
                        profile=wanted_data['profile'],
                        simc_arguments=["race={}".format(race)],
                        target_error=settings.target_error[fight_style],
                        ptr=settings.ptr,
                        default_actions=settings.default_actions,
                        executable=settings.executable,
                        iterations=settings.iterations,
                        logger=logger
                    )
                    custom_apl = None
                    if settings.custom_apl:
                        with open('custom_apl.txt') as f:
                            custom_apl = f.read()
                    if custom_apl:
                        simulation_data.simc_arguments.append(custom_apl)

                    custom_fight_style = None
                    if settings.custom_fight_style:
                        with open('custom_fight_style.txt') as f:
                            custom_fight_style = f.read()
                    if custom_fight_style:
                        simulation_data.simc_arguments.append(
                            custom_fight_style)
                else:
                    simulation_data = Simulation_Data(
                        name=race.title().replace("_", " "),
                        fight_style=fight_style,
                        simc_arguments=["race={}".format(race)],
                        target_error=settings.target_error[fight_style],
                        ptr=settings.ptr,
                        default_actions=settings.default_actions,
                        executable=settings.executable,
                        iterations=settings.iterations,
                        logger=logger
                    )

                    # adding argument for zandalari trolls
                    if race == 'zandalari_troll':
                        simulation_data.simc_arguments.append(
                            'zandalari_loa=kimbul')
                        simulation_data.name += ' Kimbul'

                simulation_group.add(simulation_data)
                logger.debug((
                    "Added race '{}' in profile '{}' to simulation_group.".format(
                        race, simulation_data.name
                    )
                ))

                if race == 'zandalari_troll':
                    # create more loa profiles and add them
                    simulation_data = None
                    for loa in ['bwonsamdi', 'paku']:
                        simulation_data = Simulation_Data(
                            name='{} {}'.format(
                                race.title().replace("_", " "), loa.title()),
                            fight_style=fight_style,
                            simc_arguments=[
                                "race={}".format(
                                    race), 'zandalari_loa={}'.format(loa)
                            ],
                            target_error=settings.target_error[fight_style],
                            ptr=settings.ptr,
                            default_actions=settings.default_actions,
                            executable=settings.executable,
                            iterations=settings.iterations,
                            logger=logger
                        )
                        simulation_group.add(simulation_data)
                        logger.debug((
                            "Added race '{}' in profile '{}' to simulation_group.".format(
                                race, simulation_data.name
                            )
                        ))

            logger.info(
                "Start {} race simulation for {} {}.".format(
                    fight_style, wow_class, wow_spec)
            )
            try:
                if settings.use_raidbots and settings.apikey:
                    settings.simc_hash = simulation_group.simulate_with_raidbots(
                        settings.apikey)
                else:
                    simulation_group.simulate()
            except Exception as e:
                logger.error(
                    "{} race simulation for {} {} failed. {}".format(
                        fight_style.title(), wow_class, wow_spec, e
                    )
                )
                continue
            else:
                logger.info(
                    "{} race simulation for {} {} ended successfully. Cleaning up.".format(
                        fight_style.title(), wow_class, wow_spec
                    )
                )

            for profile in simulation_group.profiles:
                logger.debug("Profile '{}' DPS: {}".format(
                    profile.name, profile.get_dps()))

            logger.debug(
                "Created base dict for json export. {}".format(wanted_data))

            # add dps values to json
            for profile in simulation_group.profiles:
                wanted_data["data"][profile.name] = profile.get_dps()
                logger.debug(
                    "Added '{}' with {} dps to json.".format(
                        profile.name, profile.get_dps())
                )
                # add race translations to the final json
                translated_name = wow_lib.get_race_translation(profile.name)
                if translated_name:
                    wanted_data["languages"][profile.name
                                             ] = translated_name
                else:
                    fake_translation = profile.name.title().replace("_", " ")
                    wanted_data['languages'][profile.name] = {
                        'en_US': fake_translation,
                        'it_IT': fake_translation,
                        'de_DE': fake_translation,
                        'fr_FR': fake_translation,
                        'ru_RU': fake_translation,
                        'es_ES': fake_translation,
                        'ko_KR': fake_translation,
                        'cn_CN': fake_translation
                    }

            # create ordered race name list
            tmp_list = []
            for race in wanted_data["data"]:
                tmp_list.append((race, wanted_data["data"][race]))
            logger.debug("tmp_list: {}".format(tmp_list))

            tmp_list = sorted(tmp_list, key=lambda item: item[1], reverse=True)
            logger.debug("Sorted tmp_list: {}".format(tmp_list))
            logger.info("Race {} won with {} dps.".format(
                tmp_list[0][0], tmp_list[0][1]))

            wanted_data["sorted_data_keys"] = []
            for race, _ in tmp_list:
                wanted_data["sorted_data_keys"].append(race)

            logger.debug("Final json: {}".format(wanted_data))

            if not os.path.isdir("results/races/"):
                os.makedirs("results/races/")

            # write json to file
            with open(
                "results/races/{}_{}_{}.json".format(
                    wow_class.lower(), wow_spec.lower(), fight_style.lower()
                ),
                "w",
                encoding="utf-8"
            ) as f:
                logger.debug("Print race json.")
                f.write(json.dumps(wanted_data, sort_keys=True,
                                   indent=4, ensure_ascii=False))
                logger.debug("Printed race json.")

    logger.debug("race_simulations ended")

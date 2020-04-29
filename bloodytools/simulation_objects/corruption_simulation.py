import json
import os

from bloodytools.simulation_objects.simulation_objects import Simulation_Data, Simulation_Group
from bloodytools.utils.utils import create_base_json_dict, create_basic_profile_string
from simc_support.wow_lib import get_corruptions
from typing import List, Tuple


def corruption_simulation(settings: object) -> None:
    """Simulates all available corruptions for the given specs.

    Args:
        settings (object): [description]

    Returns:
        None --
    """

    logger = settings.logger

    logger.debug("corruption_simulation start")

    specs: List[Tuple[str, str]] = settings.wow_class_spec_list

    for fight_style in settings.fight_styles:
        for wow_class, wow_spec in specs:

            # check if the baseline profile does exist
            try:
                with open(
                    create_basic_profile_string(wow_class, wow_spec, settings.tier, settings), 'r'
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
                "Corruptions", wow_class, wow_spec, fight_style, settings
            )

            # prepare hands-string
            hands_string = 'hands='
            for key in wanted_data['profile']['hands'].keys():
                if key == 'bonus_id':
                    continue
                hands_string += f',{key}={wanted_data["profile"]["hands"][key]}'
            try:
                hands_string += f',bonus_id={wanted_data["profile"]["hands"]["bonus_id"]}'
            except KeyError:
                hands_string += f',bonus_id='

            corruptions = get_corruptions(wow_class.title(), wow_spec.title())
            simulation_group = Simulation_Group(
                name="corruptions",
                threads=settings.threads,
                profileset_work_threads=settings.profileset_work_threads,
                executable=settings.executable,
                logger=logger
            )

            # create corruption filter
            blacklist = []
            for corruption in corruptions:
                for rank in corruptions[corruption]:
                    blacklist.append(corruptions[corruption][rank]['bonus_id'])

            # remove dps corruptions from profile
            for item in wanted_data['profile']['items']:
                for blacklisted in blacklist:
                    if not 'bonus_id' in wanted_data['profile']['items'][item].keys():
                        continue

                    if f'/{blacklisted}' in wanted_data['profile']['items'][item]['bonus_id']:
                        wanted_data['profile']['items'][item]['bonus_id'] = wanted_data['profile'][
                            'items'][item]['bonus_id'].replace(f'/{blacklisted}', '')
                    elif f'{blacklisted}/' in wanted_data['profile']['items'][item]['bonus_id']:
                        wanted_data['profile']['items'][item]['bonus_id'] = wanted_data['profile'][
                            'items'][item]['bonus_id'].replace(f'{blacklisted}/', '')
                    elif f'{blacklisted}' == wanted_data['profile']['items'][item]['bonus_id']:
                        del wanted_data['profile']['items'][item]['bonus_id']

            # add +800 corruption to head
            wanted_data["profile"]["head"]["bonus_id"] += '/6448'     # legacy
            wanted_data["profile"]["items"]["head"]["bonus_id"] += '/6448'

            # add baseline
            for itemlevel in settings.azerite_trait_ilevels:
                simulation_data = None

                simulation_data = Simulation_Data(
                    name=f'baseline_{itemlevel}',
                    fight_style=fight_style,
                    profile=wanted_data['profile'],
                    simc_arguments=[
                        'bfa.surging_vitality_damage_taken_period=1',     # enables Surging Vitality to try and trigger each second
                        hands_string + f',ilevel={itemlevel}',
                    ],
                    target_error=settings.target_error[fight_style],
                    ptr=settings.ptr,
                    default_actions=settings.default_actions,
                    executable=settings.executable,
                    iterations=settings.iterations,
                    logger=logger
                )
                if itemlevel == settings.azerite_trait_ilevels[0]:
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
                        simulation_data.simc_arguments.append(custom_fight_style)
                simulation_group.add(simulation_data)

            # create profiles for all corruptions and their ranks/level
            for corruption in corruptions.keys():
                rank: int
                for rank in corruptions[corruption].keys():

                    bonus_id: int = corruptions[corruption][rank]['bonus_id']
                    spell_id: int = corruptions[corruption][rank]['spell_id']
                    corruption_rating: int = corruptions[corruption][rank]['corruption']

                    # ilevel scaling
                    if corruption in [
                        "Infinite Stars", "Twisted Appendage", "Gushing Wound", "Lash of the Void"
                    ]:
                        for itemlevel in settings.azerite_trait_ilevels:

                            simulation_data = None

                            simulation_data = Simulation_Data(
                                name='{}_{}_{}'.format(corruption, rank, itemlevel),
                                fight_style=fight_style,
                                simc_arguments=[f"{hands_string}/{bonus_id},ilevel={itemlevel}"],
                                target_error=settings.target_error[fight_style],
                                ptr=settings.ptr,
                                default_actions=settings.default_actions,
                                executable=settings.executable,
                                iterations=settings.iterations,
                                logger=logger
                            )

                            simulation_group.add(simulation_data)
                            logger.debug((
                                "Added Corruption '{}:{}:{}' in profile '{}' to simulation_group."
                                .format(bonus_id, rank, itemlevel, simulation_data.name)
                            ))

                    else:
                        simulation_data = None

                        simulation_data = Simulation_Data(
                            name='{}_{}'.format(corruption, rank),
                            fight_style=fight_style,
                            simc_arguments=[
                                f"{hands_string}/{bonus_id},ilevel={settings.azerite_trait_ilevels[0]}"
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
                            "Added Corruption '{}:{}' in profile '{}' to simulation_group.".format(
                                bonus_id, rank, simulation_data.name
                            )
                        ))

                        if corruption == 'Void Ritual':
                            copy = simulation_data.copy()
                            copy.name = '{}_{}+Allies'.format(corruption, rank)
                            copy.simc_arguments += [
                                'bfa.void_ritual_increased_chance_active=1',
                            ]
                            simulation_group.add(copy)

            logger.info(
                "Start {} corruption simulation for {} {}.".format(
                    fight_style, wow_class, wow_spec
                )
            )
            try:
                if settings.use_raidbots and settings.apikey:
                    settings.simc_hash = simulation_group.simulate_with_raidbots(settings.apikey)
                else:
                    simulation_group.simulate()
            except Exception as e:
                logger.error(
                    "{} corruption simulation for {} {} failed. {}".format(
                        fight_style.title(), wow_class, wow_spec, e
                    )
                )
                continue
            else:
                logger.info(
                    "{} corruption simulation for {} {} ended successfully. Cleaning up.".format(
                        fight_style.title(), wow_class, wow_spec
                    )
                )

            for profile in simulation_group.profiles:
                logger.debug("Profile '{}' DPS: {}".format(profile.name, profile.get_dps()))

            logger.debug("Created base dict for json export. {}".format(wanted_data))

            if not 'data' in wanted_data:
                wanted_data['data'] = {}

            # add dps values to json
            for profile in simulation_group.profiles:

                if 'baseline' in profile.name:
                    if not 'baseline' in wanted_data['data'].keys():
                        wanted_data['data']['baseline'] = {}

                    wanted_data['data']['baseline'][profile.name.split('_')[1]] = profile.get_dps()
                    logger.debug(
                        "Added '{}' with {} dps to json.".format(profile.name, profile.get_dps())
                    )
                    continue

                corruption_name: str = profile.name.split('_')[0]
                corruption_rank: int = profile.name.split('_')[1].split('+')[0]
                corruption_ilevel: int = None
                try:
                    corruption_ilevel = profile.name.split('_')[2]
                except IndexError:
                    pass
                corruption_bonus_id: int = corruptions[corruption_name][corruption_rank]['bonus_id'
                                                                                         ]
                corruption_spell_id: int = corruptions[corruption_name][corruption_rank]['spell_id'
                                                                                         ]
                corruption_rating: int = corruptions[corruption_name][corruption_rank]['corruption'
                                                                                       ]
                try:
                    corruption_full_name: str = corruption_name + '_' + corruption_rank + f' ({corruption_rating})' + '+' + profile.name.split(
                        '+'
                    )[1]
                except IndexError:
                    corruption_full_name: str = corruption_name + '_' + corruption_rank + f' ({corruption_rating})'

                # create missing subdict for dps
                if not corruption_full_name in wanted_data['data']:
                    wanted_data['data'][corruption_full_name] = {}

                if corruption_ilevel == None:
                    wanted_data['data'][corruption_full_name][settings.azerite_trait_ilevels[0]
                                                              ] = profile.get_dps()
                else:
                    wanted_data['data'][corruption_full_name][corruption_ilevel] = profile.get_dps(
                    )
                logger.debug(
                    "Added '{}' with {} dps to json.".format(
                        corruption_full_name, profile.get_dps()
                    )
                )

                # create missing subdict for spell data
                if not 'spell_ids' in wanted_data:
                    wanted_data['spell_ids'] = {}

                if not corruption_full_name in wanted_data['spell_ids']:
                    wanted_data['spell_ids'][corruption_full_name] = {}

                wanted_data['spell_ids'][corruption_full_name] = corruption_spell_id

                # create missing subdict for corruption rating
                if not 'corruption_rating' in wanted_data:
                    wanted_data['corruption_rating'] = {}

                if not corruption_full_name in wanted_data['corruption_rating']:
                    wanted_data['corruption_rating'][corruption_full_name] = {}

                wanted_data['corruption_rating'][corruption_full_name] = corruption_rating

            # create ordered corruption name list
            tmp_list = []     # dps
            tmp_list_2 = []     # dps/corruption rating without duplicates
            corruption_name: str
            for corruption_name in wanted_data['data']:
                if corruption_name == 'baseline':
                    continue

                highest_ilevel = sorted(
                    wanted_data['data'][corruption_name].keys(), reverse=True
                )[0]
                rank = corruption_name.split('_')[1].split('+')[0].split(' (')[0]

                # append highest itemlevel of corruption to sortable dps list
                tmp_list.append((
                    corruption_name, wanted_data['data'][corruption_name][highest_ilevel] -
                    wanted_data['data']['baseline'][highest_ilevel]
                ))

                # don't add to list if a higher rank is available
                higher_rank = None
                try:
                    higher_rank = corruption_name.split('_')[0] + '_' + str(
                        int(rank) + 1
                    ) + f' ({corruptions[corruption_name.split("_")[0]][str(int(rank) + 1)]["corruption"]})' + '+' + corruption_name.split(
                        '+'
                    )[1]
                except IndexError:
                    try:
                        higher_rank = corruption_name.split('_')[0] + '_' + str(
                            int(rank) + 1
                        ) + f' ({corruptions[corruption_name.split("_")[0]][str(int(rank) + 1)]["corruption"]})'
                    except KeyError:
                        pass
                except KeyError:
                    pass
                if not higher_rank or 'Ineffable Truth' in corruption_name:
                    tmp_list_2.append((
                        f'{corruption_name}', (
                            wanted_data['data'][corruption_name][highest_ilevel] -
                            wanted_data['data']['baseline'][highest_ilevel]
                        ) / wanted_data['corruption_rating'][corruption_name]
                    ))

            logger.debug("tmp_list: {}".format(tmp_list))
            logger.debug("tmp_list_2: {}".format(tmp_list_2))

            tmp_list = sorted(tmp_list, key=lambda item: item[1], reverse=True)
            logger.debug("Sorted tmp_list: {}".format(tmp_list))
            logger.info("Corruption {} won with {} dps.".format(tmp_list[0][0], tmp_list[0][1]))

            wanted_data["sorted_data_keys"] = []
            for corruption_name, _ in tmp_list:
                wanted_data["sorted_data_keys"].append(corruption_name)

            tmp_list_2 = sorted(tmp_list_2, key=lambda item: item[1], reverse=True)
            logger.debug("Sorted tmp_list_2: {}".format(tmp_list_2))
            logger.info(
                "Corruption {} won with {} dps.".format(tmp_list_2[0][0], tmp_list_2[0][1])
            )

            wanted_data["sorted_data_keys_2"] = []
            for corruption_name, _ in tmp_list_2:
                wanted_data["sorted_data_keys_2"].append(corruption_name)

            # add simulated steps
            wanted_data['simulated_steps'] = settings.azerite_trait_ilevels[::-1]

            logger.debug("Final json: {}".format(wanted_data))

            # write json to file
            partial_path: str = "results/corruptions/"
            if not os.path.isdir(partial_path):
                os.makedirs(partial_path)

            with open(
                "{}{}_{}_{}.json".format(
                    partial_path, wow_class.lower(), wow_spec.lower(), fight_style.lower()
                ),
                "w",
                encoding="utf-8"
            ) as f:
                logger.debug("Print corruption json.")
                f.write(json.dumps(wanted_data, sort_keys=True, indent=4, ensure_ascii=False))
                logger.debug("Printed corruption json.")

    logger.debug("corruption_simulation ended")

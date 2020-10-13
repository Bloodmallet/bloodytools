import json
import os

from bloodytools.special_cases import special_cases
from bloodytools.simulation_objects.simulation_objects import Simulation_Data
from bloodytools.simulation_objects.simulation_objects import Simulation_Group
from bloodytools.utils.utils import create_base_json_dict
from bloodytools.utils.utils import create_basic_profile_string
from bloodytools.utils.utils import tokenize_str
from simc_support import wow_lib
from typing import List, Tuple


def azerite_trait_simulations(settings) -> None:
    """Simulate all azerite traits with an adjusted head itemlevel. Create json with trait values and with all known azerite items and their sumed up trait dps values.

    Args:
        specs (List[Tuple[str, str]]): all wow_specs you want to be simulated, e.g. `[('shaman', 'elemental'), ('warrior', 'arms')]`

    Raises:
        e: [description]

    Returns:
        None: Files will be created in /results/azerite_traits/
    """
    logger = settings.logger

    logger.debug("azerite_trait_simulations start")
    specs = settings.wow_class_spec_list
    for fight_style in settings.fight_styles:
        for wow_class, wow_spec in specs:

            basic_profile_string = create_basic_profile_string(
                wow_class, wow_spec, settings.tier, settings
            )

            # check whether the baseline profile does exist
            try:
                with open(basic_profile_string, 'r') as f:
                    for line in f:
                        if "head=" in line:
                            item_head = line[:-1]
            except FileNotFoundError:
                logger.warning(
                    "{} {} profile not found. Skipping.".format(
                        wow_spec.title(), wow_class.title()
                    )
                )
                # end this try early, no profile, no calculations
                continue

            if settings.custom_profile:
                try:
                    with open('custom_profile.txt', 'r') as f:
                        for line in f:
                            if "head=" in line:
                                item_head = line[:-1]
                except FileNotFoundError:
                    logger.warning(
                        "{} {} profile not found. Skipping.".format(
                            wow_spec.title(), wow_class.title()
                        )
                    )
                    # end this try early, no profile, no calculations
                    continue

            # save data to json
            wanted_data = create_base_json_dict(
                "Azerite Traits", wow_class, wow_spec, fight_style, settings
            )

            # fix base profile to match sim
            wanted_data["profile"]["head"].pop("azerite_powers", None)
            wanted_data["profile"]["shoulders"].pop("azerite_powers", None)
            wanted_data["profile"]["chest"].pop("azerite_powers", None)
            wanted_data['profile']['items']['head'].pop('azerite_powers', None)
            wanted_data['profile']['items']['shoulders'].pop('azerite_powers', None)
            wanted_data['profile']['items']['chest'].pop('azerite_powers', None)

            # adjust profile data for frontend for general special cases
            try:
                if '*' in special_cases[wow_class][wow_spec][fight_style][
                        'azerite_trait_simulations']:
                    data = special_cases[wow_class][wow_spec][fight_style][
                        'azerite_trait_simulations']['*'][0]
                    extra_trait_id = data['base_trait_id']
                    wanted_data['profile']['items']['head']['azerite_powers'] = extra_trait_id
                    wanted_data['profile']['head']['azerite_powers'] = extra_trait_id
            except Exception:
                pass

            item_head2 = 'head='
            for attribute, value in wanted_data['profile']['items']['head'].items():
                item_head2 += ',{}={}'.format(attribute, value)
            item_head = item_head2

            # create simulation GROUP
            azerite_traits = wow_lib.get_azerite_traits(wow_class, wow_spec)
            simulation_group = Simulation_Group(
                name="azerite_trait_simulations",
                threads=settings.threads,
                profileset_work_threads=settings.profileset_work_threads,
                executable=settings.executable,
                logger=logger
            )

            reset_string = "disable_azerite=items"

            # create baseline profile/-s
            # need this special handling of the first profile or else the other baseline profiles won't simulate correctly
            simulation_data = Simulation_Data(
                name="baseline 1_{}".format(settings.azerite_trait_ilevels[0]),
                fight_style=fight_style,
                profile=wanted_data['profile'],
                simc_arguments=[
                    reset_string,
                    item_head +
                    ",ilevel={}".format(settings.azerite_trait_ilevels[0]),
                ],
                target_error=settings.target_error[fight_style],
                executable=settings.executable,
                iterations=settings.iterations,
                ptr=settings.ptr,
                default_actions=settings.default_actions,
                logger=logger
            )
            try:
                if '*' in special_cases[wow_class][wow_spec][fight_style][
                        'azerite_trait_simulations']:
                    for change in special_cases[wow_class][wow_spec][fight_style][
                            'azerite_trait_simulations']['*']:
                        for additional_input in change['additional_input']:
                            simulation_data.simc_arguments.append(
                                '{}{}'.format(
                                    additional_input.replace(
                                        '<itemlevel>', ''),
                                    settings.azerite_trait_ilevels[0]
                                )
                            )
            except Exception:
                # logger.debug('No * special case.')
                pass
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

            # still baseline profiles, but special handled to get all itemlevels for the baseline too
            for itemlevel in settings.azerite_trait_ilevels:
                if itemlevel != settings.azerite_trait_ilevels[0]:
                    simulation_data = Simulation_Data(
                        name="baseline 1_{}".format(itemlevel),
                        fight_style=fight_style,
                        simc_arguments=[item_head +
                                        ",ilevel={}".format(itemlevel)],
                        target_error=settings.target_error[fight_style],
                        executable=settings.executable,
                        iterations=settings.iterations,
                        ptr=settings.ptr,
                        default_actions=settings.default_actions,
                        logger=logger
                    )
                    try:
                        if '*' in special_cases[wow_class][wow_spec][fight_style][
                                'azerite_trait_simulations']:
                            for change in special_cases[wow_class][wow_spec][fight_style][
                                    'azerite_trait_simulations']['*']:
                                for additional_input in change['additional_input']:
                                    simulation_data.simc_arguments.append(
                                        '{}{}'.format(
                                            additional_input.replace(
                                                '<itemlevel>', ''), itemlevel
                                        )
                                    )
                    except Exception:
                        logger.debug('No * special case.')
                    simulation_group.add(simulation_data)

            azerite_trait_name_spell_id_dict = {}

            # trait_special_handles are general additions for all specs and classes, based on the traits
            # current use are raid specific traits
            trait_special_handles = {
                # "Laser Matrix": {
                #   "additional_profiles": [
                #     {
                #       "new_name": "Laser Matrix +5RA",
                #       "translation_addition": " +5RA",
                #       "additional_input": ["bfa.reorigination_array_stacks=5"]
                #     }, {
                #       "new_name": "Laser Matrix +10RA",
                #       "translation_addition": " +10RA",
                #       "additional_input": ["bfa.reorigination_array_stacks=10"]
                #     }
                #   ],
                #   "additional_input": []
                # },
            }

            # add necessary spelldta manually
            # azerite_trait_name_spell_id_dict["5RA"] = "281237"
            # azerite_trait_name_spell_id_dict["10RA"] = "281237"

            for azerite_trait_spell_id in azerite_traits:

                for itemlevel in settings.azerite_trait_ilevels:

                    azerite_trait = azerite_traits[azerite_trait_spell_id]['name']

                    # skip itemlevel if it's not available for that trait
                    if azerite_traits[azerite_trait_spell_id]['min_itemlevel'] > int(itemlevel) or (
                        azerite_traits[azerite_trait_spell_id]['max_itemlevel'] < int(
                            itemlevel)
                        and azerite_traits[azerite_trait_spell_id]['max_itemlevel'] != -1
                    ):

                        logger.debug(
                            "Skipping trait <{}> at itemlevel {} due to itemlevel restrictions, min: {}, max: {}"
                            .format(
                                azerite_trait, itemlevel,
                                azerite_traits[azerite_trait_spell_id]['min_itemlevel'],
                                azerite_traits[azerite_trait_spell_id]['max_itemlevel']
                            )
                        )
                        continue

                    # add special handled (added) azerite traits with their correct baseline spellid
                    if not azerite_trait in azerite_trait_name_spell_id_dict:
                        azerite_trait_name_spell_id_dict[azerite_trait.split(" (")[0]
                                                         ] = azerite_trait_spell_id

                        if azerite_trait in trait_special_handles:
                            logger.debug(
                                "Adding special handled entries to azerite_trait_name_spell_id_dict"
                            )
                            for entry in trait_special_handles[azerite_trait]["additional_profiles"
                                                                              ]:
                                azerite_trait_name_spell_id_dict[entry["new_name"]
                                                                 ] = azerite_trait_spell_id

                        try:
                            special_case_list = special_cases[wow_class][wow_spec][fight_style][
                                "azerite_trait_simulations"][azerite_trait]
                        except Exception:
                            pass
                        else:
                            for special_case in special_case_list:
                                azerite_trait_name_spell_id_dict[
                                    azerite_trait + " +" +
                                    special_case["suffix"]] = azerite_trait_spell_id

                    simulation_data = None

                    # azerite_override=
                    trait_input = "azerite_override={}:{}".format(
                        tokenize_str(azerite_trait), itemlevel
                    )

                    try:
                        if '*' in special_cases[wow_class][wow_spec][fight_style][
                                'azerite_trait_simulations']:
                            for change in special_cases[wow_class][wow_spec][fight_style][
                                    'azerite_trait_simulations']['*']:
                                for additional_input in change['additional_input']:
                                    trait_input += '/{}{}'.format(
                                        additional_input.replace('<itemlevel>', '').replace(
                                            'azerite_override=', ''
                                        ), itemlevel
                                    )
                    except Exception:
                        logger.debug('No * special case.')

                    # create the new head input
                    head_input = item_head
                    if azerite_trait == "Azerite Empowered":
                        head_input += ",ilevel={}".format(int(itemlevel) + 5)
                    else:
                        head_input += ",ilevel={}".format(itemlevel)

                    simulation_data = Simulation_Data(
                        name='{} 1_{}'.format(
                            azerite_trait.split(" (")[0], itemlevel),
                        fight_style=fight_style,
                        simc_arguments=[trait_input, head_input],
                        target_error=settings.target_error[fight_style],
                        executable=settings.executable,
                        ptr=settings.ptr,
                        default_actions=settings.default_actions,
                        logger=logger
                    )

                    # add additional input from the generate trait_special_handles
                    if azerite_trait in trait_special_handles:
                        for entry in trait_special_handles[azerite_trait]["additional_input"]:
                            simulation_data.simc_arguments.append(entry)

                    try:
                        special_cases[wow_class][wow_spec][fight_style]['azerite_trait_simulations'
                                                                        ]['*']
                    except KeyError:
                        simulation_group.add(simulation_data)
                    else:
                        base_trait = None
                        for change in special_cases[wow_class][wow_spec][fight_style][
                                'azerite_trait_simulations']['*']:
                            base_trait = change['base_trait']
                        if base_trait != azerite_trait:
                            simulation_group.add(simulation_data)
                        else:
                            logger.debug(
                                'Not adding {} to simulation_group'.format(base_trait))
                    logger.debug((
                        "Added azerite trait '{}' at itemlevel {} in profile '{}' to simulation_group."
                        .format(azerite_trait, itemlevel, simulation_data.name)
                    ))

                    # create more profiles based on trait_special handles
                    if azerite_trait in trait_special_handles:
                        simulation_data = simulation_data.copy()
                        for profile in trait_special_handles[azerite_trait]["additional_profiles"]:
                            simulation_data.name = "{} 1_{}".format(
                                profile["new_name"], itemlevel)

                            for input_string in profile["additional_input"]:
                                simulation_data.simc_arguments.append(
                                    input_string)

                            simulation_group.add(simulation_data)
                            logger.debug((
                                "Added azerite trait '{}' at itemlevel {} in profile '{}' to simulation_group."
                                .format(input_string, itemlevel, simulation_data.name)
                            ))
                            # create copy to not accidentally manipulate the already to simulation_group added profile
                            simulation_data = simulation_data.copy()
                            # delete the profile specific additional input from the new copy
                            simulation_data.simc_arguments = simulation_data.simc_arguments[:-len(
                                profile["additional_input"]
                            )]

                    # add spec specific special_cases profiles to the simulation_group
                    try:
                        special_list = special_cases[wow_class][wow_spec][fight_style][
                            "azerite_trait_simulations"][azerite_trait]
                    except Exception as e:
                        logger.debug(
                            "No special case for {} of {} {} for fight_style {} was found. Error: {}"
                            .format(azerite_trait, wow_spec, wow_class, fight_style, e)
                        )
                    else:
                        # create independant copy to not alter the existing profile in simulation_group
                        simulation_data = simulation_data.copy()

                        for special_information in special_list:
                            simulation_data.name = "{} +{} 1_{}".format(
                                azerite_trait, special_information["suffix"], itemlevel
                            )
                            for item in special_information["additional_input"]:
                                simulation_data.simc_arguments.append(item)

                            # add spell ids to dict
                            for new_addition in special_information["link_data"]:
                                azerite_trait_name_spell_id_dict[
                                    new_addition] = special_information["link_data"][new_addition][
                                        "spell_id"]

                            simulation_group.add(simulation_data)
                            simulation_data = simulation_data.copy()
                            # delete additional input again
                            simulation_data.simc_arguments = simulation_data.simc_arguments[:-len(
                                special_information["additional_input"]
                            )]

                    # add stacked traits profiles to simulationgroup at max itemlevel
                    if itemlevel == settings.azerite_trait_ilevels[-1] or int(itemlevel) == int(
                        azerite_traits[azerite_trait_spell_id]['max_itemlevel']
                    ):

                        # create the new head input for 2 stacks
                        if azerite_traits[azerite_trait_spell_id]["max_stack"] >= 2:
                            head_input = item_head
                            if azerite_trait == "Azerite Empowered":
                                head_input += ",ilevel={}".format(
                                    int(itemlevel) + 10)
                            else:
                                head_input += ",ilevel={}".format(itemlevel)

                            logger.debug(
                                "Adding stacked azerite traits to highest itemlevel.")
                            doublicate_text = "/{}:{}".format(
                                tokenize_str(azerite_trait), itemlevel
                            )
                            simulation_data = None
                            simulation_data = Simulation_Data(
                                name='{} 2_{}'.format(
                                    azerite_trait.split(" (")[0], itemlevel),
                                fight_style=fight_style,
                                simc_arguments=[trait_input +
                                                doublicate_text, head_input],
                                target_error=settings.target_error[fight_style],
                                executable=settings.executable,
                                ptr=settings.ptr,
                                default_actions=settings.default_actions,
                                logger=logger
                            )

                            # add generally needed additional input
                            if azerite_trait in trait_special_handles:
                                for input_string in trait_special_handles[azerite_trait][
                                        "additional_input"]:
                                    simulation_data.simc_arguments.append(
                                        input_string)
                            # add data to group
                            simulation_group.add(simulation_data)

                            # add spec specific special_cases profiles to the simulation_group
                            try:
                                special_list = special_cases[wow_class][wow_spec][fight_style][
                                    "azerite_trait_simulations"][azerite_trait]
                            except Exception as e:
                                logger.debug(
                                    "No special case for {} of {} {} for fight_style {} was found. Error: {}"
                                    .format(azerite_trait, wow_spec, wow_class, fight_style, e)
                                )
                            else:
                                # create independant copy to not alter the existing profile in simulation_group
                                simulation_data = simulation_data.copy()

                                for special_information in special_list:
                                    simulation_data.name = "{} +{} 2_{}".format(
                                        azerite_trait, special_information["suffix"], itemlevel
                                    )
                                    for item in special_information["additional_input"]:
                                        simulation_data.simc_arguments.append(
                                            item)

                                    simulation_group.add(simulation_data)
                                    simulation_data = simulation_data.copy()
                                    # delete additional input again
                                    simulation_data.simc_arguments = simulation_data.simc_arguments[:-len(
                                        special_information["additional_input"]
                                    )]

                            # add additional profiles from trait_special_handles
                            if azerite_trait in trait_special_handles:
                                simulation_data = simulation_data.copy()

                                for profile in trait_special_handles[azerite_trait][
                                        "additional_profiles"]:
                                    simulation_data.name = "{} 2_{}".format(
                                        profile["new_name"], itemlevel
                                    )

                                    for input_string in profile["additional_input"]:
                                        simulation_data.simc_arguments.append(
                                            input_string)

                                    simulation_group.add(simulation_data)
                                    logger.debug((
                                        "Added azerite trait '{}' at itemlevel {} in profile '{}' to simulation_group."
                                        .format(input_string, itemlevel, simulation_data.name)
                                    ))

                                    # reset simulation_data
                                    simulation_data = simulation_data.copy()
                                    simulation_data.simc_arguments = simulation_data.simc_arguments[:-len(
                                        profile["additional_input"]
                                    )]

                        # create the new head input for 3 stacks
                        if azerite_traits[azerite_trait_spell_id]["max_stack"] >= 3:
                            head_input = item_head
                            if azerite_trait == "Azerite Empowered":
                                head_input += ",ilevel={}".format(
                                    int(itemlevel) + 15)
                            else:
                                head_input += ",ilevel={}".format(itemlevel)

                            simulation_data = None
                            simulation_data = Simulation_Data(
                                name='{} 3_{}'.format(
                                    azerite_trait.split(" (")[0], itemlevel),
                                fight_style=fight_style,
                                simc_arguments=[
                                    trait_input + doublicate_text + doublicate_text, head_input
                                ],
                                target_error=settings.target_error[fight_style],
                                executable=settings.executable,
                                ptr=settings.ptr,
                                default_actions=settings.default_actions,
                                logger=logger
                            )

                            if azerite_trait in trait_special_handles:
                                for input_string in trait_special_handles[azerite_trait][
                                        "additional_input"]:
                                    simulation_data.simc_arguments.append(
                                        input_string)
                            simulation_group.add(simulation_data)

                            # add spec specific special_cases profiles to the simulation_group
                            try:
                                special_list = special_cases[wow_class][wow_spec][fight_style][
                                    "azerite_trait_simulations"][azerite_trait]
                            except Exception as e:
                                logger.debug(
                                    "No special case for {} of {} {} for fight_style {} was found. Error: {}"
                                    .format(azerite_trait, wow_spec, wow_class, fight_style, e)
                                )
                            else:
                                # create independant copy to not alter the existing profile in simulation_group
                                simulation_data = simulation_data.copy()

                                for special_information in special_list:
                                    simulation_data.name = "{} +{} 3_{}".format(
                                        azerite_trait, special_information["suffix"], itemlevel
                                    )
                                    for item in special_information["additional_input"]:
                                        simulation_data.simc_arguments.append(
                                            item)

                                    simulation_group.add(simulation_data)
                                    simulation_data = simulation_data.copy()
                                    # delete additional input again
                                    simulation_data.simc_arguments = simulation_data.simc_arguments[:-len(
                                        special_information["additional_input"]
                                    )]

                            if azerite_trait in trait_special_handles:
                                simulation_data = simulation_data.copy()
                                for profile in trait_special_handles[azerite_trait][
                                        "additional_profiles"]:

                                    simulation_data.name = "{} 3_{}".format(
                                        profile["new_name"], itemlevel
                                    )

                                    for input_string in profile["additional_input"]:
                                        simulation_data.simc_arguments.append(
                                            input_string)

                                    simulation_group.add(simulation_data)
                                    logger.debug((
                                        "Added azerite trait '{}' at itemlevel {} in profile '{}' to simulation_group."
                                        .format(input_string, itemlevel, simulation_data.name)
                                    ))
                                    simulation_data = simulation_data.copy()
                                    simulation_data.simc_arguments = simulation_data.simc_arguments[:-len(
                                        profile["additional_input"]
                                    )]

            logger.info(
                "Start {} azerite_trait simulation for {} {}. {} profiles.".format(
                    fight_style, wow_class.title(), wow_spec.title(),
                    len(simulation_group.profiles)
                )
            )
            try:
                if settings.use_raidbots and settings.apikey:
                    settings.simc_hash = simulation_group.simulate_with_raidbots(
                        settings.apikey)
                else:
                    simulation_group.simulate()
            except Exception as e:
                logger.error(
                    "{} azerite_trait simulation for {} {} failed. {}".format(
                        fight_style.title(), wow_class.title(), wow_spec.title(), e
                    )
                )
                continue
            else:
                logger.info(
                    "{} azerite_trait simulation for {} {} ended successfully. Cleaning up."
                    .format(fight_style.title(), wow_class.title(), wow_spec.title())
                )

            for profile in simulation_group.profiles:
                logger.debug("Profile '{}' DPS: {}".format(
                    profile.name, profile.get_dps()))

            logger.debug(
                "Created base dict for json export. {}".format(wanted_data))

            # update used ilevel steps to the correct keys
            # add itemlevel list
            wanted_data["simulated_steps"] = []
            for itemlevel in settings.azerite_trait_ilevels:
                wanted_data["simulated_steps"].insert(0, "1_" + itemlevel)

            # add dps values to json
            for profile in simulation_group.profiles:
                azerite_trait_name = " ".join(profile.name.split()[:-1])
                azerite_trait_ilevel = profile.name.split()[-1]

                if not azerite_trait_name in wanted_data["data"]:
                    wanted_data["data"][azerite_trait_name] = {}

                wanted_data["data"][azerite_trait_name][azerite_trait_ilevel] = profile.get_dps(
                )

                # add translations for special cases to wanted_data
                if not azerite_trait_name in wanted_data[
                        "languages"] and not "baseline" in azerite_trait_name:
                    wanted_data["languages"][azerite_trait_name] = wow_lib.get_trait_translation(
                        azerite_trait_name
                    )

                    for special_handle in trait_special_handles:
                        if special_handle in azerite_trait_name:
                            for trait_profile in trait_special_handles[special_handle][
                                    "additional_profiles"]:
                                if trait_profile["new_name"] == azerite_trait_name:
                                    for language in wanted_data["languages"][azerite_trait_name]:
                                        wanted_data["languages"][azerite_trait_name][
                                            language
                                        ] = wanted_data["languages"][azerite_trait_name][
                                            language] + trait_profile["translation_addition"]

                    try:
                        special_list = special_cases[wow_class][wow_spec][fight_style][
                            "azerite_trait_simulations"][azerite_trait_name.split("+")[0][:-1]]
                    except Exception:
                        pass
                    else:
                        if "+" in azerite_trait_name:
                            for special_case in special_list:
                                if azerite_trait_name == azerite_trait_name.split("+")[
                                        0] + "+" + special_case["suffix"]:
                                    for language in wanted_data["languages"][azerite_trait_name]:
                                        wanted_data["languages"][azerite_trait_name][
                                            language] = wanted_data["languages"][
                                                azerite_trait_name][language] + " +{}".format(
                                                    special_case["suffix"]
                                        )

                logger.debug(
                    "Added '{}' with {} dps to json.".format(
                        profile.name, profile.get_dps())
                )

            # fix general special case into existance
            try:
                if '*' in special_cases[wow_class][wow_spec][fight_style][
                        'azerite_trait_simulations']:
                    for change in special_cases[wow_class][wow_spec][fight_style][
                            'azerite_trait_simulations']['*']:
                        for additional_input in change['additional_input']:
                            for itemlevel in settings.azerite_trait_ilevels:
                                wanted_data['data'][change['base_trait']][
                                    '1_' + itemlevel] = wanted_data['data']['baseline']['1_' +
                                                                                        itemlevel]
            except Exception:
                pass

            # create azerite name list based on highest simulated itemlevel of traits
            tmp_list = []
            for trait in wanted_data["data"]:
                max_available_itemlevel = "1_" + \
                    settings.azerite_trait_ilevels[-1]
                if not max_available_itemlevel in wanted_data["data"][trait]:
                    max_available_itemlevel = sorted(
                        wanted_data["data"][trait])[-1]
                    if "1_" != max_available_itemlevel[:2]:
                        max_available_itemlevel = "1_" + \
                            max_available_itemlevel[2:]

                try:
                    tmp_list.append((
                        trait, wanted_data["data"][trait][max_available_itemlevel],
                        wanted_data["data"]["baseline"][max_available_itemlevel]
                    ))
                except Exception:
                    logger.error(
                        "{}, {}, {}".format(
                            trait, max_available_itemlevel, wanted_data["data"][trait]
                        )
                    )
            logger.debug("tmp_list: {}".format(tmp_list))

            # sort
            tmp_list = sorted(tmp_list, key=lambda item: item[1], reverse=True)
            logger.debug("Sorted tmp_list: {}".format(tmp_list))
            logger.info(
                "Solo Azerite Trait {} won with {} dps.".format(
                    tmp_list[0][0], tmp_list[0][1])
            )

            azerite_weight_string = "( AzeritePowerWeights:2:\"{fight_style} {wow_spec} {wow_class}\":{class_id}:{spec_id}:".format(
                fight_style=fight_style.title(),
                wow_spec=wow_spec.title(),
                wow_class=wow_class.title(),
                class_id=wow_lib.get_class_id(wow_class),
                spec_id=wow_lib.get_spec_id(wow_class, wow_spec)
            )

            azerite_forge_string_itemlevel = "AZFORGE:{}:{}^".format(
                wow_lib.get_class_id(wow_class), wow_lib.get_spec_id(
                    wow_class, wow_spec)
            )
            azerite_forge_string_trait_stacking = "AZFORGE:{}:{}^".format(
                wow_lib.get_class_id(wow_class), wow_lib.get_spec_id(
                    wow_class, wow_spec)
            )

            # sorted ilevel trait list (one trait at max itemlevel each)
            wanted_data["sorted_data_keys"] = []

            for azerite_trait, at_dps, base_dps in tmp_list:
                wanted_data["sorted_data_keys"].append(azerite_trait)

                power_id = ""
                for spell_id in azerite_traits:
                    if azerite_traits[spell_id]["name"] == azerite_trait:
                        power_id = azerite_traits[spell_id]["trait_id"]

                if power_id:
                    azerite_weight_string += " {}={},".format(
                        power_id, at_dps - base_dps)

                    max_available_itemlevel = "1_" + \
                        settings.azerite_trait_ilevels[-1]
                    if not max_available_itemlevel in wanted_data["data"][azerite_trait]:
                        max_available_itemlevel = sorted(
                            wanted_data["data"][azerite_trait])[-1]

                    azerite_forge_string_trait_stacking += "[{}]".format(
                        power_id)
                    for trait_count in [1, 2, 3]:
                        try:
                            azerite_forge_string_trait_stacking += "{}:{},".format(
                                trait_count, wanted_data['data'][azerite_trait]
                                [str(trait_count) + '_' + max_available_itemlevel.split('1_')[1]] -
                                base_dps
                            )
                        except Exception:
                            pass
                    azerite_forge_string_trait_stacking += "^"

                    min_available_itemlevel = "1_" + \
                        settings.azerite_trait_ilevels[0]
                    if not min_available_itemlevel in wanted_data["data"][azerite_trait]:
                        min_available_itemlevel = sorted(
                            wanted_data["data"][azerite_trait])[0]

                    azerite_forge_string_itemlevel += "[{}]".format(power_id)
                    for itemlevel in wanted_data["data"][azerite_trait]:
                        if "1_" in itemlevel:
                            azerite_forge_string_itemlevel += "{}:{},".format(
                                itemlevel.split("1_")[1],
                                wanted_data["data"][azerite_trait][itemlevel] -
                                wanted_data["data"]["baseline"][min_available_itemlevel]
                            )
                    azerite_forge_string_itemlevel += "^"

            azerite_weight_string = azerite_weight_string[:-1] + ": )"

            wanted_data["azerite_weight_{}".format(
                fight_style)] = azerite_weight_string

            wanted_data["azerite_forge_{}_itemlevel".format(fight_style)
                        ] = azerite_forge_string_itemlevel

            wanted_data["azerite_forge_{}_trait_stacking".format(fight_style)
                        ] = azerite_forge_string_trait_stacking

            # TODO: make this previous passage about azerite_weight_string better
            # input from HawkCorrigan:
            # baseline_dps_385 = wanted_data['data']['baseline']['1_385']
            # list(map(lambda x: {(azerite_traits.get(find(lambda traitid: azerite_traits[traitid]['name'] == x, azerite_traits), {}).get('trait_id', 0)): round(max( wanted_data['data'][x].values())-baseline_dps_385, 2)}, wanted_data['data']))

            logger.debug(wanted_data["azerite_weight_{}".format(fight_style)])

            # create secondary azerite name list (tripple azerite trait at max itemlevel each)
            tmp_list = []
            for trait in wanted_data["data"]:
                if not "baseline" in trait:

                    max_available_itemlevel = "3_" + \
                        settings.azerite_trait_ilevels[-1]
                    if not max_available_itemlevel in wanted_data["data"][trait]:
                        max_available_itemlevel = sorted(
                            wanted_data["data"][trait])[-1]

                    tmp_list.append(
                        (trait, wanted_data["data"][trait][max_available_itemlevel]))
            logger.debug("tmp_list: {}".format(tmp_list))

            # sort
            tmp_list = sorted(tmp_list, key=lambda item: item[1], reverse=True)
            logger.debug("Sorted tmp_list: {}".format(tmp_list))
            logger.info(
                "Tripple stacked Azerite Trait {} won with {} dps.".format(
                    tmp_list[0][0], tmp_list[0][1]
                )
            )

            # sorted stacked trait list
            wanted_data["sorted_data_keys_2"] = []
            for azerite_trait, _ in tmp_list:
                wanted_data["sorted_data_keys_2"].append(azerite_trait)

            # create sorted tier 1 ilevel list
            # create sorted tier 2 ilevel list
            tmp_tier1_ilvl = []
            tmp_tier2_ilvl = []
            # create sorted tier 1 stacked list
            # create sorted tier 2 stacked list
            tmp_tier1_stacked = []
            tmp_tier2_stacked = []

            for trait in wanted_data["data"]:
                if not "baseline" in trait:

                    try:
                        trait_id = azerite_trait_name_spell_id_dict[trait]
                    except Exception:
                        # exception occurs for spec specific special_cases
                        trait_id = azerite_trait_name_spell_id_dict[trait.split(
                            "+")[0][:-1]]

                    # check for tier 2, to allow azerite empowered in tier 1 data
                    if 2 in wow_lib.get_azerite_tiers(wow_class, wow_spec, str(trait_id)):
                        tmp_tier2_ilvl.append((
                            trait,
                            wanted_data["data"][trait]["1_" +
                                                       settings.azerite_trait_ilevels[-1]]
                        ))
                        tmp_tier2_stacked.append((
                            trait,
                            wanted_data["data"][trait]["3_" +
                                                       settings.azerite_trait_ilevels[-1]]
                        ))

                    elif 1 in wow_lib.get_azerite_tiers(
                        wow_class, wow_spec, str(trait_id)
                    ) or 3 in wow_lib.get_azerite_tiers(
                        wow_class, wow_spec, str(trait_id)
                    ) or 4 in wow_lib.get_azerite_tiers(wow_class, wow_spec, str(trait_id)):

                        max_available_itemlevel = "1_" + \
                            settings.azerite_trait_ilevels[-1]
                        if not max_available_itemlevel in wanted_data["data"][trait]:
                            i = len(settings.azerite_trait_ilevels) - 1
                            while i >= 0:
                                max_available_itemlevel = "1_" + \
                                    settings.azerite_trait_ilevels[i]
                                if max_available_itemlevel in wanted_data["data"][trait]:
                                    i = -1
                                i -= 1

                        try:
                            tmp_tier1_ilvl.append(
                                (trait, wanted_data["data"]
                                 [trait][max_available_itemlevel])
                            )
                        except KeyError:
                            tmp_tier1_ilvl.append((
                                trait,
                                0,
                            ))
                            logger.debug(
                                'adding dps 0 for {} to tmp_tier1_ilvl list'.format(
                                    trait)
                            )
                        tmp_tier1_stacked.append((
                            trait,
                            wanted_data["data"][trait][sorted(wanted_data["data"][trait])[-1]] -
                            wanted_data["data"]["baseline"][
                                sorted(
                                    wanted_data["data"][trait]
                                )[-1].replace("3_", "1_").replace("2_", "1_")
                            ]
                        ))
                    else:
                        if int(trait_id) != 263978:
                            logger.error(
                                "Somehow a valid trait is neither of tier 1, 3, or 4. Trait id: {}"
                                .format(trait_id)
                            )

            logger.debug("tmp_tier1: {}".format(tmp_tier1_ilvl))
            logger.debug("tmp_tier2: {}".format(tmp_tier2_ilvl))
            # sort
            tmp_tier1_ilvl = sorted(
                tmp_tier1_ilvl, key=lambda item: item[1], reverse=True)
            tmp_tier2_ilvl = sorted(
                tmp_tier2_ilvl, key=lambda item: item[1], reverse=True)
            logger.debug("Sorted tmp_tier1: {}".format(tmp_tier1_ilvl))
            logger.info(
                "Tier 1 Trait {} won with {} dps in ilevel category.".format(
                    tmp_tier1_ilvl[0][0], tmp_tier1_ilvl[0][1]
                )
            )
            logger.debug("Sorted tmp_tier2: {}".format(tmp_tier2_ilvl))
            logger.info(
                "Tier 2 Trait {} won with {} dps in ilevel category.".format(
                    tmp_tier2_ilvl[0][0], tmp_tier2_ilvl[0][1]
                )
            )

            # sorted ilevel trait list
            wanted_data["sorted_azerite_tier_3_itemlevel"] = []
            for azerite_trait, _ in tmp_tier1_ilvl:
                wanted_data["sorted_azerite_tier_3_itemlevel"].append(
                    azerite_trait)
            wanted_data["sorted_azerite_tier_1_itemlevel"] = []
            for azerite_trait, _ in tmp_tier1_ilvl:
                wanted_data["sorted_azerite_tier_1_itemlevel"].append(
                    azerite_trait)
            # sorted ilevel trait list
            wanted_data["sorted_azerite_tier_2_itemlevel"] = []
            for azerite_trait, _ in tmp_tier2_ilvl:
                wanted_data["sorted_azerite_tier_2_itemlevel"].append(
                    azerite_trait)

            logger.debug("tmp_tier1: {}".format(tmp_tier1_stacked))
            logger.debug("tmp_tier2: {}".format(tmp_tier2_stacked))
            # sort
            tmp_tier1_stacked = sorted(
                tmp_tier1_stacked, key=lambda item: item[1], reverse=True)
            tmp_tier2_stacked = sorted(
                tmp_tier2_stacked, key=lambda item: item[1], reverse=True)
            logger.debug("Sorted tmp_tier1: {}".format(tmp_tier1_stacked))
            logger.info(
                "Tier 1 Trait {} won with {} dps in stacked trait category.".format(
                    tmp_tier1_stacked[0][0], tmp_tier1_stacked[0][1]
                )
            )
            logger.debug("Sorted tmp_tier2: {}".format(tmp_tier2_stacked))
            logger.info(
                "Tier 2 Trait {} won with {} dps in stacked trait category.".format(
                    tmp_tier2_stacked[0][0], tmp_tier2_stacked[0][1]
                )
            )

            # sorted ilevel trait list
            wanted_data["sorted_azerite_tier_3_trait_stacking"] = []
            for azerite_trait, _ in tmp_tier1_stacked:
                wanted_data["sorted_azerite_tier_3_trait_stacking"].append(
                    azerite_trait)
            wanted_data["sorted_azerite_tier_1_trait_stacking"] = []
            for azerite_trait, _ in tmp_tier1_stacked:
                wanted_data["sorted_azerite_tier_1_trait_stacking"].append(
                    azerite_trait)
            # sorted ilevel trait list
            wanted_data["sorted_azerite_tier_2_trait_stacking"] = []
            for azerite_trait, _ in tmp_tier2_stacked:
                wanted_data["sorted_azerite_tier_2_trait_stacking"].append(
                    azerite_trait)

            # spell id dict to allow link creation
            wanted_data["spell_ids"] = azerite_trait_name_spell_id_dict

            # add azerite trait IDs to allow import string creation
            wanted_data['azerite_ids'] = {}
            for azerite_trait_spell_id in azerite_traits:
                wanted_data['azerite_ids'][azerite_traits[azerite_trait_spell_id]['name']
                                           ] = azerite_traits[azerite_trait_spell_id]['trait_id']

            logger.debug("Final json: {}".format(wanted_data))

            # create directory if it doesn't exist
            if not os.path.isdir("results/azerite_traits/"):
                os.makedirs("results/azerite_traits/")

            # write json to file
            with open(
                "results/azerite_traits/{}_{}_{}.json".format(
                    wow_class.lower(), wow_spec.lower(), fight_style.lower()
                ),
                "w",
                encoding="utf-8"
            ) as f:
                logger.debug("Print azerite_traits json.")
                f.write(json.dumps(wanted_data, sort_keys=True,
                                   indent=4, ensure_ascii=False))
                logger.debug("Printed azerite_traits json.")

            #########################################################################
            # Export of Azerite Items
            azerite_items = wow_lib.get_azerite_items(wow_class, wow_spec)

            # create an export for each slot
            for slot in azerite_items:
                slot_export = create_base_json_dict(
                    "Azerite Items " + slot.title(),
                    wow_class,
                    wow_spec,
                    fight_style,
                    settings,
                )

                # fix base profile to match sim
                slot_export["profile"]["head"].pop("azerite_powers", None)
                slot_export["profile"]["shoulders"].pop("azerite_powers", None)
                slot_export["profile"]["chest"].pop("azerite_powers", None)
                slot_export['profile']['items']['head'].pop('azerite_powers', None)
                slot_export['profile']['items']['shoulders'].pop(
                    'azerite_powers', None)
                slot_export['profile']['items']['chest'].pop('azerite_powers', None)

                slot_export["simulated_steps"] = []
                for itemlevel in settings.azerite_trait_ilevels:
                    slot_export["simulated_steps"].insert(0, "1_" + itemlevel)

                # add baseline dps
                slot_export["data"]["baseline"] = {}

                for itemlevel in settings.azerite_trait_ilevels:
                    slot_export["data"]["baseline"][
                        "1_" + itemlevel] = wanted_data["data"]["baseline"]["1_" + itemlevel]

                # create shorthand for later use
                baseline_dps = slot_export["data"]["baseline"]

                # create dict of which azerite traits were used on which item
                slot_export["used_azerite_traits_per_item"] = {}

                # look at each item
                unsorted_item_dps_list = []
                for item in azerite_items[slot]:

                    # skip item if necessary fields are missing
                    if not "name" in item and not "azeriteTraits" in item:
                        continue

                    if item["name"] in slot_export["data"]:
                        continue

                    # add translation to export
                    if not "languages" in slot_export:
                        slot_export["languages"] = {}
                    if not item["name"] in slot_export["languages"]:
                        try:
                            slot_export["languages"][item["name"]
                                                     ] = wow_lib.get_azerite_item_translation(
                                                         item["name"]
                            )
                        except LookupError as e:
                            slot_export["languages"][item["name"]] = {
                                "de_DE": item["name"],
                                "en_US": item["name"],
                                "es_ES": item["name"],
                                "fr_FR": item["name"],
                                "it_IT": item["name"],
                                "pt_BR": item["name"],
                                "ko_KR": item["name"],
                                "cn_CN": item["name"],
                                "ru_RU": item["name"]
                            }

                    # get maximum available itemlevel for an item from its traits
                    max_available_itemlevel = 1000
                    for trait in item['azeriteTraits']:

                        # skip trait if no name is provided (trait is probably not yet implemented in wow anyway)
                        if not 'name' in trait:
                            continue

                        trait_id = str(trait['spellId'])

                        trait_ilvl = wow_lib.get_azerite_trait_max_ilevel(
                            wow_class, wow_spec, trait_id
                        )

                        if trait_ilvl < max_available_itemlevel:
                            max_available_itemlevel = trait_ilvl

                    # get maximum available itemlevel for an item from the available dict
                    lookup_itemlevel: int = wow_lib.get_azerite_item_max_itemlevel(
                        item["name"])
                    if lookup_itemlevel > -1 and lookup_itemlevel < max_available_itemlevel:
                        max_available_itemlevel = lookup_itemlevel

                    # early exit for this item if max_available_itemlevel is not in settings
                    if max_available_itemlevel not in [
                        int(itemlevel) for itemlevel in settings.azerite_trait_ilevels
                    ]:
                        logger.debug(
                            f'  Skipping {item["name"]} (max itemlevel: {max_available_itemlevel})'
                        )
                        continue

                    # create trait lists for each tier [(trait_name, dps)]
                    trait_dict = {2: [], 3: [], 4: []}
                    # collect trait data like spellid and power id to allow construction of links in page
                    trait_data = {}
                    for trait in item["azeriteTraits"]:

                        # if trait tier is appropriate
                        if not trait["tier"] in trait_dict:
                            continue

                        # skip trait if no name is provided (trait is probably not yet implemented in wow anyway)
                        if not "name" in trait:
                            continue

                        # if trait was not simmed previously, throw a warning and exclude trait
                        if not trait["name"] in wanted_data["data"]:
                            logger.debug(
                                "Trait <{}> wasn't found in already simed data and excluded data. Item <{}> will be evaluated without that trait as it probably would only have that trait for a different spec."
                                .format(trait['name'], item['name'])
                            )
                            continue

                        name = trait["name"]

                        trait_data[name] = {
                            "id": trait["powerId"], "spell_id": trait["spellId"]}

                        # if trait is a dps trait we simmed
                        if name in wanted_data["data"]:
                            # append tuple of name and max available itemlevel dps
                            tmp_max_available_itemlevel = "1_" + \
                                str(max_available_itemlevel)

                            if not tmp_max_available_itemlevel in wanted_data["data"][name]:
                                tmp_max_available_itemlevel = sorted(
                                    wanted_data["data"][name])[-1]
                                if "1_" != tmp_max_available_itemlevel[:2]:
                                    tmp_max_available_itemlevel = "1_" + tmp_max_available_itemlevel[
                                        2:]

                            try:
                                trait_dict[trait["tier"]].append((
                                    name, wanted_data["data"][name][tmp_max_available_itemlevel] -
                                    baseline_dps[tmp_max_available_itemlevel]
                                ))
                                logger.debug(
                                    'trait_dict: {}'.format(
                                        trait_dict[trait['tier']][-1])
                                )
                            except KeyError:
                                # special case that uses one trait as a baseline instead of zero traits
                                # compares the second stacked trait to the baseline
                                logger.info(
                                    'KeyError found. information: {}'.format(name))
                                trait_dict[trait["tier"]].append((
                                    name,
                                    wanted_data["data"][name]['2_' +
                                                              tmp_max_available_itemlevel[2:]] -
                                    baseline_dps[tmp_max_available_itemlevel]
                                ))
                                logger.debug(
                                    'trait_dict: {}'.format(
                                        trait_dict[trait['tier']][-1])
                                )

                    # create list of traits of item
                    slot_export["used_azerite_traits_per_item"][item["name"]] = []

                    # complete trait list with dps was created. add best trait names to json and sort trait_dict in place
                    for tier in sorted(trait_dict.keys()):
                        if trait_dict[tier]:
                            trait_dict[tier] = sorted(
                                trait_dict[tier], key=lambda item: item[1], reverse=True
                            )
                            slot_export["used_azerite_traits_per_item"][item["name"]].append({
                                "name": trait_dict[tier][0][0],
                                "id": trait_data[trait_dict[tier][0][0]]["id"],
                                "spell_id": trait_data[trait_dict[tier][0][0]]["spell_id"]
                            })
                            logger.debug(
                                'adding to slot export {}'.format(
                                    slot_export["used_azerite_traits_per_item"][item["name"]][-1]
                                )
                            )

                    slot_export["data"][item["name"]] = {}
                    # add values to the armor for all available itemlevels
                    for itemlevel in settings.azerite_trait_ilevels:

                        # skip itemlevel if item (trait) can't scale up to this itemlevel
                        if int(itemlevel) > max_available_itemlevel:
                            logger.debug(
                                'skipping itemlevel of {}: {} | {}'.format(
                                    item["name"],
                                    itemlevel,
                                    max_available_itemlevel,
                                )
                            )
                            continue

                        # add base dps value first to be able to add the dps value of the different tiers later
                        slot_export["data"][item["name"]]["1_" +
                                                          itemlevel] = baseline_dps["1_" +
                                                                                    itemlevel]

                        # sum up dps values of best dps traits if itemlevel was simmed
                        for tier in trait_dict:
                            if trait_dict[tier]:
                                try:
                                    slot_export["data"][item["name"]][
                                        "1_" +
                                        itemlevel] += wanted_data["data"][trait_dict[tier][0][0]][
                                            "1_" + itemlevel] - baseline_dps["1_" + itemlevel]
                                except Exception:
                                    try:
                                        slot_export["data"][item["name"]][
                                            "1_" + itemlevel
                                        ] += wanted_data["data"][trait_dict[tier][0][0]][
                                            "2_" + itemlevel] - baseline_dps["1_" + itemlevel]

                                    except Exception:
                                        logger.debug(
                                            "Itemlevel {} for trait <{}> not found. Removing the itemlevel from the item <{}> from result dict."
                                            .format(
                                                itemlevel, trait_dict[tier][0][0], item['name']
                                            )
                                        )
                                        logger.debug(
                                            'item: {}; trait: {}'.format(
                                                slot_export["data"][item["name"]],
                                                wanted_data["data"][trait_dict[tier][0][0]]
                                            )
                                        )

                                        if "1_" + itemlevel in slot_export["data"][item["name"]]:
                                            slot_export["data"][item["name"]].pop(
                                                "1_" + itemlevel)
                                        continue

                                else:
                                    logger.debug(
                                        'slot export {} {} {}'.format(
                                            item["name"], "1_" + itemlevel,
                                            slot_export["data"][item["name"]
                                                                ]["1_" + itemlevel]
                                        )
                                    )
                                    pass

                    # add tuple (item_name, item_dps) to unsorted_item_dps_list
                    max_available_itemlevel = "1_" + \
                        str(max_available_itemlevel)
                    if slot_export["data"][item["name"]]:
                        if not max_available_itemlevel in slot_export["data"][item["name"]]:
                            try:
                                max_available_itemlevel = sorted(
                                    slot_export["data"][item["name"]]
                                )[-1]
                            except IndexError as e:
                                logger.info(
                                    'IndexError found. Information: {} ### {} ### {}'.format(
                                        item["name"], slot_export["data"],
                                        slot_export["data"][item["name"]]
                                    )
                                )
                                raise e

                        unsorted_item_dps_list.append((
                            item["name"],
                            slot_export["data"][item["name"]
                                                ][max_available_itemlevel]
                        ))

                        # create item_ids dict
                        if not "item_ids" in slot_export:
                            slot_export["item_ids"] = {}

                        # add item id
                        slot_export["item_ids"][item["name"]] = str(item["id"])

                # all items are done, sort unsorted_item_dps_list
                sorted_item_dps_list = sorted(
                    unsorted_item_dps_list, key=lambda item: item[1], reverse=True
                )

                # add sorted list to slot_export
                slot_export["sorted_data_keys"] = []
                for item, _ in sorted_item_dps_list:
                    slot_export["sorted_data_keys"].append(item)

                if not os.path.isdir("results/azerite_traits/"):
                    os.makedirs("results/azerite_traits/")

                with open(
                    "results/azerite_traits/{}_{}_{}_{}.json".format(
                        wow_class.lower(), wow_spec.lower(), slot.lower(), fight_style.lower()
                    ),
                    "w",
                    encoding="utf-8"
                ) as f:
                    logger.debug("Print azerite_traits {} json.".format(slot))
                    f.write(json.dumps(slot_export, sort_keys=True,
                                       indent=4, ensure_ascii=False))
                    logger.debug(
                        "Printed azerite_traits {} json.".format(slot))

    logger.debug("azerite_trait_simulations ended")

import json
import os

from bloodytools.simulation_objects.simulation_objects import Simulation_Data
from bloodytools.simulation_objects.simulation_objects import Simulation_Group
from bloodytools.utils.utils import create_base_json_dict
from bloodytools.utils.utils import create_basic_profile_string
from simc_support import wow_lib
from typing import List, Tuple


def essence_simulation(settings: object) -> None:
    """Simulates all available races for all given specs.

    Arguments:
        specs {List[Tuple[str, str]]} -- List of all wanted wow_specs

    Returns:
        None --
    """
    logger = settings.logger

    logger.debug("essence_simulation start")

    specs: List[Tuple[str, str]] = settings.wow_class_spec_list

    for fight_style in settings.fight_styles:
        for wow_class, wow_spec in specs:

            # check whether the baseline profile does exist
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
                "Essences", wow_class, wow_spec, fight_style, settings
            )

            essences = wow_lib.get_essences(wow_class.title(), wow_spec.title())
            simulation_group = Simulation_Group(
                name="essences",
                threads=settings.threads,
                profileset_work_threads=settings.profileset_work_threads,
                executable=settings.executable,
                logger=logger
            )

            # add baseline
            simulation_data = None

            simulation_data = Simulation_Data(
                name='baseline',
                fight_style=fight_style,
                profile=wanted_data['profile'],
                simc_arguments=["azerite_essences="],
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
                simulation_data.simc_arguments.append(custom_fight_style)
            simulation_group.add(simulation_data)

            # create profiles for all essences, all ranks, all minor/major types
            for essence_id in essences.keys():
                rank: int
                for rank in range(1, 4):
                    essence_type: int
                    for essence_type in range(0, 2):

                        simulation_data = None

                        simulation_data = Simulation_Data(
                            name='{}_{}_{}'.format(essence_id, rank, essence_type),
                            fight_style=fight_style,
                            simc_arguments=[
                                "azerite_essences={}:{}:{}".format(essence_id, rank, essence_type)
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
                            "Added azerite essence '{}:{}:{}' in profile '{}' to simulation_group."
                            .format(essence_id, rank, essence_type, simulation_data.name)
                        ))

                        # special case worldvein
                        if essence_id == "4":
                            special_case = None
                            special_case = simulation_data.copy()
                            special_case.name += "+3"
                            special_case.simc_arguments.append("bfa.worldvein_allies=3")
                            simulation_group.add(special_case)

            logger.info(
                "Start {} essence simulation for {} {}.".format(fight_style, wow_class, wow_spec)
            )
            try:
                if settings.use_raidbots and settings.apikey:
                    settings.simc_hash = simulation_group.simulate_with_raidbots(settings.apikey)
                else:
                    simulation_group.simulate()
            except Exception as e:
                logger.error(
                    "{} essence simulation for {} {} failed. {}".format(
                        fight_style.title(), wow_class, wow_spec, e
                    )
                )
                continue
            else:
                logger.info(
                    "{} essence simulation for {} {} ended successfully. Cleaning up.".format(
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

                if profile.name == 'baseline':
                    wanted_data['data'][profile.name] = {}
                    wanted_data['data'][profile.name][1] = profile.get_dps()
                    logger.debug(
                        "Added '{}' with {} dps to json.".format(profile.name, profile.get_dps())
                    )
                    continue

                essence_name: str = essences[profile.name.split('_')[0]]['name']
                essence_id: int = int(profile.name.split('_')[0])
                essence_rank: int = int(profile.name.split('_')[1])
                essence_type: int = int(profile.name.split('_')[2].split('+')[0])

                altered_essence_name: str = essence_name
                if essence_type == 0:
                    altered_essence_name += ' minor'

                # add special cases
                if '+' in profile.name:
                    for i, plus in enumerate(profile.name.split('+')):
                        if i > 0:
                            altered_essence_name += ' +' + plus

                # create missing subdict
                if not altered_essence_name in wanted_data['data']:
                    wanted_data['data'][altered_essence_name] = {}

                wanted_data['data'][altered_essence_name][essence_rank] = profile.get_dps()
                logger.debug(
                    "Added '{}' with {} dps to json.".format(profile.name, profile.get_dps())
                )
                # adding spell data to dict
                if not 'spell_ids' in wanted_data:
                    wanted_data['spell_ids'] = {}

                if not altered_essence_name in wanted_data['spell_ids']:
                    wanted_data['spell_ids'][altered_essence_name] = {}

                if "minor" in altered_essence_name.split():
                    wanted_data['spell_ids'][altered_essence_name] = essences[
                        str(essence_id)]['minor']['spell_id']
                else:
                    wanted_data['spell_ids'][altered_essence_name] = essences[
                        str(essence_id)]['major']['spell_id']

                # adding power ids to dict
                power_id_name = 'power_ids'
                if not power_id_name in wanted_data:
                    wanted_data[power_id_name] = {}

                if not altered_essence_name in wanted_data[power_id_name]:
                    wanted_data[power_id_name][altered_essence_name] = {}

                wanted_data[power_id_name][altered_essence_name] = wow_lib.get_essence_power_id(
                    essence_id
                )

            # create ordered essence name list
            tmp_list = []
            essence_name: str
            for essence_name in wanted_data["data"]:
                if essence_name == 'baseline':
                    continue
                tmp_list.append((essence_name, wanted_data["data"][essence_name][3]))
            logger.debug("tmp_list: {}".format(tmp_list))

            tmp_list = sorted(tmp_list, key=lambda item: item[1], reverse=True)
            logger.debug("Sorted tmp_list: {}".format(tmp_list))
            logger.info("Essence {} won with {} dps.".format(tmp_list[0][0], tmp_list[0][1]))

            wanted_data["sorted_data_keys"] = []
            for essence_name, _ in tmp_list:
                wanted_data["sorted_data_keys"].append(essence_name)

            # add simulated steps...err ranks
            wanted_data['simulated_steps'] = []
            for i in range(1, 4):
                wanted_data['simulated_steps'].append(
                    4 - i
                )     # get the steps into the proper order...descending

            azerite_weight_string = "( AzeritePowerWeights:2:\"{fight_style} {wow_spec} {wow_class} essences\":{class_id}:{spec_id}: :".format(
                fight_style=fight_style.title(),
                wow_spec=wow_spec.title(),
                wow_class=wow_class.title(),
                class_id=wow_lib.get_class_id(wow_class),
                spec_id=wow_lib.get_spec_id(wow_class, wow_spec)
            )
            tmp_aws_dict = {}
            for essence_name in wanted_data["data"]:
                if essence_name != 'baseline':
                    # looking for the trait id in essences dict
                    for key, value in essences.items():
                        if value['name'] in essence_name:
                            if not key in tmp_aws_dict:
                                tmp_aws_dict[key] = {}
                            if ' minor' in essence_name:
                                tmp_aws_dict[key]['minor'] = wanted_data['data'][essence_name][
                                    3] - wanted_data['data']['baseline'][1]
                            else:
                                tmp_aws_dict[key]['major'] = wanted_data['data'][essence_name][
                                    3] - wanted_data['data']['baseline'][1]

            for key, value in tmp_aws_dict.items():
                azerite_weight_string += " {}={}/{},".format(key, value['major'], value['minor'])

            azerite_weight_string += " )"

            wanted_data['azerite_weight_{}'.format(fight_style.lower())] = azerite_weight_string

            logger.debug("Final json: {}".format(wanted_data))

            # write json to file
            partial_path: str = "results/essences/"
            if not os.path.isdir(partial_path):
                os.makedirs(partial_path)
            with open(
                "{}{}_{}_{}.json".format(
                    partial_path, wow_class.lower(), wow_spec.lower(), fight_style.lower()
                ),
                "w",
                encoding="utf-8"
            ) as f:
                logger.debug("Print essence json.")
                f.write(json.dumps(wanted_data, sort_keys=True, indent=4, ensure_ascii=False))
                logger.debug("Printed essence json.")

    logger.debug("essence_simulation ended")

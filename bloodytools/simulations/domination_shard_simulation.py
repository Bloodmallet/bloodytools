import json
import logging
import os

from bloodytools.utils.simulation_objects import Simulation_Data, Simulation_Group
from bloodytools.utils.utils import create_base_json_dict
from simc_support.game_data.DominationShard import (
    DOMINATION_SHARDS,
    DominationShard,
)
from simc_support.game_data.WowSpec import WowSpec
import typing

logger = logging.getLogger(__name__)


def _is_dps_shard(shard: DominationShard) -> bool:
    dps_name_parts = (
        "of Bek",
        "of Tel",
        "of Dyz",
    )
    for part in dps_name_parts:
        if part in shard.name:
            return True
    return False


def _is_shard(id: str) -> bool:
    for shard in DOMINATION_SHARDS:
        if int(id) == shard.gem_id:
            return True
    return False


def domination_shard_simulation(settings: object) -> None:
    """Simulates all dps relevant Domination Shards for given wow_classes and wow_specs.

    Arguments:
      settings {object} - loaded settings

    Raises:
      NotImplementedError -- [description]
    """
    specs: typing.List[WowSpec] = settings.wow_class_spec_list

    logger.debug("damnation_shard_simulation start")
    for fight_style in settings.fight_styles:
        for wow_spec in specs:

            # json exporter
            json_export = create_base_json_dict(
                "domination_shards", wow_spec, fight_style, settings
            )

            shards = DOMINATION_SHARDS
            # filter shard list by dps relevance:
            shard_list = list(filter(_is_dps_shard, shards))

            # remove all damnation gems from profile
            for slot_name in json_export["profile"]["items"]:
                item = json_export["profile"]["items"][slot_name]
                if "gem_id" in item.keys():
                    gem_parts: typing.List[str]
                    if "/" in item["gem_id"]:
                        gem_parts = item["gem_id"].split("/")
                    elif ":" in item["gem_id"]:
                        gem_parts = item["gem_id"].split(":")
                    else:
                        gem_parts = [item["gem_id"]]
                    filtered_gem_parts = filter(
                        lambda part: not _is_shard(part), gem_parts
                    )
                    item["gem_id"] = "/".join(filtered_gem_parts)

            json_export["shard_type"] = {}
            for shard in shard_list:
                json_export["translations"][shard.name] = shard.translations.get_dict()
                json_export["shard_type"][shard.name] = str(shard.school_type)

            simulation_group = Simulation_Group(
                name="{} {}".format(wow_spec.wow_class.simc_name, wow_spec.simc_name),
                threads=settings.threads,
                profileset_work_threads=settings.profileset_work_threads,
                executable=settings.executable,
                remove_files=not settings.keep_files,
            )

            simulation_data = Simulation_Data(
                name="baseline",
                fight_style=fight_style,
                iterations=settings.iterations,
                target_error=settings.target_error.get(fight_style, "0.1"),
                profile=json_export["profile"],
                ptr=settings.ptr,
                default_actions=settings.default_actions,
                executable=settings.executable,
            )

            custom_apl = None
            if settings.custom_apl:
                with open("custom_apl.txt") as f:
                    custom_apl = f.read()
            if custom_apl:
                simulation_data.simc_arguments.append("# custom_apl")
                simulation_data.simc_arguments.append(custom_apl)

            custom_fight_style = None
            if settings.custom_fight_style:
                with open("custom_fight_style.txt") as f:
                    custom_fight_style = f.read()
            if custom_fight_style:
                simulation_data.simc_arguments.append("# custom_fight_style")
                simulation_data.simc_arguments.append(custom_fight_style)

            simulation_group.add(simulation_data)

            for shard in shard_list:
                head = json_export["profile"]["items"]["head"]
                head_string = "head=,"
                head_string += ",".join(
                    "{}={}".format(key, value)
                    for key, value in head.items()
                    if key != "gem_id"
                )
                if head["gem_id"]:
                    head_string += ",gem_id=" + "/".join(
                        [head["gem_id"]] + [str(shard.gem_id)]
                    )
                else:
                    head_string += f",gem_id={shard.gem_id}"

                simulation_data = Simulation_Data(
                    name=f"{shard.name}",
                    fight_style=fight_style,
                    iterations=settings.iterations,
                    target_error=settings.target_error.get(fight_style, "0.1"),
                    simc_arguments=[head_string],
                    ptr=settings.ptr,
                    default_actions=settings.default_actions,
                    executable=settings.executable,
                )
                simulation_group.add(simulation_data)

            # create and simulate baseline profile
            logger.info(
                "Start {} domination_shards simulation for {}.".format(
                    fight_style, wow_spec
                )
            )
            try:
                if settings.use_raidbots and settings.apikey:
                    settings.simc_hash = simulation_group.simulate_with_raidbots(
                        settings.apikey
                    )
                else:
                    simulation_group.simulate()
            except Exception as e:
                logger.error(
                    "{} domination_shards simulation for {} failed. {}".format(
                        fight_style.title(), wow_spec, e
                    )
                )
                continue
            else:
                logger.info(
                    "{} domination_shards simulation for {} ended successfully. Cleaning up.".format(
                        fight_style.title(), wow_spec
                    )
                )
                logger.info(f"Profiles: {len(simulation_group.profiles)}")

            for profile in simulation_group.profiles:
                try:
                    logger.debug(
                        "{} {} DPS, baseline + {}".format(
                            profile.name,
                            profile.get_dps(),
                            profile.get_dps() - simulation_group.get_dps_of("baseline"),
                        )
                    )
                except Exception as e:
                    logger.error(
                        'Exception was thrown when trying to fetch the following data from simulation_group: profile.name, profile.get_dps(), profile.get_dps() - simulation_group.get_dps_of("baseline")'
                    )
                    logger.debug("profile.name {}".format(profile.name))
                    logger.debug("profile.get_dps() {}".format(profile.get_dps()))
                    logger.debug(
                        'simulation_group.get_dps_of("baseline") {}'.format(
                            simulation_group.get_dps_of("baseline")
                        )
                    )

                json_export["data"][profile.name] = profile.get_dps()

            logger.debug("Enriched json export: {}".format(json_export))

            # create ordered shard name list
            tmp_list = []
            for shard in json_export["data"]:
                if shard != "baseline":
                    tmp_list.append((shard, json_export["data"][shard]))
            logger.debug("tmp_list: {}".format(tmp_list))

            tmp_list = sorted(tmp_list, key=lambda item: item[1], reverse=True)
            logger.debug("Sorted tmp_list: {}".format(tmp_list))

            logger.info(
                "Shard {} won with {} dps.".format(tmp_list[0][0], tmp_list[0][1])
            )

            json_export["sorted_data_keys"] = []
            for shard, _ in tmp_list:
                json_export["sorted_data_keys"].append(shard)

            if not os.path.isdir("results/domination_shards/"):
                os.makedirs("results/domination_shards/")

            # write json to file
            with open(
                "results/domination_shards/{}_{}_{}.json".format(
                    wow_spec.wow_class.simc_name,
                    wow_spec.simc_name,
                    fight_style.lower(),
                ),
                "w",
                encoding="utf-8",
            ) as f:
                logger.debug("Print shard json.")
                f.write(
                    json.dumps(
                        json_export,
                        sort_keys=True,
                        indent=4 if settings.pretty else None,
                        ensure_ascii=False,
                    )
                )
                logger.debug("Printed shard json.")

    logger.debug("domination_shard_simulation ended")

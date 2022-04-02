import logging
import typing

import pkg_resources
import yaml
from bloodytools.simulations.simulator import Simulator
from bloodytools.utils.simulation_objects import Simulation_Data, Simulation_Group
from bloodytools.utils.utils import EmptyFileError, extract_profile
from simc_support.game_data.Covenant import Covenant, get_covenant
from simc_support.game_data.Legendary import (
    LEGENDARIES,
    Legendary,
    get_legendaries_for_spec,
)
from simc_support.game_data.WowSpec import WowSpec, get_wow_spec

logger = logging.getLogger(__name__)

# spell ids
UNWANTED_LEGENDARIES = [
    339340,  # Norgannon's Sagacity
    339351,  # Stable Phantasma Lure
    338743,  # Vitality Sacrifice
]


def _load_special_cases() -> typing.Dict[WowSpec, typing.List[dict]]:
    try:
        with pkg_resources.resource_stream(
            __name__, "/".join(("legendary_special_cases.yml",))
        ) as f:
            LOADED_SPECIAL_CASES = yaml.safe_load(f)
    except FileNotFoundError as e:
        logger.warning(e)
        LOADED_SPECIAL_CASES = {}

    if LOADED_SPECIAL_CASES is None:
        LOADED_SPECIAL_CASES = {}

    SPECIAL_CASES = {}
    for wow_class in LOADED_SPECIAL_CASES.keys():
        for wow_spec in LOADED_SPECIAL_CASES[wow_class].keys():
            SPECIAL_CASES[get_wow_spec(wow_class, wow_spec)] = LOADED_SPECIAL_CASES[
                wow_class
            ][wow_spec]

    return SPECIAL_CASES


def set_covenant_legendary(
    profile: dict, covenant: Covenant, legendaries: typing.List[Legendary]
) -> dict:
    """Instead of Unity set the specific covenant legendary bonus id

    Args:
        profile (dict): _description_
        covenant (Covenant): _description_
        legendaries (typing.List[Legendary]): _description_

    Raises:
        ValueError: _description_

    Returns:
        dict: _description_
    """

    wanted_legendary: typing.Optional[Legendary] = None
    for l in legendaries:
        if len(l.covenants) == 1 and l.covenants[0] == covenant:
            wanted_legendary = l

    if wanted_legendary is None:
        raise ValueError(f"Couldn't find Legendary for covenant {covenant}.")

    replace_legendary_bonus_ids = [
        l.bonus_id
        for l in legendaries
        if len(l.covenants) == 1 or "unity" in l.full_name.lower()
    ]

    for item in profile["items"]:
        item_bonus_ids: typing.List[str] = []
        try:
            tmp_item_bonus_ids = profile["items"][item]["bonus_id"].split("/")
        except KeyError:
            continue

        for element in tmp_item_bonus_ids:
            # the user could also use : to split bonus ids >.>
            for b_id in element.split(":"):
                item_bonus_ids.append(b_id)

        if item_bonus_ids and any(item_bonus_ids):
            filtered_item_bonus_ids = []

            for b_id in item_bonus_ids:
                if not int(b_id) in replace_legendary_bonus_ids:
                    filtered_item_bonus_ids.append(b_id)
                else:
                    filtered_item_bonus_ids.append(str(wanted_legendary.bonus_id))

            profile["items"][item]["bonus_id"] = "/".join(filtered_item_bonus_ids)

    return profile


def remove_bonus_ids(
    profile: dict, unwanted_ids: typing.Iterable[int]
) -> typing.Tuple[dict, typing.List[str]]:
    purged_slots: typing.List[str] = []
    for item in profile["items"]:
        item_bonus_ids: typing.List[str] = []
        try:
            tmp_item_bonus_ids = profile["items"][item]["bonus_id"].split("/")
        except KeyError:
            continue

        for element in tmp_item_bonus_ids:
            # the user could also use : to split bonus ids >.>
            for b_id in element.split(":"):
                item_bonus_ids.append(b_id)

        if item_bonus_ids and any(item_bonus_ids):
            filtered_item_bonus_ids = []

            for b_id in item_bonus_ids:
                if not int(b_id) in unwanted_ids:
                    filtered_item_bonus_ids.append(b_id)
                else:
                    purged_slots.append(item)

            profile["items"][item]["bonus_id"] = "/".join(filtered_item_bonus_ids)

    return (profile, purged_slots)


def get_legendary_special_case_name(
    base_name: str, name_additions: typing.List[str]
) -> str:
    return "[" + "+".join(name_additions) + "] " + base_name


def _get_covenant_legendary(
    covenant_name: str, legendaries: typing.List[Legendary]
) -> typing.Optional[Legendary]:
    for legendary in legendaries:
        if (
            len(legendary.covenants) == 1
            and legendary.covenants[0].simc_name == covenant_name
        ):
            return legendary
    return None


def _get_legendary(full_name: str) -> typing.Optional[Legendary]:
    for legendary in LEGENDARIES:
        if legendary.full_name == full_name:
            return legendary
    return None


def _create_item_for_legendary(profile: dict, slot: str) -> str:
    """Only the legendary ID needs to be added.

    Args:
        profile (dict): _description_
        slot (str): _description_

    Returns:
        str: _description_
    """
    item_information = profile["items"][slot]
    constructed_item = f"{slot}=,id={item_information['id']}"
    for key in item_information.keys():
        if key not in ("id", "bonus_id"):
            constructed_item += f",{key}={item_information[key]}"

    try:
        final_item = constructed_item + f",bonus_id={item_information['bonus_id']}/"
    except KeyError:
        final_item = constructed_item + f",bonus_id="

    return final_item


class LegendarySimulator(Simulator):
    @classmethod
    def name(cls) -> str:
        return "Legendaries"

    def pre_processing(self, data_dict: dict) -> dict:
        data_dict = super().pre_processing(data_dict)

        legendaries = list(get_legendaries_for_spec(wow_spec=self.wow_spec))

        if self.wow_spec == get_wow_spec("shaman", "enhancement"):
            skybreakers_fiery_demise = _get_legendary("Skybreaker's Fiery Demise")
            if skybreakers_fiery_demise:
                legendaries.append(skybreakers_fiery_demise)

        filtered_legendaries = [
            legendary
            for legendary in legendaries
            if legendary.spell_id not in UNWANTED_LEGENDARIES
            and legendary.full_name != "Unity"
        ]
        self.legendaries = filtered_legendaries

        # handle unity/covenant legendaries
        cov = get_covenant(name=data_dict["profile"]["character"]["covenant"])
        data_dict["profile"] = set_covenant_legendary(
            data_dict["profile"], cov, legendaries
        )
        for profile in data_dict["covenant_profiles"]:
            cov = get_covenant(
                name=data_dict["covenant_profiles"][profile]["character"]["covenant"]
            )
            data_dict["covenant_profiles"][profile] = set_covenant_legendary(
                data_dict["covenant_profiles"][profile], cov, legendaries
            )

        # remove non-covenant legendaries
        self.legendary_slots = {}
        non_covenant_legendary_bonus_ids = [
            legendary.bonus_id
            for legendary in legendaries
            if len(legendary.covenants) != 1
            and "unity" not in legendary.full_name.lower()
        ]
        for profile in data_dict["covenant_profiles"]:
            data_dict["covenant_profiles"][profile], purged_slots = remove_bonus_ids(
                data_dict["covenant_profiles"][profile],
                non_covenant_legendary_bonus_ids,
            )
            if len(purged_slots) != 1:
                raise ValueError(f"Slots {purged_slots} were purged. Expected 1.")
            else:
                self.legendary_slots[
                    data_dict["covenant_profiles"][profile]["character"]["covenant"]
                ] = purged_slots[0]

        data_dict["spell_ids"] = {}
        for legendary in legendaries:
            data_dict["translations"][
                legendary.full_name
            ] = legendary.translations.get_dict()
            data_dict["spell_ids"][legendary.full_name] = legendary.spell_id

        if self.settings.custom_profile:
            data_dict["covenant_profiles"] = self._adjust_covenant_profiles_itemlevels(
                data_dict["profile"],
                data_dict["covenant_profiles"],
            )

        SPECIAL_CASES = _load_special_cases()
        for special_case in SPECIAL_CASES.get(self.wow_spec, []):
            for legendary in self.legendaries:
                if legendary.full_name == special_case["name"]:
                    special_name = get_legendary_special_case_name(
                        legendary.full_name, special_case["name_additions"]
                    )
                    data_dict["translations"][
                        special_name
                    ] = legendary.translations.get_dict()

                    for language in data_dict["translations"][special_name].keys():
                        data_dict["translations"][special_name][language] = (
                            special_name.replace(legendary.full_name, "")
                            + data_dict["translations"][special_name][language]
                        )

                    data_dict["spell_ids"][special_name] = legendary.spell_id

        return data_dict

    def add_simulation_data(
        self, simulation_group: Simulation_Group, data_dict: dict
    ) -> None:

        covenant_simc_name = data_dict["profile"]["character"]["covenant"]
        covenant_item = _create_item_for_legendary(
            data_dict["profile"], self.legendary_slots[covenant_simc_name]
        )

        simulation_data = Simulation_Data(
            name="baseline",
            fight_style=self.fight_style,
            profile=data_dict["profile"],
            simc_arguments=[f"{covenant_item}"],
            target_error=self.settings.target_error.get(self.fight_style, "0.1"),
            ptr=self.settings.ptr,
            default_actions=self.settings.default_actions,
            executable=self.settings.executable,
            iterations=self.settings.iterations,
        )
        custom_apl = None
        if self.settings.custom_apl:
            with open("custom_apl.txt") as f:
                custom_apl = f.read()
        if custom_apl:
            simulation_data.simc_arguments.append("# custom_apl")
            simulation_data.simc_arguments.append(custom_apl)

        custom_fight_style = None
        if self.settings.custom_fight_style:
            with open("custom_fight_style.txt") as f:
                custom_fight_style = f.read()
        if custom_fight_style:
            simulation_data.simc_arguments.append("# custom_fight_style")
            simulation_data.simc_arguments.append(custom_fight_style)

        simulation_group.add(simulation_data)

        SPECIAL_CASES = _load_special_cases()

        for covenant_name in data_dict["covenant_profiles"]:
            covenant_item = _create_item_for_legendary(
                data_dict["covenant_profiles"][covenant_name],
                self.legendary_slots[covenant_name],
            )
            covenant_simc_name = covenant_name

            simulation_data = Simulation_Data(
                name=f"{{{covenant_name}}}",
                fight_style=self.fight_style,
                profile=data_dict["covenant_profiles"][covenant_name],
                simc_arguments=[f"{covenant_item}"],
                target_error=self.settings.target_error.get(self.fight_style, "0.1"),
                ptr=self.settings.ptr,
                default_actions=self.settings.default_actions,
                executable=self.settings.executable,
                iterations=self.settings.iterations,
            )
            simulation_group.add(simulation_data)

        for legendary in self.legendaries:

            if len(legendary.covenants) == 1 or "unity" in legendary.full_name.lower():
                # single covenant legendary simulations aren't necessary
                continue

            covenant: Covenant
            for covenant in legendary.covenants:
                if (
                    covenant.simc_name not in data_dict["covenant_profiles"]
                    and covenant.simc_name
                    != data_dict["profile"]["character"]["covenant"]
                ):
                    continue

                profile = {}
                if covenant.simc_name == data_dict["profile"]["character"]["covenant"]:
                    profile = data_dict["profile"]
                elif covenant.simc_name in data_dict["covenant_profiles"]:
                    profile = data_dict["covenant_profiles"][covenant.simc_name]

                covenant_item = _create_item_for_legendary(
                    profile, self.legendary_slots[covenant.simc_name]
                )
                covenant_simc_name = covenant.simc_name
                covenant_item += f"/{legendary.bonus_id}"

                simulation_data = Simulation_Data(
                    name=f"{{{covenant.simc_name}}} {legendary.full_name}",
                    fight_style=self.fight_style,
                    simc_arguments=[f"{covenant_item}"],
                    target_error=self.settings.target_error.get(
                        self.fight_style, "0.1"
                    ),
                    ptr=self.settings.ptr,
                    default_actions=self.settings.default_actions,
                    executable=self.settings.executable,
                    iterations=self.settings.iterations,
                    profile=profile,
                )

                simulation_group.add(simulation_data)
                logger.debug(
                    (
                        "Added legendary '{}' in profile '{}' to simulation_group.".format(
                            legendary.full_name, simulation_data.name
                        )
                    )
                )

                for special_case in SPECIAL_CASES.get(self.wow_spec, []):
                    if (
                        special_case["name"] != legendary.full_name
                        or special_case["covenant"] != covenant.simc_name
                    ):
                        continue

                    if (
                        "fight_styles" in special_case
                        and self.fight_style.lower()
                        not in [f.lower() for f in special_case["fight_styles"]]
                    ):
                        continue

                    new_simulation_data = simulation_data.copy()

                    new_simulation_data.name = (
                        f"{{{covenant.simc_name}}} "
                        + get_legendary_special_case_name(
                            legendary.full_name, special_case["name_additions"]
                        )
                    )
                    new_simulation_data.simc_arguments += special_case["overrides"]
                    simulation_group.add(new_simulation_data)

    def post_processing(self, data_dict: dict) -> dict:
        data_dict = super().post_processing(data_dict)

        data_dict = self.create_sorted_key_value_data(data_dict)

        def is_baseline_profile(name: str) -> bool:
            return "baseline" in name

        def is_covenant_profile(name: str) -> bool:
            return name.endswith("}")

        data_dict["sorted_data_keys"] = [
            name
            for name in data_dict["sorted_data_keys"]
            if not is_baseline_profile(name) and not is_covenant_profile(name)
        ]

        return data_dict

    def _adjust_covenant_profiles_itemlevels(
        self, profile: dict, covenant_profiles: dict
    ) -> dict:

        try:
            extract_profile("custom_profile.txt", self.wow_spec.wow_class)
        except EmptyFileError:
            logger.info("Nothing to adjust. No custom profile found.")
            return covenant_profiles

        simulation = Simulation_Data(
            name="Grab dem average itemlevel",
            fight_style=self.fight_style,
            target_error="0.1",
            iterations="1",
            profile=profile,
            ptr=self.settings.ptr,
            default_actions=self.settings.default_actions,
            executable=self.settings.executable,
        )
        simulation.simulate()

        logger.debug("Mini simulation is done")

        ilevels = [
            slot["ilevel"]
            for slot in simulation.json_data["sim"]["players"][0]["gear"].values()
            if slot["ilevel"] > 0
        ]
        average_itemlevel = sum(ilevels) / len(ilevels)
        logger.debug(f"Calculated average itemlevel to be: {average_itemlevel}")

        for covenant_profile in covenant_profiles.values():
            for slot in covenant_profile["items"].values():
                slot["ilevel"] = str(int(average_itemlevel))

        logger.debug("Adjusted covenant profiles to new average itemlevel")

        return covenant_profiles

import logging
import typing

from bloodytools.simulations.simulator import Simulator
from bloodytools.utils.simulation_objects import Simulation_Data, Simulation_Group
from simc_support.game_data.SimcObject import SimcObject

logger = logging.getLogger(__name__)


class WeaponEnchant(SimcObject):
    def __init__(self, name: str, item_id: str, *args, **kwargs):
        super().__init__(full_name=name, *args, **kwargs)

        self.ranks: typing.Tuple[int, ...] = (1, 2, 3)
        self.item_id: str = item_id


WEAPON_ENCHANTS = [
    WeaponEnchant(name="Sophic Writ", item_id="199971"),
    WeaponEnchant(name="Wafting Writ", item_id="199975"),
    WeaponEnchant(name="Earthen Writ", item_id="199969"),
    WeaponEnchant(name="Frozen Writ", item_id="199973"),
    WeaponEnchant(name="Burning Writ", item_id="199967"),
    WeaponEnchant(name="Sophic Devotion", item_id="199970"),
    WeaponEnchant(name="Wafting Devotion", item_id="199974"),
    WeaponEnchant(name="Frozen Devotion", item_id="199972"),
]


class WeaponEnchantmentSimulator(Simulator):
    """Abstract base simulator for consumables."""

    @classmethod
    def name(cls) -> str:
        return "Weapon Enchantments"

    def _remove_weapon_enchants(self, profile: dict) -> None:
        """Alters the provided dict and removes weapon enchants."""
        # enchant_names = [e.simc_name for e in WEAPON_ENCHANTS]

        remove_enchants = ("enchant_id", "enchant")

        for key in ("main_hand", "off_hand"):
            if key in profile["items"]:
                for enchant_key in remove_enchants:
                    if enchant_key in profile["items"][key]:
                        del profile["items"][key][enchant_key]

    def add_simulation_data(
        self,
        simulation_group: Simulation_Group,
        data_dict: dict,
    ) -> None:
        profile = data_dict["profile"]

        self._remove_weapon_enchants(profile=profile)

        simulation_data = Simulation_Data(
            name=self.get_profile_name("baseline", str(1)),
            fight_style=self.fight_style,
            profile=profile,
            target_error=self.settings.target_error.get(self.fight_style, "0.1"),
            ptr=self.settings.ptr,
            default_actions=self.settings.default_actions,
            executable=self.settings.executable,
            iterations=self.settings.iterations,
            remove_files=not self.settings.keep_files,
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

        weapon_base_string = ""
        strings = simulation_data.get_simc_arguments_from_profile(profile)
        for string in strings:
            if string.startswith("main_hand"):
                weapon_base_string = string

        for enchant in WEAPON_ENCHANTS:
            for rank in enchant.ranks:

                scaled_name = self.get_profile_name(enchant.full_name, str(rank))
                scaled_simc_string = (
                    f"{weapon_base_string},enchant={enchant.simc_name}_{rank}"
                )

                simulation_data = Simulation_Data(
                    name=scaled_name,
                    fight_style=self.fight_style,
                    profile=profile,
                    simc_arguments=[scaled_simc_string],
                    target_error=self.settings.target_error.get(
                        self.fight_style, "0.1"
                    ),
                    ptr=self.settings.ptr,
                    default_actions=self.settings.default_actions,
                    executable=self.settings.executable,
                    iterations=self.settings.iterations,
                    remove_files=not self.settings.keep_files,
                )

                simulation_group.add(simulation_data)

    def post_processing(self, data_dict: dict) -> dict:
        data_dict = super().post_processing(data_dict)

        data_dict["simulated_steps"] = [3, 2, 1]

        data_dict = self.create_sorted_key_key_value_data(data_dict)

        data_dict["sorted_data_keys"] = [
            e for e in data_dict["sorted_data_keys"] if e != "baseline"
        ]

        data_dict["item_ids"] = {e.full_name: e.item_id for e in WEAPON_ENCHANTS}

        return data_dict

import logging

from bloodytools.simulations.simulator import Simulator
from bloodytools.utils.simulation_objects import Simulation_Data, Simulation_Group
from simc_support.game_data.Conduit import get_conduits_for_spec, CONDUITS
from simc_support.game_data.WowSpec import get_wow_spec
import itertools

logger = logging.getLogger(__name__)

RANKS = [
    8,
    9,
    10,
    11,
]


class ConduitSimulator(Simulator):
    @classmethod
    def name(cls) -> str:
        return "Conduits"

    def pre_processing(self, data_dict: dict) -> dict:
        data_dict = super().pre_processing(data_dict)

        self._conduits = list(get_conduits_for_spec(self.wow_spec))
        # add special cases
        if self.wow_spec == get_wow_spec("death_knight", "blood"):
            for c in CONDUITS:
                if c.full_name == "Eternal Hunger":
                    self._conduits.append(c)

        data_dict["translations"]
        for conduit in self._conduits:
            data_dict["translations"][
                conduit.full_name
            ] = conduit.translations.get_dict()
        return data_dict

    def add_simulation_data(
        self,
        simulation_group: Simulation_Group,
        data_dict: dict,
    ) -> None:
        conduit_rank_combinations = itertools.product(self._conduits, RANKS)

        simulation_data = Simulation_Data(
            name="baseline",
            fight_style=self.fight_style,
            profile=data_dict["profile"],
            simc_arguments=[f"soulbind="],
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

        for covenant_simc_name in data_dict["covenant_profiles"]:
            simulation_data = Simulation_Data(
                name=covenant_simc_name,
                fight_style=self.fight_style,
                profile=data_dict["covenant_profiles"][covenant_simc_name],
                simc_arguments=[f"soulbind="],
                target_error=self.settings.target_error.get(self.fight_style, "0.1"),
                ptr=self.settings.ptr,
                default_actions=self.settings.default_actions,
                executable=self.settings.executable,
                iterations=self.settings.iterations,
                remove_files=not self.settings.keep_files,
            )
            simulation_group.add(simulation_data)

        for conduit, rank in conduit_rank_combinations:
            # eligible for base profile
            if (
                len(conduit.covenants) > 1
                or len(conduit.covenants) == 1
                and conduit.covenants[0].simc_name
                == data_dict["profile"]["character"]["covenant"]
            ):
                name = (
                    f"{{{data_dict['profile']['character']['covenant']}}} "
                    + self.profile_split_character().join(
                        [conduit.full_name, str(rank)]
                    )
                )
                profile = data_dict["profile"]
            # requires covenant specific baseline
            else:
                name = (
                    f"{{{conduit.covenants[0].simc_name}}} "
                    + self.profile_split_character().join(
                        [conduit.full_name, str(rank)]
                    )
                )
                profile = data_dict["covenant_profiles"][conduit.covenants[0].simc_name]
            simulation_data = Simulation_Data(
                name=name,
                fight_style=self.fight_style,
                profile=profile,
                simc_arguments=[f"soulbind={conduit.simc_name}:{rank}:1"],
                target_error=self.settings.target_error.get(self.fight_style, "0.1"),
                ptr=self.settings.ptr,
                default_actions=self.settings.default_actions,
                executable=self.settings.executable,
                iterations=self.settings.iterations,
                remove_files=not self.settings.keep_files,
            )

            simulation_group.add(simulation_data)

    def post_processing(self, data_dict: dict) -> dict:
        data_dict = super().post_processing(data_dict)

        data_dict = self.create_sorted_key_key_value_data(
            data_dict,
            ignore_keys=["baseline", "kyrian", "venthyr", "night_fae", "necrolord"],
        )

        return data_dict

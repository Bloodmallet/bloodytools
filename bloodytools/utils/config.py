import dataclasses
import typing

from bloodytools.utils.data_type import DataType
from simc_support.game_data.WowSpec import WowSpec


# ! Hier sitz ich nun ich armer Tor. Bin so klug als wie zuvor.
# ! Schrieb Module und Klassen gar. Doch wozu ich sie gebar?
# ! Drum denk ich nun, ich lass sie weg. Zuvor funktionierte's also was soll der Kek(s)?


@dataclasses.dataclass
class Config:
    """Configuration that doesn't simulate anything but has otherwise sensible default values."""

    custom_apl: bool = False
    custom_fight_style: bool = False
    custom_profile: bool = False
    data_type: DataType = DataType.DPS
    debug: bool = False
    default_actions: str = "1"
    enable_conduit_simulations: bool = False
    enable_covenant_simulations: bool = False
    enable_domination_shards: bool = False
    enable_legendary_simulations: bool = False
    enable_race_simulations: bool = False
    enable_secondary_distributions_simulations: bool = False
    enable_soul_bind_node_simulations: bool = False
    enable_soul_bind_simulations: bool = False
    enable_talent_simulations: bool = False
    enable_trinket_simulations: bool = False
    enable_tier_set_simulations: bool = False
    executable: str = "../SimulationCraft/simc"
    iterations: str = "20000"
    keep_files: bool = False
    max_ilevel: int = 259
    min_ilevel: int = 210
    pretty: bool = False
    profileset_work_threads: str = "2"
    ptr: str = "0"
    raidbots: bool = False
    remove_files = False
    secondary_distributions_step_size: int = 10
    sim_all: bool = False
    simc_hash: typing.Optional[str] = None
    single_sim: str = ""
    talent_list: typing.Dict[WowSpec, typing.Iterable[str]] = dataclasses.field(
        default_factory=dict
    )
    talent_permutations: bool = False
    target_error: typing.Dict[str, str] = dataclasses.field(default_factory=dict)
    threads: str = "8"
    tier: str = "27"
    use_raidbots: bool = False
    write_humanreadable_secondary_distribution_file: bool = False
    fight_styles: typing.List[str] = dataclasses.field(default_factory=list)
    wow_class_spec_list: typing.List[typing.Optional[WowSpec]] = dataclasses.field(
        default_factory=list
    )

    def __post_init__(self, *args, **kwargs) -> None:
        self.fight_styles.append("patchwerk")
        self.target_error["patchwerk"] = "0.1"

    def update(self, obj: object) -> "Config":
        """Update the Configuration using the provided object.

        Args:
            obj (object): configuration object, e.g. a module or a different class instance
        """
        vars(self).update(vars(obj))

        return self

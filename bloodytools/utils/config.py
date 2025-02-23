import dataclasses
import logging
import sys
import typing

from bloodytools.utils.data_type import DataType
from simc_support.game_data.WowSpec import WowSpec, get_wow_spec

from bloodytools.utils.simc import get_simc_hash

logger = logging.getLogger(__name__)

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
    executable: str = "../SimulationCraft/simc"
    """Path to the executable, including the executable"""
    iterations: str = "60000"
    keep_files: bool = False
    # affects trinkets
    max_ilevel: int = 680
    # affects trinkets
    min_ilevel: int = 635
    pretty: bool = False
    profileset_work_threads: str = "2"
    ptr: str = "0"
    raidbots: bool = False
    remove_files: bool = False
    secondary_distributions_step_size: int = 10
    simc_hash: str = ""
    single_sim: str = ""
    # Affects secondary distribution simulations
    # if no list is provided for a class-spec, all dps talent combinations will be run. If you want to only sim the base profiles, set 'talent_permutations' to False
    # talent_list = {
    #   WowSpec.ELEMENTAL: [
    #     "2301022",
    #   ],
    # }  # example for a talent list for Elemental Shamans
    # set to False, to sim only the base profile talent combinations
    talent_list: typing.Dict[WowSpec, typing.Iterable[str]] = dataclasses.field(
        default_factory=dict
    )
    talent_permutations: bool = False
    target_error: typing.Dict[str, str] = dataclasses.field(default_factory=dict)
    threads: str = ""
    tier: str = "TWW1"
    use_raidbots: bool = False
    write_humanreadable_secondary_distribution_file: bool = False
    apikey: str = ""
    simulator_type_names: typing.List[str] = dataclasses.field(default_factory=list)
    wow_class_spec_names: typing.List[typing.Tuple[str, str]] = dataclasses.field(
        default_factory=list
    )
    fight_styles: typing.List[str] = dataclasses.field(default_factory=list)

    log_warnings: bool = True
    """Log warnings for Config creation."""

    def __post_init__(self, *args, **kwargs) -> None:
        self.target_error["patchwerk"] = "0.1"
        self.target_error["castingpatchwerk"] = "0.1"
        self.target_error["hecticaddcleave"] = "0.2"
        self.target_error["beastlord"] = "0.2"
        try:
            self.set_simc_hash()
        except ValueError as e:
            logger.debug(
                "Setting simc hash failed. This is usually ok, because the default path is probably incorrect.",
                exc_info=e,
            )
            pass

    def set_simc_hash(self) -> None:
        new_hash = get_simc_hash(self.executable)
        if new_hash:
            self.simc_hash = new_hash

    @property
    def wow_specs(self) -> typing.List[WowSpec]:
        return [get_wow_spec(*name_tuple) for name_tuple in self.wow_class_spec_names]

    @classmethod
    def create_config_from_args(cls, args: object) -> "Config":
        config = cls(log_warnings=False)

        config.log_warnings = True

        if args.single_sim:  # type: ignore
            logger.debug("-s / --single_sim detected")
            try:
                (
                    simulation_type,
                    wow_class,
                    wow_spec,
                    fight_style,
                ) = args.single_sim.split(  # type: ignore
                    ","
                )
            except ValueError:
                logger.error("-s / --single_sim arg is missing parameters. Read -h.")
                sys.exit("Input error. Bloodytools terminates.")

            config.wow_class_spec_names = [
                (wow_class, wow_spec),
            ]

            config.fight_styles = [
                fight_style,
            ]
            if fight_style not in config.target_error:
                config.target_error[fight_style] = "0.1"

            config.simulator_type_names = [
                simulation_type,
            ]

        if args.executable:  # type: ignore
            config.executable = args.executable  # type: ignore
            logger.debug("Set executable to {}".format(config.executable))

        if args.threads:  # type: ignore
            config.threads = args.threads  # type: ignore
            logger.debug("Set threads to {}".format(config.threads))

        if args.profileset_work_threads:  # type: ignore
            config.profileset_work_threads = args.profileset_work_threads  # type: ignore
            logger.debug(
                "Set profileset_work_threads to {}".format(
                    config.profileset_work_threads
                )
            )

        if args.ptr:  # type: ignore
            config.ptr = "1"
        else:
            config.ptr = "0"

        config.custom_profile = args.custom_profile  # type: ignore
        config.custom_fight_style = args.custom_fight_style  # type: ignore
        config.custom_apl = args.custom_apl  # type: ignore
        if args.custom_apl:  # type: ignore
            config.default_actions = "0"

        if args.target_error:  # type: ignore
            for fight_style in config.target_error.keys():
                config.target_error[fight_style] = args.target_error  # type: ignore

        config.use_raidbots = args.raidbots  # type: ignore
        config.keep_files = args.keep_files  # type: ignore
        config.pretty = args.pretty  # type: ignore

        config.set_simc_hash()

        return config

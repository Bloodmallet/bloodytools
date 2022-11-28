import dataclasses
from simc_support.game_data import WowSpec
from bloodytools.main import main
import unittest

DONT_TEST = (
    WowSpec.RESTORATION_DRUID,
    WowSpec.HOLY_PRIEST,
    WowSpec.MISTWEAVER,
)


@dataclasses.dataclass
class ParsedInput:
    executable: str
    target_error: str
    all: bool = False
    custom_apl: bool = False
    custom_fight_style: bool = False
    custom_profile: bool = False
    debug: bool = False
    keep_files: bool = False
    pretty: bool = False
    ptr: bool = False
    raidbots: bool = False
    profileset_work_threads: str = ""
    single_sim: str = ""
    threads: str = ""


class TestAll(unittest.TestCase):
    def setUp(self) -> None:
        self.specs = WowSpec.WOWSPECS
        # remove unsupported specs
        self.specs = [spec for spec in self.specs if spec not in DONT_TEST]

        self.args = ParsedInput(
            target_error="1.0", executable="../SimulationCraft/simc.exe"
        )

    def test_legendaries(self):
        for spec in self.specs:
            with self.subTest(spec=spec):
                self.args.single_sim = (
                    f"legendaries,{spec.wow_class.simc_name},{spec.simc_name},patchwerk"
                )
                self.assertIsNone(main(self.args))

    def test_races(self):
        for spec in self.specs:
            with self.subTest(spec=spec):
                self.args.single_sim = (
                    f"races,{spec.wow_class.simc_name},{spec.simc_name},patchwerk"
                )
                self.assertIsNone(main(self.args))

    def test_secondary_distributions(self):
        for spec in self.specs:
            with self.subTest(spec=spec):
                self.args.single_sim = f"secondary_distributions,{spec.wow_class.simc_name},{spec.simc_name},patchwerk"
                self.assertIsNone(main(self.args))

    def test_soul_binds(self):
        for spec in self.specs:
            with self.subTest(spec=spec):
                self.args.single_sim = (
                    f"soul_binds,{spec.wow_class.simc_name},{spec.simc_name},patchwerk"
                )
                self.assertIsNone(main(self.args))

    def test_talents(self):
        for spec in self.specs:
            with self.subTest(spec=spec):
                self.args.single_sim = (
                    f"talents,{spec.wow_class.simc_name},{spec.simc_name},patchwerk"
                )
                self.assertIsNone(main(self.args))

    def test_trinkets(self):
        for spec in self.specs:
            with self.subTest(spec=spec):
                self.args.single_sim = (
                    f"trinkets,{spec.wow_class.simc_name},{spec.simc_name},patchwerk"
                )
                self.assertIsNone(main(self.args))

    def test_tier_sets(self):
        for spec in self.specs:
            with self.subTest(spec=spec):
                self.args.single_sim = (
                    f"tier_set,{spec.wow_class.simc_name},{spec.simc_name},patchwerk"
                )
                self.args.ptr = True
                self.args.target_error = "0.1"
                self.assertIsNone(main(self.args))

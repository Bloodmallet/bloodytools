"""Simulate and then collect all data of a tier."""

from bloodytools.utils.config import Config
from simc_support.game_data import WowSpec
from bloodytools.main import main as main_routine
import dataclasses
import logging
import json
import enum
from rich.console import Console
from rich.table import Table
import typing
import os

logging.basicConfig(level=logging.ERROR)

logger = logging.getLogger()

TIER = "30"
EXECUTABLE = "../simc/simc.exe"
FIGHT_STYLE = "castingpatchwerk"


def simulate_tier_data(specs: typing.List[typing.Tuple[str, str]]) -> None:
    config = Config(
        executable=EXECUTABLE,
        pretty=True,
        tier=TIER,
        wow_class_spec_names=specs,
        simulator_type_names=["tier_set"],
        fight_styles=[FIGHT_STYLE],
    )
    main_routine(config)


@dataclasses.dataclass
class TierData:
    wow_spec: str
    wow_class: str
    no_tier_dps: int
    tier_2pc_dps: int
    tier_4pc_dps: int


def simc_name(name: str) -> str:
    return name.replace(" ", "_").lower()


def load_tier_data(specs: typing.List[typing.Tuple[str, str]]) -> typing.List[TierData]:
    data: typing.List[TierData] = []

    print(f"Listed class-spec combination below don't  have a T{TIER} profile yet.")
    for wow_class, wow_spec in specs:
        file_path = f"results/tier_set/{simc_name(wow_class)}_{simc_name(wow_spec)}_{FIGHT_STYLE}.json"

        if not os.path.exists(file_path):
            print(f'("{wow_class}", "{wow_spec}"),')
            continue

        with open(
            file_path,
            "r",
            encoding="utf-8",
        ) as f:
            loaded_file = json.load(f)
        # data.custom profile
        #   2p
        #   4p
        #   no tier
        data.append(
            TierData(
                wow_class=wow_class,
                wow_spec=wow_spec,
                no_tier_dps=loaded_file["data"][f"T{TIER}"]["no tier"],
                tier_2pc_dps=loaded_file["data"][f"T{TIER}"]["2p"],
                tier_4pc_dps=loaded_file["data"][f"T{TIER}"]["4p"],
            )
        )
    return data


def absolute_gain(data: TierData, target: str) -> float:
    return int(getattr(data, target)) - data.no_tier_dps


def relative_gain(data: TierData, target: str) -> float:
    return (int(getattr(data, target)) - data.no_tier_dps) / data.no_tier_dps * 100.0


def custom_table(
    data: typing.List[TierData],
    fn: typing.Callable[[TierData, str], float],
    title: str,
) -> None:
    sorted_data = sorted(
        data,
        key=lambda tier_data: fn(tier_data, "tier_4pc_dps"),
        reverse=True,
    )

    table = Table(title=title)

    table.add_column("Spec")
    table.add_column("2p", justify="right")
    table.add_column("2p + 4p", justify="right")

    for tier_data in sorted_data:
        table.add_row(
            " ".join([tier_data.wow_spec, tier_data.wow_class]),
            f"{float(fn(tier_data, 'tier_2pc_dps')):5>.2f}",
            f"{float(fn(tier_data, 'tier_4pc_dps')):5>.2f}",
        )

    console = Console()
    console.print(table)


def filter_by_existing_profiles(
    specs: typing.List[typing.Tuple[str, str]]
) -> typing.List[typing.Tuple[str, str]]:
    simc_path = os.path.join(*EXECUTABLE.split("/")[:-1])
    return [
        spec
        for spec in specs
        if os.path.exists(
            f"{simc_path}/profiles/Tier{TIER}/T{TIER}_{spec[0].replace(' ', '_')}_{spec[1].replace(' ', '_')}.simc"
        )
    ]


def main() -> None:
    specs = [(s.wow_class.full_name, s.full_name) for s in WowSpec.WOWSPECS]
    specs = filter_by_existing_profiles(specs)
    # simulate_tier_data(specs)
    data = load_tier_data(specs)

    custom_table(data, absolute_gain, f"Absolute gain T{TIER}")

    custom_table(data, relative_gain, f"Relative gain T{TIER} in %")


if __name__ == "__main__":
    main()

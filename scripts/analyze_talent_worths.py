import json
from rich.console import Console
from rich.table import Table

FILE_PATH = r"results\talent_removal\shaman_elemental_castingpatchwerk.json"
FILE_PATH = r"results\talent_addition\shaman_elemental_castingpatchwerk.json"
baseline_name = "baseline"
BUILD = None


def is_addition() -> bool:
    return "talent_addition" in FILE_PATH


def main() -> None:
    with open(FILE_PATH, "r") as f:
        data = json.load(f)

    if is_addition():
        print("Talent ADDITION")
    else:
        print("Talent REMOVAL")

    print(
        "Bigger number = more important for the build. Lower number = less impact on the build. Negative number = target error at play, apl issue, or actually an improvement to not have."
    )

    for build in data["data"]:
        # if BUILD is not None and BUILD not in build:
        #     continue

        build_data = data["data"][build]
        baseline = build_data[baseline_name]

        build_title = f"{build} ({baseline})"
        # print(build_title)
        table = Table(title=build_title)

        table.add_column("", style="cyan", no_wrap=True)
        table.add_column("diff", justify="right")
        table.add_column("talent")

        dps_talents = [t for t in build_data.keys() if t != baseline_name]
        dps_talents.sort(key=lambda name: build_data[name], reverse=is_addition())  # type: ignore

        if is_addition() and dps_talents:
            max_value = build_data[dps_talents[0]] - baseline
        elif dps_talents:
            max_value = baseline - build_data[dps_talents[0]]
        else:
            print(f"Skipping {build}. dps talents couldn't get extracted")
            continue

        for dps_talent in dps_talents:
            if is_addition():
                damage_loss = build_data[dps_talent] - baseline
            else:
                damage_loss = baseline - build_data[dps_talent]
            percentage = max(damage_loss / max_value, 0)
            dashes = "-" * int(20 * percentage)
            spaces = " " * (20 - int(20 * percentage))
            bar = f"|{dashes}{spaces}|"
            # print(
            #     f"  {bar} {damage_loss: >4} ({damage_loss/baseline * 100:5.2f}%) {dps_talent}"
            # )

            table.add_row(
                dashes,
                f"{damage_loss: >4} ({damage_loss/baseline * 100:5.2f}%)",
                dps_talent,
            )

        console = Console()
        console.print(table)


if __name__ == "__main__":
    main()

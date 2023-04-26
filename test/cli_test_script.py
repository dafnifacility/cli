"""
Script for running tests of the cli as a whole via the command line

Note: Should login just before running with --snapshot as can time out
      and get stuck
"""

from pathlib import Path
import subprocess
from typing import Optional, Union

import click

# Not sure why it wasn't finding this, but this will do for now
DAFNI_SCRIPT_LOCATION = "/home/joel/.local/bin/dafni"

# Where to save snapshots
SNAPSHOT_SAVE_LOCATION = "/home/joel/dafni_cli_snapshots/"

# Commands to test - organised into sections
COMMANDS = {
    "login": ["dafni login --help", "dafni login"],
    "get": {
        "models": [
            "dafni get models --help",
            "dafni get models",
            "dafni get models --json",
            "dafni get models --long",
            "dafni get models --creation-date 01/01/2021",
            "dafni get models --creation-date 01/01/2019",
            "dafni get models --creation-date 01/01/2019 --long",
            "dafni get models --publication-date 01/01/2021",
            "dafni get models --publication-date 01/01/2019",
            "dafni get models --publication-date 01/01/2019 --long",
            "dafni get models --publication-date 01/01/2019 --long --json",
        ],
        "model": [
            "dafni get model --help",
            "dafni get model 9de4ad50-fd98-4def-9bfc-39378854e6a1",
            "dafni get model 9de4ad50-fd98-4def-9bfc-39378854e6a1 --json",
            "dafni get model ef4b22c8-63be-4b53-ba7c-c1cf301774b2 399cdaac-aab6-494d-870a-66de8a4217bb",
            "dafni get model 9de4ad50-fd98-4def-9bfc-39378854e6a1 --version-history",
            "dafni get model ef4b22c8-63be-4b53-ba7c-c1cf301774b2 399cdaac-aab6-494d-870a-66de8a4217bb --version-history",
            "dafni get model ef4b22c8-63be-4b53-ba7c-c1cf301774b2 399cdaac-aab6-494d-870a-66de8a4217bb --version-history --json",
        ],
        "datasets": [
            "dafni get datasets --help",
            "dafni get datasets",
            "dafni get datasets --json",
            "dafni get datasets --search passport",
            "dafni get datasets --start-date 01/01/2019",
            "dafni get datasets --end-date 01/01/2021",
            "dafni get datasets --start-date 01/01/2019 --end-date 01/01/2021",
            "dafni get datasets --search passport --start-date 01/01/2011",
            "dafni get datasets --search passport --end-date 01/01/2022",
            "dafni get datasets --search passport --start-date 01/01/2011 --end-date 01/01/2022",
            "dafni get datasets --search passport --start-date 01/01/2011 --end-date 01/01/2022 --json",
        ],
        "dataset": [
            "dafni get dataset --help",
            "dafni get dataset 6f6c7fb8-2f04-4ffc-b7a9-58dc2739d8c2 d8d8b3ae-9d33-42fe-bfb6-ba1d7c5f0d58",
            "dafni get dataset 6f6c7fb8-2f04-4ffc-b7a9-58dc2739d8c2 d8d8b3ae-9d33-42fe-bfb6-ba1d7c5f0d58 --long",
            "dafni get dataset 6f6c7fb8-2f04-4ffc-b7a9-58dc2739d8c2 d8d8b3ae-9d33-42fe-bfb6-ba1d7c5f0d58 -l",
            "dafni get dataset 6f6c7fb8-2f04-4ffc-b7a9-58dc2739d8c2 d8d8b3ae-9d33-42fe-bfb6-ba1d7c5f0d58 --version-history",
            "dafni get dataset 6f6c7fb8-2f04-4ffc-b7a9-58dc2739d8c2 d8d8b3ae-9d33-42fe-bfb6-ba1d7c5f0d58 --json",
            "dafni get dataset 6f6c7fb8-2f04-4ffc-b7a9-58dc2739d8c2 d8d8b3ae-9d33-42fe-bfb6-ba1d7c5f0d58 --version-history --json",
        ],
    },
}


class Output:
    def __init__(self):
        self.succeeded_commands = []
        self.failed_commands = []

    def print_output(self):
        print(
            f"{len(self.succeeded_commands)}/{len(self.succeeded_commands) + len(self.failed_commands)} succeeded"
        )


def clean_string(string: str):
    return "".join(e for e in string if e.isalnum())


def save_and_check_snapshot(
    command: str, run_result: subprocess.CompletedProcess, snapshot: int, output: Output
):
    if run_result.returncode != 0:
        print(f"[FAILED!] {command}")
        # print(run_result.stderr)
        output.failed_commands.append(command)
        return

    # Path to compare snapshot to
    path = Path(SNAPSHOT_SAVE_LOCATION, f"{clean_string(command)}.out")

    string_output = run_result.stdout.decode().splitlines()
    string_output = [line + "\n" for line in string_output]

    # Check for overwrite mode
    if snapshot == 2:
        with open(path, "w", encoding="utf-8") as file:
            file.writelines(string_output)
    elif snapshot == 1:
        if not path.exists():
            raise RuntimeError(
                f"Could not read file at {path}, did you mean to use --snapshot_overwrite?"
            )

        # Compare the result
        with open(path, "r", encoding="utf-8") as file:
            previous_contents = file.readlines()

        if previous_contents != output:
            print(f"[Failed] {command}")
            print("Expected:")
            print(previous_contents)
            print("Got:")
            print(string_output)
            output.failed_commands.append(command)
            return

    # Passed
    print(f"[Success] {command}")
    output.succeeded_commands.append(command)


def run_command(command: str, snapshot: int, output: Output):
    if snapshot:
        run_result = subprocess.run(
            command.replace("dafni", DAFNI_SCRIPT_LOCATION),
            check=False,
            shell=True,
            stdout=subprocess.PIPE,
        )
        save_and_check_snapshot(command, run_result, snapshot, output)
    else:
        print(f"--------- {command} ---------")
        run_result = subprocess.run(
            command.replace("dafni", DAFNI_SCRIPT_LOCATION),
            check=True,
            shell=True,
        )
        if run_result.returncode == 0:
            output.succeeded_commands.append(command)
        else:
            output.failed_commands.append(command)
        print("-------------------------------")
        print()
        input("Press enter to continue")
        print()


def run_commands(
    commands: Union[dict, list],
    snapshot: int,
    output: Output,
    prefix: Optional[str] = None,
):
    # If a dict then expect subsections
    if isinstance(commands, dict):
        for key, section in commands.items():
            run_commands(section, snapshot, output, prefix + ", key" if prefix else key)
    elif isinstance(commands, list):
        print(f"--------- Testing section: {prefix} ---------")
        print()
        for command in commands:
            run_command(command, snapshot, output)


@click.command()
@click.option("--section", help="Section of commands to execute")
@click.option(
    "--snapshot",
    help="Whether to snapshot the result and compare to a previous run. When true, commands will not wait and the output will not be visible.",
    is_flag=True,
    default=False,
)
@click.option(
    "--snapshot_overwrite",
    help="Whether to snapshot the result and compare to a previous run. When true, commands will not wait and the output will not be visible.",
    is_flag=True,
    default=False,
)
def run_tests(section, snapshot, snapshot_overwrite):
    commands = COMMANDS

    # Take 1 to mean compare, 2 to mean override
    if snapshot:
        snapshot = 1
    if snapshot_overwrite:
        snapshot = 2

    output = Output()

    if section:
        commands = commands[section]
        run_commands(commands, snapshot, output, section)
    else:
        run_commands(commands, snapshot, output, section)

    print()
    output.print_output()


if __name__ == "__main__":
    run_tests()

"""
Script for running tests of the cli as a whole via the command line

Notes on usage:
    - Replace DAFNI_SCRIPT_LOCATION and SNAPSHOT_SAVE_LOCATION as necessary
      before executing
    - Run on python command line e.g. python ./test/cli_test_script --help
    - Should login just before running with --snapshot as otherwise token
      could time out and get stuck
"""

import subprocess
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Union

import click

# Not sure why it wasn't finding this, but this will do for now
DAFNI_CLI_SCRIPT = "/home/joel/.local/bin/dafni"

# Where to save snapshots
SNAPSHOT_SAVE_LOCATION = "/home/joel/dafni_cli_snapshots/"


class SpecialCommand(ABC):
    """Class for special commands that may need to do some independent file
    checking e.g. download"""

    @abstractmethod
    def get_command(self) -> str:
        """Should return the command to run (also a time to do any special
        stuff e.g. creating a temporary directory)"""

    @abstractmethod
    def check_ran_correctly(self) -> bool:
        """Should return whether the command ran successfully or not"""


class DownloadDatasetCommand(SpecialCommand):
    """Command that downloads a dataset"""

    def __init__(self) -> None:
        super().__init__()

        self._temp_dir = None

    def get_command(self):
        # Create a temporary directory for the datasets being downloaded
        self._temp_dir = tempfile.TemporaryDirectory()

        return f"dafni download dataset b71f0880-ff95-4b68-82a1-aafa2e949825 c052d9b8-dbca-42b0-85b5-135016a2fbb1 --directory {self._temp_dir.name}"

    def check_ran_correctly(self) -> bool:
        file_path = Path(
            self._temp_dir.name,
            "Dataset_b71f0880-ff95-4b68-82a1-aafa2e949825_c052d9b8-dbca-42b0-85b5-135016a2fbb1.zip",
        )
        success = file_path.is_file()
        self._temp_dir.cleanup()
        return success


# Commands to test - organised into sections that can be executed separately
COMMANDS = {
    "login": ["dafni login --help", "dafni login"],
    "get": {
        "help": ["dafni get --help"],
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
        "workflows": [
            "dafni get workflows --help",
            "dafni get workflows",
            "dafni get workflows --json",
            "dafni get workflows --long",
            "dafni get workflows --creation-date 01/01/2021",
            "dafni get workflows --creation-date 01/01/2019",
            "dafni get workflows --creation-date 01/01/2019 --long",
            "dafni get workflows --publication-date 01/01/2021",
            "dafni get workflows --publication-date 01/01/2019",
            "dafni get workflows --publication-date 01/01/2019 --long",
            "dafni get workflows --publication-date 01/01/2019 --long --json",
        ],
        "workflow": [
            "dafni get workflow --help",
            "dafni get workflow cfb164b2-59de-4156-85ea-36049e147322",
            "dafni get workflow cfb164b2-59de-4156-85ea-36049e147322 --json",
            "dafni get workflow 4a7c1897-e902-4966-b4a8-d8c4c64ff092 797e8ba2-539d-4284-ba86-dea4a930206e",
            "dafni get workflow cfb164b2-59de-4156-85ea-36049e147322 --version-history",
            "dafni get workflow 4a7c1897-e902-4966-b4a8-d8c4c64ff092 797e8ba2-539d-4284-ba86-dea4a930206e --version-history",
            "dafni get workflow 4a7c1897-e902-4966-b4a8-d8c4c64ff092 797e8ba2-539d-4284-ba86-dea4a930206e --version-history --json",
        ],
    },
    # The following commented out tests may be automated, but are tricker and
    # can effect the others - probably best to run these manually for now
    # anyway
    "upload": {
        "help": ["dafni upload --help"],
        "model": [
            "dafni upload model --help",
            # 'dafni upload model model_definition.yaml tiny-example.tar --version-message "Version message"',
            # 'dafni upload model model_definition.yaml tiny-example.tar --version-message "Child model" --parent-model e8ab1364-e673-470b-b082-7d459b523a44',
        ],
        "dataset": [
            "dafni upload dataset --help",
            # "dafni upload dataset metadata.json file_1.txt file_2.csv file_3.dat",
        ],
        "workflow": [
            "dafni upload workflow --help",
            # "dafni upload workflow workflow-upload.json",
            # "dafni upload workflow-params workflow-upload.json",
        ],
    },
    "delete": {
        "help": ["dafni delete --help"],
        "model": [
            "dafni delete model --help",
            # "dafni delete model 5ec7ebcc-7fcc-451d-8bd3-74e25ab9ccc9",
        ],
        "workflow": [
            "dafni delete workflow --help",
            # "dafni delete workflow 5ec7ebcc-7fcc-451d-8bd3-74e25ab9ccc9",
        ],
    },
    "download": {
        "help": ["dafni download --help"],
        "dataset": [DownloadDatasetCommand()],
    },
    "logout": ["dafni logout --help", "dafni logout"],
}


class Output:
    """Class for storing output of running the tests"""

    def __init__(self):
        self.succeeded_commands = []
        self.failed_commands = []

    def print_output(self):
        """Outputs a summary of the commands that succeeded/failed"""
        print(
            f"{len(self.succeeded_commands)}/{len(self.succeeded_commands) + len(self.failed_commands)} succeeded"
        )
        if self.failed_commands:
            print("------ Summary of failed commands -----")
            for command in self.failed_commands:
                print(command)


def clean_string(string: str):
    """Returns a clean string that could make a valid file name"""
    return "".join(e for e in string if e.isalnum())


def save_and_check_snapshot(
    command: Union[str, SpecialCommand],
    run_result: subprocess.CompletedProcess,
    snapshot: int,
    output: Output,
):
    """Saves the result of a command as a snapshot or otherwise checks the
    result against an already existing one

    Args:
        command (str or SpecialCommand): Command that was run
        run_result (subprocess.CompletedProcess): Result of running the
                                                  command
        snapshot (int): Integer value specifying what to do:
                        0 - Do nothing
                        1 - Compare the result with a stored snapshot
                        2 - Overwrite any stored snapshot
        output (Output): Object for storing whether commands have succeeded
                         or not
    """
    success = run_result.returncode == 0
    if isinstance(command, SpecialCommand):
        success = success and command.check_ran_correctly()
        command_str = command.get_command()
    else:
        command_str = command

    if not success:
        # Command itself failed to execute
        print(f"[FAILED!] {command_str}")
        # print(run_result.stderr)
        output.failed_commands.append(command_str)
        return

    # Path to compare snapshot to
    path = Path(SNAPSHOT_SAVE_LOCATION, f"{clean_string(command_str)}.out")

    # Store as a string array with new lines ready for saving/comparing
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

        if previous_contents != string_output:
            print(f"[Failed] {command_str}")
            print()
            print("Expected:")
            print("".join(previous_contents))
            print("Got:")
            print("".join(string_output))
            output.failed_commands.append(command_str)
            return

    # Passed
    print(f"[Success] {command_str}")
    output.succeeded_commands.append(command_str)


def run_command(command: Union[str, SpecialCommand], snapshot: int, output: Output):
    """Runs a given command checking it against a snapshot if necessary

    Args:
        command (str): Command to execute
        snapshot (int): Integer value specifying what to do:
                        0 - Do nothing
                        1 - Compare the result with a stored snapshot
                        2 - Overwrite any stored snapshot
        output (Output): Object for storing whether commands have succeeded
                         or not
    """

    if isinstance(command, SpecialCommand):
        command_str = command.get_command()
    else:
        command_str = command

    if snapshot:
        # Run command, hiding input (this is where login may get stuck if
        # token times out)
        run_result = subprocess.run(
            command_str.replace("dafni", DAFNI_CLI_SCRIPT),
            check=False,
            shell=True,
            stdout=subprocess.PIPE,
        )
        save_and_check_snapshot(command, run_result, snapshot, output)
    else:
        # Run command waiting for user input before running the next one
        header = f"--------- {command_str} ---------"
        print(header)
        run_result = subprocess.run(
            command_str.replace("dafni", DAFNI_CLI_SCRIPT),
            check=False,
            shell=True,
        )

        success = run_result.returncode == 0
        if isinstance(command, SpecialCommand):
            success = success and command.check_ran_correctly()

        if success:
            output.succeeded_commands.append(command_str)
        else:
            output.failed_commands.append(command_str)
        print("-" * len(header))
        print()
        input("Press enter to continue")
        print()


def run_commands(
    commands: Union[dict, list],
    snapshot: int,
    output: Output,
    prefix: Optional[str] = None,
):
    """Runs set of commands given as either a dictionary or a list

    Args:
        commands (dict or list): Either a dictionary containing keys
                        representing sections with lists of commands to run
                        or a list containing the commands. This function is
                        recursive so additional sections in a dictionary are
                        run (but with a different 'prefix')
        snapshot (int): Integer value specifying what to do:
                        0 - Do nothing
                        1 - Compare the result with a stored snapshot
                        2 - Overwrite any stored snapshot
        output (Output): Object for storing whether commands have succeeded
                         or not
        prefix (str): Prefix for identifying the section being run in the
                      output - typically the keys in the above commands
                      dictionary
    """
    # If a dict then expect subsections
    if isinstance(commands, dict):
        for key, section in commands.items():
            run_commands(
                section, snapshot, output, f"{prefix}.{key}" if prefix else key
            )
    elif isinstance(commands, list):
        # Run commands in the list
        print(f"--------- Testing section: {prefix} ---------")
        print()
        for command in commands:
            run_command(command, snapshot, output)


@click.command()
@click.option(
    "--section",
    help="Section of commands to execute. For nested sections use '.' e.g. --section get.datasets",
)
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
    """Executes the tests"""

    commands = COMMANDS

    # Take 1 to mean compare, 2 to mean override
    if snapshot:
        snapshot = 1
    if snapshot_overwrite:
        snapshot = 2

    output = Output()

    if section:
        # Use something like get.dataset to mean ["get"]["dataset"]
        split = section.split(".")
        for key in split:
            commands = commands[key]

    run_commands(commands, snapshot, output, section)

    print()
    output.print_output()


if __name__ == "__main__":
    # pylint:disable=no-value-for-parameter
    run_tests()

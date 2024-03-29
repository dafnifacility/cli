"""
Script for running tests of the cli as a whole via the command line

Notes on usage:
    - Replace DAFNI_SCRIPT_LOCATION and DAFNI_SNAPSHOT_SAVE_LOCATION as
      necessary before executing (you can also assign them with environment
      variables)
    - Run on python command line e.g. python ./test/cli_test_script --help
    - Should login just before running with --snapshot as otherwise token
      could time out and get stuck
"""

import os
import subprocess
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Union

import click

from dafni_cli.consts import ENVIRONMENT

home_dir = Path.home()

# Where cli executable is
DAFNI_CLI_SCRIPT = os.getenv("DAFNI_CLI_SCRIPT") or f"{home_dir}/.local/bin/dafni"

# Where to save snapshots (Should be an already existing folder)
DAFNI_SNAPSHOT_SAVE_LOCATION = (
    os.getenv("DAFNI_SNAPSHOT_SAVE_LOCATION") or f"{home_dir}/dafni_cli_snapshots/"
)


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

    def get_snapshot_file_name(self, command_str: str) -> str:
        """Should return the name snapshots of this command should be saved as"""
        return clean_string(command_str)


# Dictionary of object IDs to be used in the various test commands
COMMAND_PARAMS_PRODUCTION = {
    "models": [
        {"version_id": "9de4ad50-fd98-4def-9bfc-39378854e6a1"},
        {"version_id": "ef4b22c8-63be-4b53-ba7c-c1cf301774b2"},
        {"version_id": "399cdaac-aab6-494d-870a-66de8a4217bb"},
    ],
    "datasets": [
        {
            "id": "6f6c7fb8-2f04-4ffc-b7a9-58dc2739d8c2",
            "version_id": "d8d8b3ae-9d33-42fe-bfb6-ba1d7c5f0d58",
        },
        # Used for download test
        {
            "id": "ff6790db-1602-437f-bd6c-d355ed8f04e2",
            "version_id": "74d40b2a-030f-4181-ba2c-63c8901df512",
        },
    ],
    "workflows": [
        {"version_id": "cfb164b2-59de-4156-85ea-36049e147322"},
        {"version_id": "4a7c1897-e902-4966-b4a8-d8c4c64ff092"},
        # Has some instances
        {"version_id": "4397387e-1223-4fee-a258-6fac402de82c"},
    ],
    "workflow_instances": [{"instance_id": "e7f4b809-a93c-40c1-8415-9eec8baceeda"}],
}

COMMAND_PARAMS_STAGING = {
    "models": [
        {"version_id": "9de4ad50-fd98-4def-9bfc-39378854e6a1"},
        {"version_id": "ef4b22c8-63be-4b53-ba7c-c1cf301774b2"},
        {"version_id": "399cdaac-aab6-494d-870a-66de8a4217bb"},
    ],
    "datasets": [
        {
            "id": "2808b40c-0a97-4ba1-90d3-2c825151fb44",
            "version_id": "63df8bb3-237a-4b22-ab87-07169dbf129d",
        },
        # Used for download test
        {
            "id": "ff276247-3d94-43e1-a95e-13a5a8cd8b47",
            "version_id": "81f8e9fb-bcbf-4a0a-a4ed-ec0dc95b4b9c",
        },
    ],
    "workflows": [
        {"version_id": "851bf5bf-2e09-4340-922a-205e8cf430fd"},
        {"version_id": "4f8cc1da-38ee-45ec-91e0-88de700a83ef"},
        # Has some instances
        {"version_id": "fcd964e4-4b2e-47ec-8c32-bb6bd002ba61"},
    ],
    "workflow_instances": [{"instance_id": "4048d977-c7ce-46a8-9433-1bb471775486"}],
}

COMMAND_PARAMS = (
    COMMAND_PARAMS_PRODUCTION if ENVIRONMENT == "production" else COMMAND_PARAMS_STAGING
)


class DownloadDatasetCommand(SpecialCommand):
    """Command that downloads a dataset"""

    BASE_COMMAND = (
        f"dafni download dataset {COMMAND_PARAMS['datasets'][1]['version_id']}"
    )

    def __init__(self) -> None:
        super().__init__()

        self._temp_dir = None

    def get_command(self):
        # Create a temporary directory for the datasets being downloaded
        self._temp_dir = tempfile.TemporaryDirectory()

        return f"{self.BASE_COMMAND} --directory {self._temp_dir.name}"

    def check_ran_correctly(self) -> bool:
        file_path = Path(
            self._temp_dir.name,
            f"Dataset_{COMMAND_PARAMS['datasets'][1]['id']}_{COMMAND_PARAMS['datasets'][1]['version_id']}.zip",
        )
        success = file_path.is_file()
        self._temp_dir.cleanup()
        return success

    def get_snapshot_file_name(self, command_str: str) -> str:
        # Force the name to be the same despite a temporary directory in the
        # command itself
        return clean_string(self.BASE_COMMAND)


# Commands to test - organised into sections that can be executed separately
COMMANDS = {
    "login": ["dafni login --help", "dafni login"],
    "get": {
        "help": ["dafni get --help"],
        "models": [
            "dafni get models --help",
            "dafni get models",
            "dafni get models --json",
            "dafni get models --creation-date 2021-01-01",
            "dafni get models --creation-date 2019-01-01",
            "dafni get models --publication-date 2021-01-01",
            "dafni get models --publication-date 2019-01-01",
            "dafni get models --publication-date 2019-01-01 --json",
        ],
        "model": [
            "dafni get model --help",
            f"dafni get model {COMMAND_PARAMS['models'][0]['version_id']}",
            f"dafni get model {COMMAND_PARAMS['models'][0]['version_id']} --json",
            f"dafni get model {COMMAND_PARAMS['models'][1]['version_id']} {COMMAND_PARAMS['models'][2]['version_id']}",
            f"dafni get model {COMMAND_PARAMS['models'][0]['version_id']} --version-history",
            f"dafni get model {COMMAND_PARAMS['models'][1]['version_id']} {COMMAND_PARAMS['models'][2]['version_id']} --version-history",
            f"dafni get model {COMMAND_PARAMS['models'][1]['version_id']} {COMMAND_PARAMS['models'][2]['version_id']} --version-history --json",
        ],
        "datasets": [
            "dafni get datasets --help",
            "dafni get datasets",
            "dafni get datasets --json",
            "dafni get datasets --search passport",
            "dafni get datasets --start-date 2019-01-01",
            "dafni get datasets --end-date 2021-01-01",
            "dafni get datasets --start-date 2019-01-01 --end-date 2021-01-01",
            "dafni get datasets --search passport --start-date 2011-01-01",
            "dafni get datasets --search passport --end-date 2022-01-01",
            "dafni get datasets --search passport --start-date 2011-01-01 --end-date 2022-01-01",
            "dafni get datasets --search passport --start-date 2011-01-01 --end-date 2022-01-01 --json",
        ],
        "dataset": [
            "dafni get dataset --help",
            f"dafni get dataset {COMMAND_PARAMS['datasets'][0]['version_id']}",
            f"dafni get dataset {COMMAND_PARAMS['datasets'][0]['version_id']} --long",
            f"dafni get dataset {COMMAND_PARAMS['datasets'][0]['version_id']} -l",
            f"dafni get dataset {COMMAND_PARAMS['datasets'][0]['version_id']} --version-history",
            f"dafni get dataset {COMMAND_PARAMS['datasets'][0]['version_id']} --json",
            f"dafni get dataset {COMMAND_PARAMS['datasets'][0]['version_id']} --version-history --json",
        ],
        "workflows": [
            "dafni get workflows --help",
            "dafni get workflows",
            "dafni get workflows --json",
            "dafni get workflows --creation-date 2021-01-01",
            "dafni get workflows --creation-date 2019-01-01",
            "dafni get workflows --publication-date 2021-01-01",
            "dafni get workflows --publication-date 2019-01-01",
            "dafni get workflows --publication-date 2019-01-01 --json",
        ],
        "workflow": [
            "dafni get workflow --help",
            f"dafni get workflow {COMMAND_PARAMS['workflows'][0]['version_id']}",
            f"dafni get workflow {COMMAND_PARAMS['workflows'][0]['version_id']} --json",
            f"dafni get workflow {COMMAND_PARAMS['workflows'][1]['version_id']} {COMMAND_PARAMS['workflows'][2]['version_id']}",
            f"dafni get workflow {COMMAND_PARAMS['workflows'][0]['version_id']} --version-history",
            f"dafni get workflow {COMMAND_PARAMS['workflows'][1]['version_id']} {COMMAND_PARAMS['workflows'][2]['version_id']} --version-history",
            f"dafni get workflow {COMMAND_PARAMS['workflows'][1]['version_id']} {COMMAND_PARAMS['workflows'][2]['version_id']} --version-history --json",
        ],
        "workflow-instances": [
            "dafni get workflow-instances --help",
            f"dafni get workflow-instances {COMMAND_PARAMS['workflows'][2]['version_id']}",
            f"dafni get workflow-instances {COMMAND_PARAMS['workflows'][2]['version_id']} --json",
            f"dafni get workflow-instances {COMMAND_PARAMS['workflows'][2]['version_id']} --start \"2022-01-19 14:48:33\"",
            f"dafni get workflow-instances {COMMAND_PARAMS['workflows'][2]['version_id']} --end \"2022-01-19 15:02:20\"",
            # Just a selection of status flags used here as rest are the same
            # and have unit tests
            f"dafni get workflow-instances {COMMAND_PARAMS['workflows'][2]['version_id']} --succeeded",
            f"dafni get workflow-instances {COMMAND_PARAMS['workflows'][2]['version_id']} --failed",
        ],
        "workflow-instance": [
            "dafni get workflow-instance --help",
            f"dafni get workflow-instance {COMMAND_PARAMS['workflow_instances'][0]['instance_id']}",
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
        "dataset-version": [
            "dafni upload dataset-version --help",
            # "dafni upload dataset-version d0bc2c54-69f8-4057-bae4-99476125f15c sunshine-tiny.zip --version-message \"Yet another new version test\"",
        ],
        "dataset-metadata": [
            "dafni upload dataset-metadata --help",
            # "dafni upload dataset-metadata d0bc2c54-69f8-4057-bae4-99476125f15c sunshine-tiny.zip --version-message \"New metadata version test\"",
        ],
        "workflow": [
            "dafni upload workflow --help",
            # "dafni upload workflow workflow-upload.json",
            # "dafni upload workflow-params workflow-upload.json",
        ],
    },
    "delete": {
        "help": ["dafni delete --help"],
        "model-version": [
            "dafni delete model-version --help",
            # "dafni delete model-version 5ec7ebcc-7fcc-451d-8bd3-74e25ab9ccc9",
        ],
        "dataset": [
            "dafni delete dataset --help"
            # "dafni delete dataset a4173ff8-2265-46de-89c3-02f814de4c35",
        ],
        "dataset-version": [
            "dafni delete dataset-version --help"
            # "dafni delete dataset-version a4173ff8-2265-46de-89c3-02f814de4c35",
        ],
        "workflow": [
            "dafni delete workflow-version --help",
            # "dafni delete workflow-version 5ec7ebcc-7fcc-451d-8bd3-74e25ab9ccc9",
        ],
    },
    "create": {
        "dataset-metadata": [
            "dafni create dataset-metadata --help",
            # This serves as an example, but is commented out as it is not
            # dependent on the current API and is tested via unit tests instead
            # dafni create dataset-metadata test_file.json --title "Some title" --description "Some description" --subject Environment --language en --keyword test --organisation "Some organisation" "organisation_id" --contact "Joel Davies" "joel.davies@stfc.ac.uk" --version-message "Initial version""]},
        ]
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
        snapshot_filename = command.get_snapshot_file_name(command_str)
    else:
        command_str = command
        snapshot_filename = clean_string(command_str)

    if not success:
        # Command itself failed to execute
        print(f"[FAILED!] {command_str}")
        # print(run_result.stderr)
        output.failed_commands.append(command_str)
        return

    # Path to compare snapshot to
    path = Path(DAFNI_SNAPSHOT_SAVE_LOCATION, f"{snapshot_filename}.out")

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

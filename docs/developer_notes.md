# DAFNI CLI Developer Notes

## Environment Setup
### Create a development environment
The code has been developed using Python *3.9.2* using a virtual environment.
The environment can be created using the following command, in the parent directory of the `dafni-cli` repository:

`python -m venv dafni-cli`

### Update to contain all development dependencies
The environment must then be activated for the current shell using the following command:

| Platform | Command |
| -------- | ------- |
| Windows | `path\to\dafni-cli\Scripts\activate.bat` |
| Linux | `source path/to/dafni-cli/bin/activate` |

Then run the following to add all of the required development dependencies:

| Platform | Command |
| -------- | ------- |
| Windows | `python -m pip install -r path\to\dafni-cli\docs\requirements.txt` |
| Linux | `python -m pip install -r path/to/dafni-cli/docs/requirements.txt` |

The requirements.txt file contains all required python module dependencies for both development and deployment.

___

## Running against staging

To run against staging, modify the `ENVIRONMENT` variable in `consts.py` to be `staging` instead of `production`.

## Running the tests
Whilst running the activated venv created locally for the dafni-cli, ensure you are in the root directory of the git repository, and use the following to run all tests:

`python -m unittest`

There is also a script for running full CLI commands against the current released version of DAFNI in the `/scripts` folder. To use this you first need to modify the `DAFNI_CLI_SCRIPT` variable to point to the installed CLI script or define it as an environment variable. You may be able to get away with assigning it to `dafni` but for some reason it didn't work for me so I had to use `whereis dafni` to find the location.

The script will modify the ID's of the models, dataset and workflows based on whether the CLI is installed for running on production or staging. (See [Running against staging](#running-against-staging))

Before running the tests make sure you login to the non-admin1 test account if running on production, otherwise the account shouldn't matter. If you are already logged in, logout first to ensure the refresh tokens wont expire during the execution.

You can then run the tests by using

`python ./scripts/test_script.py`

This will run each command one at a time, requiring you to press enter between commands. You may also use

`python ./scripts/test_script.py --snapshot_overwrite`

to run all in one go saving the outputs in a designated folder specified by the variable `DAFNI_SNAPSHOT_SAVE_LOCATION` (this folder should be in existence before running the script). Then using

`python ./scripts/test_script.py --snapshot`

will rerun the tests and will cause any with different outputs to fail. This is useful for comparing any changes.

Subsections of the tests can be run by naming a section as defined in the `COMMANDS` variable. E.g. `--section get` will run all 'get' commands listed under `COMMANDS["get"]`. `--section get.models` will run all `get models` commands listed under `COMMANDS["get"]["models"]`.

___
## Deployment 

### Executable Deployment
The code has been designed to be deployed as an executable, built using the pyinstaller module (https://pyinstaller.readthedocs.io/en/stable/).

A new executable can be created by running the following command in the venv environment outlined above. The dafni_cli.py is the file where the code will run from. So in this case the command is being run from within the dafni_cli folder. This command will create a dist folder with the root directory of the repository, where the **dafni_cli.exe** file will be located.

`pyinstaller --onefile dafni.py --hiddenimport=python-dateutil`

The additional option `--hiddenimport=python-dateutil` is required, as pyinstaller fails to automatically pick up the codes dependency on the python-dateutil module.

### Pip deployment
The code has also been designed to be deployed as a pip package via pypi (https://pypi.org/user/dafni-facility/).

If the code has been updated, and a new release is being made, the setup.py version number should be appropriately incremented, and then the following command run from the root directory of the repository:

`python -m build`

This will create a build and dist folder in the root folder, containing a `.tar.gz` and a `.whl` for the new version of the pip package ready to publish to pypi.
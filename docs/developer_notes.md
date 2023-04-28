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
## Running the tests
Whilst running the activated venv created locally for the dafni-cli, ensure you are in the root directory of the git repository, and use the following to run all tests:

`python -m unittest`

**Note**: Some tests currently fail as they are outdated
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
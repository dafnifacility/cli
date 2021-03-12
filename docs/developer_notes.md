# DAFNI CLI Developer Notes

## Environment Setup
### Create a development environment
The code has been developed using Python *3.9.2* using a virtual environment.
The environment can be created using the following command:

`python -m venv dafni-cli`

### Update to contain all development dependencies
The environment must then be activated using the following command:

`path\to\dafni-cli\Scripts\activate.bat`

Then run the following to add all of the required development dependencies:

`python -m pip install -r path\to\requirements.txt`

The requirements.txt file can be located within the docs folder of this repository, and contains all dependencies for both development and deployment.
___
## Running the tests
Whilst running the activated venv created locally for the dafni-cli, ensure you are in the current root directory of the git repository, and run the following to run all tests:

`python -m pytest -vv`

The `-vv` argument is to make pytest output information on any failing tests in a verbose manner.
___
## Deployment 

### Executable Deployment
The code has been designed to be deployed as an executable, built using the pyinstaller module (https://pyinstaller.readthedocs.io/en/stable/).

A new executable can be created by running the following command in the venv environment outlined above. The dafni_cli.py is the file where the code will run from. So in this case the command is being run from within the dafni_cli folder. This command will create a dist folder with the root directory of the repository, where the **dafni_cli.exe** file will be located.

`pyinstaller --onefile dafni.py --hiddenimport=python-dateutil`

The additional option `--hiddenimport=python-dateutil` is required, as pyinstaller fails to automatically pick up the codes dependency on the python-dateutil module.


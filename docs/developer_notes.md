# DAFNI CLI Developer Notes

## Environment Setup
### Create a development environment
The code has been developed using Python *3.9.5* using a virtual environment.
The environment can be created using the following command, in the parent directory of the `dafni-cli` folder:

`python -m venv .venv`

### Update to contain all development dependencies
The environment must then be activated for the current shell using the following command:

| Platform | Command |
| -------- | ------- |
| Windows | `.venv\Scripts\activate.bat` |
| Linux | `source .venv/bin/activate` |

Then run the following to add all of the required development dependencies:

```bash
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
```

The requirements.txt file contains all required python module dependencies for deployment and requirements-dev.txt contains
additional dependencies for development.

### Installing the CLI

Now install an editable install of the CLI using

```bash
python -m pip install -e .
```

This ensures any modifications are applied to the CLI itself.

## Running against staging

To run the CLI against staging, modify the `ENVIRONMENT` variable in `consts.py` to be `staging` instead of `production`. You may also need to set the `VERIFY` variable, located in the same file, to be `False` to avoid SSL errors during development. 

## Running the tests
Whilst running the activated venv created locally for the dafni-cli, ensure you are in the root directory of the git repository, and use the following to run all tests:

```bash
python -m unittest
```

There is also a script for running full CLI commands against the current released version of DAFNI in the `/scripts` folder. To use this you first need to modify the `DAFNI_CLI_SCRIPT` variable to point to the installed CLI script or define it as an environment variable. You may be able to get away with assigning it to `dafni` but for some reason it didn't work for me so I had to use `whereis dafni` to find the location.

The script will modify the ID's of the models, dataset and workflows based on whether the CLI is installed for running on production or staging. (See [Running against staging](#running-against-staging))

Before running the tests make sure you login to the non-admin1 test account. If you are already logged in, logout first to ensure the refresh tokens wont expire during the execution. You can also avoid this by assigning the `DAFNI_USERNAME` and `DAFNI_PASSWORD` environment variables.

You can then run the tests by using

```bash
python ./scripts/test_script.py
```

This will run each command one at a time, requiring you to press enter between commands. You may also use

```bash
python ./scripts/test_script.py --snapshot_overwrite
```

to run all in one go saving the outputs in a designated folder specified by the variable `DAFNI_SNAPSHOT_SAVE_LOCATION` (this folder should be in existence before running the script). Then using

```bash
python ./scripts/test_script.py --snapshot
```

will rerun the tests and will cause any with different outputs to fail. This is useful for comparing any changes.

Subsections of the tests can be run by naming a section as defined in the `COMMANDS` variable. E.g. `--section get` will run all 'get' commands listed under `COMMANDS["get"]`. `--section get.models` will run all `get models` commands listed under `COMMANDS["get"]["models"]`.

___
## Deployment 

### Automated

To deploy the CLI, push version tags in the form of `v*.*.*`. This will run the GitHub build action, performing the build, unit tests on the built package, and will then upload to test.pypi and draft a release under the GitHub releases tab.

You should then check the correct tag is selected, select the checkbox labelled pre-release if required and add any release notes. You may also check the build uploaded to test.pypi by using

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ dafni-cli
```

When ready, publish the release to trigger the upload to PyPi.

### Manual

Prior to producing a manual build you may wish to check what the version number of the CLI will be. This can be checked by running `python -m setuptools_git_versioning` in a clone of the repo. If you wish to force the version number you must modify the `pyproject.toml` by replacing the lines

```toml
dynamic = ["version"]

[tool.setuptools-git-versioning]
enabled = true
```
with the new version number e.g.
```toml
version = "0.0.1rc1"
```

Then build the package using
```bash
python -m build
```

This will create a build and dist folder in the root folder, containing a `.tar.gz` and a `.whl` for the new version of the pip package ready to publish to pypi.

You can check the build using
```bash
twine check ./dist/*
```

Manually uploading these to https://test.pypi.org/ can then be done with

```bash
twine upload --repository testpypi ./dist/*
```

or to https://pypi.org/ through

```bash
twine upload ./dist/*
```
# DAFNI CLI documentation

## Installation

## Commands

The syntax for these will change as per the requirements i.e.\
`dafni get model` instead of `dafni model get`.

### login
If `dafni_jwt.txt` exists with a JWT that has not expired yet, nothing happens.
If no such file exists, or the JWT has expired, the user is prompted for a username and password.
These are used to access a new JWT from the DAFNI API and this is stored in `dafni_jwt.txt`.

### get
Retrieve and display entities available to the user. 
If there is no valid JWT, the user will be prompted to login before the command is carried out.

**Commands:**\
get models - 
Lists the models available to the user.\
`get models [--creation-date] [--publication-date]`\
Options:
- **--creation-date**: Filter to only show the models created since a given date with format DD/MM/YYYY.
- **--publication-date**:  Filter to only show the models created since a given date with format DD/MM/YYYY.


**Deployment**
Run the following command in a venv environment using the requirements.txt file. The dafni_cli.py is the file where the code will run from. So in this case the command is being run from within the dafni_cli folder.

`pyinstaller --onefile dafni_cli.py --hiddenimport=python-dateutil`
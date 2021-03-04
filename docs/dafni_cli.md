# DAFNI CLI documentation

## Installation

## Commands

The syntax for these will change as per the requirements i.e.\
`dafni get model` instead of `dafni model get`.

### login
If `dafni_jwt.txt` exists with a JWT that has not expired yet, nothing happens.
If no such file exists, or the JWT has expired, the user is prompted for a username and password.
These are used to access a new JWT from the DAFNI API and this is stored in `dafni_jwt.txt`.

### model
Used to perform actions on models.
If there is no valid JWT, the user will br prompted to login before the command is carried out.

**list**\
Lists the models available to the user.\
Options:
- **--summary/--no-summary**: Whether the model summary should be displayed for each model.
- **--description/--no-description**: Whether the full model description should be displayed for each model.
- **--creation-date**: Filter to only show the models created since a given date with format DD/MM/YYYY.
- **--publication-date**:  Filter to only show the models created since a given date with format DD/MM/YYYY.
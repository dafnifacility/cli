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

**get models** - 
Lists the models available to the user.\
`get models [--creation-date] [--publication-date]`

Options:
- **--creation-date**: Filter to only show the models created since a given date with format DD/MM/YYYY.
- **--publication-date**:  Filter to only show the models created since a given date with format DD/MM/YYYY.

Example output:
<pre>
Name: Model 1     ID: abc10-ab20-3abc-12345678a1b2      Date: January 1st 2020
Summary: This is a summary of the model.
Name: Model 2     ID: xyz10-xy20-3xyz-12345678x1y2      Date: January 1st 2020
Summary: This is a summary of another model.
</pre>

get model - Displays the metadata for the model.\
`get model [version_id]`

Parameters:
- **version_id**: Version of the model to display the metadata of.
Multiple version IDs can be specified and the metadata of each model will be displayed in sequence.

Example output:
<pre>
Name: Model 1
Date: January 1st 2020
Summary:
This is a summary of the model.
Description:
This is a longer description of the model, perhaps touching on more details 
and other things. It uses text wrapping to be more readable.

Input Parameters:
Title       Type       Min    Max    Default  Description
--------------------------------------------------------------------
param1      integer    1      10     1        A fancy parameter
param2      string                   normal   A fancy setting

Input Data Slots:
Name: Input file
Path in container: inputs/
Required: True
Default Datasets:
Name: Dataset 1    ID: xyz09-xy09-8xyz-87654321x9y8   Version ID: xyz09-xy09-8xyz-56843975x9y8

Outputs:
Name                                     Format    Summary
a_very_big_table_of_results.csv          CSV       The results you care about
another_very_big_table_of_results.csv    CSV       Some extra results you may find useful
</pre>


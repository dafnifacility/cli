# DAFNI CLI documentation

## Introduction
This package provides a command line interface for the [DAFNI platform](https://www.dafni.ac.uk/).

## Installation and basic usage

With python and [pip](https://pip.pypa.io/en/stable/getting-started/) installed and available on the command line use the following to install the CLI

```bash
pip install dafni-cli
```

Once installed all commands will be accessible via `dafni`. For example you can use

```bash
dafni --help
```

to view a list of all of the available sub commands. Use `--help` on any unfamiliar command to receive more information about it.

Note, if you are installing directly to a linux system you may find that the executable, `dafni`, may not be 
on the system path (this will result in the `dafni` command not being found). You can fix this (in eg. Ubuntu) by adding the local 
path with following line (in the line replace bob with your own username), 

```bash
export PATH="/home/bob/.local/bin:${PATH}"
```
You can confirm /home/bob/.local/bin is the correct location to add with the command

```bash
find . -name "dafni"
```
which will recursively search for `dafni`

## Authentication

Almost all commands require authentication and there are two methods to achieve this.

### 1. Using the login command

To login interactively use the login command e.g.
```bash
dafni login
```
Then enter your username and password into the prompts. If your session expires which will always occur after about 30 minutes of not running any commands, you will be prompted to re-enter your password in the same way when you go to run a command. In this way you never actually have to run `dafni login` explicitly.

### 2. Using environment variables

You may also login using environment variables. To do this define the environment variables `DAFNI_USERNAME` and `DAFNI_PASSWORD` prior to using any commands. These will be used automatically rather than requesting you to enter a username or password. This will also avoid any timeouts experienced with the first method.

### Logout
No matter which method you use, a `.dafni_cli` file will be saved to your home directory to store the current or last used access tokens for the platform. These will become invalid after 30 minutes but may be removed at any time by using the logout command e.g.

```bash
dafni logout
```

This will also immediately invalidate the last access token that was saved.


## Common usage

### Getting information from the platform

The `dafni get` command can be used to look up and filter entities on the platform. For example

```bash
dafni get datasets
```

will list all datasets you have access to. Then you can inspect a particular dataset further using its version ID e.g.

```bash
dafni get dataset <version-id>
```

It is also possible to select datasets based on a search term with the following command (the search term will filter datasets based on keywords, as well as the dataset title and description).

```bash
dafni get datasets --search "Transport"
```

If you would prefer to output the results in a json file you can use the command

```bash
dafni get datasets --search "Transport" -j
```

### Uploading a new dataset

Uploading a new dataset requires both a metadata `.json` file, and at least one file you wish to upload as part of the dataset.

#### Creating the metadata json file

To make this easier you may use the `dafni create dataset-metadata` command. This will take a variety of inputs as found in its `--help` documentation and will save a metadata file you can then use to for the upload. A minimal example with all required options given is

```bash
dafni create dataset-metadata dataset_metadata.json \
    --title "Dataset title" --description "Dataset description" \
    --subject Environment --language en --keyword some_keyword \
    --organisation "Organisation name" "http://www.example.com/" \
    --contact "Joel Davies" "joel.davies@stfc.ac.uk" \
    --version-message "Initial version"
```

This creates a file named `dataset_metadata.json` containing your given parameters which can then be used during the upload.

You may also write this file directly following the schema found [here](https://github.com/dafnifacility/metadata-schema/blob/main/metadata_schema_for_upload.json). If you are following this approach you may find it useful to view the existing json metadata for datasets that have already been uploaded. You may view this using `dafni get dataset <version_id> --json`.

#### Uploading the dataset files
You may now upload the metadata with any number of dataset files e.g.

```bash
dafni upload dataset dataset_metadata.json file1.csv file2.zip
```

You will be prompted to confirm your upload although you may also use `-y` to skip this if you prefer.

Wildcards are also accepted here, so if you have many `.csv` files and wish to add all of them you may use

```bash
dafni upload dataset dataset_metadata.json *.csv
```

Or you could upload the contents of an entire directory named `data` with

```bash
dafni upload dataset dataset_metadata.json ./data/*
```

Any folders that are found will also themselves be uploaded, but will keep their folder structure in the uploaded file names. For example if you have a folder that looks like
```
data
    folder
        file1.csv
    file2.csv
```
Then uploading with
```bash
dafni upload dataset dataset_metadata.json ./data/*
```
will upload with the names
```
folder/file1.csv
file2.csv
```

### Updating an existing dataset to create a new version

If you wish to create a new dataset version you may use `dafni upload dataset-version`. To use this you need any version id of the dataset you wish to update. Then the simplest way you can upload the new files is with

```bash
dafni upload dataset-version <existing_version_id> file1.csv file2.zip -m "New version message"
```

This command will obtain the existing metadata, change the version message and then reupload it with the new dataset files you specify.

The same options that are found for the `dafni create dataset-metadata` command are also available here.

For more advanced use cases you may also save the existing metadata file with any modifications using the `--save <file-path>` option and then reupload or use your own metadata file by using `--metadata <file-path>` to specify the metadata file to use.

### Updating an existing dataset version's metadata

To make a modification the metadata of an existing dataset version use the `dafni upload dataset-metadata` command. This has the same options as the `dafni upload dataset-version` command, and functions in the same way so that to make a small modification to the description for example you may use

```bash
dafni upload dataset-metadata <existing_version_id> --description "New dataset description"
```

### Uploading a new model

Uploading a model requires both the model definition `.yaml` file and the image file itself. Documentation on writing the definition file can be found [here](https://docs.secure.dafni.rl.ac.uk/docs/how-to/how-to-write-a-model-definition-file) and for generating the image [here](https://docs.secure.dafni.rl.ac.uk/docs/how-to/how-to-upload-a-model).

Once you have these you can upload them using

```bash
dafni upload model definition.yaml image.tar.gz -m "Version message"
```

### Uploading a new version of an existing model

To upload a new version of an existing model you first need its `Parent ID` which you may find either on the front end when you inspect the existing model or via the `dafni get model <version-id>` command. Then you may use

```bash
dafni upload model definition.yaml image.tar.gz --parent-id <parent-id> -m "New version message"
```
to upload the new version.

### Uploading a workflow or a new version of an existing workflow

Uploading a workflow is almost identical to uploading a model except you only need the workflow definition `.json` file. It is unfortunately not as simple to create as workflows can become quite complicated so we would recommend using the front end in these cases. If you want to create or modify an existing workflow you can always use others as a guide for the creation as you can get an existing definition using `dafni get workflow <version-id> --json`.

Once you have a definition file the command to upload it is

```bash
dafni upload workflow definition.json -m "Version message"
```

To upload a new version of an existing workflow use

```bash
dafni upload model definition.json --parent-id <parent-id> -m "New version message"
```

where the `Parent ID` can again be found when by inspecting an existing workflow.

### Uploading a workflow parameter set

As in [Uploading a workflow or a new version of an existing workflow](#uploading-a-workflow-or-a-new-version-of-an-existing-workflow) the main difficulty in uploading a workflow parameter set is in producing a parameter set definition file to upload. Again you may inspect existing parameter sets using

```bash
dafni get workflow-parameter-set <workflow-version-id> <parameter-set-id> --json
```

Once you have the definition, you may upload it with

```bash
dafni upload workflow-parameter-set definition.json
```

### Downloading datasets

You may download all the files of a dataset using its version id via the command

```bash
dafni download dataset <version-id>
```

You may also select specific files by using their names e.g.

```bash
dafni download dataset <version-id> file1.csv file2.zip
```

As with the dataset upload you may also use wildcards. For example

```bash
dafni download dataset <version-id> "*.csv"
```

will download all `.csv` files in the dataset.

> **_NOTE:_** You should use quotation marks, `""`, here to avoid any confusion with local files that may be in your current directory.

### Deleting entities

You may delete entities on the platform using one of the `dafni delete` commands. All of these will take an existing version id for a dataset, model or workflow and will display a brief summary with a confirmation prompt prior to actual deletion. e.g.


Delete a model version with
```bash
dafni delete model-version <version-id>
```

or a workflow version with
```bash
dafni delete workflow-version <version-id>
```

There are two options for datasets. You may either delete an entire dataset with all its versions with

```bash
dafni delete dataset <version-id>
```

> **_NOTE:_** This still takes a version id. It doesn't matter which is given in this case as it will delete the associated parent dataset

or just a version with

```bash
dafni delete dataset-version <version-id>
```

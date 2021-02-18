# The DAFNI CLI

## Use Cases
The DAFNI CLI has been identified as requirement for in the following cases:
### 1. CERAF project
#### Applicable bid text:

The applicable text of this bid is as follows (note: this is from a pre-submission draft, so may differ from the final version):

> "This environment will be deployed using a combination of JASMIN unmanaged cloud available to the project with a pipeline allowing containerisation and deployment onto the DAFNI platform."

> "We will collect community standards already in use from existing partners in the FS area, as well as through our expertise in data management services suggest those not yet in use but that could dramatically simplify service & pipeline creation.  DAFNI will incorporate appropriate data standards within its information integration framework, to support a catalogue of FAIR compliant standards"

> "To achieve this we will; ...
> * define standard operating procedures to allow import and utilisation in secure manner of externally provided data in a non-persistent manner;
> * build, execute, share, reuse and export flagship pipelines within a secure environment, accessible to the non-developer community; and
> * ensure data storage system utilising shared capabilities with other platforms of relevance (e.g. JASMIN, DAFNI).
> * Deploy a custom user management interface to allow the concurrent utilisation by potentially competing user communities whilst ensuring sandboxing of applications, service and all user activities"

The agreement made between DAFNI and Oxford OERC in planning for this bid, was that the CLI would support CERAF users working on JASMIN  - as a model development environment - to seamlessly port their work through to DAFNI for execution.


##### Key priorities in this case

As a project which has not yet kicked off, there is still some uncertainty about the specifics of the CERAF work. Bearing in mind that uncertainty, the priorities in this particular use case can be reasonably assumed to be as follows:
1. Download data (for model development and results analysis)
2. Upload models to DAFNI
3. Share DAFNI models and data with collaborators through DAFNI groups
4. Update workflows with these new models
5. Execute the workflows
As well as all associated asset discovery and removal capabilities

_For more information contact Bethan Perkins / James Hannah / Brian Matthews_

### 2. DAFNI modellers forum

In November 2019 a forum was held with DAFNI pilot modellers in order to ascertain their priority features for the DAFNI platform. A DAFNI CLI was seen as a very valuable asset by the group. The following summarise the [notes taken during the forum](https://wiki.dafni.rl.ac.uk/display/DAFNIDEV/Observations+and+Conclusions).

* THE CLI was consistenly prioritised above other features by all modellers
* Modellers want to use a CLI for smoothly transitioning models from their local development environments to runtime/compute environments.
* A CLI is seen as more "trustworthy" than a github
* Modellers would use a CLI for the following:
    + Uploading models and data
    + Downloading data
    + Running models and/or workflows

##### Key priorities in this case
1. Uploading models and data
2. Downloading data
3. Running models and/or workflows

_For more information contact Bethan Perkins / Rose Dickinson_

### 3. Feature requests on github

Searches of the requests provided on the [DAFNI User Feedback GitHub Issue Tracker](https://github.com/dafnifacility/user-feedback) provide the following specific user request relating to CLI / remote access:

[Issue 45](https://github.com/dafnifacility/user-feedback/issues/45)
> It would be great to have access to some DAFNI functionalities through an API (e.g. http or webdav), in particular for model upload (for local connexion speed or local disk space reasons, I often manage my models and images on a remote server - it would be useful to be able to directly upload from there with the command line).

##### Key priority in this case
1. Model upload

_For more information, see link_

### 4. Food Network users

A food network group are currently onboarding to DAFNI would like to use the platform as an area to host large datasets to support their work. The aspect which relates to a CLI is that of being able to autmoatically download latest results into a local web-app. 


##### Key priority in this case
1. Dataset download

_For more information, contact Tom Gowland / Marion Samler_

## Feature Priority
From the use cases described above, the following list of features is defined. These are placed in priority order, taking in to account the use cases above as well as the work required to develop each feature. 

Admin #1:
* Log in (Log out should be automatic)
* See own user details 
    + User Name
    + User UUID

Models:
* List all models available to user
* Filter list of models available to user
* View specific model metadata (model definition file..?)
* Upload a new model
* Delete a model

Datasets:
* List all datasets available to user
* Filter list of datasets available to user.
* View specific dataset metadata
* Download dataset data and metadata
* Upload a new dataset
* Update dataset metadata
* Update dataset data files to create new version
* Delete a dataset
* Delete a dataset version

Workflows:
* List all workflows available to user
* Filter list of available workflows
* View specific workflow metadata
* Execute a workflow (without changing any properties of the workflow)
* Create workflow (using workflow definition file)
* Edit workflow env params and create new workflow
* Edit workflow data slots and create new workflow

Groups: 
* List available groups
* Create new group
* View group information (all users and all shared assets with their permissions)
* Add user(s) to a group (using id numbers?)
* Remove user(s) from a group
* Add a dataset to a group
* Remove a dataset from a group
* Add a model to a group
* Remove a model from a group
* Edit dataset permissions
* Edit model permissions
* Non-admin to leave a group
* Edit group title
* Edit group description

Public:
* Request global dataset permissions change -> Making them public / private (user P.O.V)

Admin #2:
* Search for another users' details

Future:
* Visualsiation features (more thought needed here on what to pass back to the user - templates perhaps?)
* Download models (not currently implemented)
* Request a DAFNI account (not currently implemented)
* Admin functions
    + (e.g adding users? or confirming accounts?)
    + managing assets - removing/changing asset visibility?
    + service/outage message management?
    + (far far future) billing/accounting
​
## Functions
* Will have to login to DAFNI with a `POST` to the login app with a username and password
* When Keycloak comes in, there will be an OAuth flow to be able to do this in a better way
​
## Syntax
 * `dafni get datasets` vs `dafni datasets get`
 * `dafni post model -metadata def.yaml -image myimage`
 * `dafni post dataset -metadata def.yaml -files`
​
## Other requirements
 - Must be also able to be used as a client library (eg. `import dafni`)
 - Must be installable as an exe (through `pyinstaller` or `py2exe`)
​
## Notes
* Probably think we should use [Click](https://github.com/pallets/click)
* Need to keep in mind that the APIs are currently not fixed (we're making best efforts to not change them too much but they are liable to change) The CLI does need to be fixed so it probably needs to send a UserAgent API header to let us know which version of the API they're using so that in future we can know not to break stuff that's going to affect a lot of people.
​
## Tasks
 - Bethan to firm up use cases and prioritise these
 - James to think about syntax of the CLI and make a decision for us to fight about

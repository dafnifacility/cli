# The DAFNI CLI

## Use Cases
The DAFNI CLI has been identified as requirement for the following users/use cases:
### 1. CERAF project
#### Applicable bid text
_(NOTE: this is not the final submitted version. Update needed - Bethan)_
> "This environment will be deployed using a combination of JASMIN unmanaged cloud available to the project with a pipeline allowing containerisation and deployment onto the DAFNI platform."

> "We will collect community standards already in use from existing partners in the FS area, as well as through our expertise in data management services suggest those not yet in use but that could dramatically simplify service & pipeline creation.  DAFNI will incorporate appropriate data standards within its information integration framework, to support a catalogue of FAIR compliant standards"

> "To achieve this we will; ...
3) define standard operating procedures to allow import and utilisation in secure manner of externally provided data in a non-persistent manner;
4) build, execute, share, reuse and export flagship pipelines within a secure environment, accessible to the non-developer community; and
4) ensure data storage system utilising shared capabilities with other platforms of relevance (e.g. JASMIN, DAFNI).
5) Deploy a custom user management interface to allow the concurrent utilisation by potentially competing user communities whilst ensuring sandboxing of applications, service and all user activities"

The verbal agreement made between DAFNI and David Wallom was that this work would support users in using JASMIN as a model development environemnt, and then seamlessly link this through to DAFNI using CLI commands.

#### Priorities

There is still uncertainty about the form of the CERAF work and how this interfaces with the working practices of David Walloms team. Bearing in mind that uncertainty, the priorities in this use case are reasonably assumed to be the ability to:
1. Download data (for model development and results analysis)
2. Upload models to DAFNI
3. Share DAFNI models and data with collaborators through DAFNI groups
4. Update workflows with these new models
5. Execute the workflows
As well as all associated discovery and rollback capabilities



## Priority Features
Procedures for current and future DAFNI users, in priority order:
Admin #1:
* Log in (Log out should be automatic)
* See own user details

Models:
* List available models
* View specific model metadata (model definition file..?)
* Upload a new model

Datasets:
* List available datasets
* View specific dataset metadata
* Download dataset data and metadata
* Upload a new dataset
* Update dataset metadata
* Update dataset data files to create new version

Workflows #1:
* List available workflows
* View specific workflow metadata
* Execute a workflow (without changing any properties of the workflow)

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

Workflows #2:
* Edit workflow env params and create new workflow
* Edit workflow data slots and create new workflow
* Create a new workflow 
* Save new workflow
* Create a new workflow model step in new/existing workflow
* Create a new workflow iterator step in new/existing workflow
* Create a new workflow visualisation step in new/existing workflow 
* Create a new workflow publish step in existing new/workflow

Future:
* Download models (not currently implemented)
* Request a DAFNI account (not currently implemented)
* Admin functions
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

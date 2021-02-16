# The DAFNI CLI
​
## Use Cases
* Upload new datasets and dataset versions
* Download datasets
* Upload new models
* Execute a workflow 
* Create a workflow
* Create groups
* Make changes to groups
* Admin group functions (adding / removing users)
* Share with groups
* View group users and permissions
* View group assets and permissions
* Login / Logout
* Dataset discovery
* See own user details
* Model discovery
* Workflow discovery
* Seeing groups you're part of
* Leaving a group you're part of
* Download models (not currently implemented)
* Request a DAFNI account (not currently implemented)
* Admin functions
* Request global dataset permissions change -> Making them public / private (user P.O.V)
​
## Functions
* Will have to login to DAFNI with a `POST` to the login app with a username and password
* When Keycloak comes in, there will be an OAuth flow to be able to do this in a better way
*  
​
## Syntax
 * `dafni get datasets` vs `dafni datasets get`
 * `dafni post model -metadata def.yaml -image myimage`
 * `dafni post dataset -metadata def.yaml -files`
​
## Other requirements
​
 - Must be also able to be used as a client library (eg. `import dafni`)
 - Must be installable as an exe (through `pyinstaller` or `py2exe`)
​
## Notes
* Probably think we should use [Click](https://github.com/pallets/click)
* Need to keep in mind that the APIs are currently not fixed (we're making best efforts to not change them too much but they are liable to change) The CLI does need to be fixed so it probably needs to send a UserAgent API header to let us know which version of the API they're using so that in future we can know not to break stuff that's going to affect a lot of people.
​
## Tasks
​
 - Bethan to firm up use cases and prioritise these
 - James to think about syntax of the CLI and make a decision for us to fight about
import click
import datetime as dt

from dateutil import parser

from dafni_cli.workflow.workflow_metadata import WorkflowMetadata
from dafni_cli.consts import CONSOLE_WIDTH, TAB_SPACE
from dafni_cli.api.workflows_api import (
    get_single_workflow_dict,
#    get_workflow_metadata_dict
)
from dafni_cli.utils import (
    prose_print,
    print_json
)
from dafni_cli.auth import Auth


class Workflow:
    """
    Contains information about a DAFNI workflow.
    The information (as attributes) for a workflow can be populated from a dictionary, or a DAFNI workflow UUID.

    Methods:
        get_details_from_dict(dict): populates attributes from the workflow dictionary from the DAFNI API
        get_details_from_id(jwt (str), id (str)): populates attributes from the workflow version ID by calling DAFNI API.
        get_metadata(jwt (str)): After details have been obtained, populate metadata attributes.
        filter_by_date(key (str), date (str)): calculates whether the workflow was created/published before a date.
        output_details(): Prints key information of workflow to console.
        output_metadata(): Prints key information of workflow metadata to console.

    Attributes:
        api_version: The version of the API that created the data
        auth: credentials used to retrieve the data
        creation_date: Date and time the workflow was created
        description: More detailed information on the model
        display_name: Name of the workflow used in the web app
        id: ID used to identify the specific workflow version
        instances: A list of the workflow version run instances
        kind: The type of asset (will be 'W', workflow)
        metadata: a sub-group containing the workflow metadata:
            description: More detailed information on the model
            display_name: Name of the workflow used in the web app
            name: DAFNI workflow name
            publisher: Organisation publishing the model
            summary: One-line summary of what the model does
            source_code: Generally, a link (e.g. Github) link to the project source
            status: ?
        name: DAFNI workflow name
        owner: UUID of the workflow owner
        parameter_sets:
        parent: UUID of the workflow's parent
        publication_date: Date and time the model was published
        publisher: Organisation publishing the model
        spec: JSON description of the workflow steps
        summary: One-line summary of what the model does
        version_history: A list of all versions of the workflow
        version_message: Message attached when the model was updated to this model version
        version_tags: Any tags created by the publisher for this version

        dictionary: Full description of the model as retrieved from the API
        metadata_obj: ModelMetadata object containing metadata for the model
    """

    def __init__(self, identifier=None):
        # Attributes that are also workflow dictionary keys
        self.api_version = None
        self.auth = Auth()
        self.creation_date = None
        self.display_name = None
        self.description = None # present??
        self.id = identifier
        self.instances = None
        self.kind = None
        self.metadata = None
        self.name = None
        self.owner = None
        self.parameter_sets = None
        self.parent = None
        self.publication_date = None
        self.publisher = None
        self.spec = None
        self.summary = None
        self.version_history = None
        self.version_message = None
        self.version_tags = None

        # Set of workflow dictionary keys, for use in validation functions
        workflow_attributes = vars(self).keys()
        self.workflow_attributes = set(workflow_attributes)

        # Attributes that are not also workflow dictionary keys
        self.dictionary = None
        self.metadata_obj = None

        return


    def set_attributes_from_dict(self, workflow_dict: dict):
        """
        Attempts to store workflow details from a dictionary returned from the DAFNI API.
        Not all of the details need be present in workflow_dict.
 
        Args:
            workflow_dict (dict): Dictionary returned from DAFNI API at /workflows endpoints

        Returns:
            a set of attributes of Workflow that could not be set as they were not present in workflow_dict
        """
        workflow_attributes = self.workflow_attributes
        #special_attributes = {"auth", "creation_date", "publication_date"}
        #workflow_attributes = self.workflow_attributes.difference_update(special_attributes)

        missing_workflow_attributes = set()
        for key in workflow_attributes:
            try:
                setattr(self, key, workflow_dict[key])
            except:
                missing_workflow_attributes.add(key)
            pass

        # Special treatment. If these keys are not in the missing attributes set, then
        # they have already been added above and we just need to ignore the exception
        try:
            self.auth = Auth(workflow_dict["auth"])
        except:
            pass

        try:
            self.creation_date = parser.isoparse(workflow_dict["creation_date"])
        except:
            pass

        try:
            self.publication_date = parser.isoparse(workflow_dict["publication_date"])
        except:
            pass

        #  If workflow_dict is not a dictionary then an exception will have already been raised
        self.dictionary = workflow_dict

        return missing_workflow_attributes


    def get_attributes_from_id(self, jwt_string: str, version_id_string: str):
        """
        Retrieve workflow attributes from the DAFNI API using the /workflows/<version-id> endpoint.
 
        Args:
            jwt_string (str): JWT for login purposes
            version_id_string (str): Version ID of the model
        """
        workflow_dict = get_single_workflow_dict(jwt_string, version_id_string)
        self.set_attributes_from_dict(workflow_dict)
        # TODO: Check: Version message key appears on single workflow API response, but not list of all workflows response
        self.version_message = workflow_dict["version_message"]
        return


    def get_metadata(self, jwt_string: str):
        """
        Retrieve metadata for the workflow using the workflow details.
        Args:
            jwt_string (str): JWT for login purposes
        """
#        metadata_dict = get_workflow_metadata_dict(jwt_string, self.id)
        self.metadata_obj = WorkflowMetadata(self.dictionary)
        return


    def filter_by_date(self, key: str, date: str) -> bool:
        """Filters workflows based on the date given as an option.
        Args:
            key (str): Key for WORKFLOW_DICT in which date is contained
            date (str): Date for which workflows are to be filtered on: format DD/MM/YYYY

        Returns:
            bool: Whether to display the model based on the filter
        """
        day, month, year = date.split("/")
        date = dt.date(int(year), int(month), int(day))
        if key.lower() == "creation":
            return self.creation_date.date() >= date
        elif key.lower() == "publication":
            return self.publication_date.date() >= date
        else:
            raise KeyError("Key should be CREATION or PUBLICATION")


    def output_details(self, long: bool = False):
        """
        Prints relevant workflow attributes to command line
        """
        click.echo(
            "Name: "
            + self.display_name
            + TAB_SPACE
            + "ID: "
            + self.id
            + TAB_SPACE
            + "Date: "
            + self.creation_date.date().strftime("%B %d %Y")
        )
        click.echo("Summary: " + self.summary)
        if long:
            click.echo("Description: ")
            prose_print(self.description, CONSOLE_WIDTH)
        click.echo("")
        return

#post /workflows/<parent_id>/upload
#https://dafni-nims-api.secure.dafni.rl.ac.uk/swagger/

    def output_metadata(self, json_flag: bool = False):
        """
        Prints the metadata for the workflow to command line.

        Args:
            json_flag (bool): Whether to print raw json or pretty print information. Defaults to False.
        """
        if not json_flag:
            click.echo("Name: " + self.metadata["display_name"])
            click.echo("Date: " + self.creation_date.strftime("%B %d %Y"))
            click.echo("Summary: ")
            click.echo(self.metadata["summary"])
            prose_print(self.metadata["description"], CONSOLE_WIDTH)
            click.echo("")
            if self.metadata_obj.inputs:
                click.echo("Input Parameters: ")
                click.echo(self.metadata_obj.format_parameters())
                click.echo("Input Data Slots: ")
                click.echo(self.metadata_obj.format_dataslots())
            if self.metadata_obj.outputs:
                click.echo("Outputs: ")
                click.echo(self.metadata_obj.format_outputs())
        else:
            print_json(self.dictionary)
        return


    def output_version_details(self) -> str:
        """
        Prints version ID, display name, publication time and version message on one line
        """
        return("ID: " +
               self.id +
               TAB_SPACE +
               "Name: " +
               self.metadata["display_name"] +
               TAB_SPACE +
               "Publication date: " +
               self.publication_date.date().strftime("%B %d %Y") +
               TAB_SPACE +
               "Version message: " +
               self.version_message
               )

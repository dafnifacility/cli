import click
import datetime as dt

from dateutil import parser

from dafni_cli.workflow.workflow_metadata import WorkflowMetadata
from dafni_cli.consts import CONSOLE_WIDTH, TAB_SPACE
from dafni_cli.api.workflows_api import (
    get_single_workflow_dict,
    get_workflow_metadata_dict
)
from dafni_cli.utils import (
    prose_print,
    print_json
)
from dafni_cli.auth import Auth


class Workflow:
    """
    Contains information about a DAFNI workflow DAFNI.
    The information (as attributes) for a workflow can be populated from a dictionary, or an id.

    Methods:
        get_details_from_dict(dict): populates attributes from the workflow dictionary from the DAFNI API
        get_details_from_id(jwt (str), id (str)): populates attributes from the workflow version ID by calling DAFNI API.
        get_metadata(jwt (str)): After details have been obtained, populate metadata attributes by calling API.
        filter_by_date(key (str), date (str)): calculates whether the workflow was created/published before a date.
        output_details(): Prints key information of workflow to console.
        output_metadata(): Prints key information of workflow metadata to console.

    Attributes:
        container: Location of the docker image the model should be run in
        creation_time: Time the model was created
        description: More-detailed information of the model
        dictionary: Dictionary of full model information
        display_name: Name of the model shown in the web app
        metadata: ModelMetadata object containing metadata for the model
        publication_time: Time the model was published
        summary: One-line summary of what the model does
        version_id: ID used to identify the specific version and model
        version_message: Message attached when the model was updated to this model version
        version_tags: Any tags created by the publisher for this version
    """

    def __init__(self, identifier=None):
        self.auth = Auth()
        self.api_version = None
        self.creation_date = None
        self.description = None
        self.dictionary = None
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
        self.version_id = identifier
        self.version_message = None
        self.version_tags = None
        return

    def set_details_from_dict(self, workflow_dict: dict):
        """
        Take workflow details straight from the dictionary returned from the DAFNI API.
 
        Args:
            model_dict (dict): Dictionary returned from DAFNI API at /workflows endpoints
        """
        print(workflow_dict)
        self.auth = Auth(workflow_dict["auth"])
        self.api_version = workflow_dict["api_version"]
        self.creation_date = parser.isoparse(workflow_dict["creation_date"])
        self.description = workflow_dict["description"]
        self.dictionary = workflow_dict
        self.display_name = workflow_dict["display_name"]
        self.kind = workflow_dict["kind"]
        self.name = workflow_dict["name"]
        self.owner = workflow_dict["owner"]
        self.parent = workflow_dict["parent"]
        self.publication_date = parser.isoparse(workflow_dict["publication_date"])
        self.publisher = workflow_dict["publisher"]
        self.spec = workflow_dict["spec"]
        self.summary = workflow_dict["summary"]
        self.version_history = workflow_dict["version_history"]
        self.version_id = workflow_dict["id"]
        self.version_message = workflow_dict["version_message"]
        self.version_tags = workflow_dict["version_tags"]
        return

    def get_details_from_id(self, jwt_string: str, version_id_string: str):
        """
        Retrieve workflow details from the DAFNI API using the
        /workflows/<version-id> endpoint.
 
        Args:
            jwt_string (str): JWT for login purposes
            version_id_string (str): Version ID of the model
        """
        workflow_dict = get_single_workflow_dict(jwt_string, version_id_string)
        self.set_details_from_dict(workflow_dict)
        # TODO: Check: Version message key appears on single workflow API response, but not list of all workflows response
        self.version_message = workflow_dict["version_message"]
        return

    def get_metadata(self, jwt_string: str):
        """
        Retrieve metadata for the workflow using the workflow details and
        the /models/<version-id>/description/ endpoint.
        Args:
            jwt_string (str): JWT for login purposes
        """
        metadata_dict = get_workflow_metadata_dict(jwt_string, self.version_id)
        self.metadata = WorkflowMetadata(metadata_dict)
        return

    def filter_by_date(self, key: str, date: str) -> bool:
        """Filters workflows based on the date given as an option.
        Args:
            key (str): Key for MODEL_DICT in which date is contained
            date (str): Date for which models are to be filtered on: format DD/MM/YYYY

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
        """Prints relevant model attributes to command line"""
        click.echo(
            "Name: "
            + self.display_name
            + TAB_SPACE
            + "ID: "
            + self.version_id
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

    def output_metadata(self, json_flag: bool = False):
        """Prints the metadata for the model to command line.

        Args:
            json_flag (bool): Whether to print raw json or pretty print information. Defaults to False.
        """
        if not json_flag:
            click.echo("Name: " + self.display_name)
            click.echo("Date: " + self.creation_date.strftime("%B %d %Y"))
            click.echo("Summary: ")
            click.echo(self.summary)
            click.echo("Description: ")
            prose_print(self.description, CONSOLE_WIDTH)
            click.echo("")
            if self.metadata.inputs:
                click.echo("Input Parameters: ")
                click.echo(self.metadata.format_parameters())
                click.echo("Input Data Slots: ")
                click.echo(self.metadata.format_dataslots())
            if self.metadata.outputs:
                click.echo("Outputs: ")
                click.echo(self.metadata.format_outputs())
        else:
            print_json(self.metadata.dictionary)
        return

    def output_version_details(self) -> str:
        """Prints version ID, display name, publication time and version message on one line"""
        return("ID: " +
               self.version_id +
               TAB_SPACE +
               "Name: " +
               self.display_name +
               TAB_SPACE +
               "Publication date: " +
               self.publication_date.date().strftime("%B %d %Y") +
               TAB_SPACE +
               "Version message: " +
               self.version_message
               )

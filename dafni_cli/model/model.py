import click
import datetime as dt

from dateutil import parser

from dafni_cli.model.model_metadata import ModelMetadata
from dafni_cli.consts import CONSOLE_WIDTH, TAB_SPACE
from dafni_cli.api.models_api import (
    get_single_model_dict,
    get_model_metadata_dict,
)
from dafni_cli.utils import prose_print


class Model:
    """
    Contains information about a model uploaded to DAFNI.
    The information (as attributes) for a model can be populated from a dictionary, or an id.

    Methods:
        get_details_from_dict(dict): populates attributes from the model dictionary from the DAFNI API
        get_details_from_id(jwt (str), id (str)): populates attributes from the model version ID by calling DAFNI API.
        get_metadata(jwt (str)): After details have been obtained, populate metadata attributes by calling API.
        filter_by_date(key (str), date (str)): calculates whether the model was created/published before a date.
        output_details(): Prints key information of model to console.
        output_metadata(): Prints key information of model metadata to console.

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
        self.container = None
        self.creation_time = None
        self.description = None
        self.dictionary = None
        self.display_name = None
        self.metadata = None
        self.publication_time = None
        self.summary = None
        self.version_id = identifier
        self.version_message = None
        self.version_tags = None
        pass

    def set_details_from_dict(self, model_dict: dict):
        """Take model details straight from the dictionary returned from the DAFNI API.
        Args:
            model_dict (dict): Dictionary returned from DAFNI API at /models endpoints
        """
        self.creation_time = parser.isoparse(model_dict["creation_date"])
        self.container = model_dict["container"]
        self.description = model_dict["description"]
        self.dictionary = model_dict
        self.display_name = model_dict["name"]
        self.publication_time = parser.isoparse(model_dict["publication_date"])
        self.summary = model_dict["summary"]
        self.version_id = model_dict["id"]
        self.version_tags = model_dict["version_tags"]

    def get_details_from_id(self, jwt_string: str, version_id_string: str):
        """Retrieve model details from the DAFNI API by calling /models/<version-id> endpoint.
        Args:
            jwt_string (str): JWT for login purposes
            version_id_string (str): Version ID of the model
        """
        model_dict = get_single_model_dict(jwt_string, version_id_string)
        self.set_details_from_dict(model_dict)

    def get_metadata(self, jwt_string: str):
        """Retrieve metadata for the model using the model details and the /models/<version-id>/description/ endpoint.
        Args:
            jwt_string (str): JWT for login purposes
        """
        metadata_dict = get_model_metadata_dict(jwt_string, self.version_id)
        self.metadata = ModelMetadata(metadata_dict)

    def filter_by_date(self, key: str, date: str) -> bool:
        """Filters models based on the date given as an option.
        Args:
            key (str): Key for MODEL_DICT in which date is contained
            date (str): Date for which models are to be filtered on: format DD/MM/YYYY

        Returns:
            bool: Whether to display the model based on the filter
        """
        day, month, year = date.split("/")
        date = dt.date(int(year), int(month), int(day))
        if key.lower() == "creation":
            return self.creation_time.date() >= date
        elif key.lower() == "publication":
            return self.publication_time.date() >= date
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
            + self.creation_time.date().strftime("%B %d %Y")
        )
        click.echo("Summary: " + self.summary)
        if long:
            click.echo("Description: ")
            prose_print(self.description, CONSOLE_WIDTH)
        click.echo("")

    def output_metadata(self):
        """Prints the metadata for the model to command line."""
        click.echo("Name: " + self.display_name)
        click.echo("Date: " + self.creation_time.strftime("%B %d %Y"))
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

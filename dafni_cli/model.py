import click
import datetime as dt
from dateutil import parser

from dafni_cli.API_requests import (
    get_models_dicts,
    get_single_model_dict,
    get_model_metadata_dicts,
)
from dafni_cli.login import login
from dafni_cli.consts import DATE_TIME_FORMAT


class Model:
    """
    Contains information about a model uploaded to DAFNI.
    The information (as attributes) for a model can be populated from a dictionary, or an id.

    Methods:
        get_details_from_dict(dict): populates attributes from the model dictionary from the DAFNI API
        get_details_from_id(jwt (str), id (str)): populates attributes from the model version ID by calling DAFNI API.
        get_metadata(jwt (str)): After details have been obtained, populate metadata attributes by calling API.
        filter_by_date(key (str), date (str)): calculates whether the model was created/published before a date.
        output_model_details(): Prints key information of model to console.
        output_model_metadata(): Prints key information of model metadata to console.

    Attributes:
        container: Location of the docker image the model should be run in
        creation_time: Time the model was created
        description: More-detailed information of the model
        display_name: Name of the model shown in the web app
        inputs: Dictionary describing the inputs for a model
        name: Name used to identify the model
        outputs: Dictionary describing the outputs for a model
        publication_time: Time the model was published
        summary: One-line summary of what the model does
        version_id: ID used to identify the specific version and model
        version_tags: Any tags created by the publisher for this version

    """

    def __init__(self, identifier=None):
        self.container = None
        self.creation_time = None
        self.description = None
        self.display_name = None
        self.inputs = None
        self.name = None
        self.outputs = None
        self.publication_time = None
        self.summary = None
        self.version_id = identifier
        self.version_tags = None
        pass

    def set_details_from_dict(self, model_dict: dict):
        """Take model details straight from the dictionary returned from the DAFNI API.
        Args:
            model_dict (dict): Dictionary returned from DAFNI API at /models endpoints
        """
        self.display_name = model_dict["name"]
        self.summary = model_dict["summary"]
        self.description = model_dict["description"]
        self.creation_time = parser.isoparse(model_dict["creation_date"])
        self.publication_time = parser.isoparse(model_dict["publication_date"])
        self.version_id = model_dict["id"]
        self.version_tags = model_dict["version_tags"]
        self.container = model_dict["container"]

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
        metadata_dict = get_model_metadata_dicts(jwt_string, self.version_id)
        self.name = metadata_dict["metadata"]["name"]
        self.inputs = metadata_dict["spec"]["inputs"]
        self.outputs = metadata_dict["spec"]["outputs"]

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

    def output_model_details(self):
        """Prints relevant model attributes to command line"""
        click.echo(
            "Name: "
            + self.display_name
            + "     ID: "
            + self.version_id
            + "     Date: "
            + self.creation_time.date().strftime(DATE_TIME_FORMAT)
        )
        click.echo("Summary: " + self.summary)

    def output_model_metadata(self):
        """Displays the metadata for the model.

        Args:
            ctx (context): contains JWT for authentication
            model_version_id (str): Version ID for the model to display the metadata of
        """
        # TODO Implement this
        pass


def create_model_list(model_dict_list: list) -> list:
    """
    Produces a list of Model objects from a list of model dictionaries obtained from the /models/ DAFNI API endpoint.
    Args:
        model_dict_list (list[dict]): List of dictionaries for several models.

    Returns:
        model_list (list[Model]): List of Model objects with the attributes populated from the dictionaries.
    """
    model_list = []
    for model_dict in model_dict_list:
        single_model = Model()
        single_model.set_details_from_dict(model_dict)
        model_list.append(single_model)
    return model_list

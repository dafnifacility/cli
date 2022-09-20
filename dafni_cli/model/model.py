from xml.sax.xmlreader import InputSource
import click
import datetime as dt

from dateutil import parser

from dafni_cli.model.model_metadata import ModelMetadata
from dafni_cli.consts import CONSOLE_WIDTH, TAB_SPACE
from dafni_cli.api.models_api import (
    get_single_model_dict,
    get_model_metadata_dict,
)
from dafni_cli.utils import (
    prose_print,
    print_json
)
from dafni_cli.auth import Auth


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
        # Attributes that are also workflow dictionary keys
        self.api_version = None
        self.auth = Auth()
        self.container = None
        self.container_version = None
        self.creation_date = None
        self.ingest_completed_date = None
        self.id = identifier
        self.kind = None
        self.metadata = None
        self.owner = None
        self.parent = None
        self.publication_date = None
        self.spec = None
        self.type = None
        self.version_history = None
        self.version_message = None
        self.version_tags = None

        # Set of workflow dictionary keys, for use in validation functions
        # TODO: Is .vars() reliable?
        model_attributes = vars(self).keys()
        self.model_attributes = set(model_attributes)

        # Attributes that are not also workflow dictionary keys
        self.dictionary = None
        pass


    def set_details_from_dict(self, model_dict: dict):
        """
        Attempts to store model details from a dictionary returned from the DAFNI API.
        Not all of the details need be present in model_dict.
        
        Args:
            model_dict (dict): Dictionary returned from DAFNI API at /models endpoints
        
        Returns:
            a set of attributes of Workflow that could not be set as they were not present in model_dict
        """
        model_attributes = self.model_attributes
        #special_attributes = {"auth", "creation_date", "publication_date"}
        #model_attributes = self.model_attributes.difference_update(special_attributes)

        missing_model_attributes = set()
        for key in model_attributes:
            try:
                setattr(self, key, model_dict[key])
            except:
                missing_model_attributes.add(key)
            pass

        # Special treatment. If these keys are not in the missing attributes set, then
        # they have already been added above and we just need to ignore the exception
        try:
            self.auth = Auth(model_dict["auth"])
        except:
            pass

        try:
            self.creation_date = parser.isoparse(model_dict["creation_date"])
        except:
            pass

        try:
            self.publication_date = parser.isoparse(model_dict["publication_date"])
        except:
            pass

        # Will raise an exception anyway if model_dict is not a dictionary
        self.dictionary = model_dict

        return missing_model_attributes


    def get_details_from_id(self, jwt_string: str, version_id_string: str):
        """
        Retrieve model details from the DAFNI API by calling /models/<version-id>/ endpoint.

        Args:
            jwt_string (str): JWT for login purposes
            version_id_string (str): Version ID of the model
        """
        model_dict = get_single_model_dict(jwt_string, version_id_string)
        print("======================================")
        print(model_dict)
        print("======================================")
        self.set_details_from_dict(model_dict)
        # Version message key appears on single model API response, but not list of all models response
        self.version_message = model_dict["version_message"]


    def get_metadata(self, jwt_string: str):
        """
        Retrieve metadata for the model using the model details and the /models/<version-id>/description/ endpoint.

        Args:
            jwt_string (str): JWT for login purposes
        """
        print(self.metadata)
#        metadata_dict = get_model_metadata_dict(jwt_string, self.id)
        self.metadata_obj = ModelMetadata(self.dictionary)
        pass


    def filter_by_date(self, key: str, date: str) -> bool:
        """
        Filters models based on the date given as an option.

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
        """
        Prints relevant model attributes to command line
        """
        click.echo(
            "Name: "
            + self.metadata["display_name"]
            + TAB_SPACE
            + "ID: "
            + self.id
            + TAB_SPACE
            + "Date: "
            + self.creation_date.date().strftime("%B %d %Y")
        )
        click.echo("Summary: " + self.metadata["summary"])
        if long:
            click.echo("Description: ")
            prose_print(self.description, CONSOLE_WIDTH)
        click.echo("")


    def output_metadata(self, json_flag: bool = False):
        """
        Prints the metadata for the model to command line.

        Args:
            json_flag (bool): Whether to print raw json or pretty print information. Defaults to False.
        """
        print("++++++++++++++++++++++++++++++++++++++++++")
        print(vars(self))
        print("++++++++++++++++++++++++++++++++++++++++++")
        if not json_flag:
            click.echo("Name: " + self.metadata["display_name"])
            click.echo("Date: " + self.creation_date.strftime("%B %d %Y"))
            click.echo("Summary: ")
            click.echo(self.metadata["summary"])
            click.echo("Description: ")
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


    def output_version_details(self) -> str:
        """
        Prints version ID, display name, publication date and version message on one line
        """
        return("ID: " +
               self.id +
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

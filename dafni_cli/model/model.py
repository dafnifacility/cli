import datetime as dt

import click
from dateutil import parser

from dafni_cli.api.models_api import get_model
from dafni_cli.api.session import DAFNISession  # get_model_metadata_dict,
from dafni_cli.auth import Auth
from dafni_cli.consts import CONSOLE_WIDTH, TAB_SPACE
from dafni_cli.model.model_metadata import ModelMetadata
from dafni_cli.utils import print_json, prose_print


class Model:
    """
    Contains information about a model uploaded to DAFNI.
    The information (as attributes) for a model can be populated from a dictionary, or an id.

    Methods:
        get_attributes_from_dict(dict): populates attributes from the model dictionary from the DAFNI API
        get_attributes_from_id(session (DAFNISession), id (str)): populates attributes from the model version ID by calling DAFNI API.
        get_metadata(session (DAFNISession)): After details have been obtained, populate metadata attributes by calling API.
        filter_by_date(key (str), date (str)): calculates whether the model was created/published before a date.
        output_details(): Prints key information of model to console.
        output_metadata(): Prints key information of model metadata to console.

    Attributes:
        api_version: Version of the DAFNI API used to retrieve model data
        auth: Authentication credentials used to retrieve model data
        container: Location of the docker image the model should be run in
        container_version: Version of the docker image
        creation_date: Date and time the model was created
        ingest_completed_date: date and time the model was ingested into minio
        id: Model version ID
        kind: Type of DAFNI object (should be "M" for model)
        metadata: model metadata ...
            description: More-detailed information of the model
            display_name: Name of the model shown in the web app
            name: The full name of the model
            summary: A short description of the model
            source_code: A link to the models source doce (e.g. Github)
            status:
        owner: The model owner
        parent: The parent model ID
        publication_date: Date and time the model was published
        spec: Full description of the model
        type: Type of dafni object ("model")
        version_history: Full version history of the model with UUIDs for each previous version
        version_message: Message attached when the model was updated to this model version
        version_tags: Any tags created by the publisher for this version

        dictionary: Dictionary of full model information
        metadata_obj: ModelMetadata object containing metadata for the model
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

    def set_metadata_from_dict(self, model_dict: dict):
        """
        Sets the "metadata" property from fields in the main body of the
        dictionary

        Args:
        model_dict (dict): Dictionary returned from DAFNI API at /models endpoints

        Returns:
            a set of Model metadata attributes that could not be set as they were not present in model_dict
        """
        metadata_attributes = {
            "description",
            "display_name",
            "name",
            "publisher",
            "summary",
            "source_code",
            "status",
        }
        missing_metadata_attributes = set()
        self.metadata = {}
        for key in metadata_attributes:
            try:
                self.metadata[key] = model_dict[key]
            except:
                missing_metadata_attributes.add(key)

    def set_attributes_from_dict(self, model_dict: dict):
        """
        Attempts to store model attributes from a dictionary returned from the DAFNI API.
        Not all of the attributes need be present in model_dict. If the "metadata" key is
        not present, attempt to create it

        Args:
            model_dict (dict): Dictionary returned from DAFNI API at /models endpoints

        Returns:
            a set of Model attributes that could not be set as they were not present in model_dict
        """
        model_attributes = self.model_attributes
        # special_attributes = {"auth", "creation_date", "publication_date"}
        # model_attributes = self.model_attributes.difference_update(special_attributes)

        missing_model_attributes = set()
        for key in model_attributes:
            try:
                setattr(self, key, model_dict[key])
            except:
                if key == "metadata":
                    self.set_metadata_from_dict(model_dict)
                else:
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

    def get_attributes_from_id(self, session: DAFNISession, version_id_string: str):
        """
        Retrieve model details from the DAFNI API by calling /models/<version-id>/ endpoint.

        Args:
            session (DAFNISession): User session
            version_id_string (str): Version ID of the model
        """
        model_dict = get_model(session, version_id_string)
        self.set_attributes_from_dict(model_dict)
        # Version message key appears on single model API response, but not list of all models response
        self.version_message = model_dict["version_message"]

    def get_metadata(self, session: str):
        """
        Retrieve metadata for the model using the model details.

        Args:
            session (DAFNISession): User session
        """
        #        metadata_dict = get_model_metadata_dict(session, self.id)
        self.metadata_obj = ModelMetadata(self.dictionary)

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
        return (
            "ID: "
            + self.id
            + TAB_SPACE
            + "Name: "
            + self.metadata["display_name"]
            + TAB_SPACE
            + "Publication date: "
            + self.publication_date.date().strftime("%B %d %Y")
            + TAB_SPACE
            + "Version message: "
            + self.version_message
        )

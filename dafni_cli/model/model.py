from dataclasses import dataclass
from datetime import date, datetime
from typing import ClassVar, List, Optional

import click

from dafni_cli.api.auth import Auth
from dafni_cli.api.parser import ParserBaseObject, ParserParam, parse_datetime
from dafni_cli.consts import (
    CONSOLE_WIDTH,
    TAB_SPACE,
)
from dafni_cli.model.inputs import ModelInputs
from dafni_cli.model.outputs import ModelOutputs
from dafni_cli.utils import prose_print


@dataclass
class ModelMetadata(ParserBaseObject):
    """Dataclass representing a DAFNI model's metadata

    Attributes:
        display_name (str): The display name of the Model
        name (str): Name of the model
        summary (str): A short summary of the Model's function
        status (str): Status of model ingest
            P - Pending
            F - Failed
            L - Live
            S - Superseded
            D - Deprecated

        The following are only present for the /model/<version_id> endpoint
        (but are guaranteed not to be None for it)
        --------
        description (str): A rich description of the Model's function
        publisher (str): The name of the person or organisation who has
                         published the Model
        source_code (str): A URL pointing to the source code for this Model
    """

    display_name: str
    name: str
    summary: str
    status: str

    description: Optional[str] = None
    publisher: Optional[str] = None
    source_code: Optional[str] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("display_name", "display_name", str),
        ParserParam("name", "name", str),
        ParserParam("summary", "summary", str),
        ParserParam("status", "status", str),
        ParserParam("description", "description", str),
        ParserParam("publisher", "publisher", str),
        ParserParam("source_code", "source_code", str),
    ]


@dataclass
class ModelSpec(ParserBaseObject):
    """Dataclass representing the specification of a model (containing
       the image url and inputs)

    Attributes:
        image_url (str): URL of the image of the model
        inputs (ModelInputs): Structure containing the input of the model
    """

    image_url: str
    inputs: Optional[ModelInputs] = None
    outputs: Optional[ModelOutputs] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("image_url", "image", str),
        ParserParam("inputs", "inputs", ModelInputs),
        ParserParam("outputs", "outputs", ModelOutputs),
    ]


@dataclass
class ModelVersion(ParserBaseObject):
    """Dataclass containing information on a historic version of a model

    Attributes:
        version_id (str): ID of the version
        version_message (str): Message labelling the model version
        version_tags (List[str]): Version tags e.g. 'latest'
        publication_date: Date and time this version was published
    """

    version_id: str
    version_message: str
    version_tags: List[str]
    publication_date: datetime

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("version_id", "id", str),
        ParserParam("version_message", "version_message", str),
        ParserParam("version_tags", "version_tags"),
        ParserParam("publication_date", "publication_date", parse_datetime),
    ]


@dataclass
class Model(ParserBaseObject):
    """Dataclass representing a DAFNI model

    Inconsistencies in the metadata storage in the /models and
    /model/<version_id> endpoints are handled here by internally storing the
    metadata as _metadata om the latter case, but defining a property named
    'metadata' that will automatically assign it using the data from the
    former endpoint before returning it. Between these two points the
    additional parameters are all stored with underscores e.g. _display_name.

    Attributes:
        model_id (str): Model version ID
        kind (str): Type of DAFNI object (should be "M" for model)
        owner_id (str): ID of the model owner
        parent (str): Parent model ID
        creation_date (datetime): Date and time the model was created
        publication_date (datetime): Date and time the model was published
        version_message (str): Message attached when the model was updated to
                               this model version
        version_tags (List[str]): Any tags created by the publisher for this
                                  model version
        version_history (List[ModelVersion]): Full version history of the
                                              model
        auth (Auth): Authentication credentials giving the permissions the
                     current user has on the model
        ingest_completed_date (datetime or None): Date and time the model
                                           finished ingesting if applicable
        metadata (ModelMetadata): Metadata of the model


        The following are only present for the /model/<version_id> endpoint
        (but are guaranteed not to be None for it)
        --------
        api_version (Optional[str]): Version of the DAFNI API used to retrieve
                                   the model data
        container (Optional[str]): Name of the docker image the model should
                                   be run in
        container_version (Optional[str]): Version of the docker image
        type (Optional[str]): Type of DAFNI object ("model")
        spec (Optional[ModelSpec]): Model specification - includes the image
                                    url and its inputs
    """

    model_id: str
    kind: str
    owner_id: str
    parent_id: str
    creation_date: datetime
    publication_date: datetime
    version_message: str
    version_tags: List[str]
    version_history: List[ModelVersion]
    auth: Auth
    ingest_completed_date: Optional[datetime] = None

    api_version: Optional[str] = None
    container: Optional[str] = None
    container_version: Optional[str] = None
    type: Optional[str] = None
    spec: Optional[ModelSpec] = None

    # Internal metadata storage - Defined explicitly for the
    # /model/<version_id> endpoint but is None otherwise, the property
    # 'metadata' handles this discrepancy
    _metadata: Optional[ModelMetadata] = None

    # These are found in ModelMetadata but appear here when using the /models
    # endpoint, the property 'metadata' handles this discrepancy
    _display_name: Optional[str] = None
    _name: Optional[str] = None
    _summary: Optional[str] = None
    _status: Optional[str] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("model_id", "id", str),
        ParserParam("kind", "kind", str),
        ParserParam("owner_id", "owner", str),
        ParserParam("parent_id", "parent", str),
        ParserParam("type", "api_version", str),
        ParserParam("creation_date", "creation_date", parse_datetime),
        ParserParam("publication_date", "publication_date", parse_datetime),
        ParserParam("version_message", "version_message", str),
        ParserParam("version_tags", "version_tags"),
        ParserParam("version_history", "version_history", ModelVersion),
        ParserParam("auth", "auth", Auth),
        ParserParam("ingest_completed_date", "ingest_completed_date", parse_datetime),
        ParserParam("_metadata", "metadata", ModelMetadata),
        ParserParam("api_version", "api_version", str),
        ParserParam("container", "container", str),
        ParserParam("container_version", "container_version", str),
        ParserParam("type", "api_version", str),
        ParserParam("spec", "spec", ModelSpec),
        ParserParam("_display_name", "display_name", str),
        ParserParam("_name", "name", str),
        ParserParam("_summary", "summary", str),
        ParserParam("_status", "status", str),
    ]

    @property
    def metadata(self) -> ModelMetadata:
        """ModelMetadata: Metadata of the model

        In the case of loading a Model from the /model/<version_id> endpoint
        this will just return the metadata loaded directly from the json. In
        the case of the /models endpoint this will create and return a new
        instance containing most of the parameters as described in
        ModelMetadata, having obtained them from their locations that are
        different for this endpoint.

        Returns:
            ModelMetadata: Metadata of the model
        """

        # Return what already exists if possible
        if self._metadata is not None:
            return self._metadata
        # In the case of the /models endpoint, _metadata won't be assigned but
        # most of the parameters will be assigned in model, so create the
        # metadata instance here to ensure consistency in the rest of the code
        self._metadata = ModelMetadata(
            display_name=self._display_name,
            name=self._name,
            summary=self._summary,
            status=self._status,
        )
        return self._metadata

    # TODO: Replace with .filter???
    def filter_by_date(self, key: str, date_str: str) -> bool:
        """Returns whether a particular date is greater than or equal to the
           creation/publication date of this model.

        Args:
            key (str): Key for which date to check must be either 'creation'
                       or 'publication'
            date_str (str): Date for which models are to be filtered on - format
                            DD/MM/YYYY

        Returns:
            bool: Whether the given date is greater than or equal to the
                  chosen date
        """
        day, month, year = date_str.split("/")
        date_val = date(int(year), int(month), int(day))
        if key.lower() == "creation":
            return self.creation_date.date() >= date_val
        if key.lower() == "publication":
            return self.publication_date.date() >= date_val
        raise KeyError("Key should be 'creation' or 'publication'")

    def output_details(self, long: bool = False):
        """Prints relevant model attributes to command line

        Args:
            long (bool): Whether to print with the (potentially long)
                         description (ignored if description is None)
        """

        click.echo(
            "Name: "
            + self.metadata.display_name
            + TAB_SPACE
            + "ID: "
            + self.model_id
            + TAB_SPACE
            + "Date: "
            + self.creation_date.date().strftime("%B %d %Y")
        )
        click.echo("Summary: " + self.metadata.summary)
        if long and self.metadata.description is not None:
            click.echo("Description: ")
            prose_print(self.metadata.description, CONSOLE_WIDTH)
        click.echo("")

    def output_info(self):
        """Prints information about the model to command line"""

        click.echo("Name: " + self.metadata.display_name)
        click.echo("Date: " + self.creation_date.strftime("%B %d %Y"))
        click.echo("Summary: ")
        click.echo(self.metadata.summary)
        click.echo("Description: ")
        prose_print(self.metadata.description, CONSOLE_WIDTH)
        click.echo("")
        if self.spec.inputs is not None:
            click.echo("Input Parameters: ")
            click.echo(self.spec.inputs.format_parameters())
            click.echo("Input Data Slots: ")
            click.echo(self.spec.inputs.format_dataslots())
        if self.spec.outputs is not None:
            click.echo("Outputs: ")
            click.echo(self.spec.outputs.format_outputs())

    def output_version_details(self) -> str:
        """Prints model ID, display name, publication date and version
        message on one line
        """
        return (
            "ID: "
            + self.model_id
            + TAB_SPACE
            + "Name: "
            + self.metadata.display_name
            + TAB_SPACE
            + "Publication date: "
            + self.publication_date.date().strftime("%B %d %Y")
            + TAB_SPACE
            + "Version message: "
            + self.version_message
        )

    def output_version_history(self):
        """Prints the version history for the model to the command line"""
        for version in self.version_history:
            click.echo(
                "Name: "
                + self.metadata.display_name
                + TAB_SPACE
                + "ID: "
                + version.version_id
                + TAB_SPACE
                + "Date: "
                + version.publication_date.strftime("%B %d %Y")
            )
            click.echo(f"Version message: {version.version_message}")
            click.echo(f"Version tags: {', '.join(version.version_tags)}")
            click.echo("")


# The following methods mostly exists to get round current python limitations
# with typing (see https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class)
def parse_models(model_dictionary_list: List[dict]) -> List[Model]:
    """Parses the output of get_all_models and returns a list of Model
    instances"""
    return ParserBaseObject.parse_from_dict_list(Model, model_dictionary_list)


def parse_model(model_dictionary: dict) -> Model:
    """Parses the output of get_model and returns a list of Model
    instances"""
    return ParserBaseObject.parse_from_dict(Model, model_dictionary)

from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar, List, Optional

import click
from tabulate import tabulate

from dafni_cli.api.auth import Auth
from dafni_cli.api.parser import ParserBaseObject, ParserParam, parse_datetime
from dafni_cli.consts import (
    CONSOLE_WIDTH,
    TAB_SPACE,
    TABLE_PUBLICATION_DATE_HEADER,
    TABLE_VERSION_ID_HEADER,
    TABLE_VERSION_MESSAGE_HEADER,
    TABLE_VERSION_TAGS_HEADER,
)
from dafni_cli.models.inputs import ModelInputs
from dafni_cli.models.outputs import ModelOutputs
from dafni_cli.utils import format_datetime, format_table, prose_print


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
    contact_point_name: str
    contact_point_email: str

    description: Optional[str] = None
    publisher: Optional[str] = None
    source_code: Optional[str] = None
    licence: Optional[str] = None
    rights: Optional[str] = None

    STATUS_STRINGS = {
        "P": "Pending",
        "F": "Failed",
        "L": "Live",
        "S": "Superseded",
        "D": "Deprecated",
    }

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("display_name", "display_name", str),
        ParserParam("name", "name", str),
        ParserParam("summary", "summary", str),
        ParserParam("status", "status", str),
        ParserParam("description", "description", str),
        ParserParam("publisher", "publisher", str),
        ParserParam("source_code", "source_code", str),
        ParserParam("contact_point_name", "contact_point_name", str),
        ParserParam("contact_point_email", "contact_point_email", str),
        ParserParam("licence", "licence", str),
        ParserParam("rights", "rights", str),
    ]

    def get_status_string(self) -> str:
        """Return a human readable string representing the status of the model
        this metadata is for

        e.g.
            P - Pending
            F - Failed
            L - Live
            S - Superseded
            D - Deprecated
        """
        return self.STATUS_STRINGS.get(self.status, "Unknown")


@dataclass
class ModelSpec(ParserBaseObject):
    """Dataclass representing the specification of a model (containing
       the image url and inputs)

    Attributes:
        image_url (Optional[str]): URL of the image of the model (None if ingest failed)
        inputs (Optional[ModelInputs]): Structure containing the inputs of the model
        outputs (Optional[ModelOutputs]): Structure containing the outputs of the model
    """

    image_url: Optional[str] = None
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
    _licence: Optional[str] = None
    _rights: Optional[str] = None
    _contact_point_name: Optional[str] = ""
    _contact_point_email: Optional[str] = ""

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("model_id", "id", str),
        ParserParam("kind", "kind", str),
        ParserParam("owner_id", "owner", str),
        ParserParam("parent_id", "parent", str),
        ParserParam("creation_date", "creation_date", parse_datetime),
        ParserParam("publication_date", "publication_date", parse_datetime),
        ParserParam("version_message", "version_message", str),
        ParserParam("version_tags", "version_tags"),
        ParserParam("version_history", "version_history", ModelVersion),
        ParserParam("auth", "auth", Auth),
        ParserParam("ingest_completed_date", "ingest_completed_date", parse_datetime),
        ParserParam("_metadata", "metadata", ModelMetadata),
        ParserParam("api_version", "api_version", str),
        ParserParam("type", "type", str),
        ParserParam("spec", "spec", ModelSpec),
        ParserParam("_display_name", "display_name", str),
        ParserParam("_name", "name", str),
        ParserParam("_summary", "summary", str),
        ParserParam("_status", "status", str),
        ParserParam("_contact_point_name", "contact_point_name", str),
        ParserParam("_contact_point_email", "contact_point_email", str),
        ParserParam("_licence", "licence", str),
        ParserParam("_rights", "rights", str),
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
            contact_point_name=self._contact_point_name,
            contact_point_email=self._contact_point_email,
            licence=self._licence,
            rights=self._rights,
        )
        return self._metadata

    def get_brief_details(self) -> List:
        """Returns an array containing brief details about this model for
        the get models command

        Returns
            List: Containing display_name, model_id, status, access,
                  publication date and summary
        """
        return [
            self.metadata.display_name,
            self.model_id,
            self.metadata.get_status_string(),
            self.auth.get_permission_string(),
            format_datetime(self.publication_date, include_time=False),
            self.metadata.summary,
        ]

    def output_details(self):
        """Prints information about the model to command line (used for get
        model)"""

        click.echo(
            f"{self.metadata.display_name}  |  Status: {self.metadata.get_status_string()}  |  Tags: {', '.join(self.version_tags)}"
        )
        click.echo("")
        click.echo(f"Published by: {self.metadata.publisher}")
        click.echo(
            f"Contact Point: {self.metadata.contact_point_name} ({self.metadata.contact_point_email})"
        )
        click.echo("")
        click.echo(
            tabulate(
                [
                    ["Date:", format_datetime(self.creation_date, include_time=True)],
                    ["ID:", self.model_id],
                    ["Parent ID:", self.parent_id],
                ],
                tablefmt="plain",
            )
        )
        click.echo("")
        click.echo("Version message:")
        click.echo(self.version_message)
        click.echo("")
        click.echo("Summary:")
        click.echo(self.metadata.summary)
        click.echo("")
        click.echo("Description:")
        prose_print(self.metadata.description, CONSOLE_WIDTH)
        click.echo("")
        click.echo("Source code:")
        click.echo(self.metadata.source_code)
        click.echo(f"Licence: {self.metadata.licence}")
        click.echo(f"Rights: {self.metadata.rights}")
        if self.spec.inputs is not None:
            click.echo("")
            click.echo("Input Parameters: ")
            click.echo(self.spec.inputs.format_parameters())
            click.echo("")
            click.echo("Input Data Slots: ")
            click.echo(self.spec.inputs.format_dataslots())
        if self.spec.outputs is not None:
            click.echo("")
            click.echo("Outputs: ")
            click.echo(self.spec.outputs.format_outputs())

    def get_version_details(self) -> str:
        """Returns a string with the model ID, display name, publication date
        and version message (used prior to deletion)
        """
        return (
            f"Name: {self.metadata.display_name}\n"
            f"ID: {self.model_id}\n"
            f"Publication date: {format_datetime(self.publication_date, include_time=True)}\n"
            f"Version message: {self.version_message}\n"
        )

    def output_version_history(self):
        """Iterates through all versions and outputs their details in a table
        printed to the command line"""
        table_rows = []
        for version in self.version_history:
            table_rows.append(
                [
                    version.version_id,
                    format_datetime(version.publication_date, include_time=True),
                    ", ".join(version.version_tags),
                    version.version_message,
                ]
            )
        click.echo(
            format_table(
                headers=[
                    TABLE_VERSION_ID_HEADER,
                    TABLE_PUBLICATION_DATE_HEADER,
                    TABLE_VERSION_TAGS_HEADER,
                    TABLE_VERSION_MESSAGE_HEADER,
                ],
                rows=table_rows,
            )
        )


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

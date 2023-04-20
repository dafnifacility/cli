from dataclasses import dataclass
from datetime import datetime
from typing import Any, ClassVar, List

from dafni_cli.api.models_api import get_model
from dafni_cli.api.parser import ParserBaseObject, ParserParam, parse_datetime
from dafni_cli.api.session import DAFNISession


@dataclass
class ModelMetadata(ParserBaseObject):
    """Dataclass representing a DAFNI model's metadata

    Attributes:
        description (str): A rich description of the Model's function
        display_name (str): The display name of the Model
        name (str): Name of the model
        publisher (str): The name of the person or organisation who has
                         published the Model
        summary (str): A short summary of the Model's function
        source_code: A URL pointing to the source code for this Model
        status: Status of model ingest
                    P - Pending
                    F - Failed
                    L - Live
                    S - Superseded
                    D - Deprecated
    """

    description: str
    display_name: str
    name: str
    publisher: str
    summary: str
    source_code: str
    status: str

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("description", "description", str),
        ParserParam("display_name", "display_name", str),
        ParserParam("name", "name", str),
        ParserParam("publisher", "publisher", str),
        ParserParam("summary", "summary", str),
        ParserParam("source_code", "source_code", str),
        ParserParam("status", "status", str),
    ]


@dataclass
class ModelAuth(ParserBaseObject):
    """Dataclass representing the access the user has for a DAFNI model

    Attributes:
        asset_id (str): ID of the model
        view (bool): View access
        read (bool): Read access
        update (bool): Update access
        destroy (bool): Deletion access
        reason (str): Reason user has access to view this model
    """

    asset_id: str
    view: bool
    read: bool
    update: bool
    destroy: bool
    reason: str

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("asset_id", "asset_id", str),
        ParserParam("view", "view"),
        ParserParam("read", "read"),
        ParserParam("update", "update"),
        ParserParam("destroy", "destroy"),
        ParserParam("reason", "reason", str),
    ]


@dataclass
class ModelDataslot(ParserBaseObject):
    """Dataclass representing an input dataslot for a DAFNI
       model

    Attributes:
        name (str): Name of the slot
        path (str): Path of the file expected in the container
        defaults (List[str]): List of default dataset ids
        required (str): Whether the slot is required
        description (str): Description of the slot
    """

    name: str
    path: str
    defaults: List[str]
    required: bool
    description: str

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("name", "name", str),
        ParserParam("path", "path", str),
        ParserParam("defaults", "default"),
        ParserParam("required", "required"),
        ParserParam("description", "description"),
    ]


@dataclass
class ModelParameter(ParserBaseObject):
    """Dataclass representing an input parameter for a DAFNI model

    Attributes:
        name (str): Name of the parameter
        type (str): Type of the parameter
        title(str): Title of the parameter
        default (Any): Default value of the parameter
        required (bool): Whether the parameter is required
        description (str): Description of the model parameter
    """

    name: str
    type: str
    title: str
    default: Any
    required: bool
    description: str

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("name", "name", str),
        ParserParam("type", "type", str),
        ParserParam("title", "title"),
        ParserParam("default", "default"),
        ParserParam("required", "required"),
        ParserParam("description", "description"),
    ]


@dataclass
class ModelInputs(ParserBaseObject):
    """Dataclass representing an inputs for a DAFNI model

    Attributes:
        dataslots (List[ModelDataslot]): List of dataslots for the model
        parameters (List[ModelParameters]): List of parameters for the model
    """

    dataslots: List[ModelDataslot]
    parameters: List[ModelParameter]

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("dataslots", "dataslots", ModelDataslot),
        ParserParam("parameters", "parameters", ModelParameter),
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
    inputs: ModelInputs

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("image_url", "image", str),
        ParserParam("inputs", "inputs", ModelInputs),
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

    Attributes:
        api_version(str): Version of the DAFNI API used to retrieve model data
        model_id (str): Model version ID
        container (str): Name of the docker image the model should be run in
        container_version (str): Version of the docker image
        kind (str): Type of DAFNI object (should be "M" for model)
        owner_id (str): ID of the model owner
        parent (str): Parent model ID
        type (str): Type of dafni object ("model")
        creation_date (datetime): Date and time the model was created
        publication_date (datetime): Date and time the model was published
        ingest_completed_date (datetime): Date and time the model finished
                                          ingesting
        version_message (str): Message attached when the model was updated to
                               this model version
        version_tags (List[str]): Any tags created by the publisher for this
                                  model version
        version_history (List[ModelVersion]): Full version history of the
                                              model
        auth (ModelAuth): Authentication credentials giving the permissions
                          the current user has on the model
        metadata (ModelMetadata): Metadata of the model
        spec (ModelSpec): Model specification - includes the image url and its
                          inputs
    """

    api_version: str
    model_id: str
    container: str
    container_version: str
    kind: str
    owner_id: str
    parent_id: str
    type: str
    creation_date: datetime
    publication_date: datetime
    ingest_completed_date: datetime
    version_message: str
    version_tags: List[str]
    version_history: List[ModelVersion]
    auth: ModelAuth
    metadata: ModelMetadata
    spec: ModelSpec

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("api_version", "api_version", str),
        ParserParam("model_id", "id", str),
        ParserParam("container", "container", str),
        ParserParam("container_version", "container_version", str),
        ParserParam("kind", "kind", str),
        ParserParam("owner_id", "owner", str),
        ParserParam("parent_id", "parent", str),
        ParserParam("type", "api_version", str),
        ParserParam("creation_date", "creation_date", parse_datetime),
        ParserParam("publication_date", "publication_date", parse_datetime),
        ParserParam("ingest_completed_date", "ingest_completed_date", parse_datetime),
        ParserParam("version_message", "version_message", str),
        ParserParam("version_tags", "version_tags"),
        ParserParam("version_history", "version_history", ModelVersion),
        ParserParam("auth", "auth", ModelAuth),
        ParserParam("metadata", "metadata", ModelMetadata),
        ParserParam("spec", "spec", ModelSpec),
    ]


session = DAFNISession()

data = get_model(
    session,
    "94e5726f-40f9-44d3-aa6b-70de18ae0bfe",
)
model: Model = ParserBaseObject.parse_from_dict(Model, data)
print(model.spec.image_url)

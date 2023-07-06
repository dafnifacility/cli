from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar, List

from dafni_cli.api.parser import ParserBaseObject, ParserParam, parse_datetime


@dataclass
class WorkflowParameterSetMetadata(ParserBaseObject):
    """Dataclass representing the metadata of a parameter set in a DAFNI
       workflow

    Attributes:
        description (str): A rich description of the parameter set's function
        display_name (str): The display name of the parameter set
        name (str): Name of the parameter set
        publisher (str): The name of the person or organisation who has
                         published the parameter set
        workflow_version_id (str): Version id of the workflow
    """

    description: str
    display_name: str
    name: str
    publisher: str
    workflow_version_id: str

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("description", "description", str),
        ParserParam("display_name", "display_name", str),
        ParserParam("name", "name", str),
        ParserParam("publisher", "publisher", str),
        ParserParam("workflow_version_id", "workflow_version", str),
    ]


@dataclass
class WorkflowParameterSet(ParserBaseObject):
    """Dataclass representing a parameter set of a DAFNI workflow

    Should be identical to ParameterSetRead on swagger.

    Attributes:
        parameter_set_id (str): ID of the parameter set
        owner_id (str): ID of the parameter set owner
        creation_date (datetime): Date and time the parameter set was created
        publication_date (datetime): Date and time the parameter set was
                                     published
        kind (str): Type of DAFNI object (should be "P" for parameter set)
        api_version (str): Version of the DAFNI API used to retrieve the
                           parameter set data
        spec (dict): Specification of the parameter set (contains information
                     on the dataslots and parameters)
        metadata (WorkflowParameterSetMetadata): Metadata of the parameter set
    """

    parameter_set_id: str
    owner_id: str
    creation_date: datetime
    publication_date: datetime
    kind: str
    api_version: str
    # TODO: Left as a dict for now, would just need its own parsing function
    spec: dict
    metadata: WorkflowParameterSetMetadata

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("parameter_set_id", "id", str),
        ParserParam("owner_id", "owner", str),
        ParserParam("creation_date", "creation_date", parse_datetime),
        ParserParam("publication_date", "publication_date", parse_datetime),
        ParserParam("kind", "kind", str),
        ParserParam("api_version", "api_version", str),
        ParserParam("spec", "spec"),
        ParserParam("metadata", "metadata", WorkflowParameterSetMetadata),
    ]

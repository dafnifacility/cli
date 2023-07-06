from dataclasses import dataclass
from datetime import datetime
from typing import Any, ClassVar, Dict, List

from dafni_cli.api.parser import (
    ParserBaseObject,
    ParserParam,
    parse_datetime,
    parse_dict_retaining_keys,
)
from dafni_cli.workflows.specification import WorkflowSpecification


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
class WorkflowParameterSetSpecDataslot(ParserBaseObject):
    """Dataclass representing a step dataslot as it appears in a workflow
    parameters specification

    Not everything is parsed here as there can be a lot of variation and not
    all is currently needed.

    Attributes:
        datasets (List[str]): List of version IDs of datasets that fill the
                              slot
        name (str): Name of the dataslot
        path (str): Path to the data in the dataset
    """

    datasets: List[str]
    name: str
    path: str

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("datasets", "datasets"),
        ParserParam("name", "name", str),
        ParserParam("path", "path", str),
    ]


@dataclass
class WorkflowParameterSetSpecParameter(ParserBaseObject):
    """Dataclass representing a step parameter as it appears in a workflow
    parameters specification

    Not everything is parsed here as there can be a lot of variation and not
    all is currently needed.

    Attributes:
        name (str): Name of the parameter
        value (str): Value of the parameter
    """

    name: str
    value: Any

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("datasets", "datasets"),
        ParserParam("name", "name", str),
        ParserParam("value", "value"),
    ]


@dataclass
class WorkflowParameterSetSpecStep(ParserBaseObject):
    """Dataclass representing a step as it appears in a workflow parameters
    specification

    Not everything is parsed here as there can be a lot of variation and not
    all is currently needed.

    Attributes:
        dataslots (List[WorkflowParameterSetSpecDataslot]): List of dataslots
        kind (str): Type of step e.g. publisher, model
        parameters (List[WorkflowParameterSetSpecParameter]) List of parameters
    """

    dataslots: List[WorkflowParameterSetSpecDataslot]
    kind: str
    parameters: List[WorkflowParameterSetSpecParameter]

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("dataslots", "dataslots", WorkflowParameterSetSpecDataslot),
        ParserParam("kind", "kind", str),
        ParserParam("parameters", "parameters", WorkflowParameterSetSpecParameter),
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
        spec (Dict[str, WorkflowSpecificationStep]): Dictionary of step
                                       ID's and parameters for each step
        metadata (WorkflowParameterSetMetadata): Metadata of the parameter set
    """

    parameter_set_id: str
    owner_id: str
    creation_date: datetime
    publication_date: datetime
    kind: str
    api_version: str
    spec: Dict[str, WorkflowParameterSetSpecStep]
    metadata: WorkflowParameterSetMetadata

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("parameter_set_id", "id", str),
        ParserParam("owner_id", "owner", str),
        ParserParam("creation_date", "creation_date", parse_datetime),
        ParserParam("publication_date", "publication_date", parse_datetime),
        ParserParam("kind", "kind", str),
        ParserParam("api_version", "api_version", str),
        ParserParam(
            "spec",
            "spec",
            parse_dict_retaining_keys(WorkflowParameterSetSpecStep),
        ),
        ParserParam("metadata", "metadata", WorkflowParameterSetMetadata),
    ]

    def output_details(self, workflow_spec: WorkflowSpecification):
        """Prints information about this parameter set to command line
        (used for get workflow-parameter-set)

        Args:
            workflow_spec (WorkflowSpecfication): Workflow specification this
                                    parameter set comes from (needed to looking
                                    up step's themselves e.g. for their names)
        """

from dataclasses import dataclass
from typing import ClassVar, Dict, List, Optional

from dafni_cli.api.parser import (
    ParserBaseObject,
    ParserParam,
    parse_dict_retaining_keys,
)


@dataclass
class WorkflowSpecificationStep(ParserBaseObject):
    """Dataclass representing a step as it appears in a workflow's
    specification

    Not everything is parsed here as there can be a lot of variation and not
    all is currently needed.

    Attributes:
        dependencies (List[str]): List of IDs of any steps that this step
                                  depends on
        kind (str): Type of step e.g. publisher, model
        name (str): Name of the step

        metadata (Optional[dict]): Metadata to be used for a publisher step
                                   (if applicable)

        model_version (Optional[str]) Model version ID used for a model step
                                     (if applicable)
    """

    dependencies: List[str]
    kind: str
    name: str

    # Present only for a publisher step
    metadata: Optional[dict] = None

    # Present only for a model step
    model_version: Optional[str] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("dependencies", "dependencies"),
        ParserParam("kind", "kind", str),
        ParserParam("name", "name", str),
        ParserParam("metadata", "name", str),
        ParserParam("model_version", "model_version", str),
    ]


@dataclass
class WorkflowSpecification(ParserBaseObject):
    """Dataclass representing Workflows's specification

    Attributes:
        steps (Dict[str, WorkflowSpecificationStep]): Dictionary of step
                                                      ID's and definitions
    """

    steps: Dict[str, WorkflowSpecificationStep]

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam(
            "steps",
            "steps",
            parse_dict_retaining_keys(WorkflowSpecificationStep),
        ),
    ]

from dataclasses import dataclass
from typing import ClassVar, Dict, List

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
        dependencies (List[str]): List of IDs of any steps that this step depends on
        kind (str): Type of step e.g. publisher, model
        name (str): Name of the step
    """

    dependencies: List[str]
    kind: str
    name: str

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("dependencies", "dependencies"),
        ParserParam("kind", "kind", str),
        ParserParam("name", "name", str),
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

from dataclasses import dataclass, field
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
        inputs (List[str]): List of IDs of any steps that this step
                            takes inputs from

        metadata (Optional[dict]): Metadata to be used for a publisher step
                                   (if applicable)

        model_version (Optional[str]): Model version ID used for a model step
                                      (if applicable)

        iteration_mode (Optional[str]): Iteration mode for a loop step
                                        (sequential or parallel)
        workflow_version (Optional[str]): Workflow version ID used for a
                                          loop step (if applicable)
    """

    dependencies: List[str]
    kind: str
    name: str
    inputs: List[str] = field(default_factory=list)

    # Present only for a publisher step
    metadata: Optional[dict] = None

    # Present only for a model step
    model_version: Optional[str] = None

    # Present only for a loop step
    iteration_mode: Optional[str] = None
    workflow_version: Optional[str] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("dependencies", "dependencies"),
        ParserParam("kind", "kind", str),
        ParserParam("name", "name", str),
        ParserParam("inputs", "inputs"),
        ParserParam("metadata", "metadata"),
        ParserParam("model_version", "model_version", str),
        ParserParam("iteration_mode", "iteration_mode", str),
        ParserParam("workflow_version", "workflow_version", str),
    ]


@dataclass
class WorkflowSpecification(ParserBaseObject):
    """Dataclass representing Workflows's specification

    Attributes:
        steps (Dict[str, WorkflowSpecificationStep]): Dictionary of step
                                                      ID's and definitions
        errors (Optional[List[str]]): List of any errors that occurred when fetching
                            the data e.g. if a model doesn't have read
                            permissions for the current user but is needed
                            for a step
    """

    steps: Dict[str, WorkflowSpecificationStep]
    errors: Optional[List[str]] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam(
            "steps",
            "steps",
            parse_dict_retaining_keys(WorkflowSpecificationStep),
        ),
        ParserParam("errors", "errors"),
    ]

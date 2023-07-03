from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar, List

from dafni_cli.api.parser import ParserBaseObject, ParserParam, parse_datetime


@dataclass
class WorkflowInstanceListParameterSet(ParserBaseObject):
    """Dataclass representing the information gathered about the parameter set
       a workflow instance was executed with

    Attributes:
        parameter_set_id (str): ID of the parameter set
        display_name (str): Display name of the parameter set
    """

    parameter_set_id: str
    display_name: str

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("parameter_set_id", "id", str),
        ParserParam("display_name", "display_name", str),
    ]


@dataclass
class WorkflowInstanceListWorkflowVersion(ParserBaseObject):
    """Dataclass representing the information gathered about the workflow
       version a workflow instance was executed with

    Attributes:
        version_id (str): Version ID of the workflow
        version_message (str): Message labelling the workflow version
    """

    version_id: str
    version_message: str

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("version_id", "id", str),
        ParserParam("version_message", "version_message", str),
    ]


@dataclass
class WorkflowInstanceList(ParserBaseObject):
    """Dataclass representing a workflow instance (an execution of a DAFNI
       workflow) as returned when getting a Workflow

    Attributes:
        instance_id (str): ID of this instance
        submission_time (datetime): Date and time the instance was submitted
                                    for execution
        overall_status (str): Status of the overall workflow execution e.g.
                              'Succeeded'
        parameter_set (WorkflowInstanceParameterSet): Information on the
                            parameter set the instance used
        workflow_version (WorkflowInstanceWorkflowVersion): Information on the
                            workflow version the instance used
        finished_time (Optional[datetime]): Date and time the instance
                            finished execution if applicable
    """

    instance_id: str
    submission_time: datetime
    overall_status: str
    parameter_set: WorkflowInstanceListParameterSet
    workflow_version: WorkflowInstanceListWorkflowVersion
    finished_time: datetime = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("instance_id", "instance_id", str),
        ParserParam("submission_time", "submission_time", parse_datetime),
        ParserParam("overall_status", "overall_status", str),
        ParserParam("parameter_set", "parameter_set", WorkflowInstanceListParameterSet),
        ParserParam(
            "workflow_version", "workflow_version", WorkflowInstanceListWorkflowVersion
        ),
        ParserParam("finished_time", "finished_time", parse_datetime),
    ]

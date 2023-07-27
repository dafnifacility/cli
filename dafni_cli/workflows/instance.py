from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar, Dict, List, Optional

import click
from tabulate import tabulate

from dafni_cli.api.auth import Auth
from dafni_cli.api.parser import (
    ParserBaseObject,
    ParserParam,
    parse_datetime,
    parse_dict_retaining_keys,
)
from dafni_cli.consts import (
    TABLE_ASSERT_VERSION_ID_HEADER,
    TABLE_STATUS_HEADER,
    TABLE_STEP_NAME_HEADER,
    TABLE_STEP_TYPE_HEADER,
)
from dafni_cli.utils import format_datetime, format_table
from dafni_cli.workflows.metadata import WorkflowMetadata
from dafni_cli.workflows.parameter_set import WorkflowParameterSet
from dafni_cli.workflows.specification import (
    WorkflowSpecification,
    WorkflowSpecificationStep,
)


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
        parameter_set (WorkflowInstanceListParameterSet): Information on the
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
    finished_time: Optional[datetime] = None

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

    def get_brief_details(self) -> List:
        """Returns an array containing brief details about this instance for
        the get workflow-instances command

        Returns
            List: Containing instance_id, workflow version_id, parameters_set
                  display name, submission time, finished time and overall
                  status
        """
        return [
            self.instance_id,
            self.workflow_version.version_id,
            self.parameter_set.display_name,
            format_datetime(self.submission_time, include_time=True),
            format_datetime(self.finished_time, include_time=True),
            self.overall_status,
        ]


@dataclass
class WorkflowInstanceStepStatus(ParserBaseObject):
    """Dataclass containing information on a workflow step's status

    Attributes:
        status (str): Status of the step e.g. 'Succeeded'
        started_at (Optional[datetime]): Date and time this step started
        finished_at (Optional[datetime]): Date and time this step finished
    """

    status: str
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("status", "status", str),
        ParserParam("started_at", "started_at", parse_datetime),
        ParserParam("finished_at", "finished_at", parse_datetime),
    ]


@dataclass
class WorkflowInstanceProducedAsset(ParserBaseObject):
    """Dataclass containing information on a workflow's produced asset

    Attributes:
        dataset_id (str): ID of a produced dataset asset
        metadata_id (str): Metadata ID of a produced dataset asset
        version_id str: Version ID of a produced dataset asset
        kind (str): String describing the type of asset
    """

    dataset_id: str
    metadata_id: str
    version_id: str
    kind: str

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("dataset_id", "dataset_id", str),
        ParserParam("metadata_id", "metadata_id", str),
        ParserParam("version_id", "version_id", str),
        ParserParam("kind", "kind", str),
    ]


@dataclass
class WorkflowInstanceWorkflowVersion(ParserBaseObject):
    """Dataclass containing information on a Workflow version as found in the
    get workflow instance endpoint

    Effectively a stripped down version of Workflow (WorkflowVersionBasic on
    swagger)

    Attributes:
        workflow_id (str): Workflow ID
        metadata (WorkflowMetadata): Workflow metadata
        api_version (str): Version of the DAFNI API used to retrieve
                                     the workflow data
        kind (str): Type of DAFNI object (should be "W" for workflow)
        creation_date (datetime): Date and time the workflow was created
        publication_date (datetime): Date and time the workflow was published
        owner_id: str
        version_tags (List[str]): Any tags created by the publisher for this
                                  workflow version
        version_message (str): Message attached when the workflow was updated
                               to this workflow version
        parent_id (str): Parent workflow ID
        spec (WorkflowSpecification): Specification of the workflow (contains the
                                      steps of the workflow)
    """

    workflow_id: str
    metadata: WorkflowMetadata
    api_version: str
    kind: str
    creation_date: datetime
    publication_date: datetime
    owner_id: str
    version_tags: List[str]
    version_message: str
    parent_id: str
    spec: Optional[WorkflowSpecification] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("workflow_id", "id", str),
        ParserParam("metadata", "metadata", WorkflowMetadata),
        ParserParam("api_version", "api_version", str),
        ParserParam("kind", "kind", str),
        ParserParam("creation_date", "creation_date", parse_datetime),
        ParserParam("publication_date", "publication_date", parse_datetime),
        ParserParam("owner_id", "owner", str),
        ParserParam("version_tags", "version_tags"),
        ParserParam("version_message", "version_message", str),
        ParserParam("parent_id", "parent", str),
        ParserParam("spec", "spec", WorkflowSpecification),
    ]


@dataclass
class WorkflowInstance(ParserBaseObject):
    """Dataclass representing a workflow instance (an execution of a DAFNI
    workflow)

    Attributes:
        auth (Auth): Authentication credentials giving the permissions the
                     current user has on the workflow instance
        instance_id (str): Workflow instance ID
        submission_time (datetime): Date and time the instance was submitted
                                    for execution
        overall_status (str): Status of the overall workflow execution e.g.
                              'Succeeded'
        step_status (Dict[str, WorkflowInstanceStepStatus]): Dictionary of
                               step ID's and statuses
        produced_assets (Dict[str, WorkflowInstanceProducedAsset]): Dictionary
                                of produced assets ID's and info
        parameter_set (WorkflowParameterSet): Parameter set this instance used
        finished_time (Optional[datetime]): Date and time the instance
                            finished execution if applicable
    """

    auth: Auth
    instance_id: str
    submission_time: datetime
    overall_status: str
    step_statuses: Dict[str, WorkflowInstanceStepStatus]
    produced_assets: Dict[str, WorkflowInstanceProducedAsset]
    parameter_set: WorkflowParameterSet
    workflow_version: WorkflowInstanceWorkflowVersion
    finished_time: Optional[datetime] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("auth", "auth", Auth),
        ParserParam("instance_id", "instance_id", str),
        ParserParam("submission_time", "submission_time", parse_datetime),
        ParserParam("overall_status", "overall_status", str),
        ParserParam(
            "step_statuses",
            "step_status",
            parse_dict_retaining_keys(WorkflowInstanceStepStatus),
        ),
        ParserParam(
            "produced_assets",
            "produced_assets",
            parse_dict_retaining_keys(WorkflowInstanceProducedAsset),
        ),
        ParserParam("parameter_set", "parameter_set", WorkflowParameterSet),
        ParserParam(
            "workflow_version", "workflow_version", WorkflowInstanceWorkflowVersion
        ),
        ParserParam("finished_time", "finished_time", parse_datetime),
    ]

    def _find_step_info(self, step_id: str, step: WorkflowSpecificationStep):
        """Returns information about a given step to display in a table
        for format_steps

        Arguments:
            step_id (str): Step ID
            step (WorkflowSpecificationStep): Step dataclass instance

        Returns:
            List: Containing the name, type, asset version id, and status
                  The asset version id will be the produced dataset version
                  id in the case of a publisher step, and the model version
                  id used in the case of a model step.
        """

        # Check the step type and assign an asset version id to display
        asset_version_id = None
        if step.kind == "publisher" or step.kind == "visualisation":
            # Here once finished expect an asset to be produced, so
            # display that once available
            if step_id in self.produced_assets:
                asset_version_id = self.produced_assets[step_id].version_id
        elif step.kind == "model":
            # Here model step is taking in a model, so display its version
            # id
            asset_version_id = step.model_version
        elif step.kind == "loop":
            # Here loop step is taking in a workflow, so display its version
            # id
            asset_version_id = step.workflow_version

        return [
            step.name,
            step.kind,
            asset_version_id,
            self.step_statuses[step_id].status,
        ]

    def format_steps(self) -> str:
        """Formats steps and their statuses into a string which prints as a
        table

        Returns:
            str: Formatted string that will appear as a table when printed
        """

        return format_table(
            headers=[
                TABLE_STEP_NAME_HEADER,
                TABLE_STEP_TYPE_HEADER,
                TABLE_ASSERT_VERSION_ID_HEADER,
                TABLE_STATUS_HEADER,
            ],
            rows=[
                self._find_step_info(step_id, step)
                for step_id, step in self.workflow_version.spec.steps.items()
            ],
        )

    def output_details(self):
        """Prints information about the workflow instance to command line
        (used for get workflow-instance)"""

        click.echo(self.workflow_version.metadata.display_name)
        click.echo()

        if self.workflow_version.spec.errors:
            click.echo("Retrieving full Workflow failed:")
            for error_msg in self.workflow_version.spec.errors:
                click.echo(f"ERROR: {error_msg}")
            click.echo()

        click.echo(
            tabulate(
                [
                    # Information about the workflow this is an instance of
                    ["Workflow version ID:", self.workflow_version.workflow_id],
                    ["Parameter set ID:", self.parameter_set.parameter_set_id],
                    # Information about this instance
                    [
                        "Started:",
                        format_datetime(self.submission_time, include_time=True),
                    ],
                    [
                        "Finished:",
                        format_datetime(self.finished_time, include_time=True),
                    ],
                    ["Overall status:", self.overall_status],
                ],
                tablefmt="plain",
            )
        )
        click.echo()

        # Workflow execution info
        click.echo(self.format_steps())


# The following method mostly exists to get round current python limitations
# with typing (see https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class)
def parse_workflow_instance(workflow_instance_dictionary: dict) -> WorkflowInstance:
    """Parses the output of get_workflow and returns Workflow instance"""
    return ParserBaseObject.parse_from_dict(
        WorkflowInstance, workflow_instance_dictionary
    )

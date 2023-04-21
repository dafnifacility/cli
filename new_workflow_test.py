from dataclasses import dataclass
import datetime
import time
from typing import ClassVar, List, Optional

from dafni_cli.api.models_api import get_all_models, get_model
from dafni_cli.api.parser import ParserBaseObject, ParserParam, parse_datetime
from dafni_cli.api.session import DAFNISession
from dafni_cli.api.workflows_api import get_workflow, get_all_workflows
from dafni_cli.model.model import Model


@dataclass
class WorkflowMetadata(ParserBaseObject):
    """Dataclass representing a DAFNI workflows's metadata

    Attributes:
        description (str): A rich description of the Model's function
        display_name (str): The display name of the Model
        name (str): Name of the model
        publisher_id (str): The id of the person or organisation who has
                          published the Model
        summary (str): A short summary of the Model's function
    """

    description: str
    display_name: str
    name: str
    publisher_id: str
    summary: str

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("description", "description", str),
        ParserParam("display_name", "display_name", str),
        ParserParam("name", "name", str),
        ParserParam("publisher_id", "publisher", str),
        ParserParam("summary", "summary", str),
    ]


# TODO: Unify with ModelVersion
@dataclass
class WorkflowVersion(ParserBaseObject):
    """Dataclass containing information on a historic version of a workflow

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


# TODO: Unify with ModelAuth
@dataclass
class WorkflowAuth(ParserBaseObject):
    """Dataclass representing the access the user has for a DAFNI workflow

    Attributes:
        view (bool): View access
        read (bool): Read access
        update (bool): Update access
        destroy (bool): Deletion access
        reason (str): Reason user has access to view this model


        The following are only present for the /workflow/<version_id> endpoint
        (but are guaranteed for it)
        --------
        asset_id (Optional[str]): ID of the workflow


        The following are only present for the /workflows endpoint
        (but are guaranteed for it)
        --------
        role_id (Optional[str]): Role ID of the user
        name (Optional[str]): Name associated with the auth type
    """

    view: bool
    read: bool
    update: bool
    destroy: bool
    reason: str

    asset_id: Optional[str] = None
    name: Optional[str] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("view", "view"),
        ParserParam("read", "read"),
        ParserParam("update", "update"),
        ParserParam("destroy", "destroy"),
        ParserParam("reason", "reason", str),
        ParserParam("asset_id", "asset_id", str),
    ]


@dataclass
class WorkflowInstanceParameterSet(ParserBaseObject):
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
class WorkflowInstanceWorkflowVersion(ParserBaseObject):
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


# TODO: Check parsing mid workflow execution (expect finished time to be None?)
@dataclass
class WorkflowInstance(ParserBaseObject):
    """Dataclass representing a workflow instance (an execution of a DAFNI
       workflow)

    Attributes:
        instance_id (str): ID of this instance
        submission_time (datetime): Date and time the instance was submitted
                                    for execution
        finished_time (datetime): Date and time the instance finished
                                  execution
        overall_status (str): Status of the overall workflow execution e.g.
                              'Succeeded'
        parameter_set (WorkflowInstanceParameterSet): Information on the
                            parameter set the instance used
        workflow_version (WorkflowInstanceWorkflowVersion): Information on the
                            wowkflow version the instance used
    """

    instance_id: str
    submission_time: datetime
    finished_time: datetime
    overall_status: str
    parameter_set: WorkflowInstanceParameterSet
    workflow_version: WorkflowInstanceWorkflowVersion

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("instance_id", "instance_id", str),
        ParserParam("submission_time", "submission_time", str),
        ParserParam("finished_time", "finished_time", str),
        ParserParam("overall_status", "overall_status", str),
        ParserParam("parameter_set", "parameter_set", WorkflowInstanceParameterSet),
        ParserParam(
            "workflow_version", "workflow_version", WorkflowInstanceWorkflowVersion
        ),
    ]


@dataclass
class WorkflowParameterSetMetadata(ParserBaseObject):
    """Dataclass representing the metadata of a parameter set in a DAFNI
       workflow

    Attributes:
        description (str): A rich description of the Model's function
        display_name (str): The display name of the Model
        name (str): Name of the model
        publisher (str): The name of the person or organisation who has
                         published the Model
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


@dataclass
class Workflow(ParserBaseObject):
    """Dataclass representing a DAFNI workflow

    Attributes:
        metadata (WorkflowMetadata): Metadata of the workflow
        version_history (List[WorkflowVersion]): Full version history of the
                                                 workflow
        auth (WorkflowAuth): Authentication credentials giving the permissions
                             the current user has on the model
        instances (List[WorkflowInstance]): Workflow instances (executions of
                                            this workflow)
        parameter_sets (List[WorkflowInstance]): Parameter sets that can be
                                                 run with this workflow
        api_version (Optional[str]): Version of the DAFNI API used to retrieve
                                     the model data
        kind (str): Type of DAFNI object (should be "W" for workflow)
        creation_date (datetime): Date and time the workflow was created
        publication_date (datetime): Date and time the workflow was published
        owner_id (str): ID of the model owner
        version_tags (List[str]): Any tags created by the publisher for this
                                  workflow version
        version_message (str): Message attached when the workflow was updated
                               to this model version
        spec (dict): Specification of the workflow (contains the steps of the
                     workflow)
        parent_id (str): Parent workflow ID
    """

    metadata: WorkflowMetadata
    version_history: WorkflowVersion
    auth: WorkflowAuth
    instances: List[WorkflowInstance]
    parameter_sets: List[WorkflowParameterSet]
    api_version: str
    kind: str
    creation_date: datetime
    publication_date: datetime
    owner_id: str
    version_tags: List[str]
    version_message: str
    # TODO: Left as a dict for now, would just need its own parsing function
    spec: dict
    parent_id: str

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("metadata", "metadata", WorkflowMetadata),
        ParserParam("version_history", "version_history", WorkflowVersion),
        ParserParam("auth", "auth", WorkflowAuth),
        ParserParam("instances", "instances", WorkflowInstance),
        ParserParam("parameter_sets", "parameter_sets", WorkflowParameterSet),
        ParserParam("api_version", "api_version", str),
        ParserParam("kind", "kind", str),
        ParserParam("creation_date", "creation_date", parse_datetime),
        ParserParam("publication_date", "publication_date", parse_datetime),
        ParserParam("owner_id", "owner", str),
        ParserParam("version_tags", "version_tags"),
        ParserParam("version_message", "version_message", str),
        ParserParam("spec", "spec"),
        ParserParam("parent_id", "parent", str),
    ]


session = DAFNISession()

data = get_workflow(
    session,
    "0ca2e905-a7c0-4824-a91a-41d16238c1d6",  # Mine
    # "cfb164b2-59de-4156-85ea-36049e147322",  # Test
)
workflow: Workflow = ParserBaseObject.parse_from_dict(Workflow, data)
print(workflow.spec)


# data = get_all_workflows(
#     session,
# )
# print(data[0])

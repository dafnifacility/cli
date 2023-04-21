from dataclasses import dataclass
from datetime import date, datetime
from typing import ClassVar, List, Optional

import click

from dafni_cli.api.parser import ParserBaseObject, ParserParam, parse_datetime
from dafni_cli.consts import CONSOLE_WIDTH, TAB_SPACE
from dafni_cli.utils import prose_print


@dataclass
class WorkflowMetadata(ParserBaseObject):
    """Dataclass representing a DAFNI workflows's metadata

    Attributes:
        display_name (str): The display name of the Workflow
        name (str): Name of the Workflow
        summary (str): A short summary of the Workflow

        The following are only present for the /workflow/<version_id> endpoint
        (but are guaranteed for it)
        --------
        publisher_id (Optional[str]): The name of the person or organisation who has
                            published the Workflow
        description (Optional[str]): A rich description of the Workflow
    """

    display_name: str
    name: str
    summary: str

    publisher_id: Optional[str] = None
    description: Optional[str] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("display_name", "display_name", str),
        ParserParam("name", "name", str),
        ParserParam("summary", "summary", str),
        ParserParam("description", "description", str),
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
        workflow_id (str): Workflow ID
        version_history (List[WorkflowVersion]): Full version history of the
                                                 workflow
        auth (WorkflowAuth): Authentication credentials giving the permissions
                             the current user has on the model
        kind (str): Type of DAFNI object (should be "W" for workflow)
        creation_date (datetime): Date and time the workflow was created
        publication_date (datetime): Date and time the workflow was published
        owner_id (str): ID of the model owner
        version_tags (List[str]): Any tags created by the publisher for this
                                  workflow version
        version_message (str): Message attached when the workflow was updated
                               to this model version
        parent_id (str): Parent workflow ID
        metadata (WorkflowMetadata): Metadata of the workflow


        The following are only present for the /model/<version_id> endpoint
        (but are guaranteed for it)
        --------
        instances (Optional[List[WorkflowInstance]]): Workflow instances
                                (executions of this workflow)
        parameter_sets (Optional[List[WorkflowInstance]]): Parameter sets that
                                can be run with this workflow
        api_version (Optional[str]): Version of the DAFNI API used to retrieve
                                     the workflow data
        spec (Optional[dict]): Specification of the workflow (contains the
                              steps of the workflow)
    """

    workflow_id: str
    version_history: List[WorkflowVersion]
    auth: WorkflowAuth
    kind: str
    creation_date: datetime
    publication_date: datetime
    owner_id: str
    version_tags: List[str]
    version_message: str
    parent_id: str

    instances: Optional[List[WorkflowInstance]] = None
    parameter_sets: Optional[List[WorkflowParameterSet]] = None
    api_version: Optional[str] = None
    # TODO: Left as a dict for now, would just need its own parsing function
    spec: Optional[dict] = None

    # Internal metadata storage - Defined explicitly for the
    # /workflow/<version_id> endpoint but is None otherwise, the property
    # 'metadata' handles this discrepancy
    _metadata: Optional[WorkflowMetadata] = None

    # These are found in ModelMetadata but appear here when using the
    # /workflows endpoint, the property 'metadata' handles this discrepancy
    _display_name: Optional[str] = None
    _name: Optional[str] = None
    _summary: Optional[str] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("workflow_id", "id", str),
        ParserParam("version_history", "version_history", WorkflowVersion),
        ParserParam("auth", "auth", WorkflowAuth),
        ParserParam("kind", "kind", str),
        ParserParam("creation_date", "creation_date", parse_datetime),
        ParserParam("publication_date", "publication_date", parse_datetime),
        ParserParam("owner_id", "owner", str),
        ParserParam("version_tags", "version_tags"),
        ParserParam("version_message", "version_message", str),
        ParserParam("parent_id", "parent", str),
        ParserParam("instances", "instances", WorkflowInstance),
        ParserParam("parameter_sets", "parameter_sets", WorkflowParameterSet),
        ParserParam("api_version", "api_version", str),
        ParserParam("spec", "spec"),
        ParserParam("_metadata", "metadata", WorkflowMetadata),
        ParserParam("_display_name", "display_name", str),
        ParserParam("_name", "name", str),
        ParserParam("_summary", "summary", str),
    ]

    @property
    def metadata(self) -> WorkflowMetadata:
        """WorkflowMetadata: Metadata of the workflow

        In the case of loading a Workflow from the /workflow/<version_id>
        endpoint this will just return the metadata loaded directly from the
        json. In the case of the /workflows endpoint this will create and
        return a new instance containing most of the parameters as described in
        WorkflowMetadata, having obtained them from their locations that are
        different for this endpoint.

        Returns:
            WorkflowMetadata: Metadata of the workflow
        """

        # Return what already exists if possible
        if self._metadata is not None:
            return self._metadata
        # In the case of the /models endpoint, _metadata won't be assigned but
        # most of the parameters will be assigned in model, so create the
        # metadata instance here to ensure consistency in the rest of the code
        self._metadata = WorkflowMetadata(
            display_name=self._display_name,
            name=self._name,
            summary=self._summary,
        )
        return self._metadata

    # TODO: Unify with Model
    def filter_by_date(self, key: str, date_str: str) -> bool:
        """Returns whether a particular date is greater than or equal to the
           creation/publication date of this model.

        Args:
            key (str): Key for which date to check must be either 'creation'
                       or 'publication'
            date_str (str): Date for which models are to be filtered on - format
                            DD/MM/YYYY

        Returns:
            bool: Whether the given date is greater than or equal to the
                  chosen date
        """
        day, month, year = date_str.split("/")
        date_val = date(int(year), int(month), int(day))
        if key.lower() == "creation":
            return self.creation_date.date() >= date_val
        if key.lower() == "publication":
            return self.publication_date.date() >= date_val
        raise KeyError("Key should be 'creation' or 'publication'")

    def output_details(self, long: bool = False):
        """Prints relevant workflow attributes to command line

        Args:
            long (bool): Whether to print with the (potentially long)
                         description (ignored if description is None)
        """
        click.echo(
            "Name: "
            + self.metadata.display_name
            + TAB_SPACE
            + "ID: "
            + self.workflow_id
            + TAB_SPACE
            + "Date: "
            + self.creation_date.date().strftime("%B %d %Y")
        )
        click.echo("Summary: " + self.metadata.summary)
        if long and self.metadata.description is not None:
            click.echo("Description: ")
            prose_print(self.metadata.description, CONSOLE_WIDTH)
        click.echo("")

    def output_info(self):
        """Prints information about the workflow to command line"""

        click.echo("Name: " + self.metadata.display_name)
        click.echo("Date: " + self.creation_date.strftime("%B %d %Y"))
        click.echo("Summary: ")
        click.echo(self.metadata.summary)
        prose_print(self.metadata.description, CONSOLE_WIDTH)
        click.echo("")

        # TODO: Update this so can view inputs and outputs?
        # if self.metadata_obj.inputs:
        #     click.echo("Input Parameters: ")
        #     click.echo(self.metadata_obj.format_parameters())
        #     click.echo("Input Data Slots: ")
        #     click.echo(self.metadata_obj.format_dataslots())
        # if self.metadata_obj.outputs:
        #     click.echo("Outputs: ")
        #     click.echo(self.metadata_obj.format_outputs())

    def output_version_details(self) -> str:
        """Prints workflow ID, display name, publication time and version
        message on one line
        """
        return (
            "ID: "
            + self.workflow_id
            + TAB_SPACE
            + "Name: "
            + self.metadata.display_name
            + TAB_SPACE
            + "Publication date: "
            + self.publication_date.date().strftime("%B %d %Y")
            + TAB_SPACE
            + "Version message: "
            + self.version_message
        )

    def output_version_history(self):
        """Prints the version history for the workflow to the command line"""
        for version in self.version_history:
            click.echo(
                "Name: "
                + self.metadata.display_name
                + TAB_SPACE
                + "ID: "
                + version.version_id
                + TAB_SPACE
                + "Date: "
                + version.publication_date.strftime("%B %d %Y")
            )
            click.echo(f"Version message: {version.version_message}")
            click.echo(f"Version tags: {', '.join(version.version_tags)}")
            click.echo("")

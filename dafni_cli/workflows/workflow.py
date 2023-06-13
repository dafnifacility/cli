from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar, List, Optional

import click

from dafni_cli.api.auth import Auth
from dafni_cli.api.parser import ParserBaseObject, ParserDatetime, ParserParam
from dafni_cli.consts import (
    CONSOLE_WIDTH,
    TAB_SPACE,
    TABLE_FINISHED_HEADER,
    TABLE_ID_HEADER,
    TABLE_NAME_HEADER,
    TABLE_PARAMETER_SET_HEADER,
    TABLE_PUBLISHED_BY_HEADER,
    TABLE_PUBLISHED_DATE_HEADER,
    TABLE_STARTED_HEADER,
    TABLE_STATUS_HEADER,
    TABLE_WORKFLOW_VERSION_ID_HEADER,
)
from dafni_cli.utils import format_datetime, format_table, prose_print
from dafni_cli.workflows.instance import WorkflowInstance
from dafni_cli.workflows.parameter_set import WorkflowParameterSet


@dataclass
class WorkflowMetadata(ParserBaseObject):
    """Dataclass representing a DAFNI workflows's metadata

    Attributes:
        display_name (str): The display name of the Workflow
        name (str): Name of the Workflow
        summary (str): A short summary of the Workflow

        The following are only present for the /workflow/<version_id> endpoint
        (but are guaranteed not to be None for it)
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
        ParserParam("publication_date", "publication_date", ParserDatetime),
    ]


@dataclass
class Workflow(ParserBaseObject):
    """Dataclass representing a DAFNI workflow

    Attributes:
        workflow_id (str): Workflow ID
        version_history (List[WorkflowVersion]): Full version history of the
                                                 workflow
        auth (Auth): Authentication credentials giving the permissions the
                     current user has on the workflow
        kind (str): Type of DAFNI object (should be "W" for workflow)
        creation_date (datetime): Date and time the workflow was created
        publication_date (datetime): Date and time the workflow was published
        owner_id (str): ID of the workflow owner
        version_tags (List[str]): Any tags created by the publisher for this
                                  workflow version
        version_message (str): Message attached when the workflow was updated
                               to this workflow version
        parent_id (str): Parent workflow ID
        metadata (WorkflowMetadata): Metadata of the workflow


        The following are only present for the /workflow/<version_id> endpoint
        (but are guaranteed not to be None for it)
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
    auth: Auth
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
        ParserParam("auth", "auth", Auth),
        ParserParam("kind", "kind", str),
        ParserParam("creation_date", "creation_date", ParserDatetime),
        ParserParam("publication_date", "publication_date", ParserDatetime),
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
    def filter_by_date(self, key: str, date: datetime) -> bool:
        """Returns whether a particular date is less than or equal to the
           creation/publication date of this workflow.

        Args:
            key (str): Key for which date to check must be either 'creation'
                       or 'publication'
            date (datetime): Datetime object (only the date will be used)

        Returns:
            bool: Whether the given date is less than or equal to the
                  chosen date
        """
        date_val = date.date()
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
            f"Name: {self.metadata.display_name}{TAB_SPACE}"
            f"ID: {self.workflow_id}{TAB_SPACE}"
            f"Created: {format_datetime(self.creation_date, include_time=True)}"
        )
        click.echo(f"Summary: {self.metadata.summary}")
        if long and self.metadata.description is not None:
            click.echo("Description: ")
            prose_print(self.metadata.description, CONSOLE_WIDTH)
        click.echo("")

    def format_parameter_sets(self) -> str:
        """Formats parameter_sets into a string which prints as a table

        Returns:
            str: Formatted string that will appear as a table when printed
        """
        return format_table(
            headers=[
                TABLE_ID_HEADER,
                TABLE_NAME_HEADER,
                TABLE_PUBLISHED_BY_HEADER,
                TABLE_PUBLISHED_DATE_HEADER,
            ],
            rows=[
                [
                    parameter_set.parameter_set_id,
                    parameter_set.metadata.display_name,
                    parameter_set.metadata.publisher,
                    format_datetime(parameter_set.publication_date, include_time=False),
                ]
                for parameter_set in self.parameter_sets
            ],
        )

    def format_instances(self) -> str:
        """Formats instances into a string which prints as a table

        Returns:
            str: Formatted string that will appear as a table when printed
        """
        return format_table(
            headers=[
                TABLE_ID_HEADER,
                TABLE_WORKFLOW_VERSION_ID_HEADER,
                TABLE_PARAMETER_SET_HEADER,
                TABLE_STARTED_HEADER,
                TABLE_FINISHED_HEADER,
                TABLE_STATUS_HEADER,
            ],
            rows=[
                [
                    instance.instance_id,
                    instance.workflow_version.version_id,
                    instance.parameter_set.display_name,
                    format_datetime(instance.submission_time, include_time=True),
                    format_datetime(instance.finished_time, include_time=True),
                    instance.overall_status,
                ]
                for instance in self.instances
            ],
        )

    def output_info(self):
        """Prints information about the workflow to command line"""

        click.echo(f"Name: {self.metadata.display_name}")
        click.echo(f"Created: {format_datetime(self.creation_date, include_time=True)}")
        click.echo("Version message:")
        click.echo(self.version_message)
        click.echo("Summary:")
        click.echo(self.metadata.summary)
        click.echo("Description:")
        prose_print(self.metadata.description, CONSOLE_WIDTH)
        if self.parameter_sets is not None:
            click.echo("")
            click.echo("Parameter sets:")
            click.echo(self.format_parameter_sets())
        if self.instances is not None:
            click.echo("")
            click.echo("Instances:")
            click.echo(self.format_instances())

    def get_version_details(self) -> str:
        """Returns a string with the workflow ID, display name, publication
        time and version message on one line
        """
        return (
            f"ID: {self.workflow_id}{TAB_SPACE}"
            f"Name: {self.metadata.display_name}{TAB_SPACE}"
            f"Publication date: {format_datetime(self.publication_date, include_time=True)}{TAB_SPACE}"
            f"Version message: {self.version_message}"
        )

    def output_version_history(self):
        """Prints the version history for the workflow to the command line"""
        for version in self.version_history:
            click.echo(
                f"Name: {self.metadata.display_name}{TAB_SPACE}"
                f"ID: {version.version_id}{TAB_SPACE}"
                f"Publication date: {format_datetime(version.publication_date, include_time=True)}"
            )
            click.echo(f"Version message: {version.version_message}")
            click.echo(f"Version tags: {', '.join(version.version_tags)}")
            click.echo("")


# The following methods mostly exists to get round current python limitations
# with typing (see https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class)
def parse_workflows(workflow_dictionary_list: List[dict]) -> List[Workflow]:
    """Parses the output of get_all_workflows and returns a list of Workflow
    instances"""
    return ParserBaseObject.parse_from_dict_list(Workflow, workflow_dictionary_list)


def parse_workflow(workflow_dictionary: dict) -> Workflow:
    """Parses the output of get_workflow and returns Workflow instance"""
    return ParserBaseObject.parse_from_dict(Workflow, workflow_dictionary)

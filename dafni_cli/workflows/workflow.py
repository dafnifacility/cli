from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar, List, Optional, Tuple

import click
from tabulate import tabulate

from dafni_cli.api.auth import Auth
from dafni_cli.api.exceptions import ResourceNotFoundError
from dafni_cli.api.parser import ParserBaseObject, ParserParam, parse_datetime
from dafni_cli.consts import (
    CONSOLE_WIDTH,
    TABLE_FINISHED_HEADER,
    TABLE_ID_HEADER,
    TABLE_NAME_HEADER,
    TABLE_PARAMETER_SET_HEADER,
    TABLE_PUBLICATION_DATE_HEADER,
    TABLE_PUBLISHED_BY_HEADER,
    TABLE_PUBLISHED_DATE_HEADER,
    TABLE_STARTED_HEADER,
    TABLE_STATUS_HEADER,
    TABLE_VERSION_ID_HEADER,
    TABLE_VERSION_MESSAGE_HEADER,
    TABLE_VERSION_TAGS_HEADER,
    TABLE_WORKFLOW_VERSION_ID_HEADER,
)
from dafni_cli.utils import format_datetime, format_table, prose_print
from dafni_cli.workflows.instance import WorkflowInstanceList
from dafni_cli.workflows.metadata import WorkflowMetadata
from dafni_cli.workflows.parameter_set import WorkflowParameterSet
from dafni_cli.workflows.specification import WorkflowSpecification


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
        parameter_sets (Optional[List[WorkflowParameterSet]]): Parameter sets
                                that can be run with this workflow
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

    instances: Optional[List[WorkflowInstanceList]] = None
    parameter_sets: Optional[List[WorkflowParameterSet]] = None
    api_version: Optional[str] = None
    spec: Optional[WorkflowSpecification] = None

    # Internal metadata storage - Defined explicitly for the
    # /workflow/<version_id> endpoint but is None otherwise, the property
    # 'metadata' handles this discrepancy
    _metadata: Optional[WorkflowMetadata] = None

    # These are found in ModelMetadata but appear here when using the
    # /workflows endpoint, the property 'metadata' handles this discrepancy
    _display_name: Optional[str] = None
    _name: Optional[str] = None
    _summary: Optional[str] = None
    _contact_point_name: Optional[str] = ""
    _contact_point_email: Optional[str] = ""
    _licence: Optional[str] = None
    _rights: Optional[str] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("workflow_id", "id", str),
        ParserParam("version_history", "version_history", WorkflowVersion),
        ParserParam("auth", "auth", Auth),
        ParserParam("kind", "kind", str),
        ParserParam("creation_date", "creation_date", parse_datetime),
        ParserParam("publication_date", "publication_date", parse_datetime),
        ParserParam("owner_id", "owner", str),
        ParserParam("version_tags", "version_tags"),
        ParserParam("version_message", "version_message", str),
        ParserParam("parent_id", "parent", str),
        ParserParam("instances", "instances", WorkflowInstanceList),
        ParserParam("parameter_sets", "parameter_sets", WorkflowParameterSet),
        ParserParam("api_version", "api_version", str),
        ParserParam("spec", "spec", WorkflowSpecification),
        ParserParam("_metadata", "metadata", WorkflowMetadata),
        ParserParam("_display_name", "display_name", str),
        ParserParam("_name", "name", str),
        ParserParam("_summary", "summary", str),
        ParserParam("_contact_point_name", "contact_point_name", str),
        ParserParam("_contact_point_email", "contact_point_email", str),
        ParserParam("_licence", "licence", str),
        ParserParam("_rights", "rights", str),
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
            contact_point_name=self._contact_point_name,
            contact_point_email=self._contact_point_email,
            licence=self._licence,
            rights=self._rights,
        )
        return self._metadata

    def get_brief_details(self) -> List:
        """Returns an array containing brief details about this workflow for
        the get workflows command

        Returns
            List: Containing display_name, workflow_id, publication date and
                  summary
        """
        return [
            self.metadata.display_name,
            self.workflow_id,
            format_datetime(self.publication_date, include_time=False),
            self.metadata.summary,
        ]

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
                for parameter_set in sorted(
                    self.parameter_sets,
                    key=lambda param_set: param_set.publication_date,
                )
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
                instance.get_brief_details()
                for instance in sorted(
                    self.instances,
                    key=lambda inst: inst.finished_time,
                )
            ],
        )

    def output_details(self):
        """Prints information about this workflow to command line (used for get
        workflow)"""

        click.echo(
            f"{self.metadata.display_name}  |  Tags: {', '.join(self.version_tags)}"
        )
        click.echo("")
        click.echo(f"Published by: {self.metadata.publisher_id}")
        click.echo(
            f"Contact Point: {self.metadata.contact_point_name} ({self.metadata.contact_point_email})"
        )
        click.echo("")
        click.echo(
            tabulate(
                [
                    ["Date:", format_datetime(self.creation_date, include_time=True)],
                    ["ID:", self.workflow_id],
                    ["Parent ID:", self.parent_id],
                ],
                tablefmt="plain",
            )
        )
        click.echo("")
        click.echo("Version message:")
        click.echo(self.version_message)
        click.echo("")
        click.echo("Summary:")
        click.echo(self.metadata.summary)
        click.echo("")
        click.echo("Description:")
        prose_print(self.metadata.description, CONSOLE_WIDTH)
        click.echo("")
        click.echo(f"Licence: {self.metadata.licence}")
        click.echo(f"Rights: {self.metadata.rights}")
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
        time and version message (used prior to deletion)
        """
        return (
            f"ID: {self.workflow_id}\n"
            f"Name: {self.metadata.display_name}\n"
            f"Publication date: {format_datetime(self.publication_date, include_time=True)}\n"
            f"Version message: {self.version_message}\n"
        )

    def output_version_history(self):
        """Iterates through all versions and outputs their details in a table
        printed to the command line"""
        table_rows = []
        for version in self.version_history:
            table_rows.append(
                [
                    version.version_id,
                    format_datetime(version.publication_date, include_time=True),
                    ", ".join(version.version_tags),
                    version.version_message,
                ]
            )
        click.echo(
            format_table(
                headers=[
                    TABLE_VERSION_ID_HEADER,
                    TABLE_PUBLICATION_DATE_HEADER,
                    TABLE_VERSION_TAGS_HEADER,
                    TABLE_VERSION_MESSAGE_HEADER,
                ],
                rows=table_rows,
            )
        )

    def get_parameter_set(self, parameter_set_id: str) -> WorkflowParameterSet:
        """Returns a parameter set with a given ID

        Args:
            parameters_set_id (str): ID of the parameter set to obtain

        Raises:
            ResourceNotFoundError: If a parameter set with the given id wasn't found
        """

        for parameter_set in self.parameter_sets:
            if parameter_set.parameter_set_id == parameter_set_id:
                return parameter_set
        raise ResourceNotFoundError(
            f"Unable to find a parameter set with id '{parameter_set_id}'"
        )


# The following methods mostly exists to get round current python limitations
# with typing (see https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class)
def parse_workflows(workflow_dictionary_list: List[dict]) -> List[Workflow]:
    """Parses the output of get_all_workflows and returns a list of Workflow
    instances"""
    return ParserBaseObject.parse_from_dict_list(Workflow, workflow_dictionary_list)


def parse_workflow(workflow_dictionary: dict) -> Workflow:
    """Parses the output of get_workflow and returns Workflow instance"""
    return ParserBaseObject.parse_from_dict(Workflow, workflow_dictionary)

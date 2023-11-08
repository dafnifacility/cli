import copy
from datetime import datetime
from unittest import TestCase
from unittest.mock import call, patch

from dateutil.tz import tzutc

from dafni_cli.api.auth import Auth
from dafni_cli.api.exceptions import ResourceNotFoundError
from dafni_cli.api.parser import ParserBaseObject
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
from dafni_cli.tests.fixtures.workflow_parameter_set import TEST_WORKFLOW_PARAMETER_SET
from dafni_cli.tests.fixtures.workflows import (
    TEST_WORKFLOW,
    TEST_WORKFLOW_DATA_WORKFLOWS_ENDPOINT,
    TEST_WORKFLOW_METADATA,
    TEST_WORKFLOW_VERSION,
    TEST_WORKFLOWS,
)
from dafni_cli.utils import format_datetime
from dafni_cli.workflows.instance import WorkflowInstanceList
from dafni_cli.workflows.parameter_set import WorkflowParameterSet
from dafni_cli.workflows.specification import WorkflowSpecification
from dafni_cli.workflows.workflow import (
    Workflow,
    WorkflowVersion,
    parse_workflow,
    parse_workflows,
)


class TestWorkflowVersion(TestCase):
    """Tests the WorkflowVersion dataclass"""

    def test_parse(self):
        """Tests parsing of WorkflowVersion"""
        workflow_version: WorkflowVersion = ParserBaseObject.parse_from_dict(
            WorkflowVersion, TEST_WORKFLOW_VERSION
        )

        self.assertEqual(workflow_version.version_id, TEST_WORKFLOW_VERSION["id"])
        self.assertEqual(
            workflow_version.version_message, TEST_WORKFLOW_VERSION["version_message"]
        )
        self.assertEqual(
            workflow_version.version_tags, TEST_WORKFLOW_VERSION["version_tags"]
        )
        self.assertEqual(
            workflow_version.publication_date,
            datetime(2023, 4, 4, 8, 34, 36, 531809, tzinfo=tzutc()),
        )


class TestWorkflow(TestCase):
    """Tests the Workflow dataclass"""

    def test_parse_workflows(self):
        """Tests parsing of a workflow using test data for the
        /workflows endpoint"""
        workflow: Workflow = parse_workflows(TEST_WORKFLOWS)[0]

        self.assertEqual(
            workflow.workflow_id, TEST_WORKFLOW_DATA_WORKFLOWS_ENDPOINT["id"]
        )

        # WorkflowVersion (contents tested in TestWorkflowVersion)
        self.assertEqual(len(workflow.version_history), 1)
        self.assertEqual(type(workflow.version_history[0]), WorkflowVersion)

        # Auth (contents tested in TestAuth)
        self.assertEqual(type(workflow.auth), Auth)

        self.assertEqual(workflow.kind, TEST_WORKFLOW_DATA_WORKFLOWS_ENDPOINT["kind"])
        self.assertEqual(
            workflow.creation_date,
            datetime(2023, 4, 4, 8, 34, 36, 531809, tzinfo=tzutc()),
        )
        self.assertEqual(
            workflow.publication_date,
            datetime(2023, 4, 4, 8, 34, 36, 531809, tzinfo=tzutc()),
        )
        self.assertEqual(
            workflow.owner_id, TEST_WORKFLOW_DATA_WORKFLOWS_ENDPOINT["owner"]
        )
        self.assertEqual(
            workflow.version_tags, TEST_WORKFLOW_DATA_WORKFLOWS_ENDPOINT["version_tags"]
        )
        self.assertEqual(
            workflow.version_message,
            TEST_WORKFLOW_DATA_WORKFLOWS_ENDPOINT["version_message"],
        )
        self.assertEqual(
            workflow.parent_id, TEST_WORKFLOW_DATA_WORKFLOWS_ENDPOINT["parent"]
        )

        # WorkflowInstance's
        self.assertEqual(workflow.instances, None)

        # WorkflowParameterSet's
        self.assertEqual(workflow.parameter_sets, None)

        self.assertEqual(workflow.api_version, None)
        self.assertEqual(workflow.spec, None)

        # Ensure the metadata is correct
        self.assertEqual(
            workflow.metadata.display_name,
            TEST_WORKFLOW_DATA_WORKFLOWS_ENDPOINT["display_name"],
        )
        self.assertEqual(
            workflow.metadata.name, TEST_WORKFLOW_DATA_WORKFLOWS_ENDPOINT["name"]
        )
        self.assertEqual(
            workflow.metadata.summary, TEST_WORKFLOW_DATA_WORKFLOWS_ENDPOINT["summary"]
        )
        self.assertEqual(
            workflow.metadata.publisher_id,
            None,
        )
        self.assertEqual(
            workflow.metadata.description,
            None,
        )

    def test_parse_workflow(self):
        """Tests parsing of a workflow using test data for the
        /workflow/<version_id> endpoint"""
        workflow: Workflow = parse_workflow(TEST_WORKFLOW)

        self.assertEqual(workflow.workflow_id, TEST_WORKFLOW["id"])

        # WorkflowVersion (contents tested in TestWorkflowVersion)
        self.assertEqual(len(workflow.version_history), 1)
        self.assertEqual(type(workflow.version_history[0]), WorkflowVersion)

        # Auth (contents tested in TestAuth)
        self.assertEqual(type(workflow.auth), Auth)

        self.assertEqual(workflow.kind, TEST_WORKFLOW["kind"])
        self.assertEqual(
            workflow.creation_date,
            datetime(2023, 4, 4, 8, 34, 36, 531809, tzinfo=tzutc()),
        )
        self.assertEqual(
            workflow.publication_date,
            datetime(2023, 4, 4, 8, 34, 36, 531809, tzinfo=tzutc()),
        )
        self.assertEqual(workflow.owner_id, TEST_WORKFLOW["owner"])
        self.assertEqual(workflow.version_tags, TEST_WORKFLOW["version_tags"])
        self.assertEqual(workflow.version_message, TEST_WORKFLOW["version_message"])
        self.assertEqual(workflow.parent_id, TEST_WORKFLOW["parent"])

        # WorkflowInstanceList's (contents tested in TestWorkflowInstanceList)
        self.assertEqual(len(workflow.instances), 1)
        self.assertEqual(type(workflow.instances[0]), WorkflowInstanceList)

        # WorkflowParameterSet's (contents tested in TestWorkflowInstanceListParameterSet)
        self.assertEqual(len(workflow.parameter_sets), 1)
        self.assertEqual(type(workflow.parameter_sets[0]), WorkflowParameterSet)

        self.assertEqual(workflow.api_version, TEST_WORKFLOW["api_version"])

        # WorkflowSpecification (contents tested in TestWorkflowSpecification)
        self.assertEqual(
            type(workflow.spec),
            WorkflowSpecification,
        )

        # Ensure the metadata is correct
        self.assertEqual(
            workflow.metadata.display_name, TEST_WORKFLOW_METADATA["display_name"]
        )
        self.assertEqual(workflow.metadata.name, TEST_WORKFLOW_METADATA["name"])
        self.assertEqual(workflow.metadata.summary, TEST_WORKFLOW_METADATA["summary"])
        self.assertEqual(
            workflow.metadata.publisher_id, TEST_WORKFLOW_METADATA["publisher"]
        )
        self.assertEqual(
            workflow.metadata.description, TEST_WORKFLOW_METADATA["description"]
        )

    def test_get_brief_details(self):
        """Tests get_brief_details works correctly"""
        # SETUP
        workflow: Workflow = parse_workflow(TEST_WORKFLOW)

        # CALL
        result = workflow.get_brief_details()

        # ASSERT
        self.assertEqual(
            result,
            [
                workflow.metadata.display_name,
                workflow.workflow_id,
                format_datetime(workflow.publication_date, include_time=False),
                workflow.metadata.summary,
            ],
        )

    @patch("dafni_cli.workflows.workflow.format_table")
    def test_format_parameter_sets(
        self,
        mock_format_table,
    ):
        """Tests format_parameter_sets works correctly"""
        # SETUP
        workflow: Workflow = parse_workflow(TEST_WORKFLOW)

        # Two (almost) identical parameter sets
        workflow.parameter_sets.append(copy.deepcopy(workflow.parameter_sets[0]))

        workflow.parameter_sets[0].publication_date = datetime(2023, 4, 4)
        workflow.parameter_sets[1].publication_date = datetime(2023, 2, 4)

        # CALL
        result = workflow.format_parameter_sets()

        # ASSERT
        mock_format_table.assert_called_once_with(
            headers=[
                TABLE_ID_HEADER,
                TABLE_NAME_HEADER,
                TABLE_PUBLISHED_BY_HEADER,
                TABLE_PUBLISHED_DATE_HEADER,
            ],
            rows=[
                # Should have oldest first
                [
                    "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
                    "First parameter set",
                    "Joel Davies",
                    "2023-02-04",
                ],
                [
                    "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
                    "First parameter set",
                    "Joel Davies",
                    "2023-04-04",
                ],
            ],
        )
        self.assertEqual(result, mock_format_table.return_value)

    @patch("dafni_cli.workflows.workflow.format_table")
    def test_format_instances(
        self,
        mock_format_table,
    ):
        """Tests format_instances works correctly"""
        # SETUP
        workflow: Workflow = parse_workflow(TEST_WORKFLOW)

        # Two identical instances
        workflow.instances.append(workflow.instances[0])

        # CALL
        result = workflow.format_instances()

        # ASSERT
        mock_format_table.assert_called_once_with(
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
                    "0a0a0a0a-0a00-0a00-a000-0a0a0000000c",
                    "0a0a0a0a-0a00-0a00-a000-0a0a0000000b",
                    "First parameter set",
                    "2023-04-06T12:46:38",
                    "2023-04-06T12:58:35",
                    "Succeeded",
                ],
            ]
            * 2,
        )
        self.assertEqual(result, mock_format_table.return_value)

    @patch("dafni_cli.workflows.workflow.tabulate")
    @patch("dafni_cli.workflows.workflow.prose_print")
    @patch("dafni_cli.workflows.workflow.click")
    @patch.object(Workflow, "format_parameter_sets")
    @patch.object(Workflow, "format_instances")
    def test_output_details(
        self,
        mock_format_instances,
        mock_format_parameter_sets,
        mock_click,
        mock_prose_print,
        mock_tabulate,
    ):
        """Tests output_details works correctly"""
        # SETUP
        workflow = parse_workflow(TEST_WORKFLOW)

        # CALL
        workflow.output_details()

        # ASSERT
        mock_format_parameter_sets.assert_called_once()
        mock_format_instances.assert_called_once()
        self.assertEqual(
            mock_click.echo.mock_calls,
            [
                call(
                    f"{workflow.metadata.display_name}  |  Tags: {', '.join(workflow.version_tags)}"
                ),
                call(""),
                call(f"Published by: {workflow.metadata.publisher_id}"),
                call(
                    f"Contact Point: {workflow.metadata.contact_point_name} ({workflow.metadata.contact_point_email})"
                ),
                call(""),
                call(mock_tabulate.return_value),
                call(""),
                call("Version message:"),
                call(workflow.version_message),
                call(""),
                call("Summary:"),
                call(workflow.metadata.summary),
                call(""),
                call("Description:"),
                call(""),
                call(f"Licence: {workflow.metadata.licence}"),
                call(f"Rights: {workflow.metadata.rights}"),
                call(""),
                call("Parameter sets:"),
                call(mock_format_parameter_sets.return_value),
                call(""),
                call("Instances:"),
                call(mock_format_instances.return_value),
            ],
        )
        mock_tabulate.assert_called_once_with(
            [
                ["Date:", format_datetime(workflow.creation_date, include_time=True)],
                ["ID:", workflow.workflow_id],
                ["Parent ID:", workflow.parent_id],
            ],
            tablefmt="plain",
        )
        mock_prose_print.assert_called_once_with(
            workflow.metadata.description, CONSOLE_WIDTH
        )

    @patch("dafni_cli.workflows.workflow.tabulate")
    @patch("dafni_cli.workflows.workflow.prose_print")
    @patch("dafni_cli.workflows.workflow.click")
    @patch.object(Workflow, "format_parameter_sets")
    @patch.object(Workflow, "format_instances")
    def test_output_details_when_parameters_sets_and_instances_none(
        self,
        mock_format_instances,
        mock_format_parameter_sets,
        mock_click,
        mock_prose_print,
        mock_tabulate,
    ):
        """Tests output_details works correctly"""
        # SETUP
        workflow = parse_workflow(TEST_WORKFLOW)
        workflow.parameter_sets = None
        workflow.instances = None

        # CALL
        workflow.output_details()

        # ASSERT
        mock_format_parameter_sets.assert_not_called()
        mock_format_instances.assert_not_called()
        mock_click.echo.assert_has_calls(
            [
                call(
                    f"{workflow.metadata.display_name}  |  Tags: {', '.join(workflow.version_tags)}"
                ),
                call(""),
                call(f"Published by: {workflow.metadata.publisher_id}"),
                call(
                    f"Contact Point: {workflow.metadata.contact_point_name} ({workflow.metadata.contact_point_email})"
                ),
                call(""),
                call(mock_tabulate.return_value),
                call(""),
                call("Version message:"),
                call(workflow.version_message),
                call(""),
                call("Summary:"),
                call(workflow.metadata.summary),
                call(""),
                call("Description:"),
                call(""),
                call(f"Licence: {workflow.metadata.licence}"),
                call(f"Rights: {workflow.metadata.rights}"),
            ]
        )
        mock_tabulate.assert_called_once_with(
            [
                ["Date:", format_datetime(workflow.creation_date, include_time=True)],
                ["ID:", workflow.workflow_id],
                ["Parent ID:", workflow.parent_id],
            ],
            tablefmt="plain",
        )
        mock_prose_print.assert_called_once_with(
            workflow.metadata.description, CONSOLE_WIDTH
        )

    def test_get_version_details(self):
        """Tests get_version_details works correctly"""
        # SETUP
        workflow = parse_workflow(TEST_WORKFLOW)

        # CALL
        result = workflow.get_version_details()

        # ASSERT
        self.assertEqual(
            result,
            f"ID: 0a0a0a0a-0a00-0a00-a000-0a0a0000000a\n"
            f"Name: A Workflow\n"
            f"Publication date: {format_datetime(workflow.publication_date, include_time=True)}\n"
            "Version message: Initial Workflow version\n",
        )

    @patch("dafni_cli.workflows.workflow.format_table")
    @patch("dafni_cli.workflows.workflow.click")
    def test_output_version_history(self, mock_click, mock_format_table):
        """Tests output_version_history works correctly"""
        # SETUP
        workflow = parse_workflow(TEST_WORKFLOW)

        # CALL
        workflow.output_version_history()

        # ASSERT
        mock_format_table.assert_called_once_with(
            headers=[
                TABLE_VERSION_ID_HEADER,
                TABLE_PUBLICATION_DATE_HEADER,
                TABLE_VERSION_TAGS_HEADER,
                TABLE_VERSION_MESSAGE_HEADER,
            ],
            rows=[
                [
                    "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
                    format_datetime(datetime(2023, 4, 4, 8, 34, 36), include_time=True),
                    "latest",
                    "Initial Workflow version",
                ]
            ],
        )
        mock_click.echo.assert_called_once_with(mock_format_table.return_value)

    def test_get_parameter_set(self):
        """Tests get_parameter_set works correctly"""

        # SETUP
        workflow = parse_workflow(TEST_WORKFLOW)

        # CALL
        result = workflow.get_parameter_set(TEST_WORKFLOW_PARAMETER_SET["id"])

        # ASSERT
        self.assertEqual(result, workflow.parameter_sets[0])

    def test_get_parameter_set_when_not_found(self):
        """Tests get_parameter_set raises an error when the parameter set
        isn't found in the workflow"""

        # SETUP
        workflow = parse_workflow(TEST_WORKFLOW)
        parameter_set_id = "invalid_id"

        # CALL & ASSERT
        with self.assertRaises(ResourceNotFoundError) as err:
            workflow.get_parameter_set(parameter_set_id)
        self.assertEqual(
            str(err.exception),
            f"Unable to find a parameter set with id '{parameter_set_id}'",
        )

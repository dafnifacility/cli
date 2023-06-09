from datetime import datetime
from unittest import TestCase
from unittest.mock import call, patch

from dateutil.tz import tzutc

from dafni_cli.api.auth import Auth
from dafni_cli.api.parser import ParserBaseObject
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
from dafni_cli.utils import format_datetime
from dafni_cli.workflows.instance import WorkflowInstance
from dafni_cli.workflows.parameter_set import WorkflowParameterSet
from dafni_cli.workflows.workflow import (
    Workflow,
    WorkflowVersion,
    parse_workflow,
    parse_workflows,
)

from test.fixtures.workflows import (
    TEST_WORKFLOW,
    TEST_WORKFLOW_DATA_WORKFLOWS_ENDPOINT,
    TEST_WORKFLOW_METADATA,
    TEST_WORKFLOW_VERSION,
    TEST_WORKFLOWS,
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

        # WorkflowInstance's (contents tested in TestWorkflowInstance)
        self.assertEqual(len(workflow.instances), 1)
        self.assertEqual(type(workflow.instances[0]), WorkflowInstance)

        # WorkflowParameterSet's (contents tested in TestWorkflowInstance)
        self.assertEqual(len(workflow.parameter_sets), 1)
        self.assertEqual(type(workflow.parameter_sets[0]), WorkflowParameterSet)

        self.assertEqual(workflow.api_version, TEST_WORKFLOW["api_version"])
        self.assertEqual(workflow.spec, TEST_WORKFLOW["spec"])

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

    def _test_filter_by_date(
        self, workflow: Workflow, key: str, date_str: str, expected_output: bool
    ):
        """Utility function to check a particular set of parameters to
        filter_by_date does what is expected"""
        self.assertEqual(workflow.filter_by_date(key, date_str), expected_output)

    def test_filter_by_date(self):
        """Tests filter_by_date works correctly"""
        # SETUP
        workflow = parse_workflow(TEST_WORKFLOW)

        # Creation date and publication date's are:
        # 2023-04-04T08:34:36.531809Z
        # 2023-04-04T08:34:36.531809Z

        # CALL

        # Before
        self._test_filter_by_date(workflow, "creation", datetime(2018, 5, 16), True)
        self._test_filter_by_date(workflow, "publication", datetime(2018, 5, 16), True)
        # Equal
        self._test_filter_by_date(workflow, "creation", datetime(2023, 4, 4), True)
        self._test_filter_by_date(workflow, "publication", datetime(2023, 4, 4), True)
        # After
        self._test_filter_by_date(workflow, "creation", datetime(2023, 4, 25), False)
        self._test_filter_by_date(workflow, "publication", datetime(2023, 4, 25), False)

    def test_filter_by_date_error(self):
        """Tests filter_by_date raises an error if the key is wrong"""
        # SETUP
        workflow = parse_workflow(TEST_WORKFLOW)

        with self.assertRaises(KeyError):
            workflow.filter_by_date("key", datetime(2020, 12, 11))

    @patch("dafni_cli.workflows.workflow.click")
    def test_output_details(self, mock_click):
        """Tests output_details works correctly"""
        # SETUP
        workflow = parse_workflow(TEST_WORKFLOW)

        # CALL
        workflow.output_details()

        # ASSERT
        mock_click.echo.assert_has_calls(
            [
                call(
                    f"Name: A Workflow{TAB_SPACE}"
                    f"ID: 0a0a0a0a-0a00-0a00-a000-0a0a0000000a{TAB_SPACE}"
                    f"Created: {format_datetime(workflow.creation_date, include_time=True)}"
                ),
                call("Summary: Test workflow created to learn about DAFNI"),
                call(""),
            ]
        )

    @patch("dafni_cli.workflows.workflow.prose_print")
    @patch("dafni_cli.workflows.workflow.click")
    def test_output_details_with_long(self, mock_click, mock_prose_print):
        """Tests output_details works correctly when 'long' is set to True"""
        # SETUP
        workflow = parse_workflow(TEST_WORKFLOW)

        # CALL
        workflow.output_details(long=True)

        # ASSERT
        mock_click.echo.assert_has_calls(
            [
                call(
                    f"Name: A Workflow{TAB_SPACE}"
                    f"ID: 0a0a0a0a-0a00-0a00-a000-0a0a0000000a{TAB_SPACE}"
                    f"Created: {format_datetime(workflow.creation_date, include_time=True)}"
                ),
                call("Summary: Test workflow created to learn about DAFNI"),
                call("Description: "),
                call(""),
            ]
        )
        mock_prose_print.called_once_with("description", CONSOLE_WIDTH)

    @patch("dafni_cli.workflows.workflow.format_table")
    def test_format_parameter_sets(
        self,
        mock_format_table,
    ):
        """Tests format_parameter_sets works correctly"""
        # SETUP
        workflow: Workflow = parse_workflow(TEST_WORKFLOW)

        # Two identical parameter sets
        workflow.parameter_sets.append(workflow.parameter_sets[0])

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
                [
                    "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
                    "First parameter set",
                    "Joel Davies",
                    "2023-04-04",
                ],
            ]
            * 2,
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

    @patch("dafni_cli.workflows.workflow.prose_print")
    @patch("dafni_cli.workflows.workflow.click")
    @patch.object(Workflow, "format_parameter_sets")
    @patch.object(Workflow, "format_instances")
    def test_output_info(
        self,
        mock_format_instances,
        mock_format_parameter_sets,
        mock_click,
        mock_prose_print,
    ):
        """Tests output_info works correctly"""
        # SETUP
        workflow = parse_workflow(TEST_WORKFLOW)

        # CALL
        workflow.output_info()

        # ASSERT
        mock_format_parameter_sets.assert_called_once()
        mock_format_instances.assert_called_once()
        mock_click.echo.assert_has_calls(
            [
                call(f"Name: {workflow.metadata.display_name}"),
                call(
                    f"Created: {format_datetime(workflow.creation_date, include_time=True)}"
                ),
                call("Version message:"),
                call(workflow.version_message),
                call("Summary:"),
                call(workflow.metadata.summary),
                call("Description:"),
                call(""),
                call("Parameter sets:"),
                call(mock_format_parameter_sets.return_value),
                call(""),
                call("Instances:"),
                call(mock_format_instances.return_value),
            ]
        )
        mock_prose_print.assert_called_once_with(
            workflow.metadata.description, CONSOLE_WIDTH
        )

    @patch("dafni_cli.workflows.workflow.prose_print")
    @patch("dafni_cli.workflows.workflow.click")
    @patch.object(Workflow, "format_parameter_sets")
    @patch.object(Workflow, "format_instances")
    def test_output_info_when_parameters_sets_and_instances_none(
        self,
        mock_format_instances,
        mock_format_parameter_sets,
        mock_click,
        mock_prose_print,
    ):
        """Tests output_info works correctly"""
        # SETUP
        workflow = parse_workflow(TEST_WORKFLOW)
        workflow.parameter_sets = None
        workflow.instances = None

        # CALL
        workflow.output_info()

        # ASSERT
        mock_format_parameter_sets.assert_not_called()
        mock_format_instances.assert_not_called()
        mock_click.echo.assert_has_calls(
            [
                call(f"Name: {workflow.metadata.display_name}"),
                call(
                    f"Created: {format_datetime(workflow.creation_date, include_time=True)}"
                ),
                call("Version message:"),
                call(workflow.version_message),
                call("Summary:"),
                call(workflow.metadata.summary),
                call("Description:"),
            ]
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
            f"ID: 0a0a0a0a-0a00-0a00-a000-0a0a0000000a{TAB_SPACE}"
            f"Name: A Workflow{TAB_SPACE}"
            f"Publication date: {format_datetime(workflow.publication_date, include_time=True)}{TAB_SPACE}"
            "Version message: Initial Workflow version",
        )

    @patch("dafni_cli.workflows.workflow.click")
    def test_output_version_history(self, mock_click):
        """Tests output_version_history works correctly"""
        # SETUP
        workflow = parse_workflow(TEST_WORKFLOW)

        # CALL
        workflow.output_version_history()

        # ASSERT
        mock_click.echo.assert_has_calls(
            [
                call(
                    f"Name: A Workflow{TAB_SPACE}"
                    f"ID: 0a0a0a0a-0a00-0a00-a000-0a0a0000000a{TAB_SPACE}"
                    f"Publication date: {format_datetime(workflow.publication_date, include_time=True)}"
                ),
                call("Version message: Initial Workflow version"),
                call("Version tags: latest"),
                call(""),
            ]
        )

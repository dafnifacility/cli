from datetime import datetime
from unittest import TestCase
from unittest.mock import call, patch

from dateutil.tz import tzutc

from dafni_cli.api.auth import Auth
from dafni_cli.api.parser import ParserBaseObject
from dafni_cli.consts import (
    TABLE_ASSERT_VERSION_ID_HEADER,
    TABLE_STATUS_HEADER,
    TABLE_STEP_NAME_HEADER,
    TABLE_STEP_TYPE_HEADER,
)
from dafni_cli.tests.fixtures.workflow_instance import (
    TEST_WORKFLOW_INSTANCE,
    TEST_WORKFLOW_INSTANCE_LIST,
    TEST_WORKFLOW_INSTANCE_LIST_DEFAULT,
    TEST_WORKFLOW_INSTANCE_LIST_PARAMETER_SET,
    TEST_WORKFLOW_INSTANCE_LIST_WORKFLOW_VERSION,
    TEST_WORKFLOW_INSTANCE_PRODUCED_ASSET,
    TEST_WORKFLOW_INSTANCE_STEP_STATUS,
    TEST_WORKFLOW_INSTANCE_STEP_STATUS_DEFAULT,
    TEST_WORKFLOW_INSTANCE_WORKFLOW_VERSION,
)
from dafni_cli.utils import format_datetime
from dafni_cli.workflows.instance import (
    WorkflowInstance,
    WorkflowInstanceList,
    WorkflowInstanceListParameterSet,
    WorkflowInstanceListWorkflowVersion,
    WorkflowInstanceProducedAsset,
    WorkflowInstanceStepStatus,
    WorkflowInstanceWorkflowVersion,
    parse_workflow_instance,
)
from dafni_cli.workflows.metadata import WorkflowMetadata
from dafni_cli.workflows.parameter_set import WorkflowParameterSet
from dafni_cli.workflows.specification import WorkflowSpecification


class TestWorkflowInstanceListParameterSet(TestCase):
    """Tests the WorkflowInstanceListParameterSet dataclass"""

    def test_parse(self):
        """Tests parsing of WorkflowInstanceListParameterSet"""
        workflow_instance_param_set: WorkflowInstanceListParameterSet = (
            ParserBaseObject.parse_from_dict(
                WorkflowInstanceListParameterSet,
                TEST_WORKFLOW_INSTANCE_LIST_PARAMETER_SET,
            )
        )

        self.assertEqual(
            workflow_instance_param_set.parameter_set_id,
            TEST_WORKFLOW_INSTANCE_LIST_PARAMETER_SET["id"],
        )
        self.assertEqual(
            workflow_instance_param_set.display_name,
            TEST_WORKFLOW_INSTANCE_LIST_PARAMETER_SET["display_name"],
        )


class TestWorkflowInstanceListWorkflowVersion(TestCase):
    """Tests the WorkflowInstanceListWorkflowVersion dataclass"""

    def test_parse(self):
        """Tests parsing of WorkflowInstanceWorkflowVersion"""
        workflow_instance_workflow_version: WorkflowInstanceListWorkflowVersion = (
            ParserBaseObject.parse_from_dict(
                WorkflowInstanceListWorkflowVersion,
                TEST_WORKFLOW_INSTANCE_LIST_WORKFLOW_VERSION,
            )
        )

        self.assertEqual(
            workflow_instance_workflow_version.version_id,
            TEST_WORKFLOW_INSTANCE_LIST_WORKFLOW_VERSION["id"],
        )
        self.assertEqual(
            workflow_instance_workflow_version.version_message,
            TEST_WORKFLOW_INSTANCE_LIST_WORKFLOW_VERSION["version_message"],
        )


class TestWorkflowInstanceList(TestCase):
    """Tests the WorkflowInstanceList dataclass"""

    def test_parse(self):
        """Tests parsing of WorkflowInstance"""
        workflow_instance: WorkflowInstanceList = ParserBaseObject.parse_from_dict(
            WorkflowInstanceList, TEST_WORKFLOW_INSTANCE_LIST
        )

        self.assertEqual(
            workflow_instance.instance_id,
            TEST_WORKFLOW_INSTANCE_LIST["instance_id"],
        )
        self.assertEqual(
            workflow_instance.submission_time,
            datetime(2023, 4, 6, 12, 46, 38, 31244, tzinfo=tzutc()),
        )
        self.assertEqual(
            workflow_instance.overall_status,
            TEST_WORKFLOW_INSTANCE_LIST["overall_status"],
        )

        # WorkflowInstanceListParameterSet (contents tested in TestWorkflowInstanceListParameterSet)
        self.assertEqual(
            type(workflow_instance.parameter_set), WorkflowInstanceListParameterSet
        )

        # WorkflowInstanceWorkflowVersion (contents tested in TestWorkflowInstanceWorkflowVersion)
        self.assertEqual(
            type(workflow_instance.workflow_version),
            WorkflowInstanceListWorkflowVersion,
        )

        self.assertEqual(
            workflow_instance.finished_time,
            datetime(2023, 4, 6, 12, 58, 35, tzinfo=tzutc()),
        )

    def test_parse_default(self):
        """Tests parsing of WorkflowInstance when optional parameters are
        missing"""
        workflow_instance: WorkflowInstanceList = ParserBaseObject.parse_from_dict(
            WorkflowInstanceList, TEST_WORKFLOW_INSTANCE_LIST_DEFAULT
        )

        # Only test the parameters that are supposed to be missing as the
        # rest are tested above anyway
        self.assertEqual(workflow_instance.finished_time, None)

    def test_get_brief_details(self):
        """Tests get_brief_details works correctly"""
        # SETUP
        workflow_instance_list: WorkflowInstanceList = ParserBaseObject.parse_from_dict(
            WorkflowInstanceList, TEST_WORKFLOW_INSTANCE_LIST
        )

        # CALL
        result = workflow_instance_list.get_brief_details()

        # ASSERT
        self.assertEqual(
            result,
            [
                workflow_instance_list.instance_id,
                workflow_instance_list.workflow_version.version_id,
                workflow_instance_list.parameter_set.display_name,
                format_datetime(
                    workflow_instance_list.submission_time, include_time=True
                ),
                format_datetime(
                    workflow_instance_list.finished_time, include_time=True
                ),
                workflow_instance_list.overall_status,
            ],
        )


class TestWorkflowInstanceStepStatus(TestCase):
    """Tests the WorkflowInstanceStepStatus dataclass"""

    def test_parse(self):
        """Tests parsing of WorkflowInstanceStepStatus"""
        workflow_instance_step_status: WorkflowInstanceStepStatus = (
            ParserBaseObject.parse_from_dict(
                WorkflowInstanceStepStatus,
                TEST_WORKFLOW_INSTANCE_STEP_STATUS,
            )
        )

        self.assertEqual(
            workflow_instance_step_status.status,
            TEST_WORKFLOW_INSTANCE_STEP_STATUS["status"],
        )
        self.assertEqual(
            workflow_instance_step_status.started_at,
            datetime(2023, 6, 15, 11, 41, 33, tzinfo=tzutc()),
        )
        self.assertEqual(
            workflow_instance_step_status.finished_at,
            datetime(2023, 6, 15, 11, 41, 43, tzinfo=tzutc()),
        )

    def test_parse_default(self):
        """Tests parsing of WorkflowInstanceStepStatus when all optional
        values are missing"""
        workflow_instance_step_status: WorkflowInstanceStepStatus = (
            ParserBaseObject.parse_from_dict(
                WorkflowInstanceStepStatus,
                TEST_WORKFLOW_INSTANCE_STEP_STATUS_DEFAULT,
            )
        )

        self.assertEqual(
            workflow_instance_step_status.status,
            TEST_WORKFLOW_INSTANCE_STEP_STATUS["status"],
        )
        self.assertEqual(workflow_instance_step_status.started_at, None)
        self.assertEqual(workflow_instance_step_status.finished_at, None)


class TestWorkflowInstanceProducedAsset(TestCase):
    """Tests the WorkflowInstanceProducedAsset dataclass"""

    def test_parse(self):
        """Tests parsing of WorkflowInstanceProducedAsset"""
        workflow_instance_produced_asset: WorkflowInstanceProducedAsset = (
            ParserBaseObject.parse_from_dict(
                WorkflowInstanceProducedAsset,
                TEST_WORKFLOW_INSTANCE_PRODUCED_ASSET,
            )
        )

        self.assertEqual(
            workflow_instance_produced_asset.dataset_id,
            TEST_WORKFLOW_INSTANCE_PRODUCED_ASSET["dataset_id"],
        )
        self.assertEqual(
            workflow_instance_produced_asset.metadata_id,
            TEST_WORKFLOW_INSTANCE_PRODUCED_ASSET["metadata_id"],
        )
        self.assertEqual(
            workflow_instance_produced_asset.version_id,
            TEST_WORKFLOW_INSTANCE_PRODUCED_ASSET["version_id"],
        )
        self.assertEqual(
            workflow_instance_produced_asset.kind,
            TEST_WORKFLOW_INSTANCE_PRODUCED_ASSET["kind"],
        )


class TestWorkflowInstanceWorkflowVersion(TestCase):
    """Tests the WorkflowInstanceWorkflowVersion dataclass"""

    def test_parse(self):
        """Tests parsing of WorkflowInstanceWorkflowVersion"""
        workflow_instance_workflow_version: WorkflowInstanceWorkflowVersion = (
            ParserBaseObject.parse_from_dict(
                WorkflowInstanceWorkflowVersion,
                TEST_WORKFLOW_INSTANCE_WORKFLOW_VERSION,
            )
        )

        self.assertEqual(
            workflow_instance_workflow_version.workflow_id,
            TEST_WORKFLOW_INSTANCE_WORKFLOW_VERSION["id"],
        )

        # WorkflowMetadata (contents tested in TestWorkflowMetadata)
        self.assertEqual(
            type(workflow_instance_workflow_version.metadata), WorkflowMetadata
        )

        self.assertEqual(
            workflow_instance_workflow_version.api_version,
            TEST_WORKFLOW_INSTANCE_WORKFLOW_VERSION["api_version"],
        )
        self.assertEqual(
            workflow_instance_workflow_version.kind,
            TEST_WORKFLOW_INSTANCE_WORKFLOW_VERSION["kind"],
        )
        self.assertEqual(
            workflow_instance_workflow_version.creation_date,
            datetime(2023, 6, 12, 15, 37, 23, 658116, tzinfo=tzutc()),
        )
        self.assertEqual(
            workflow_instance_workflow_version.publication_date,
            datetime(2023, 6, 12, 15, 37, 23, 658116, tzinfo=tzutc()),
        )
        self.assertEqual(
            workflow_instance_workflow_version.owner_id,
            TEST_WORKFLOW_INSTANCE_WORKFLOW_VERSION["owner"],
        )
        self.assertEqual(
            workflow_instance_workflow_version.version_tags,
            TEST_WORKFLOW_INSTANCE_WORKFLOW_VERSION["version_tags"],
        )
        self.assertEqual(
            workflow_instance_workflow_version.version_message,
            TEST_WORKFLOW_INSTANCE_WORKFLOW_VERSION["version_message"],
        )
        self.assertEqual(
            workflow_instance_workflow_version.parent_id,
            TEST_WORKFLOW_INSTANCE_WORKFLOW_VERSION["parent"],
        )

        # WorkflowSpecification (contents tested in TestWorkflowSpecification)
        self.assertEqual(
            type(workflow_instance_workflow_version.spec),
            WorkflowSpecification,
        )


class TestWorkflowInstance(TestCase):
    """Tests the WorkflowInstance dataclass"""

    def test_parse(self):
        """Tests parsing of WorkflowInstance"""
        workflow_instance: WorkflowInstance = parse_workflow_instance(
            TEST_WORKFLOW_INSTANCE,
        )

        # Auth (contents tested in TestAuth)
        self.assertEqual(type(workflow_instance.auth), Auth)

        self.assertEqual(
            workflow_instance.instance_id,
            TEST_WORKFLOW_INSTANCE["instance_id"],
        )
        self.assertEqual(
            workflow_instance.submission_time,
            datetime(2023, 6, 15, 11, 37, 21, 660040, tzinfo=tzutc()),
        )
        self.assertEqual(
            workflow_instance.overall_status,
            TEST_WORKFLOW_INSTANCE["overall_status"],
        )

        # WorkflowInstanceStepStatus (contents tested in TestWorkflowInstanceStepStatus)
        self.assertEqual(
            workflow_instance.step_statuses.keys(),
            TEST_WORKFLOW_INSTANCE["step_status"].keys(),
        )
        for step_status in workflow_instance.step_statuses.values():
            self.assertEqual(type(step_status), WorkflowInstanceStepStatus)

        # WorkflowInstanceProducedAsset (contents tested in TestWorkflowInstanceProducedAsset)
        self.assertEqual(
            workflow_instance.produced_assets.keys(),
            TEST_WORKFLOW_INSTANCE["produced_assets"].keys(),
        )
        for produced_asset in workflow_instance.produced_assets.values():
            self.assertEqual(type(produced_asset), WorkflowInstanceProducedAsset)

        # WorkflowParameterSet (contents tested in TestWorkflowParameterSet)
        self.assertEqual(type(workflow_instance.parameter_set), WorkflowParameterSet)

        # WorkflowInstanceWorkflowVersion (contents tested in TestWorkflowInstanceWorkflowVersion)
        self.assertEqual(
            type(workflow_instance.workflow_version), WorkflowInstanceWorkflowVersion
        )

        self.assertEqual(
            workflow_instance.finished_time,
            datetime(2023, 6, 15, 11, 41, 53, tzinfo=tzutc()),
        )

    @patch("dafni_cli.workflows.instance.format_table")
    def test_format_steps(self, mock_format_table):
        """Tests format_steps works correctly"""

        # SETUP
        workflow_instance = parse_workflow_instance(TEST_WORKFLOW_INSTANCE)

        # CALL
        result = workflow_instance.format_steps()

        # ASSERT
        mock_format_table.assert_called_once_with(
            headers=[
                TABLE_STEP_NAME_HEADER,
                TABLE_STEP_TYPE_HEADER,
                TABLE_ASSERT_VERSION_ID_HEADER,
                TABLE_STATUS_HEADER,
            ],
            rows=[
                [
                    "some-name",
                    "publisher",
                    "0a0a0a0a-0a00-0a00-a000-0a0a0000000d",
                    "Succeeded",
                ],
                ["test", "model", "0a0a0a0a-0a00-0a00-a000-0a0a0000000e", "Succeeded"],
                ["test", "model", "0a0a0a0a-0a00-0a00-a000-0a0a0000000f", "Succeeded"],
                ["test_loop", "loop", "0a0a0a0a-0a00-0a00-a000-0a0a0000000e", "Failed"],
                [
                    "test_loop",
                    "loop",
                    "0a0a0a0a-0a00-0a00-a000-0a0a0000000e",
                    "Succeeded",
                ],
                [
                    "pub-and-vis-1",
                    "visualisation",
                    "0a0a0a0a-0a00-0a00-a000-0a0a0000000d",
                    "Succeeded",
                ],
                ["vis-1", "visualisation", None, "Succeeded"],
            ],
        )
        self.assertEqual(result, mock_format_table.return_value)

    @patch("dafni_cli.workflows.instance.tabulate")
    @patch("dafni_cli.workflows.instance.click")
    @patch.object(WorkflowInstance, "format_steps")
    def test_output_details(self, mock_format_steps, mock_click, mock_tabulate):
        """Tests output_details works correctly"""

        # SETUP
        workflow_instance = parse_workflow_instance(TEST_WORKFLOW_INSTANCE)

        # CALL
        workflow_instance.output_details()

        # ASSERT
        mock_format_steps.assert_called_once()
        self.assertEqual(
            mock_click.echo.mock_calls,
            [
                call(workflow_instance.workflow_version.metadata.display_name),
                call(),
                call(mock_tabulate.return_value),
                call(),
                call(mock_format_steps.return_value),
            ],
        )
        mock_tabulate.assert_called_once_with(
            [
                [
                    "Workflow version ID:",
                    workflow_instance.workflow_version.workflow_id,
                ],
                ["Parameter set ID:", workflow_instance.parameter_set.parameter_set_id],
                [
                    "Started:",
                    format_datetime(
                        workflow_instance.submission_time, include_time=True
                    ),
                ],
                [
                    "Finished:",
                    format_datetime(workflow_instance.finished_time, include_time=True),
                ],
                ["Overall status:", workflow_instance.overall_status],
            ],
            tablefmt="plain",
        )

    @patch("dafni_cli.workflows.instance.tabulate")
    @patch("dafni_cli.workflows.instance.click")
    @patch.object(WorkflowInstance, "format_steps")
    def test_output_details_with_error_messages(
        self, mock_format_steps, mock_click, mock_tabulate
    ):
        """Tests output_details works correctly when there are error messages to display"""

        # SETUP
        workflow_instance = parse_workflow_instance(TEST_WORKFLOW_INSTANCE)
        workflow_instance.workflow_version.spec.errors = [
            "Error message 1",
            "Error message 2",
        ]

        # CALL
        workflow_instance.output_details()

        # ASSERT
        mock_format_steps.assert_called_once()
        self.assertEqual(
            mock_click.echo.mock_calls,
            [
                call(workflow_instance.workflow_version.metadata.display_name),
                call(),
                call("Retrieving full Workflow failed:"),
                call("ERROR: Error message 1"),
                call("ERROR: Error message 2"),
                call(),
                call(mock_tabulate.return_value),
                call(),
                call(mock_format_steps.return_value),
            ],
        )
        mock_tabulate.assert_called_once_with(
            [
                [
                    "Workflow version ID:",
                    workflow_instance.workflow_version.workflow_id,
                ],
                ["Parameter set ID:", workflow_instance.parameter_set.parameter_set_id],
                [
                    "Started:",
                    format_datetime(
                        workflow_instance.submission_time, include_time=True
                    ),
                ],
                [
                    "Finished:",
                    format_datetime(workflow_instance.finished_time, include_time=True),
                ],
                ["Overall status:", workflow_instance.overall_status],
            ],
            tablefmt="plain",
        )

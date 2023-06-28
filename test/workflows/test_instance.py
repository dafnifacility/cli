from datetime import datetime
from unittest import TestCase

from dateutil.tz import tzutc

from dafni_cli.api.parser import ParserBaseObject
from dafni_cli.utils import format_datetime
from dafni_cli.workflows.instance import (
    WorkflowInstance,
    WorkflowInstanceParameterSet,
    WorkflowInstanceWorkflowVersion,
)

TEST_WORKFLOW_INSTANCE_PARAMETER_SET = {
    "id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
    "display_name": "First parameter set",
}

TEST_WORKFLOW_INSTANCE_WORKFLOW_VERSION = {
    "id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000b",
    "version_message": "Initial Workflow version",
}

TEST_WORKFLOW_INSTANCE = {
    "instance_id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000c",
    "submission_time": "2023-04-06T12:46:38.031244Z",
    "overall_status": "Succeeded",
    "parameter_set": TEST_WORKFLOW_INSTANCE_PARAMETER_SET,
    "workflow_version": TEST_WORKFLOW_INSTANCE_WORKFLOW_VERSION,
    "finished_time": "2023-04-06T12:58:35Z",
}

TEST_WORKFLOW_INSTANCE_DEFAULT = {
    "instance_id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000c",
    "submission_time": "2023-04-06T12:46:38.031244Z",
    "overall_status": "Succeeded",
    "parameter_set": TEST_WORKFLOW_INSTANCE_PARAMETER_SET,
    "workflow_version": TEST_WORKFLOW_INSTANCE_WORKFLOW_VERSION,
}


class TestWorkflowInstanceParameterSet(TestCase):
    """Tests the WorkflowInstanceParameterSet dataclass"""

    def test_parse(self):
        """Tests parsing of WorkflowInstanceParameterSet"""
        workflow_instance_param_set: WorkflowInstanceParameterSet = (
            ParserBaseObject.parse_from_dict(
                WorkflowInstanceParameterSet, TEST_WORKFLOW_INSTANCE_PARAMETER_SET
            )
        )

        self.assertEqual(
            workflow_instance_param_set.parameter_set_id,
            TEST_WORKFLOW_INSTANCE_PARAMETER_SET["id"],
        )
        self.assertEqual(
            workflow_instance_param_set.display_name,
            TEST_WORKFLOW_INSTANCE_PARAMETER_SET["display_name"],
        )


class TestWorkflowInstanceWorkflowVersion(TestCase):
    """Tests the WorkflowInstanceWorkflowVersion dataclass"""

    def test_parse(self):
        """Tests parsing of WorkflowInstanceWorkflowVersion"""
        workflow_instance_workflow_version: WorkflowInstanceWorkflowVersion = (
            ParserBaseObject.parse_from_dict(
                WorkflowInstanceWorkflowVersion, TEST_WORKFLOW_INSTANCE_WORKFLOW_VERSION
            )
        )

        self.assertEqual(
            workflow_instance_workflow_version.version_id,
            TEST_WORKFLOW_INSTANCE_WORKFLOW_VERSION["id"],
        )
        self.assertEqual(
            workflow_instance_workflow_version.version_message,
            TEST_WORKFLOW_INSTANCE_WORKFLOW_VERSION["version_message"],
        )


class TestWorkflowInstance(TestCase):
    """Tests the WorkflowInstance dataclass"""

    def test_parse(self):
        """Tests parsing of WorkflowInstance"""
        workflow_instance: WorkflowInstance = ParserBaseObject.parse_from_dict(
            WorkflowInstance, TEST_WORKFLOW_INSTANCE
        )

        self.assertEqual(
            workflow_instance.instance_id,
            TEST_WORKFLOW_INSTANCE["instance_id"],
        )
        self.assertEqual(
            workflow_instance.submission_time,
            datetime(2023, 4, 6, 12, 46, 38, 31244, tzinfo=tzutc()),
        )
        self.assertEqual(
            workflow_instance.overall_status,
            TEST_WORKFLOW_INSTANCE["overall_status"],
        )

        # WorkflowInstanceParameterSet (contents tested in TestWorkflowInstanceParameterSet)
        self.assertEqual(
            type(workflow_instance.parameter_set), WorkflowInstanceParameterSet
        )

        # WorkflowInstanceWorkflowVersion (contents tested in TestWorkflowInstanceWorkflowVersion)
        self.assertEqual(
            type(workflow_instance.workflow_version), WorkflowInstanceWorkflowVersion
        )

        self.assertEqual(
            workflow_instance.finished_time,
            datetime(2023, 4, 6, 12, 58, 35, tzinfo=tzutc()),
        )

    def test_parse_default(self):
        """Tests parsing of WorkflowInstance when optional parameters are
        missing"""
        workflow_instance: WorkflowInstance = ParserBaseObject.parse_from_dict(
            WorkflowInstance, TEST_WORKFLOW_INSTANCE_DEFAULT
        )

        # Only test the parameters that are supposed to be missing as the
        # rest are tested above anyway
        self.assertEqual(workflow_instance.finished_time, None)

    def test_get_brief_details(self):
        """Tests get_brief_details works correctly"""
        # SETUP
        workflow_instance: WorkflowInstance = ParserBaseObject.parse_from_dict(
            WorkflowInstance, TEST_WORKFLOW_INSTANCE
        )

        # CALL
        result = workflow_instance.get_brief_details()

        # ASSERT
        self.assertEqual(
            result,
            [
                workflow_instance.instance_id,
                workflow_instance.workflow_version.version_id,
                workflow_instance.parameter_set.display_name,
                format_datetime(workflow_instance.submission_time, include_time=True),
                format_datetime(workflow_instance.finished_time, include_time=True),
                workflow_instance.overall_status,
            ],
        )

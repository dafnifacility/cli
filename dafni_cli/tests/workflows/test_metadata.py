from unittest import TestCase

from dafni_cli.api.parser import ParserBaseObject
from dafni_cli.tests.fixtures.workflow_metadata import TEST_WORKFLOW_METADATA
from dafni_cli.workflows.metadata import WorkflowMetadata


class TestWorkflowMetadata(TestCase):
    """Tests the WorkflowMetadata dataclass"""

    def test_parse(self):
        """Tests parsing of a workflow using test data for the
        /workflows endpoint"""
        metadata: WorkflowMetadata = ParserBaseObject.parse_from_dict(
            WorkflowMetadata, TEST_WORKFLOW_METADATA
        )

        self.assertEqual(
            metadata.display_name,
            TEST_WORKFLOW_METADATA["display_name"],
        )
        self.assertEqual(metadata.name, TEST_WORKFLOW_METADATA["name"])
        self.assertEqual(metadata.summary, TEST_WORKFLOW_METADATA["summary"])
        self.assertEqual(
            metadata.publisher_id,
            TEST_WORKFLOW_METADATA["publisher"],
        )
        self.assertEqual(metadata.description, TEST_WORKFLOW_METADATA["description"])

from datetime import datetime
from unittest import TestCase

from dateutil.tz import tzutc

from dafni_cli.api.parser import ParserBaseObject
from dafni_cli.workflow.instance import (
    WorkflowInstance,
    WorkflowInstanceParameterSet,
    WorkflowInstanceWorkflowVersion,
)
from dafni_cli.workflow.parameter_set import (
    WorkflowParameterSet,
    WorkflowParameterSetMetadata,
)

TEST_WORKFLOW_PARAMETER_SET_METADATA = {
    "description": "First parameter set",
    "display_name": "First parameter set",
    "name": "first-param-set",
    "publisher": "Joel Davies",
    "workflow_version": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
}

TEST_WORKFLOW_PARAMETER_SET = {
    "id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
    "owner": "0a0a0a0a-0a00-0a00-a000-0a0a0000000b",
    "creation_date": "2023-04-04T08:34:36.823227Z",
    "publication_date": "2023-04-04T08:34:36.823227Z",
    "kind": "P",
    "api_version": "v1.0.0",
    "spec": {
        "0a0a0a0a-0a00-0a00-a000-0a0a0000000c": {
            "kind": "model",
            "dataslots": [
                {
                    "name": "Rainfall data",
                    "path": "inputs/rainfall/",
                    "datasets": ["0a0a0a0a-0a00-0a00-a000-0a0a0000000d"],
                },
                {
                    "name": "Maximum Temperature data",
                    "path": "inputs/maximum-temperature/",
                    "datasets": ["0a0a0a0a-0a00-0a00-a000-0a0a0000000e"],
                },
            ],
            "parameters": [
                {"name": "PROCESS_RAINFALL", "value": True},
                {"name": "PREDICTION_CYCLE", "value": "daily"},
            ],
        }
    },
    "metadata": TEST_WORKFLOW_PARAMETER_SET_METADATA,
}


class TestWorkflowParameterSetMetadata(TestCase):
    """Tests the WorkflowParameterSetMetadata dataclass"""

    def test_parse(self):
        """Tests parsing of WorkflowInstanceParameterSet"""
        workflow_param_set_meta: WorkflowParameterSetMetadata = (
            ParserBaseObject.parse_from_dict(
                WorkflowParameterSetMetadata, TEST_WORKFLOW_PARAMETER_SET_METADATA
            )
        )

        self.assertEqual(
            workflow_param_set_meta.description,
            TEST_WORKFLOW_PARAMETER_SET_METADATA["description"],
        )
        self.assertEqual(
            workflow_param_set_meta.display_name,
            TEST_WORKFLOW_PARAMETER_SET_METADATA["display_name"],
        )
        self.assertEqual(
            workflow_param_set_meta.name,
            TEST_WORKFLOW_PARAMETER_SET_METADATA["name"],
        )
        self.assertEqual(
            workflow_param_set_meta.publisher,
            TEST_WORKFLOW_PARAMETER_SET_METADATA["publisher"],
        )
        self.assertEqual(
            workflow_param_set_meta.workflow_version_id,
            TEST_WORKFLOW_PARAMETER_SET_METADATA["workflow_version"],
        )


class TestWorkflowParameterSet(TestCase):
    """Tests the WorkflowParameterSet dataclass"""

    def test_parse(self):
        """Tests parsing of WorkflowInstanceParameterSet"""
        workflow_param_set: WorkflowParameterSet = ParserBaseObject.parse_from_dict(
            WorkflowParameterSet, TEST_WORKFLOW_PARAMETER_SET
        )

        self.assertEqual(
            workflow_param_set.parameter_set_id,
            TEST_WORKFLOW_PARAMETER_SET["id"],
        )
        self.assertEqual(
            workflow_param_set.owner_id,
            TEST_WORKFLOW_PARAMETER_SET["owner"],
        )
        self.assertEqual(
            workflow_param_set.creation_date,
            datetime(2023, 4, 4, 8, 34, 36, 823227, tzinfo=tzutc()),
        )
        self.assertEqual(
            workflow_param_set.publication_date,
            datetime(2023, 4, 4, 8, 34, 36, 823227, tzinfo=tzutc()),
        )
        self.assertEqual(
            workflow_param_set.kind,
            TEST_WORKFLOW_PARAMETER_SET["kind"],
        )
        self.assertEqual(
            workflow_param_set.api_version,
            TEST_WORKFLOW_PARAMETER_SET["api_version"],
        )
        self.assertEqual(
            workflow_param_set.spec,
            TEST_WORKFLOW_PARAMETER_SET["spec"],
        )
        # WorkflowParameterSetMetadata (contents tested in TestWorkflowParameterSetMetadata)
        self.assertEqual(
            type(workflow_param_set.metadata),
            WorkflowParameterSetMetadata,
        )

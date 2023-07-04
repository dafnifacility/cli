from unittest import TestCase

from dafni_cli.api.parser import ParserBaseObject
from dafni_cli.workflows.specification import (
    WorkflowSpecification,
    WorkflowSpecificationStep,
)

from test.fixtures.workflow_specification import (
    TEST_WORKFLOW_SPECIFICATION,
    TEST_WORKFLOW_SPECIFICATION_STEP,
)


class TestWorkflowSpecificationStep(TestCase):
    """Tests the WorkflowSpecificationStep dataclass"""

    def test_parse(self):
        """Tests parsing of WorkflowSpecificationStep"""
        workflow_specification_step: WorkflowSpecificationStep = (
            ParserBaseObject.parse_from_dict(
                WorkflowSpecificationStep, TEST_WORKFLOW_SPECIFICATION_STEP
            )
        )

        self.assertEqual(
            workflow_specification_step.dependencies,
            TEST_WORKFLOW_SPECIFICATION_STEP["dependencies"],
        )
        self.assertEqual(
            workflow_specification_step.kind,
            TEST_WORKFLOW_SPECIFICATION_STEP["kind"],
        )
        self.assertEqual(
            workflow_specification_step.name,
            TEST_WORKFLOW_SPECIFICATION_STEP["name"],
        )


class TestWorkflowSpecification(TestCase):
    """Tests the WorkflowSpecification dataclass"""

    def test_parse(self):
        """Tests parsing of WorkflowSpecificationStep"""
        workflow_specification: WorkflowSpecification = (
            ParserBaseObject.parse_from_dict(
                WorkflowSpecification, TEST_WORKFLOW_SPECIFICATION
            )
        )

        # WorkflowSpecificationStep (contents tested in TestWorkflowSpecificationStep)
        self.assertEqual(
            workflow_specification.steps.keys(),
            TEST_WORKFLOW_SPECIFICATION["steps"].keys(),
        )
        for step in workflow_specification.steps.values():
            self.assertEqual(type(step), WorkflowSpecificationStep)

from unittest import TestCase

from dafni_cli.api.parser import ParserBaseObject
from dafni_cli.tests.fixtures.workflow_specification import (
    TEST_WORKFLOW_SPECIFICATION,
    TEST_WORKFLOW_SPECIFICATION_DEFAULT,
    TEST_WORKFLOW_SPECIFICATION_STEP,
)
from dafni_cli.workflows.specification import (
    WorkflowSpecification,
    WorkflowSpecificationStep,
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
        self.assertEqual(
            workflow_specification_step.inputs,
            TEST_WORKFLOW_SPECIFICATION_STEP["inputs"],
        )

        self.assertEqual(
            workflow_specification_step.metadata,
            TEST_WORKFLOW_SPECIFICATION_STEP["metadata"],
        )
        self.assertEqual(
            workflow_specification_step.model_version,
            TEST_WORKFLOW_SPECIFICATION_STEP["model_version"],
        )

        self.assertEqual(
            workflow_specification_step.iteration_mode,
            TEST_WORKFLOW_SPECIFICATION_STEP["iteration_mode"],
        )
        self.assertEqual(
            workflow_specification_step.workflow_version,
            TEST_WORKFLOW_SPECIFICATION_STEP["workflow_version"],
        )

    def test_parse_default(self):
        """Tests parsing of WorkflowSpecificationStep when optional parameters
        are missing"""
        workflow_specification_step: WorkflowSpecificationStep = (
            ParserBaseObject.parse_from_dict(
                WorkflowSpecificationStep, TEST_WORKFLOW_SPECIFICATION_DEFAULT
            )
        )

        # Only test the parameters that are supposed to be missing as the
        # rest are tested above anyway
        self.assertEqual(workflow_specification_step.inputs, [])
        self.assertEqual(workflow_specification_step.metadata, None)
        self.assertEqual(workflow_specification_step.model_version, None)
        self.assertEqual(workflow_specification_step.iteration_mode, None)
        self.assertEqual(workflow_specification_step.workflow_version, None)


class TestWorkflowSpecification(TestCase):
    """Tests the WorkflowSpecification dataclass"""

    def test_parse(self):
        """Tests parsing of WorkflowSpecification"""
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

        self.assertEqual(workflow_specification.errors, None)

    def test_parse_with_errors(self):
        """Tests parsing of WorkflowSpecification when errors are defined"""
        test_dict = TEST_WORKFLOW_SPECIFICATION.copy()
        test_dict.update({"errors": ["Some test error"]})

        workflow_specification: WorkflowSpecification = (
            ParserBaseObject.parse_from_dict(WorkflowSpecification, test_dict)
        )

        # WorkflowSpecificationStep (contents tested in TestWorkflowSpecificationStep)
        self.assertEqual(
            workflow_specification.steps.keys(),
            TEST_WORKFLOW_SPECIFICATION["steps"].keys(),
        )
        for step in workflow_specification.steps.values():
            self.assertEqual(type(step), WorkflowSpecificationStep)

        self.assertEqual(workflow_specification.errors, test_dict["errors"])

from datetime import datetime
from unittest import TestCase

from dateutil.tz import tzutc

from dafni_cli.api.parser import ParserBaseObject
from dafni_cli.workflows.parameter_set import (
    WorkflowParameterSet,
    WorkflowParameterSetMetadata,
    WorkflowParameterSetSpecDataslot,
    WorkflowParameterSetSpecParameter,
    WorkflowParameterSetSpecStep,
)

from test.fixtures.workflow_parameter_set import (
    TEST_WORKFLOW_PARAMETER_SET,
    TEST_WORKFLOW_PARAMETER_SET_METADATA,
    TEST_WORKFLOW_PARAMETER_SET_SPEC_DATASLOT_LOOP,
    TEST_WORKFLOW_PARAMETER_SET_SPEC_DATASLOT_MODEL,
    TEST_WORKFLOW_PARAMETER_SET_SPEC_PARAMETER_LOOP,
    TEST_WORKFLOW_PARAMETER_SET_SPEC_PARAMETER_MODEL,
    TEST_WORKFLOW_PARAMETER_SET_SPEC_STEP,
    TEST_WORKFLOW_PARAMETER_SET_SPEC_STEP_DEFAULT,
)


class TestWorkflowParameterSetMetadata(TestCase):
    """Tests the WorkflowParameterSetMetadata dataclass"""

    def test_parse(self):
        """Tests parsing of WorkflowInstanceListParameterSet"""
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


class TestWorkflowParameterSetSpecDataslot(TestCase):
    """Tests the WorkflowParameterSetSpecDataslot dataclass"""

    def test_parse_model(self):
        """Tests parsing of WorkflowParameterSetSpecDataslot using data for a
        model step"""
        dataslot: WorkflowParameterSetSpecDataslot = ParserBaseObject.parse_from_dict(
            WorkflowParameterSetSpecDataslot,
            TEST_WORKFLOW_PARAMETER_SET_SPEC_DATASLOT_MODEL,
        )

        self.assertEqual(
            dataslot.datasets,
            TEST_WORKFLOW_PARAMETER_SET_SPEC_DATASLOT_MODEL["datasets"],
        )
        self.assertEqual(
            dataslot.name,
            TEST_WORKFLOW_PARAMETER_SET_SPEC_DATASLOT_MODEL["name"],
        )
        self.assertEqual(
            dataslot.path,
            TEST_WORKFLOW_PARAMETER_SET_SPEC_DATASLOT_MODEL["path"],
        )

    def test_parse_loop(self):
        """Tests parsing of WorkflowParameterSetSpecDataslot using data for a
        loop step"""
        dataslot: WorkflowParameterSetSpecDataslot = ParserBaseObject.parse_from_dict(
            WorkflowParameterSetSpecDataslot,
            TEST_WORKFLOW_PARAMETER_SET_SPEC_DATASLOT_LOOP,
        )

        self.assertEqual(
            dataslot.datasets,
            TEST_WORKFLOW_PARAMETER_SET_SPEC_DATASLOT_LOOP["datasets"],
        )
        self.assertEqual(
            dataslot.steps,
            TEST_WORKFLOW_PARAMETER_SET_SPEC_DATASLOT_LOOP["steps"],
        )
        self.assertEqual(
            dataslot.dataslot,
            TEST_WORKFLOW_PARAMETER_SET_SPEC_DATASLOT_LOOP["dataslot"],
        )


class TestWorkflowParameterSetSpecParameter(TestCase):
    """Tests the WorkflowParameterSetSpecParameter dataclass"""

    def test_parse_model(self):
        """Tests parsing of WorkflowParameterSetSpecParameter using data for a
        model step"""
        parameter: WorkflowParameterSetSpecParameter = ParserBaseObject.parse_from_dict(
            WorkflowParameterSetSpecParameter,
            TEST_WORKFLOW_PARAMETER_SET_SPEC_PARAMETER_MODEL,
        )

        self.assertEqual(
            parameter.name,
            TEST_WORKFLOW_PARAMETER_SET_SPEC_PARAMETER_MODEL["name"],
        )
        self.assertEqual(
            parameter.value,
            TEST_WORKFLOW_PARAMETER_SET_SPEC_PARAMETER_MODEL["value"],
        )

    def test_parse_loop(self):
        """Tests parsing of WorkflowParameterSetSpecParameter using data for a
        loop step"""
        parameter: WorkflowParameterSetSpecParameter = ParserBaseObject.parse_from_dict(
            WorkflowParameterSetSpecParameter,
            TEST_WORKFLOW_PARAMETER_SET_SPEC_PARAMETER_LOOP,
        )

        self.assertEqual(
            parameter.steps,
            TEST_WORKFLOW_PARAMETER_SET_SPEC_PARAMETER_LOOP["steps"],
        )
        self.assertEqual(
            parameter.values,
            TEST_WORKFLOW_PARAMETER_SET_SPEC_PARAMETER_LOOP["values"],
        )
        self.assertEqual(
            parameter.parameter,
            TEST_WORKFLOW_PARAMETER_SET_SPEC_PARAMETER_LOOP["parameter"],
        )
        self.assertEqual(
            parameter.calculate_values,
            TEST_WORKFLOW_PARAMETER_SET_SPEC_PARAMETER_LOOP["calculate_values"],
        )


class TestWorkflowParameterSetSpecStep(TestCase):
    """Tests the WorkflowParameterSetSpecStep dataclass"""

    def test_parse(self):
        """Tests parsing of WorkflowInstanceListParameterSet"""
        spec: WorkflowParameterSetSpecStep = ParserBaseObject.parse_from_dict(
            WorkflowParameterSetSpecStep, TEST_WORKFLOW_PARAMETER_SET_SPEC_STEP
        )

        # WorkflowParameterSetSpecDataslot (contents tested in TestWorkflowParameterSetSpecDataslot)
        self.assertEqual(len(spec.dataslots), 2)
        for dataslot in spec.dataslots:
            self.assertEqual(type(dataslot), WorkflowParameterSetSpecDataslot)

        self.assertEqual(
            spec.kind,
            TEST_WORKFLOW_PARAMETER_SET_SPEC_STEP["kind"],
        )

        # WorkflowParameterSetSpecParameter (contents tested in TestWorkflowParameterSetSpecParameter)
        self.assertEqual(len(spec.parameters), 2)
        for parameter in spec.parameters:
            self.assertEqual(type(parameter), WorkflowParameterSetSpecParameter)

        self.assertEqual(
            spec.base_parameter_set,
            TEST_WORKFLOW_PARAMETER_SET_SPEC_STEP["base_parameter_set"],
        )

    def test_parse_default(self):
        """Tests parsing of WorkflowInstanceListParameterSet when all optional
        values are missing"""
        spec: WorkflowParameterSetSpecStep = ParserBaseObject.parse_from_dict(
            WorkflowParameterSetSpecStep, TEST_WORKFLOW_PARAMETER_SET_SPEC_STEP_DEFAULT
        )

        # Only test the parameters that are supposed to be missing as the
        # rest are tested above anyway
        self.assertEqual(spec.base_parameter_set, None)


class TestWorkflowParameterSet(TestCase):
    """Tests the WorkflowParameterSet dataclass"""

    def test_parse(self):
        """Tests parsing of WorkflowInstanceListParameterSet"""
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

        # WorkflowParameterSetSpecStep (contents tested in TestWorkflowParameterSetSpecStep)
        self.assertEqual(
            workflow_param_set.spec.keys(),
            TEST_WORKFLOW_PARAMETER_SET["spec"].keys(),
        )
        for step in workflow_param_set.spec.values():
            self.assertEqual(type(step), WorkflowParameterSetSpecStep)

        # WorkflowParameterSetMetadata (contents tested in TestWorkflowParameterSetMetadata)
        self.assertEqual(
            type(workflow_param_set.metadata),
            WorkflowParameterSetMetadata,
        )

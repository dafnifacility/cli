from datetime import datetime
from unittest import TestCase
from unittest.mock import call, patch

from dateutil.tz import tzutc

from dafni_cli.api.parser import ParserBaseObject
from dafni_cli.consts import (
    CONSOLE_WIDTH,
    TABLE_DATASET_VERSION_IDS_HEADER,
    TABLE_GENERATE_VALUES_HEADER,
    TABLE_NAME_HEADER,
    TABLE_PARAMETER_HEADER,
    TABLE_PATH_TO_DATA_HEADER,
    TABLE_STEPS_THAT_CONTAIN_DATASLOT_HEADER,
    TABLE_STEPS_THAT_CONTAIN_PARAMETER_HEADER,
    TABLE_VALUE_HEADER,
    TABLE_VALUES_HEADER,
)
from dafni_cli.tests.fixtures.workflow_parameter_set import (
    TEST_WORKFLOW_PARAMETER_SET,
    TEST_WORKFLOW_PARAMETER_SET_METADATA,
    TEST_WORKFLOW_PARAMETER_SET_SPEC_DATASLOT_LOOP,
    TEST_WORKFLOW_PARAMETER_SET_SPEC_DATASLOT_MODEL,
    TEST_WORKFLOW_PARAMETER_SET_SPEC_PARAMETER_LOOP,
    TEST_WORKFLOW_PARAMETER_SET_SPEC_PARAMETER_MODEL,
    TEST_WORKFLOW_PARAMETER_SET_SPEC_STEP_DEFAULT,
    TEST_WORKFLOW_PARAMETER_SET_SPEC_STEP_LOOP,
    TEST_WORKFLOW_PARAMETER_SET_SPEC_STEP_MODEL,
)
from dafni_cli.tests.fixtures.workflow_specification import TEST_WORKFLOW_SPECIFICATION
from dafni_cli.workflows.parameter_set import (
    WorkflowParameterSet,
    WorkflowParameterSetMetadata,
    WorkflowParameterSetSpecDataslot,
    WorkflowParameterSetSpecParameter,
    WorkflowParameterSetSpecStep,
)
from dafni_cli.workflows.specification import WorkflowSpecification


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
            WorkflowParameterSetSpecStep, TEST_WORKFLOW_PARAMETER_SET_SPEC_STEP_MODEL
        )

        # WorkflowParameterSetSpecDataslot (contents tested in TestWorkflowParameterSetSpecDataslot)
        self.assertEqual(len(spec.dataslots), 2)
        for dataslot in spec.dataslots:
            self.assertEqual(type(dataslot), WorkflowParameterSetSpecDataslot)

        self.assertEqual(
            spec.kind,
            TEST_WORKFLOW_PARAMETER_SET_SPEC_STEP_MODEL["kind"],
        )

        # WorkflowParameterSetSpecParameter (contents tested in TestWorkflowParameterSetSpecParameter)
        self.assertEqual(len(spec.parameters), 2)
        for parameter in spec.parameters:
            self.assertEqual(type(parameter), WorkflowParameterSetSpecParameter)

        self.assertEqual(
            spec.base_parameter_set,
            TEST_WORKFLOW_PARAMETER_SET_SPEC_STEP_MODEL["base_parameter_set"],
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

    def test_format_parameters_no_parameters(self):
        """Tests format_parameters works correctly when there are no parameters"""

        # SETUP
        spec: WorkflowParameterSetSpecStep = ParserBaseObject.parse_from_dict(
            WorkflowParameterSetSpecStep, TEST_WORKFLOW_PARAMETER_SET_SPEC_STEP_MODEL
        )
        spec.parameters = []

        # CALL
        result = spec.format_parameters()

        # ASSERT
        self.assertEqual(result, "No parameters")

    @patch("dafni_cli.workflows.parameter_set.format_table")
    def test_format_parameters_model(self, mock_format_table):
        """Tests format_parameters works correctly for a model step"""
        spec: WorkflowParameterSetSpecStep = ParserBaseObject.parse_from_dict(
            WorkflowParameterSetSpecStep, TEST_WORKFLOW_PARAMETER_SET_SPEC_STEP_MODEL
        )

        # CALL
        result = spec.format_parameters()

        # ASSERT
        mock_format_table.assert_called_once_with(
            headers=[TABLE_PARAMETER_HEADER, TABLE_VALUE_HEADER],
            rows=[["PROCESS_RAINFALL", True], ["PREDICTION_CYCLE", "daily"]],
        )
        self.assertEqual(result, mock_format_table.return_value)

    @patch("dafni_cli.workflows.parameter_set.format_table")
    def test_format_parameters_loop(self, mock_format_table):
        """Tests format_parameters works correctly for a loop step"""
        spec: WorkflowParameterSetSpecStep = ParserBaseObject.parse_from_dict(
            WorkflowParameterSetSpecStep, TEST_WORKFLOW_PARAMETER_SET_SPEC_STEP_LOOP
        )
        spec.kind = "loop"

        # CALL
        result = spec.format_parameters()

        # ASSERT
        mock_format_table.assert_called_once_with(
            headers=[
                TABLE_NAME_HEADER,
                TABLE_STEPS_THAT_CONTAIN_PARAMETER_HEADER,
                TABLE_GENERATE_VALUES_HEADER,
                TABLE_VALUES_HEADER,
            ],
            rows=[
                [
                    "BATCH_FILENAME",
                    "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
                    False,
                    "some_file.csv",
                ],
                [
                    "SEQUENCE_LENGTH",
                    "0a0a0a0a-0a00-0a00-a000-0a0a0000000b\n0a0a0a0a-0a00-0a00-a000-0a0a0000000c",
                    False,
                    "10\n20\n30\n40",
                ],
            ],
        )
        self.assertEqual(result, mock_format_table.return_value)

    def test_format_dataslots_no_dataslots(self):
        """Tests format_dataslots works correctly when there are no dataslots"""

        # SETUP
        spec: WorkflowParameterSetSpecStep = ParserBaseObject.parse_from_dict(
            WorkflowParameterSetSpecStep, TEST_WORKFLOW_PARAMETER_SET_SPEC_STEP_MODEL
        )
        spec.dataslots = []

        # CALL
        result = spec.format_dataslots()

        # ASSERT
        self.assertEqual(result, "No dataslots")

    @patch("dafni_cli.workflows.parameter_set.format_table")
    def test_format_dataslots_model(self, mock_format_table):
        """Tests format_dataslots works correctly for a model step"""
        spec: WorkflowParameterSetSpecStep = ParserBaseObject.parse_from_dict(
            WorkflowParameterSetSpecStep, TEST_WORKFLOW_PARAMETER_SET_SPEC_STEP_MODEL
        )

        # CALL
        result = spec.format_dataslots()

        # ASSERT
        mock_format_table.assert_called_once_with(
            headers=[
                TABLE_NAME_HEADER,
                TABLE_PATH_TO_DATA_HEADER,
                TABLE_DATASET_VERSION_IDS_HEADER,
            ],
            rows=[
                [
                    "Rainfall data",
                    "inputs/rainfall/",
                    "0a0a0a0a-0a00-0a00-a000-0a0a0000000d",
                ],
                [
                    "Maximum Temperature data",
                    "inputs/maximum-temperature/",
                    "0a0a0a0a-0a00-0a00-a000-0a0a0000000e",
                ],
            ],
        )
        self.assertEqual(result, mock_format_table.return_value)

    @patch("dafni_cli.workflows.parameter_set.format_table")
    def test_format_dataslots_loop(self, mock_format_table):
        """Tests format_dataslots works correctly for a loop step"""
        spec: WorkflowParameterSetSpecStep = ParserBaseObject.parse_from_dict(
            WorkflowParameterSetSpecStep, TEST_WORKFLOW_PARAMETER_SET_SPEC_STEP_LOOP
        )

        # CALL
        result = spec.format_dataslots()

        # ASSERT
        mock_format_table.assert_called_once_with(
            headers=[
                TABLE_NAME_HEADER,
                TABLE_STEPS_THAT_CONTAIN_DATASLOT_HEADER,
                TABLE_DATASET_VERSION_IDS_HEADER,
            ],
            rows=[
                [
                    "Data",
                    "0a0a0a0a-0a00-0a00-a000-0a0a0000000d",
                    "Iteration - 0: 0a0a0a0a-0a00-0a00-a000-0a0a0000000a\n0a0a0a0a-0a00-0a00-a000-0a0a0000000b\nIteration - 1: 0a0a0a0a-0a00-0a00-a000-0a0a0000000c",
                ],
                [
                    "AnotherSlot",
                    "0a0a0a0a-0a00-0a00-a000-0a0a0000000e\n0a0a0a0a-0a00-0a00-a000-0a0a0000001b",
                    "Iteration - 0: 0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
                ],
            ],
        )
        self.assertEqual(result, mock_format_table.return_value)


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

    @patch("dafni_cli.workflows.parameter_set.click")
    @patch("dafni_cli.workflows.parameter_set.tabulate")
    def test_output_details(self, mock_tabulate, mock_click):
        """Tests output_details works correctly"""

        # SETUP
        workflow_param_set: WorkflowParameterSet = ParserBaseObject.parse_from_dict(
            WorkflowParameterSet, TEST_WORKFLOW_PARAMETER_SET
        )

        workflow_spec: WorkflowSpecification = ParserBaseObject.parse_from_dict(
            WorkflowSpecification, TEST_WORKFLOW_SPECIFICATION
        )

        # To test all branches need one model step with extra inputs and one
        # without

        # Steps as found in the workflow spec (1 and 2 are identical
        # except in WorkflowSpecification)
        workflow_step1 = list(workflow_param_set.spec.values())[0]
        workflow_spec_step1 = workflow_spec.steps[
            list(workflow_param_set.spec.keys())[0]
        ]
        workflow_spec_step2 = workflow_spec.steps[
            list(workflow_param_set.spec.keys())[1]
        ]
        workflow_step3 = list(workflow_param_set.spec.values())[2]
        workflow_step4 = list(workflow_param_set.spec.values())[3]
        workflow_spec_step3 = workflow_spec.steps[
            list(workflow_param_set.spec.keys())[2]
        ]
        workflow_spec_step4 = workflow_spec.steps[
            list(workflow_param_set.spec.keys())[3]
        ]

        # CALL
        workflow_param_set.output_details(workflow_spec)

        # ASSERT
        mock_click.echo.assert_has_calls(
            [
                call(workflow_param_set.metadata.display_name),
                call(),
                # First step
                call("-" * CONSOLE_WIDTH),
                call(f"Step - {workflow_spec_step1.name}"),
                call(),
                call(f"Model version ID: {workflow_spec_step1.model_version}"),
                call(),
                call(workflow_step1.format_parameters()),
                call(),
                call("Steps data included from: test"),
                call(workflow_step1.format_dataslots()),
                call(),
                # Second step (Same as first but doesn't have any 'inputs')
                call("-" * CONSOLE_WIDTH),
                call(f"Step - {workflow_spec_step2.name}"),
                call(),
                call(f"Model version ID: {workflow_spec_step2.model_version}"),
                call(),
                call(workflow_step1.format_parameters()),
                call(),
                call("Steps data included from: No data included from previous steps"),
                call(workflow_step1.format_dataslots()),
                call(),
                # Third step
                call("-" * CONSOLE_WIDTH),
                call(f"Step - {workflow_spec_step3.name}"),
                call(),
                call(mock_tabulate.return_value),
                call(),
                call("Parameters to iterate:"),
                call(workflow_step3.format_parameters()),
                call(),
                call("Dataslots to iterate:"),
                call(workflow_step3.format_dataslots()),
                call(),
                # Fourth step
                call("-" * CONSOLE_WIDTH),
                call(f"Step - {workflow_spec_step4.name}"),
                call(),
                call(mock_tabulate.return_value),
                call(),
                call("Parameters to iterate:"),
                call(workflow_step4.format_parameters()),
                call(),
                call("Dataslots to iterate:"),
                call(workflow_step4.format_dataslots()),
                call(),
            ]
        )

        mock_tabulate.assert_has_calls(
            [
                call(
                    [
                        [
                            "Looping workflow version ID:",
                            workflow_spec_step3.workflow_version,
                        ],
                        ["Iteration mode:", workflow_spec_step3.iteration_mode],
                        ["Base parameter set ID:", workflow_step3.base_parameter_set],
                    ],
                    tablefmt="plain",
                ),
                call(
                    [
                        [
                            "Looping workflow version ID:",
                            workflow_spec_step4.workflow_version,
                        ],
                        ["Iteration mode:", workflow_spec_step4.iteration_mode],
                        [
                            "Base parameter set ID:",
                            "No base parameter set",
                        ],
                    ],
                    tablefmt="plain",
                ),
            ]
        )

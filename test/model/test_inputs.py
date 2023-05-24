import copy
from unittest import TestCase
from unittest.mock import patch

from dafni_cli.api.parser import ParserBaseObject
from dafni_cli.consts import (
    INPUT_DEFAULT_HEADER,
    INPUT_DESCRIPTION_HEADER,
    INPUT_DESCRIPTION_MAX_COLUMN_WIDTH,
    INPUT_MAX_HEADER,
    INPUT_MIN_HEADER,
    INPUT_NAME_HEADER,
    INPUT_REQUIRED_HEADER,
    INPUT_TITLE_HEADER,
    INPUT_TYPE_HEADER,
    TAB_SPACE,
)
from dafni_cli.model.inputs import ModelDataslot, ModelInputs, ModelParameter

from test.fixtures.model_inputs import (
    TEST_MODEL_INPUT_DATASLOT,
    TEST_MODEL_INPUT_PARAMETER,
    TEST_MODEL_INPUTS,
    TEST_MODEL_INPUTS_DEFAULT,
)


class TestModelDataslot(TestCase):
    """Tests the ModelDataslot dataclass"""

    def test_parse(self):
        """Tests parsing of ModelDataslot"""
        model_input_dataslot: ModelDataslot = ParserBaseObject.parse_from_dict(
            ModelDataslot, TEST_MODEL_INPUT_DATASLOT
        )

        self.assertEqual(model_input_dataslot.name, TEST_MODEL_INPUT_DATASLOT["name"])
        self.assertEqual(model_input_dataslot.path, TEST_MODEL_INPUT_DATASLOT["path"])
        self.assertEqual(
            model_input_dataslot.defaults, TEST_MODEL_INPUT_DATASLOT["default"]
        )
        self.assertEqual(
            model_input_dataslot.required, TEST_MODEL_INPUT_DATASLOT["required"]
        )
        self.assertEqual(model_input_dataslot.description, None)


class TestModelParameter(TestCase):
    """Tests the ModelParameter dataclass"""

    def test_parse(self):
        """Tests parsing of ModelParameter"""
        model_input_param: ModelParameter = ParserBaseObject.parse_from_dict(
            ModelParameter, TEST_MODEL_INPUT_PARAMETER
        )

        self.assertEqual(model_input_param.name, TEST_MODEL_INPUT_PARAMETER["name"])
        self.assertEqual(model_input_param.type, TEST_MODEL_INPUT_PARAMETER["type"])
        self.assertEqual(model_input_param.title, TEST_MODEL_INPUT_PARAMETER["title"])
        self.assertEqual(
            model_input_param.required, TEST_MODEL_INPUT_PARAMETER["required"]
        )
        self.assertEqual(
            model_input_param.description, TEST_MODEL_INPUT_PARAMETER["description"]
        )
        self.assertEqual(
            model_input_param.default, TEST_MODEL_INPUT_PARAMETER["default"]
        )
        self.assertEqual(model_input_param.min, TEST_MODEL_INPUT_PARAMETER["min"])
        self.assertEqual(model_input_param.max, TEST_MODEL_INPUT_PARAMETER["max"])


class TestInputs(TestCase):
    """Tests the ModelInputs dataclass"""

    def test_parse(self):
        """Tests parsing of ModelInputs"""
        model_inputs: ModelInputs = ParserBaseObject.parse_from_dict(
            ModelInputs, TEST_MODEL_INPUTS
        )

        # ModelParameters (contents tested in TestModelParameters)
        self.assertEqual(len(model_inputs.parameters), 1)
        for parameter in model_inputs.parameters:
            self.assertEqual(type(parameter), ModelParameter)

        # ModelDataslots (contents tested in TestModelDataslots)
        self.assertEqual(len(model_inputs.dataslots), 1)
        for dataslot in model_inputs.dataslots:
            self.assertEqual(type(dataslot), ModelDataslot)

    def test_parse_default(self):
        """Tests parsing of ModelInputs when all optional values excluded"""
        model_inputs: ModelInputs = ParserBaseObject.parse_from_dict(
            ModelInputs, TEST_MODEL_INPUTS_DEFAULT
        )

        # ModelParameters (contents tested in TestModelParameters)
        self.assertEqual(len(model_inputs.parameters), 1)
        for parameter in model_inputs.parameters:
            self.assertEqual(type(parameter), ModelParameter)

        # ModelDataslots (contents tested in TestModelDataslots)
        self.assertEqual(model_inputs.dataslots, [])

    @patch("dafni_cli.model.inputs.format_table")
    def test_format_parameters(
        self,
        mock_format_table,
    ):
        """Tests format_parameters works correctly"""
        # SETUP
        model_inputs: ModelInputs = ParserBaseObject.parse_from_dict(
            ModelInputs, TEST_MODEL_INPUTS_DEFAULT
        )

        # Two identical parameters but one required and one not
        model_inputs.parameters = [
            model_inputs.parameters[0],
            copy.deepcopy(model_inputs.parameters[0]),
        ]
        model_inputs.parameters[0].required = True
        model_inputs.parameters[1].required = False

        # CALL
        result = model_inputs.format_parameters()

        # ASSERT
        mock_format_table.assert_called_once_with(
            headers=[
                INPUT_TITLE_HEADER,
                INPUT_DESCRIPTION_HEADER,
                INPUT_NAME_HEADER,
                INPUT_TYPE_HEADER,
                INPUT_MIN_HEADER,
                INPUT_MAX_HEADER,
                INPUT_DEFAULT_HEADER,
                INPUT_REQUIRED_HEADER,
            ],
            rows=[
                [
                    "Year input",
                    "Year input description",
                    "YEAR",
                    "integer",
                    2016,
                    2025,
                    2018,
                    "Yes",
                ],
                [
                    "Year input",
                    "Year input description",
                    "YEAR",
                    "integer",
                    2016,
                    2025,
                    2018,
                    "No",
                ],
            ],
            max_column_widths=[
                None,
                INPUT_DESCRIPTION_MAX_COLUMN_WIDTH,
                None,
                None,
                None,
                None,
                None,
                None,
            ],
        )
        self.assertEqual(result, mock_format_table.return_value)

    def test_dataslots_string_is_formatted_properly_if_it_exists(self):
        """Tests format_dataslots works correctly"""
        # SETUP
        model_inputs: ModelInputs = ParserBaseObject.parse_from_dict(
            ModelInputs, TEST_MODEL_INPUTS
        )
        # Expected output
        expected = (
            "Name: Inputs\n"
            + "Path in container: inputs/\n"
            + "Required: True\n"
            + "Default Datasets: \n"
            + "ID: 0a0a0a0a-0a00-0a00-a000-0a0a0000000f"
            + TAB_SPACE
            + "\n"
        )

        # CALL
        dataslot_string = model_inputs.format_dataslots()

        # ASSERT
        self.assertEqual(dataslot_string, expected)

    def test_none_returned_if_there_are_no_dataslots(self):
        """Tests format_dataslots works correctly when there are no dataslots"""
        # SETUP
        model_inputs: ModelInputs = ParserBaseObject.parse_from_dict(
            ModelInputs, TEST_MODEL_INPUTS_DEFAULT
        )

        # CALL
        dataslot_string = model_inputs.format_dataslots()

        # ASSERT
        self.assertEqual(dataslot_string, None)

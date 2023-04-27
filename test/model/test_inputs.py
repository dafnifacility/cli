from unittest import TestCase
from unittest.mock import patch

from dafni_cli.api.parser import ParserBaseObject
from dafni_cli.consts import (
    INPUT_DEFAULT_HEADER,
    INPUT_DESCRIPTION_HEADER,
    INPUT_DESCRIPTION_LINE_WIDTH,
    INPUT_MAX_HEADER,
    INPUT_MIN_HEADER,
    INPUT_MIN_MAX_COLUMN_WIDTH,
    INPUT_TITLE_HEADER,
    INPUT_TYPE_COLUMN_WIDTH,
    INPUT_TYPE_HEADER,
    TAB_SPACE,
)
from dafni_cli.model.inputs import ModelDataslot, ModelInputs, ModelParameter

TEST_MODEL_INPUT_DATASLOT: dict = {
    "name": "Inputs",
    "path": "inputs/",
    "default": ["0a0a0a0a-0a00-0a00-a000-0a0a0000000f"],
    "required": True,
}

TEST_MODEL_INPUT_PARAMETER: dict = {
    "max": 2025,
    "min": 2016,
    "name": "YEAR",
    "type": "integer",
    "title": "Year input",
    "default": 2018,
    "required": True,
    "description": "Year input description",
}

TEST_MODEL_INPUTS: dict = {
    "dataslots": [TEST_MODEL_INPUT_DATASLOT],
    "parameters": [
        TEST_MODEL_INPUT_PARAMETER,
    ],
}

TEST_MODEL_INPUTS_DEFAULT: dict = {
    "parameters": [
        {
            "max": 2025,
            "min": 2016,
            "name": "YEAR",
            "type": "integer",
            "title": "Year input",
            "default": 2018,
            "required": True,
            "description": "Year input description",
        },
    ],
}

TEST_MODEL_OUTPUTS: dict = {
    "datasets": [
        {
            "name": "example_dataset.csv",
            "type": "CSV",
            "description": "",
        },
    ]
}


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

    def test_header_row_is_formatted_properly(self):
        """Tests params_table_header works as expected"""
        # SETUP
        title_column_width = 10
        default_column_width = 10
        # Expected headings string
        expected = (
            INPUT_TITLE_HEADER
            + " " * (title_column_width - len(INPUT_TITLE_HEADER))
            + INPUT_TYPE_HEADER
            + " " * (INPUT_TYPE_COLUMN_WIDTH - len(INPUT_TYPE_HEADER))
            + INPUT_MIN_HEADER
            + " " * (INPUT_MIN_MAX_COLUMN_WIDTH - len(INPUT_MIN_HEADER))
            + INPUT_MAX_HEADER
            + " " * (INPUT_MIN_MAX_COLUMN_WIDTH - len(INPUT_MAX_HEADER))
            + INPUT_DEFAULT_HEADER
            + " " * (default_column_width - len(INPUT_DEFAULT_HEADER))
            + INPUT_DESCRIPTION_HEADER
        )

        # CALL
        header_string = ModelInputs.params_table_header(
            title_column_width, default_column_width
        )

        # ASSERT
        self.assertEqual(header_string.split("\n")[0], expected)

    def test_dashed_line_is_of_expected_length(self):
        """Tests params_table_header produces a dashed line of the expected
        length"""
        # SETUP
        title_column_width = 10
        default_column_width = 10
        # Expected headings string
        expected = "-" * (
            title_column_width
            + INPUT_TYPE_COLUMN_WIDTH
            + 2 * INPUT_MIN_MAX_COLUMN_WIDTH
            + default_column_width
            + INPUT_DESCRIPTION_LINE_WIDTH
        )

        # CALL
        header_string = ModelInputs.params_table_header(
            title_column_width, default_column_width
        )

        # ASSERT
        self.assertEqual(header_string.split("\n")[1], expected)

    @patch.object(ModelInputs, "params_table_header")
    @patch("dafni_cli.model.inputs.optional_column")
    def test_parameters_table_is_formatted_properly(self, mock_column, mock_header):
        """Tests format_parameters works correctly"""
        # SETUP
        model_inputs: ModelInputs = ParserBaseObject.parse_from_dict(
            ModelInputs, TEST_MODEL_INPUTS_DEFAULT
        )

        # Ignore table header
        mock_header.return_value = ""
        # Setup optional column return values
        optional_column_outputs = [
            "0.1" + " " * (INPUT_MIN_MAX_COLUMN_WIDTH - 3),
            "2.0" + " " * (INPUT_MIN_MAX_COLUMN_WIDTH - 3),
            "1.5" + " " * 16,
            " " * INPUT_MIN_MAX_COLUMN_WIDTH,
            " " * INPUT_MIN_MAX_COLUMN_WIDTH,
            "long_default_name" + " " * 2,
        ]
        mock_column.side_effect = optional_column_outputs
        # Expected table
        expected_table = (
            "Year input"
            + " " * 2
            + "integer"
            + " " * (INPUT_TYPE_COLUMN_WIDTH - 7)
            + optional_column_outputs[0]
            + optional_column_outputs[1]
            + optional_column_outputs[2]
            + "Year input description\n"
        )
        # CALL
        table_string = model_inputs.format_parameters()

        # ASSERT
        self.assertEqual(expected_table, table_string)

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

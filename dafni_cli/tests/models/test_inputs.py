import copy
from unittest import TestCase
from unittest.mock import patch

from dafni_cli.api.parser import ParserBaseObject
from dafni_cli.consts import (
    TABLE_DEFAULT_DATASETS_HEADER,
    TABLE_DEFAULT_HEADER,
    TABLE_DESCRIPTION_HEADER,
    TABLE_DESCRIPTION_MAX_COLUMN_WIDTH,
    TABLE_MAX_HEADER,
    TABLE_MIN_HEADER,
    TABLE_NAME_HEADER,
    TABLE_PATH_IN_CONTAINER_HEADER,
    TABLE_REQUIRED_HEADER,
    TABLE_TITLE_HEADER,
    TABLE_TYPE_HEADER,
)
from dafni_cli.models.inputs import ModelDataslot, ModelInputs, ModelParameter
from dafni_cli.tests.fixtures.model_inputs import (
    TEST_MODEL_INPUT_DATASLOT,
    TEST_MODEL_INPUT_DATASLOT_DEFAULT,
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
            model_input_dataslot.required, TEST_MODEL_INPUT_DATASLOT["required"]
        )
        self.assertEqual(
            model_input_dataslot.defaults, TEST_MODEL_INPUT_DATASLOT["default"]
        )
        self.assertEqual(
            model_input_dataslot.description, TEST_MODEL_INPUT_DATASLOT["description"]
        )

    def test_parse_default(self):
        """Tests parsing of ModelDataslot when all optional values are
        excluded"""
        model_input_dataslot: ModelDataslot = ParserBaseObject.parse_from_dict(
            ModelDataslot, TEST_MODEL_INPUT_DATASLOT_DEFAULT
        )

        self.assertEqual(model_input_dataslot.name, TEST_MODEL_INPUT_DATASLOT["name"])
        self.assertEqual(model_input_dataslot.path, TEST_MODEL_INPUT_DATASLOT["path"])
        self.assertEqual(
            model_input_dataslot.required, TEST_MODEL_INPUT_DATASLOT["required"]
        )
        self.assertEqual(model_input_dataslot.defaults, [])
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
        """Tests parsing of ModelInputs when all optional values are
        excluded"""
        model_inputs: ModelInputs = ParserBaseObject.parse_from_dict(
            ModelInputs, TEST_MODEL_INPUTS_DEFAULT
        )

        # ModelParameters (contents tested in TestModelParameters)
        self.assertEqual(len(model_inputs.parameters), 1)
        for parameter in model_inputs.parameters:
            self.assertEqual(type(parameter), ModelParameter)

        # ModelDataslots (contents tested in TestModelDataslots)
        self.assertEqual(model_inputs.dataslots, [])

    @patch("dafni_cli.models.inputs.format_table")
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
        model_inputs.parameters[0].name = "YEAR"
        model_inputs.parameters[1].required = False
        model_inputs.parameters[1].name = "ANOTHER_YEAR"

        # CALL
        result = model_inputs.format_parameters()

        # ASSERT
        mock_format_table.assert_called_once_with(
            headers=[
                TABLE_TITLE_HEADER,
                TABLE_DESCRIPTION_HEADER,
                TABLE_NAME_HEADER,
                TABLE_TYPE_HEADER,
                TABLE_MIN_HEADER,
                TABLE_MAX_HEADER,
                TABLE_DEFAULT_HEADER,
                TABLE_REQUIRED_HEADER,
            ],
            rows=[
                # Should be in alphabetical order of names
                [
                    "Year input",
                    "Year input description",
                    "ANOTHER_YEAR",
                    "integer",
                    2016,
                    2025,
                    2018,
                    "No",
                ],
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
            ],
            max_column_widths=[
                None,
                TABLE_DESCRIPTION_MAX_COLUMN_WIDTH,
                None,
                None,
                None,
                None,
                None,
                None,
            ],
        )
        self.assertEqual(result, mock_format_table.return_value)

    def test_format_parameters_if_there_are_no_parameters(self):
        """Tests format_parameters works correctly when there are no parameters"""
        # SETUP
        model_inputs: ModelInputs = ParserBaseObject.parse_from_dict(
            ModelInputs, TEST_MODEL_INPUTS_DEFAULT
        )
        model_inputs.parameters = []

        # CALL
        result = model_inputs.format_parameters()

        # ASSERT
        self.assertEqual(result, "No parameters")

    @patch("dafni_cli.models.inputs.format_table")
    def test_format_dataslots_if_it_exists(self, mock_format_table):
        """Tests format_dataslots works correctly"""
        # SETUP
        model_inputs: ModelInputs = ParserBaseObject.parse_from_dict(
            ModelInputs, TEST_MODEL_INPUTS
        )

        # Two identical dataslots but one required and one not
        model_inputs.dataslots = [
            model_inputs.dataslots[0],
            copy.deepcopy(model_inputs.dataslots[0]),
        ]
        model_inputs.dataslots[0].required = True
        model_inputs.dataslots[0].name = "Inputs"
        model_inputs.dataslots[1].required = False
        model_inputs.dataslots[1].name = "Another input"

        # CALL
        result = model_inputs.format_dataslots()

        # ASSERT
        mock_format_table.assert_called_once_with(
            headers=[
                TABLE_TITLE_HEADER,
                TABLE_DESCRIPTION_HEADER,
                TABLE_PATH_IN_CONTAINER_HEADER,
                TABLE_DEFAULT_DATASETS_HEADER,
                TABLE_REQUIRED_HEADER,
            ],
            rows=[
                # Should be in alphabetical order of names
                [
                    "Another input",
                    "Dataslot description",
                    "inputs/",
                    "0a0a0a0a-0a00-0a00-a000-0a0a0000000f",
                    "No",
                ],
                [
                    "Inputs",
                    "Dataslot description",
                    "inputs/",
                    "0a0a0a0a-0a00-0a00-a000-0a0a0000000f",
                    "Yes",
                ],
            ],
            max_column_widths=[
                None,
                TABLE_DESCRIPTION_MAX_COLUMN_WIDTH,
                None,
                None,
                None,
            ],
        )
        self.assertEqual(result, mock_format_table.return_value)

    @patch("dafni_cli.models.inputs.format_table")
    def test_format_dataslots_if_it_exists_and_a_slot_has_multiple_defaults(
        self, mock_format_table
    ):
        """Tests format_dataslots works correctly"""
        # SETUP
        model_inputs: ModelInputs = ParserBaseObject.parse_from_dict(
            ModelInputs, TEST_MODEL_INPUTS
        )

        # Ensure the list of defaults has multiple values
        model_inputs.dataslots[0].defaults = [
            "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
            "0a0a0a0a-0a00-0a00-a000-0a0a0000000b",
        ]

        # CALL
        result = model_inputs.format_dataslots()

        # ASSERT
        mock_format_table.assert_called_once_with(
            headers=[
                TABLE_TITLE_HEADER,
                TABLE_DESCRIPTION_HEADER,
                TABLE_PATH_IN_CONTAINER_HEADER,
                TABLE_DEFAULT_DATASETS_HEADER,
                TABLE_REQUIRED_HEADER,
            ],
            rows=[
                [
                    "Inputs",
                    "Dataslot description",
                    "inputs/",
                    "0a0a0a0a-0a00-0a00-a000-0a0a0000000a\n0a0a0a0a-0a00-0a00-a000-0a0a0000000b",
                    "Yes",
                ]
            ],
            max_column_widths=[
                None,
                TABLE_DESCRIPTION_MAX_COLUMN_WIDTH,
                None,
                None,
                None,
            ],
        )
        self.assertEqual(result, mock_format_table.return_value)

    def test_format_dataslots_if_there_are_no_dataslots(self):
        """Tests format_dataslots works correctly when there are no dataslots"""
        # SETUP
        model_inputs: ModelInputs = ParserBaseObject.parse_from_dict(
            ModelInputs, TEST_MODEL_INPUTS_DEFAULT
        )

        # CALL
        result = model_inputs.format_dataslots()

        # ASSERT
        self.assertEqual(result, "No dataslots")

from unittest import TestCase
from unittest.mock import patch

from dafni_cli.api.parser import ParserBaseObject
from dafni_cli.consts import (
    INPUT_TYPE_COLUMN_WIDTH,
    OUTPUT_FORMAT_COLUMN_WIDTH,
    OUTPUT_FORMAT_HEADER,
    OUTPUT_NAME_HEADER,
    OUTPUT_SUMMARY_COLUMN_WIDTH,
    OUTPUT_SUMMARY_HEADER,
)
from dafni_cli.model.inputs import ModelParameter
from dafni_cli.model.outputs import ModelOutputDataset, ModelOutputs

TEST_MODEL_OUTPUTS: dict = {
    "datasets": [
        {
            "name": "example_dataset.csv",
            "type": "CSV",
            "description": "",
        },
    ]
}


class TestModelOutputDataset(TestCase):
    """Tests the ModelOutputDataset dataclass"""

    def test_parse(self):
        """Tests parsing of ModelOutputs"""
        model_output_dataset: ModelOutputDataset = ParserBaseObject.parse_from_dict(
            ModelOutputDataset, TEST_MODEL_OUTPUTS["datasets"][0]
        )

        self.assertEqual(
            model_output_dataset.name, TEST_MODEL_OUTPUTS["datasets"][0]["name"]
        )
        self.assertEqual(
            model_output_dataset.type, TEST_MODEL_OUTPUTS["datasets"][0]["type"]
        )
        self.assertEqual(
            model_output_dataset.description,
            TEST_MODEL_OUTPUTS["datasets"][0]["description"],
        )


class TestModelOutputs(TestCase):
    """Tests the ModelOutputs dataclass"""

    def test_parse(self):
        """Tests parsing of ModelOutputs"""
        model_outputs: ModelOutputs = ParserBaseObject.parse_from_dict(
            ModelOutputs, TEST_MODEL_OUTPUTS
        )

        # ModelOutputDatasets (contents tested in TestModelDatasets)
        self.assertEqual(len(model_outputs.datasets), 1)
        for dataset in model_outputs.datasets:
            self.assertEqual(type(dataset), ModelOutputDataset)

    def test_header_row_is_formatted_properly(self):
        """Tests params_table_header works as expected"""
        # SETUP
        name_column_width = 10
        # Expected headings string
        expected = (
            OUTPUT_NAME_HEADER
            + " " * (name_column_width - len(OUTPUT_NAME_HEADER))
            + OUTPUT_FORMAT_HEADER
            + " " * (OUTPUT_FORMAT_COLUMN_WIDTH - len(OUTPUT_FORMAT_HEADER))
            + OUTPUT_SUMMARY_HEADER
        )

        # CALL
        header_string = ModelOutputs.outputs_table_header(name_column_width)

        # ASSERT
        self.assertEqual(header_string.split("\n")[0], expected)

    def test_dashed_line_is_of_expected_length(self):
        """Tests params_table_header produces a dashed line of the expected
        length"""
        # SETUP
        name_column_width = 10
        # Expected headings string
        expected = "-" * (
            name_column_width + OUTPUT_FORMAT_COLUMN_WIDTH + OUTPUT_SUMMARY_COLUMN_WIDTH
        )

        # CALL
        header_string = ModelOutputs.outputs_table_header(name_column_width)

        # ASSERT
        self.assertEqual(header_string.split("\n")[1], expected)

    @patch.object(ModelOutputs, "outputs_table_header")
    @patch("dafni_cli.model.outputs.optional_column")
    def test_format_outputs(self, mock_column, mock_header):
        """Tests format_outputs works correctly"""
        # SETUP
        model_outputs: ModelOutputs = ParserBaseObject.parse_from_dict(
            ModelOutputs, TEST_MODEL_OUTPUTS
        )
        # Repeat the first one twice
        model_outputs.datasets.append(model_outputs.datasets[0])

        # Ignore table header
        mock_header.return_value = ""
        # Setup optional column return values
        optional_column_outputs = ["Dataset 1 description", "Dataset 2 description"]
        mock_column.side_effect = optional_column_outputs
        # Expected table
        expected_table = (
            "example_dataset.csv"
            + " " * 2
            + "CSV"
            + " " * (OUTPUT_FORMAT_COLUMN_WIDTH - 3)
            + optional_column_outputs[0]
            + "\n"
            + "example_dataset.csv"
            + " " * 2
            + "CSV"
            + " " * (INPUT_TYPE_COLUMN_WIDTH - 3)
            + optional_column_outputs[1]
            + "\n"
        )
        # CALL
        table_string = model_outputs.format_outputs()

        print(table_string)

        # ASSERT
        self.assertEqual(expected_table, table_string)

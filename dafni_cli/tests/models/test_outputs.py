import copy
from unittest import TestCase
from unittest.mock import patch

from dafni_cli.api.parser import ParserBaseObject
from dafni_cli.consts import (
    TABLE_FORMAT_HEADER,
    TABLE_NAME_HEADER,
    TABLE_SUMMARY_HEADER,
    TABLE_SUMMARY_MAX_COLUMN_WIDTH,
)
from dafni_cli.models.outputs import ModelOutputDataset, ModelOutputs
from dafni_cli.tests.fixtures.model_outputs import TEST_MODEL_OUTPUTS


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

    @patch("dafni_cli.models.outputs.format_table")
    def test_format_outputs(
        self,
        mock_format_table,
    ):
        """Tests format_outputs works correctly"""
        # SETUP
        model_outputs: ModelOutputs = ParserBaseObject.parse_from_dict(
            ModelOutputs, TEST_MODEL_OUTPUTS
        )
        # Repeat the first one twice
        model_outputs.datasets.append(copy.deepcopy(model_outputs.datasets[0]))

        model_outputs.datasets[0].name = "example_dataset.csv"
        model_outputs.datasets[1].name = "another_dataset.csv"

        # CALL
        result = model_outputs.format_outputs()

        # ASSERT
        mock_format_table.assert_called_once_with(
            headers=[
                TABLE_NAME_HEADER,
                TABLE_FORMAT_HEADER,
                TABLE_SUMMARY_HEADER,
            ],
            rows=[
                # Should be in alphabetical order of names
                ["another_dataset.csv", "CSV", ""],
                ["example_dataset.csv", "CSV", ""],
            ],
            max_column_widths=[
                None,
                None,
                TABLE_SUMMARY_MAX_COLUMN_WIDTH,
            ],
        )
        self.assertEqual(result, mock_format_table.return_value)

    @patch("dafni_cli.models.outputs.format_table")
    def test_format_outputs_when_name_and_type_none(
        self,
        mock_format_table,
    ):
        """Tests format_outputs works correctly when the dataset name or type
        are None"""
        # SETUP
        model_outputs: ModelOutputs = ParserBaseObject.parse_from_dict(
            ModelOutputs, TEST_MODEL_OUTPUTS
        )
        model_outputs.datasets[0].name = None
        model_outputs.datasets[0].type = None

        # CALL
        result = model_outputs.format_outputs()

        # ASSERT
        mock_format_table.assert_called_once_with(
            headers=[
                TABLE_NAME_HEADER,
                TABLE_FORMAT_HEADER,
                TABLE_SUMMARY_HEADER,
            ],
            rows=[
                ["Unknown", "Unknown", ""],
            ],
            max_column_widths=[
                None,
                None,
                TABLE_SUMMARY_MAX_COLUMN_WIDTH,
            ],
        )
        self.assertEqual(result, mock_format_table.return_value)

    def test_format_outputs_if_there_are_no_outputs(self):
        """Tests format_outputs works correctly when there are no parameters"""
        # SETUP
        model_outputs: ModelOutputs = ParserBaseObject.parse_from_dict(
            ModelOutputs, TEST_MODEL_OUTPUTS
        )
        model_outputs.datasets = []

        # CALL
        result = model_outputs.format_outputs()

        # ASSERT
        self.assertEqual(result, "No outputs")

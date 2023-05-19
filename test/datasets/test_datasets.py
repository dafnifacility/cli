from datetime import datetime
from unittest import TestCase
from unittest.mock import call, patch

from dateutil.tz import tzutc

from dafni_cli.consts import CONSOLE_WIDTH, TAB_SPACE
from dafni_cli.datasets.dataset import parse_datasets

from test.fixtures.datasets import TEST_DATASETS_DATA


class TestDataset(TestCase):
    """Tests the Dataset dataclass"""

    def test_parse_datasets(self):
        """Tests parsing of a list of datasets"""
        datasets = parse_datasets(TEST_DATASETS_DATA)

        self.assertEqual(len(datasets), 2)

        # This dataset is missing the optional values
        dataset1 = datasets[0]
        dataset1_metadata = TEST_DATASETS_DATA["metadata"][0]

        self.assertEqual(dataset1.asset_id, dataset1_metadata["id"]["asset_id"])
        self.assertEqual(dataset1.dataset_id, dataset1_metadata["id"]["dataset_uuid"])
        self.assertEqual(dataset1.version_id, dataset1_metadata["id"]["version_uuid"])
        self.assertEqual(dataset1.metadata_id, dataset1_metadata["id"]["metadata_uuid"])
        self.assertEqual(dataset1.formats, [])
        self.assertEqual(
            dataset1.modified_date,
            datetime(2021, 3, 4, 15, 59, 26, tzinfo=tzutc()),
        )
        self.assertEqual(dataset1.source, dataset1_metadata["source"])
        self.assertEqual(dataset1.subject, dataset1_metadata["subject"])
        self.assertEqual(dataset1.title, dataset1_metadata["title"])
        self.assertEqual(dataset1.description, None)
        self.assertEqual(dataset1.date_range_start, None)
        self.assertEqual(dataset1.date_range_end, None)

        # This dataset is not missing the optional values
        dataset2 = datasets[1]
        dataset2_metadata = TEST_DATASETS_DATA["metadata"][1]

        self.assertEqual(dataset2.asset_id, dataset2_metadata["id"]["asset_id"])
        self.assertEqual(dataset2.dataset_id, dataset2_metadata["id"]["dataset_uuid"])
        self.assertEqual(dataset2.version_id, dataset2_metadata["id"]["version_uuid"])
        self.assertEqual(dataset2.metadata_id, dataset2_metadata["id"]["metadata_uuid"])
        self.assertEqual(dataset2.formats, dataset2_metadata["formats"])
        self.assertEqual(
            dataset2.modified_date,
            datetime(2020, 8, 26, 13, 21, 18, 522000, tzinfo=tzutc()),
        )
        self.assertEqual(dataset2.source, dataset2_metadata["source"])
        self.assertEqual(dataset2.subject, dataset2_metadata["subject"])
        self.assertEqual(dataset2.title, dataset2_metadata["title"])
        self.assertEqual(dataset2.description, dataset2_metadata["description"])
        self.assertEqual(
            dataset2.date_range_start, datetime(2019, 1, 1, 12, 0, tzinfo=tzutc())
        )
        self.assertEqual(
            dataset2.date_range_end, datetime(2021, 1, 1, 12, 0, tzinfo=tzutc())
        )

    @patch("dafni_cli.datasets.dataset.prose_print")
    @patch("dafni_cli.datasets.dataset.click")
    def test_output_dataset_details_when_no_optional_values(
        self, mock_click, mock_prose
    ):
        """Tests output_dataset_details works correctly when the optional
        values are missing"""

        datasets = parse_datasets(TEST_DATASETS_DATA)
        dataset1 = datasets[0]

        dataset1.output_dataset_details()

        mock_click.echo.assert_has_calls(
            [
                call("Title: " + dataset1.title),
                call("ID: " + dataset1.dataset_id),
                call("Latest Version: " + dataset1.version_id),
                call("Publisher: " + dataset1.source),
                call(f"From: {TAB_SPACE}{TAB_SPACE}To: {TAB_SPACE}"),
                call("Description: "),
                call(""),
            ]
        )
        mock_prose.assert_called_once_with("", CONSOLE_WIDTH)

    @patch("dafni_cli.datasets.dataset.prose_print")
    @patch("dafni_cli.datasets.dataset.click")
    def test_output_dataset_details_when_optional_values_available(
        self, mock_click, mock_prose
    ):
        """Tests output_dataset_details works correctly when the optional
        values are available"""
        datasets = parse_datasets(TEST_DATASETS_DATA)
        dataset2 = datasets[1]

        # setup expected date strings
        start = dataset2.date_range_start.date().strftime("%B %d %Y")
        end = dataset2.date_range_end.date().strftime("%B %d %Y")

        dataset2.output_dataset_details()

        # ASSERT
        mock_click.echo.assert_has_calls(
            [
                call("Title: " + dataset2.title),
                call("ID: " + dataset2.dataset_id),
                call("Latest Version: " + dataset2.version_id),
                call("Publisher: " + dataset2.source),
                call(f"From: {start}{TAB_SPACE}To: {end}"),
                call("Description: "),
                call(""),
            ]
        )
        mock_prose.assert_called_once_with(dataset2.description, CONSOLE_WIDTH)

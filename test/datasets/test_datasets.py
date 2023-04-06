from dateutil.tz import tzutc
from datetime import datetime as dt
from mock import patch, call

from dafni_cli.consts import TAB_SPACE, CONSOLE_WIDTH
from dafni_cli.datasets import dataset
from test.fixtures.dataset_fixtures import get_dataset_list_fixture


class TestDataset:
    """Test class to test the Dataset class"""

    class TestInit:
        """Test class to test Dataset.__init__() functionality"""

        def test_constructor_creates_class_with_correct_values(self):
            # SETUP
            expected_keys = [
                "asset_id",
                "date_range_end",
                "date_range_start",
                "description",
                "formats",
                "id",
                "metadata_id",
                "modified",
                "source",
                "subject",
                "title",
                "version_id",
            ]

            # CALL
            instance = dataset.Dataset()

            assert all(getattr(instance, key) is None for key in expected_keys)

    class TestSetDetailsFromDict:
        """Test class to test the Dataset.set_attributes_from_dict() functionality"""

        def test_dataset_details_set_correctly_when_no_date_range_dates(
            self, get_dataset_list_fixture
        ):
            # SETUP
            # First dataset has no date range dates set
            dataset_dict = get_dataset_list_fixture["metadata"][0]

            instance = dataset.Dataset()

            # CALL
            instance.set_attributes_from_dict(dataset_dict)

            # ASSERT
            assert instance.asset_id == dataset_dict["id"]["asset_id"]
            assert instance.description == dataset_dict["description"]
            assert instance.formats == dataset_dict["formats"]
            assert instance.id == dataset_dict["id"]["dataset_uuid"]
            assert instance.metadata_id == dataset_dict["id"]["metadata_uuid"]
            assert instance.modified == dataset_dict["modified_date"]
            assert instance.source == dataset_dict["source"]
            assert instance.subject == dataset_dict["subject"]
            assert instance.title == dataset_dict["title"]
            assert instance.version_id == dataset_dict["id"]["version_uuid"]
            assert instance.date_range_end is None
            assert instance.date_range_start is None

        def test_dataset_details_set_correctly_when_date_range_dates_available(
            self, get_dataset_list_fixture
        ):
            # SETUP
            # Second dataset has date range dates set
            dataset_dict = get_dataset_list_fixture["metadata"][1]

            instance = dataset.Dataset()

            # CALL
            instance.set_attributes_from_dict(dataset_dict)

            # ASSERT
            assert instance.date_range_end == dt(2021, 1, 1, 12, 0, tzinfo=tzutc())
            assert instance.date_range_start == dt(2019, 1, 1, 12, 0, tzinfo=tzutc())

    @patch("dafni_cli.datasets.dataset.prose_print")
    @patch("dafni_cli.datasets.dataset.click")
    class TestOutputDatasetDetails:
        """Test class to test the Dataset.output_dataset_details() functionality"""

        def test_dataset_details_outputted_correctly_when_no_daterange_values(
            self, mock_click, mock_prose, get_dataset_list_fixture
        ):
            # SETUP
            dataset_dict = get_dataset_list_fixture["metadata"][0]
            instance = dataset.Dataset()
            instance.set_attributes_from_dict(dataset_dict)

            # CALL
            instance.output_dataset_details()

            # ASSERT
            assert mock_click.echo.call_args_list == [
                call("Title: " + instance.title),
                call("ID: " + instance.id),
                call("Latest Version: " + instance.version_id),
                call("Publisher: " + instance.source),
                call("From: {0}{0}To: {0}".format(TAB_SPACE)),
                call("Description: "),
                call(""),
            ]
            mock_prose.assert_called_once_with(instance.description, CONSOLE_WIDTH)

        def test_dataset_details_outputted_correctly_when_daterange_values_available(
            self, mock_click, mock_prose, get_dataset_list_fixture
        ):
            # SETUP
            dataset_dict = get_dataset_list_fixture["metadata"][1]
            instance = dataset.Dataset()
            instance.set_attributes_from_dict(dataset_dict)
            # setup expected date strings
            start = instance.date_range_start.date().strftime("%B %d %Y")
            end = instance.date_range_end.date().strftime("%B %d %Y")

            # CALL
            instance.output_dataset_details()

            # ASSERT
            assert mock_click.echo.call_args_list == [
                call("Title: " + instance.title),
                call("ID: " + instance.id),
                call("Latest Version: " + instance.version_id),
                call("Publisher: " + instance.source),
                call("From: {0}{1}To: {2}".format(start, TAB_SPACE, end)),
                call("Description: "),
                call(""),
            ]
            mock_prose.assert_called_once_with(instance.description, CONSOLE_WIDTH)

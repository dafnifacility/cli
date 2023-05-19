from typing import Optional
from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from dafni_cli.datasets import dataset_filtering


@patch("dafni_cli.datasets.dataset_filtering.process_date_filter")
class TestDatasetFiltering(TestCase):
    """Test class to test the functions in dataset_filtering.py"""

    def _check_process_datasets_filters_result(
        self,
        search_terms: Optional[str],
        start: Optional[str],
        end: Optional[str],
        expected_result: dict,
    ):
        """Helper function comparing the output of process_datasets_filters
        to a given result"""

        # CALL
        result = dataset_filtering.process_datasets_filters(search_terms, start, end)

        # ASSERT
        self.assertEqual(result, expected_result)

    def test_process_datasets_filters_with_no_filters(self, mock_process_date_filter):
        """Tests that process_datasets_filters works as expected when no
        filters are defined"""

        self._check_process_datasets_filters_result(None, None, None, {})

    def test_process_datasets_filters_with_only_search_term(
        self, mock_process_date_filter
    ):
        """Tests that process_datasets_filters works as expected when only a
        search term is defined"""

        self._check_process_datasets_filters_result(
            "DAFNI Search", None, None, {"search_text": "DAFNI Search"}
        )

    def test_process_datasets_filters_with_only_start_date(
        self, mock_process_date_filter
    ):
        """Tests that process_datasets_filters works as expected when only a
        start date is defined"""

        self._check_process_datasets_filters_result(
            None,
            "Start Date",
            None,
            {
                "date_range": {
                    "begin": mock_process_date_filter.return_value,
                    "data_with_no_date": False,
                }
            },
        )

        mock_process_date_filter.assert_called_once_with("Start Date")

    def test_process_datasets_filters_with_only_end_date(
        self, mock_process_date_filter
    ):
        """Tests that process_datasets_filters works as expected when only an
        end date is defined"""

        self._check_process_datasets_filters_result(
            None,
            None,
            "End Date",
            {
                "date_range": {
                    "end": mock_process_date_filter.return_value,
                    "data_with_no_date": False,
                }
            },
        )

        mock_process_date_filter.assert_called_once_with("End Date")

    def test_process_datasets_filters_with_search_term_and_start_date(
        self, mock_process_date_filter
    ):
        """Tests that process_datasets_filters works as expected when a search
        term and start date is defined"""

        self._check_process_datasets_filters_result(
            "Search term",
            "Start Date",
            None,
            {
                "search_text": "Search term",
                "date_range": {
                    "begin": mock_process_date_filter.return_value,
                    "data_with_no_date": False,
                },
            },
        )

        mock_process_date_filter.assert_called_once_with("Start Date")

    def test_process_datasets_filters_with_search_term_and_end_date(
        self, mock_process_date_filter
    ):
        """Tests that process_datasets_filters works as expected when a search
        term and end date is defined"""

        self._check_process_datasets_filters_result(
            "Search term",
            None,
            "End Date",
            {
                "search_text": "Search term",
                "date_range": {
                    "end": mock_process_date_filter.return_value,
                    "data_with_no_date": False,
                },
            },
        )

        mock_process_date_filter.assert_called_once_with("End Date")

    def test_process_datasets_filters_with_date_range(self, mock_process_date_filter):
        """Tests that process_datasets_filters works as expected when a
        date range is defined"""

        start_date_mock = MagicMock()
        end_date_mock = MagicMock()
        mock_process_date_filter.side_effect = [start_date_mock, end_date_mock]

        self._check_process_datasets_filters_result(
            None,
            "Start Date",
            "End Date",
            {
                "date_range": {
                    "begin": start_date_mock,
                    "end": end_date_mock,
                    "data_with_no_date": False,
                },
            },
        )

        mock_process_date_filter.assert_has_calls(
            [call("Start Date"), call("End Date")]
        )

    def test_process_datasets_filters_with_search_term_and_date_range(
        self, mock_process_date_filter
    ):
        """Tests that process_datasets_filters works as expected when a search
        term and date range is defined"""

        start_date_mock = MagicMock()
        end_date_mock = MagicMock()
        mock_process_date_filter.side_effect = [start_date_mock, end_date_mock]

        self._check_process_datasets_filters_result(
            "Search term",
            "Start Date",
            "End Date",
            {
                "search_text": "Search term",
                "date_range": {
                    "begin": start_date_mock,
                    "end": end_date_mock,
                    "data_with_no_date": False,
                },
            },
        )

        mock_process_date_filter.assert_has_calls(
            [call("Start Date"), call("End Date")]
        )

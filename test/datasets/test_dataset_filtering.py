from datetime import datetime
from typing import Optional
from unittest import TestCase

from dafni_cli.datasets import dataset_filtering


class TestDatasetFiltering(TestCase):
    """Test class to test the functions in dataset_filtering.py"""

    def _check_process_datasets_filters_result(
        self,
        search_terms: Optional[str],
        start: Optional[datetime],
        end: Optional[datetime],
        expected_result: dict,
    ):
        """Helper function comparing the output of process_datasets_filters
        to a given result"""

        # CALL
        result = dataset_filtering.process_datasets_filters(search_terms, start, end)

        # ASSERT
        self.assertEqual(result, expected_result)

    def test_process_datasets_filters_with_no_filters(self):
        """Tests that process_datasets_filters works as expected when no
        filters are defined"""

        self._check_process_datasets_filters_result(None, None, None, {})

    def test_process_datasets_filters_with_only_search_term(self):
        """Tests that process_datasets_filters works as expected when only a
        search term is defined"""

        self._check_process_datasets_filters_result(
            "DAFNI Search", None, None, {"search_text": "DAFNI Search"}
        )

    def test_process_datasets_filters_with_only_start_date(self):
        """Tests that process_datasets_filters works as expected when only a
        start date is defined"""

        start_date = datetime(2023, 1, 10)

        self._check_process_datasets_filters_result(
            None,
            start_date,
            None,
            {
                "date_range": {
                    "begin": start_date.isoformat(),
                    "data_with_no_date": False,
                }
            },
        )

    def test_process_datasets_filters_with_only_end_date(self):
        """Tests that process_datasets_filters works as expected when only an
        end date is defined"""

        end_date = datetime(2023, 1, 10)

        self._check_process_datasets_filters_result(
            None,
            None,
            end_date,
            {
                "date_range": {
                    "end": end_date.isoformat(),
                    "data_with_no_date": False,
                }
            },
        )

    def test_process_datasets_filters_with_search_term_and_start_date(self):
        """Tests that process_datasets_filters works as expected when a search
        term and start date is defined"""

        start_date = datetime(2023, 1, 10)

        self._check_process_datasets_filters_result(
            "Search term",
            start_date,
            None,
            {
                "search_text": "Search term",
                "date_range": {
                    "begin": start_date.isoformat(),
                    "data_with_no_date": False,
                },
            },
        )

    def test_process_datasets_filters_with_search_term_and_end_date(self):
        """Tests that process_datasets_filters works as expected when a search
        term and end date is defined"""

        end_date = datetime(2023, 1, 10)

        self._check_process_datasets_filters_result(
            "Search term",
            None,
            end_date,
            {
                "search_text": "Search term",
                "date_range": {
                    "end": end_date.isoformat(),
                    "data_with_no_date": False,
                },
            },
        )

    def test_process_datasets_filters_with_date_range(self):
        """Tests that process_datasets_filters works as expected when a
        date range is defined"""

        start_date = datetime(2023, 1, 10)
        end_date = datetime(2023, 5, 10)

        self._check_process_datasets_filters_result(
            None,
            start_date,
            end_date,
            {
                "date_range": {
                    "begin": start_date.isoformat(),
                    "end": end_date.isoformat(),
                    "data_with_no_date": False,
                },
            },
        )

    def test_process_datasets_filters_with_search_term_and_date_range(self):
        """Tests that process_datasets_filters works as expected when a search
        term and date range is defined"""

        start_date = datetime(2023, 1, 10)
        end_date = datetime(2023, 5, 10)

        self._check_process_datasets_filters_result(
            "Search term",
            start_date,
            end_date,
            {
                "search_text": "Search term",
                "date_range": {
                    "begin": start_date.isoformat(),
                    "end": end_date.isoformat(),
                    "data_with_no_date": False,
                },
            },
        )

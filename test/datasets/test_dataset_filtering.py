import pytest
from mock import patch

from dafni_cli.datasets import dataset_filtering


@patch("dafni_cli.datasets.dataset_filtering.process_date_filter")
class TestProcessDatasetsFiltering:
    """Test class to test the process_datasets_filtering"""

    @pytest.mark.parametrize(
        "search, start, end, expected",
        [
            (None, None, None, {}),
            ("DAFNI Search", None, None, {"search_text": "DAFNI Search"}),
            (None, "Start Date", None, {"date_range": {"begin": "Start Date"}}),
            (None, None, "End Date", {"date_range": {"end": "End Date"}}),
            (
                "DAFNI Search",
                None,
                "End Date",
                {"search_text": "DAFNI Search", "date_range": {"end": "End Date"}},
            ),
            (
                "DAFNI Search",
                "Start Date",
                "End Date",
                {
                    "search_text": "DAFNI Search",
                    "date_range": {"begin": "Start Date", "end": "End Date"},
                },
            ),
        ],ids=[
            'Case 1 - No filters defined',
            'Case 2 - Only Search term defined',
            'Case 3 - Only Start Date defined',
            'Case 4 - Only End date defined',
            'Case 5 - Search term & End date defined',
            'Case 6 - Search term and date range defined'
        ]
    )
    def test_correct_filter_dict_returned_for_given_filters(
        self, mock_date, search, start, end, expected
    ):
        # SETUP
        # returns the given arg
        mock_date.side_effect = lambda *args: args[0]

        # CALL
        result = dataset_filtering.process_datasets_filters(search, start, end)

        # ASSERT
        assert result == expected
import pytest
from mock import patch
from requests.exceptions import HTTPError

from dafni_cli.consts import DISCOVERY_API_URL
from dafni_cli.api import datasets_api
from test.fixtures.jwt_fixtures import request_response_fixture, JWT


@patch("dafni_cli.api.datasets_api.dafni_post_request")
class TestGetAllDatasets:
    """Test class to test the get_all_datasets functionality"""

    @pytest.mark.parametrize(
        "filters",
        [
            {"search_text": "DAFNI Search"},
            {
                "search_text": "DAFNI Search",
                "date_range": {"begin": "Start Date", "end": "End Date"},
            },
            {},
        ],
        ids=[
            "Case 1 - Single key on filters",
            "Case 2 - Multiple nested keys on filters",
            "Case 3 - Empty dict",
        ],
    )
    def test_dafni_post_request_called_correctly(self, mock_post, filters):

        # SETUP
        mock_post.return_value = [{"key": "value"}]

        # CALL
        result = datasets_api.get_all_datasets(JWT, filters)

        # ASSERT
        assert result == [{"key": "value"}]
        mock_post.assert_called_once_with(
            DISCOVERY_API_URL + "/catalogue/",
            JWT,
            {"offset": {"start": 0, "size": 1000}, "sort_by": "recent", **filters},
            allow_redirect=True,
        )

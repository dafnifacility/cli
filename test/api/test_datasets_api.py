import pytest
from mock import patch
from requests.exceptions import HTTPError

from dafni_cli.consts import DISCOVERY_API_URL
from dafni_cli.api import datasets_api
from test.fixtures.jwt_fixtures import request_response_fixture, JWT


@patch("dafni_cli.api.datasets_api.dafni_post_request")
class TestGetAllDatasets:
    """Test class to test the get_all_datasets functionality"""

    def test_dafni_post_request_called_correctly(self, mock_post):

        # SETUP
        mock_post.return_value = [{"key": "value"}]

        # CALL
        result = datasets_api.get_all_datasets(JWT)

        # ASSERT
        assert result == [{"key": "value"}]
        mock_post.assert_called_once_with(
            DISCOVERY_API_URL + "/catalogue/",
            JWT,
            {"offset": {"start": 0, "size": 1000}, "sort_by": "recent"},
            allow_redirect=True,
        )

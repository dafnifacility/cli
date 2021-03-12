import pytest
from mock import patch
from requests.exceptions import HTTPError

from dafni_cli.consts import MODELS_API_URL
from dafni_cli import API_requests
from test.fixtures.jwt_fixtures import request_response_fixture, JWT


@patch("dafni_cli.API_requests.requests")
class TestDafniGetRequest:
    """Test class to test the dafni_get_request functionality"""

    def test_requests_response_processed_correctly(
        self, mock_request, request_response_fixture
    ):

        # SETUP
        # setup return value for requests call
        mock_request.get.return_value = request_response_fixture
        # setup data for call
        url = "dafni/models/url"
        jwt = JWT

        # CALL
        result = API_requests.dafni_get_request(url, jwt)

        # ASSERT
        assert result == {"key": "value"}
        mock_request.get.assert_called_once_with(
            url,
            headers={"Content-Type": "application/json", "authorization": jwt},
            allow_redirects=False,
        )

    def test_exception_raised_for_failed_call(
        self, mock_request, request_response_fixture
    ):

        # SETUP
        # setup return value for requests call
        request_response_fixture.raise_for_status.side_effect = HTTPError(
            "404 client model"
        )
        mock_request.get.return_value = request_response_fixture

        # setup data for call
        url = "dafni/models/url"
        jwt = JWT

        # CALL
        # ASSERT
        with pytest.raises(HTTPError, match="404 client model"):
            API_requests.dafni_get_request(url, jwt)


@patch("dafni_cli.API_requests.dafni_get_request")
class TestGetModelsDicts:
    """Test class to test the get_models_dicts functionality"""

    def test_dafni_get_request_called_correctly(self, mock_get):

        # SETUP
        mock_get.return_value = [{"key": "value"}]

        # CALL
        result = API_requests.get_models_dicts(JWT)

        # ASSERT
        assert result == [{"key": "value"}]
        mock_get.assert_called_once_with(MODELS_API_URL + "/models/", JWT)


@patch("dafni_cli.API_requests.dafni_get_request")
class TestGetSingleModelDict:
    """Test class to test the get_single_model_dict functionality"""

    def test_dafni_get_request_called_correctly(self, mock_get):

        # SETUP
        mock_get.return_value = {"key": "value"}

        model_version = "version_1"

        # CALL
        result = API_requests.get_single_model_dict(JWT, model_version)

        # ASSERT
        assert result == {"key": "value"}
        mock_get.assert_called_once_with(MODELS_API_URL + "/models/version_1/", JWT)


@patch("dafni_cli.API_requests.dafni_get_request")
class TestModelMetaDataDicts:
    """Test class to test the get_model_metadata_dict functionality"""

    def test_dafni_get_request_called_correctly(self, mock_get):

        # SETUP
        mock_get.return_value = {"key": "value"}

        model_version = "version_1"

        # CALL
        result = API_requests.get_model_metadata_dict(JWT, model_version)

        # ASSERT
        assert result == {"key": "value"}
        mock_get.assert_called_once_with(
            MODELS_API_URL + "/models/version_1/definition/", JWT
        )

import pytest
from mock import patch
from requests.exceptions import HTTPError

from dafni_cli.consts import MODELS_API_URL
from dafni_cli.api import models_api
from test.fixtures.jwt_fixtures import request_response_fixture, JWT


@patch("dafni_cli.api.models_api.dafni_get_request")
class TestGetModelsDicts:
    """Test class to test the get_models_dicts functionality"""

    def test_dafni_get_request_called_correctly(self, mock_get):

        # SETUP
        mock_get.return_value = [{"key": "value"}]

        # CALL
        result = models_api.get_models_dicts(JWT)

        # ASSERT
        assert result == [{"key": "value"}]
        mock_get.assert_called_once_with(MODELS_API_URL + "/models/", JWT)


@patch("dafni_cli.api.models_api.dafni_get_request")
class TestGetSingleModelDict:
    """Test class to test the get_single_model_dict functionality"""

    def test_dafni_get_request_called_correctly(self, mock_get):

        # SETUP
        mock_get.return_value = {"key": "value"}

        model_version = "version_1"

        # CALL
        result = models_api.get_single_model_dict(JWT, model_version)

        # ASSERT
        assert result == {"key": "value"}
        mock_get.assert_called_once_with(MODELS_API_URL + "/models/version_1/", JWT)


@patch("dafni_cli.api.models_api.dafni_get_request")
class TestModelMetaDataDict:
    """Test class to test the get_model_metadata_dict functionality"""

    def test_dafni_get_request_called_correctly(self, mock_get):

        # SETUP
        mock_get.return_value = {"key": "value"}

        model_version = "version_1"

        # CALL
        result = models_api.get_model_metadata_dict(JWT, model_version)

        # ASSERT
        assert result == {"key": "value"}
        mock_get.assert_called_once_with(
            MODELS_API_URL + "/models/version_1/definition/", JWT
        )

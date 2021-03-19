import pytest
from mock import patch, mock_open
from requests.exceptions import HTTPError
from pathlib import Path

from dafni_cli.consts import (
    MODELS_API_URL,
    VALIDATE_MODEL_CT,
    MINIO_UPLOAD_CT
)
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


@patch("dafni_cli.api.models_api.dafni_put_request")
@patch(
        "builtins.open", new_callable=mock_open, read_data="definition file"
    )
class TestValidateModelDefinition:
    """Test class to test the validate_model_definition functionality"""

    def test_valid_model_definition_file_processed_correctly(
            self,
            open_mock,
            mock_put,
            request_response_fixture
    ):
        # SETUP
        request_response_fixture.json.return_value = {"valid": True}
        mock_put.return_value = request_response_fixture
        mock_file = Path("definition_file")
        jwt = "JWT"

        # CALL
        response, error_message = models_api.validate_model_definition(jwt, mock_file)

        # ASSERT
        open_mock.assert_called_once_with(
            mock_file, "rb"
        )
        mock_put.assert_called_once_with(
            MODELS_API_URL + "/models/definition/validate/", jwt, open(mock_file, "rb"), VALIDATE_MODEL_CT
        )
        assert response
        assert error_message == ""

    def test_invalid_model_definition_file_processed_correctly(
            self,
            open_mock,
            mock_put,
            request_response_fixture
    ):
        # SETUP
        request_response_fixture.json.return_value = {"valid": False, "errors": ["error message"]}
        mock_put.return_value = request_response_fixture
        mock_file = Path("definition_file")
        jwt = "JWT"

        # CALL
        response, errors = models_api.validate_model_definition(jwt, mock_file)

        # ASSERT
        open_mock.assert_called_once_with(
            mock_file, "rb"
        )
        mock_put.assert_called_once_with(
            MODELS_API_URL + "/models/definition/validate/", jwt, open(mock_file, "rb"), VALIDATE_MODEL_CT
        )
        assert not response
        assert errors == "error message"


@patch("dafni_cli.api.models_api.dafni_post_request")
class TestGetModelUploadUrls:
    """Test class to test the get_model_upload_urls functionality"""

    def test_post_request_called_with_correct_arguments(self, mock_post):
        # SETUP
        jwt = "JWT"
        url = MODELS_API_URL + "/models/upload/"
        data = {"image": True, "definition": True}

        # CALL
        _, _ = models_api.get_model_upload_urls(jwt)

        # ASSERT
        mock_post.assert_called_once_with(
            url, jwt, data
        )

    def test_response_dictionary_is_handled_correctly_and_returns_both_id_and_urls(self, mock_post):
        # SETUP
        jwt = "JWT"
        urls_dict = {"definition": "definition url", "image": "image url"}
        mock_post.return_value = {"id": "upload id",
                                  "urls": urls_dict}

        # CALL
        upload_id, urls = models_api.get_model_upload_urls(jwt)

        # ASSERT
        assert upload_id == "upload id"
        assert urls == urls_dict


@patch("dafni_cli.api.models_api.dafni_put_request")
@patch(
        "builtins.open", new_callable=mock_open, read_data="definition file"
    )
class TestUploadFileToMinio:
    """Test class to test the upload_file_to_minio functionality"""

    def test_put_request_and_open_called_with_correct_arguments(
            self,
            open_mock,
            mock_put
    ):
        # SETUP
        jwt = "JWT"
        url = "example.url"
        file_path = Path("path/to/file")

        # CALL
        models_api.upload_file_to_minio(jwt, url, file_path)

        # ASSERT
        open_mock.assert_called_once_with(file_path, "rb")
        mock_put.assert_called_once_with(
            url, jwt, open(Path(file_path), "rb"), MINIO_UPLOAD_CT
        )


@patch("dafni_cli.api.models_api.dafni_post_request")
class TestModelVersionIngest:
    """Test class to test the model_ingest functionality"""

    def test_post_request_called_with_correct_arguments_when_no_parent_model(
            self,
            mock_post
    ):
        # SETUP
        jwt = "JWT"
        upload_id = "uploadID"
        version_message = "version message"

        # CALL
        models_api.model_version_ingest(jwt, upload_id, version_message)

        # ASSERT
        mock_post.assert_called_once_with(
            MODELS_API_URL + "/models/upload/uploadID/ingest/",
            jwt,
            {"version_message": "version message"}
        )

    def test_post_request_called_with_correct_arguments_when_there_is_a_parent_model(
            self,
            mock_post
    ):
        # SETUP
        jwt = "JWT"
        upload_id = "uploadID"
        version_message = "version message"
        model_id = "parentModel"

        # CALL
        models_api.model_version_ingest(jwt, upload_id, version_message, model_id)

        # ASSERT
        mock_post.assert_called_once_with(
            MODELS_API_URL + "/models/parentModel/upload/uploadID/ingest/",
            jwt,
            {"version_message": "version message"}
        )


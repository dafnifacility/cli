from pathlib import Path
from unittest import TestCase
from unittest.mock import ANY, MagicMock, call, patch

from dafni_cli.api.exceptions import ValidationError
from dafni_cli.models import upload

from test.api.test_models_api import TEST_MODELS_UPLOAD_RESPONSE


@patch("dafni_cli.models.upload.click")
@patch("dafni_cli.models.upload.validate_model_definition")
@patch("dafni_cli.models.upload.get_model_upload_urls")
@patch("dafni_cli.models.upload.upload_file_to_minio")
@patch("dafni_cli.models.upload.model_version_ingest")
class TestModelUpload(TestCase):
    """Test class to test the functions in model/upload.py"""

    def test_model_upload(
        self,
        mock_model_version_ingest,
        mock_upload_file_to_minio,
        mock_get_model_upload_urls,
        mock_validate_model_definition,
        mock_click,
    ):
        """Tests that upload_dataset works as expected"""
        # SETUP
        session = MagicMock()
        definition_path = Path("path/to/definition")
        image_path = Path("path/to/image")
        version_message = "version_message"
        parent_id = MagicMock()
        mock_get_model_upload_urls.return_value = (
            TEST_MODELS_UPLOAD_RESPONSE["id"],
            TEST_MODELS_UPLOAD_RESPONSE["urls"],
        )

        # CALL
        upload.upload_model(
            session, definition_path, image_path, version_message, parent_id
        )

        # ASSERT
        mock_validate_model_definition.assert_called_once_with(session, definition_path)
        mock_get_model_upload_urls.assert_called_once_with(session)
        mock_upload_file_to_minio.assert_has_calls(
            [
                call(
                    session,
                    TEST_MODELS_UPLOAD_RESPONSE["urls"]["definition"],
                    definition_path,
                ),
                call(
                    session,
                    TEST_MODELS_UPLOAD_RESPONSE["urls"]["image"],
                    image_path,
                ),
            ]
        )
        mock_model_version_ingest.assert_called_once_with(
            session, TEST_MODELS_UPLOAD_RESPONSE["id"], "version_message", parent_id
        )

        mock_click.echo.assert_has_calls(
            [
                call("Validating model definition"),
                call("Getting urls"),
                call("Uploading model definition and image"),
                call("Ingesting model"),
                call("Model upload complete"),
            ]
        )

    def test_model_upload_exits_for_validation_error(
        self,
        mock_model_version_ingest,
        mock_upload_file_to_minio,
        mock_get_model_upload_urls,
        mock_validate_model_definition,
        mock_click,
    ):
        """Tests that upload_dataset works as expected without"""
        # SETUP
        session = MagicMock()
        definition_path = Path("path/to/definition")
        image_path = Path("path/to/image")
        version_message = "version_message"
        parent_id = MagicMock()
        mock_get_model_upload_urls.return_value = (
            TEST_MODELS_UPLOAD_RESPONSE["id"],
            TEST_MODELS_UPLOAD_RESPONSE["urls"],
        )
        mock_validate_model_definition.side_effect = ValidationError(
            "Some validation error message"
        )

        # CALL & ASSERT
        with self.assertRaises(SystemExit):
            upload.upload_model(
                session, definition_path, image_path, version_message, parent_id
            )

        mock_validate_model_definition.assert_called_once_with(session, definition_path)
        mock_get_model_upload_urls.assert_not_called()
        mock_upload_file_to_minio.assert_not_called()
        mock_model_version_ingest.assert_not_called()

        mock_click.echo.assert_has_calls(
            [
                call("Validating model definition"),
                call(mock_validate_model_definition.side_effect),
            ]
        )

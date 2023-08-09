from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from dafni_cli.api.exceptions import ValidationError
from dafni_cli.models import upload
from dafni_cli.tests.api.test_models_api import TEST_MODELS_UPLOAD_RESPONSE


class TestModelUpload(TestCase):
    """Test class to test the functions in model/upload.py"""

    def setUp(self) -> None:
        super().setUp()

        self.mock_model_version_ingest = patch(
            "dafni_cli.models.upload.model_version_ingest"
        ).start()
        self.mock_upload_file_to_minio = patch(
            "dafni_cli.models.upload.upload_file_to_minio"
        ).start()
        self.mock_get_model_upload_urls = patch(
            "dafni_cli.models.upload.get_model_upload_urls"
        ).start()
        self.mock_validate_model_definition = patch(
            "dafni_cli.models.upload.validate_model_definition"
        ).start()
        self.mock_print_json = patch("dafni_cli.models.upload.print_json").start()
        self.mock_optional_echo = patch("dafni_cli.models.upload.optional_echo").start()
        self.mock_click = patch("dafni_cli.models.upload.click").start()

        self.addCleanup(patch.stopall)

    def _test_model_upload(self, json: bool):
        """Tests that upload_model works as expected with a given json value"""
        # SETUP
        session = MagicMock()

        definition_path = Path("path/to/definition.yml")
        image_path = Path("path/to/image.tar")
        version_message = MagicMock()
        parent_id = MagicMock()
        details = {
            # NIMS always returns True here
            "success": True,
            "version_id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
        }

        self.mock_model_version_ingest.return_value = details
        self.mock_get_model_upload_urls.return_value = (
            TEST_MODELS_UPLOAD_RESPONSE["id"],
            TEST_MODELS_UPLOAD_RESPONSE["urls"],
        )

        # CALL
        upload.upload_model(
            session, definition_path, image_path, version_message, parent_id, json=json
        )

        # ASSERT
        self.mock_validate_model_definition.assert_called_once_with(
            session, definition_path
        )
        self.mock_get_model_upload_urls.assert_called_once_with(session)
        self.assertEqual(
            self.mock_upload_file_to_minio.call_args_list,
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
                    progress_bar=not json,
                ),
            ],
        )
        self.mock_model_version_ingest.assert_called_once_with(
            session, TEST_MODELS_UPLOAD_RESPONSE["id"], version_message, parent_id
        )

        self.assertEqual(
            self.mock_optional_echo.call_args_list,
            [
                call("Validating model definition", json),
                call("Getting urls", json),
                call("Uploading model definition and image", json),
                call("Ingesting model", json),
            ],
        )

        if json:
            self.mock_print_json.assert_called_once_with(details)
        else:
            self.assertEqual(
                self.mock_click.echo.call_args_list,
                [
                    call("\nUpload successful"),
                    call(f"Version ID: {details['version_id']}"),
                ],
            )

    def test_model_upload(self):
        """Tests that upload_model works as expected with json = False"""
        self._test_model_upload(json=False)

    def test_model_upload_json(self):
        """Tests that upload_model works as expected with json = True"""
        self._test_model_upload(json=True)

    def _test_model_upload_exits_for_validation_error(self, json: bool):
        """Tests that upload_dataset works as expected when there is a
        validation error with a given value of json"""

        # SETUP
        session = MagicMock()

        definition_path = Path("path/to/definition.yml")
        image_path = Path("path/to/image.tar")

        version_message = "version_message"
        parent_id = MagicMock()
        self.mock_get_model_upload_urls.return_value = (
            TEST_MODELS_UPLOAD_RESPONSE["id"],
            TEST_MODELS_UPLOAD_RESPONSE["urls"],
        )
        self.mock_validate_model_definition.side_effect = ValidationError(
            "Some validation error message"
        )

        # CALL & ASSERT
        with self.assertRaises(SystemExit) as err:
            upload.upload_model(
                session,
                definition_path,
                image_path,
                version_message,
                parent_id,
                json=json,
            )

        self.mock_optional_echo.assert_called_once_with(
            "Validating model definition", json
        )
        self.mock_validate_model_definition.assert_called_once_with(
            session, definition_path
        )
        self.assertEqual(err.exception.code, 1)
        self.mock_get_model_upload_urls.assert_not_called()
        self.mock_upload_file_to_minio.assert_not_called()
        self.mock_model_version_ingest.assert_not_called()

        self.mock_click.echo.assert_called_once_with(
            self.mock_validate_model_definition.side_effect
        )

    def test_model_upload_exits_for_validation_error(self):
        """Tests that upload_dataset works as expected when there is a
        validation error with json = False"""

        self._test_model_upload_exits_for_validation_error(json=False)

    def test_model_upload_exits_for_validation_error_json(self):
        """Tests that upload_dataset works as expected when there is a
        validation error with json = True"""

        self._test_model_upload_exits_for_validation_error(json=True)

    def test_model_upload_exits_for_incorrect_model_definition_file_type(self):
        """Tests that upload_dataset works as expected when there is an
        invalid model definition file type."""

        # SETUP
        session = MagicMock()
        definition_path = Path("path/to/definition")
        image_path = Path("path/to/image.tar")
        version_message = "version_message"
        parent_id = MagicMock()

        # CALL & ASSERT
        with self.assertRaises(SystemExit) as err:
            upload.upload_model(
                session,
                definition_path,
                image_path,
                version_message,
                parent_id,
            )

        self.mock_click.echo.assert_called_once_with(
            "Your model definition file type is incorrect. Please check you've entered the correct file and try again. Valid file types are '.yml', '.yaml', '.json'"
        )
        self.assertEqual(err.exception.code, 1)

        self.mock_optional_echo.assert_not_called()
        self.mock_validate_model_definition.assert_not_called()
        self.mock_get_model_upload_urls.assert_not_called()
        self.mock_upload_file_to_minio.assert_not_called()
        self.mock_model_version_ingest.assert_not_called()

    def test_model_upload_exits_for_incorrect_image_file_type(self):
        """Tests that upload_model works as expected when an incorrect image file is added"""

        # SETUP
        session = MagicMock()
        definition_path = Path("path/to/definition.yaml")
        image_path = Path("path/to/image")
        version_message = "version_message"
        parent_id = MagicMock()

        # CALL & ASSERT
        with self.assertRaises(SystemExit) as err:
            upload.upload_model(
                session,
                definition_path,
                image_path,
                version_message,
                parent_id,
            )

        self.mock_click.echo.assert_called_once_with(
            "Your model image file type is incorrect. Please check you've enetered the correct file and try again. Valid file types are '.tar', '.tar.gz'"
        )
        self.assertEqual(err.exception.code, 1)

        self.mock_optional_echo.assert_not_called()
        self.mock_validate_model_definition.assert_not_called()
        self.mock_get_model_upload_urls.assert_not_called()
        self.mock_upload_file_to_minio.assert_not_called()
        self.mock_model_version_ingest.assert_not_called()

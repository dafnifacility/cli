from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, mock_open, patch

from dafni_cli.api import models_api
from dafni_cli.api.exceptions import (
    EndpointNotFoundError,
    ResourceNotFoundError,
    ValidationError,
)
from dafni_cli.consts import NIMS_API_URL, VALIDATE_MODEL_CT
from dafni_cli.tests.fixtures.session import create_mock_response

TEST_MODELS_UPLOAD_RESPONSE = {
    "id": "upload_id",
    "urls": {
        "definition": "model_definition_upload_url",
        "image": "image_upload_url",
    },
}


class TestModelsAPI(TestCase):
    """Test class to test the functions in models_api.py"""

    def test_get_all_models(self):
        """Tests that get_all_models works as expected"""

        # SETUP
        session = MagicMock()

        # CALL
        result = models_api.get_all_models(session)

        # ASSERT
        session.get_request.assert_called_once_with(
            f"{NIMS_API_URL}/models/",
        )
        self.assertEqual(result, session.get_request.return_value)

    def test_get_model(self):
        """Tests that get_model works as expected"""

        # SETUP
        session = MagicMock()
        version_id = "some-model-version-id"

        # CALL
        result = models_api.get_model(session, version_id=version_id)

        # ASSERT
        session.get_request.assert_called_once_with(
            f"{NIMS_API_URL}/models/{version_id}/",
        )
        self.assertEqual(result, session.get_request.return_value)

    def test_get_model_raises_resource_not_found(self):
        """Tests that get_model handles an EndpointNotFoundError as
        expected"""

        # SETUP
        session = MagicMock()
        version_id = "some-model-version-id"
        session.get_request.side_effect = EndpointNotFoundError(
            "Some 404 error message"
        )

        # CALL
        with self.assertRaises(ResourceNotFoundError) as err:
            models_api.get_model(session, version_id=version_id)

        # ASSERT
        self.assertEqual(
            str(err.exception),
            f"Unable to find a model with version id '{version_id}'",
        )

    @patch("builtins.open", new_callable=mock_open, read_data="definition file")
    def test_validate_model_definition(self, open_mock):
        """Tests that validate_model_definition works as expected when the
        definition is found to be valid"""

        # SETUP
        session = MagicMock()
        model_definition_path = Path("path/to/file")
        session.put_request.return_value = create_mock_response(
            200, json={"valid": True}
        )

        # CALL
        models_api.validate_model_definition(
            session, model_definition_path=model_definition_path
        )

        # ASSERT
        open_mock.assert_called_once_with(model_definition_path, "rb")
        session.put_request.assert_called_once_with(
            url=f"{NIMS_API_URL}/models/validate/",
            content_type=VALIDATE_MODEL_CT,
            data=open(model_definition_path, "rb"),
        )

    @patch("builtins.open", new_callable=mock_open, read_data="definition file")
    def test_validate_model_definition_when_def_invalid(self, open_mock):
        """Tests that validate_model_definition works as expected when the
        definition is found to be invalid"""

        # SETUP
        session = MagicMock()
        model_definition_path = Path("path/to/file")
        session.put_request.return_value = create_mock_response(
            200, json={"valid": False, "errors": ["Error 1", "Error 2"]}
        )

        # CALL
        with self.assertRaises(ValidationError) as err:
            models_api.validate_model_definition(
                session, model_definition_path=model_definition_path
            )

        # ASSERT
        open_mock.assert_called_once_with(model_definition_path, "rb")
        session.put_request.assert_called_once_with(
            url=f"{NIMS_API_URL}/models/validate/",
            content_type=VALIDATE_MODEL_CT,
            data=open(model_definition_path, "rb"),
        )
        self.assertEqual(
            str(err.exception),
            "Model definition validation failed with the following "
            f"message:\n\n{session.get_error_message(session.put_request.return_value)}\n\n"
            "See "
            "https://docs.secure.dafni.rl.ac.uk/docs/how-to/models/how-to-write-a-model-definition-file/ "
            "for guidance on writing a model definition file",
        )

    def test_get_model_upload_urls(self):
        """Tests that get_model_upload_urls works as expected"""

        # SETUP
        session = MagicMock()
        session.post_request.return_value = TEST_MODELS_UPLOAD_RESPONSE

        # CALL
        result = models_api.get_model_upload_urls(session)

        # ASSERT
        session.post_request.assert_called_once_with(
            url=f"{NIMS_API_URL}/models/upload/",
            json={"image": True, "definition": True},
        )
        self.assertEqual(
            result,
            (
                "upload_id",
                {
                    "definition": "model_definition_upload_url",
                    "image": "image_upload_url",
                },
            ),
        )

    def test_model_version_ingest(self):
        """Tests that model_version_ingest works as expected without a parent
        model"""

        # SETUP
        session = MagicMock()
        upload_id = "upload-id"
        version_message = "Version message"

        # CALL
        result = models_api.model_version_ingest(
            session, upload_id=upload_id, version_message=version_message
        )

        # ASSERT
        session.post_request.assert_called_once_with(
            url=f"{NIMS_API_URL}/models/upload/{upload_id}/ingest/",
            json={"version_message": version_message},
        )
        self.assertEqual(result, session.post_request.return_value)

    def test_model_version_ingest_with_parent_model(self):
        """Tests that model_version_ingest works as expected with a parent
        model"""

        # SETUP
        session = MagicMock()
        upload_id = "upload-id"
        version_message = "Version message"
        model_id = "parent-model-id"

        # CALL
        result = models_api.model_version_ingest(
            session,
            upload_id=upload_id,
            version_message=version_message,
            model_id=model_id,
        )

        # ASSERT
        session.post_request.assert_called_once_with(
            url=f"{NIMS_API_URL}/models/{model_id}/upload/{upload_id}/ingest/",
            json={"version_message": version_message},
        )
        self.assertEqual(result, session.post_request.return_value)

    def test_delete_model_version(self):
        """Tests that delete_model_version works as expected"""

        # SETUP
        session = MagicMock()
        version_id = "version-id"

        # CALL
        result = models_api.delete_model_version(session, version_id=version_id)

        # ASSERT
        session.delete_request.assert_called_once_with(
            f"{NIMS_API_URL}/models/{version_id}/",
        )
        self.assertEqual(result, session.delete_request.return_value)

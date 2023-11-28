from unittest import TestCase
from unittest.mock import MagicMock, patch

import requests

from dafni_cli.api import datasets_api
from dafni_cli.api.exceptions import (
    DAFNIError,
    EndpointNotFoundError,
    ResourceNotFoundError,
    ValidationError,
)
from dafni_cli.consts import NID_API_URL, SEARCH_AND_DISCOVERY_API_URL
from dafni_cli.tests.fixtures.session import create_mock_metadata_errors_response


class TestDatasetsAPI(TestCase):
    """Test class to test the functions in datasets_api.py"""

    def test_validate_metadata_function_called_correctly_on_good_post_request(self):
        """Tests that validate_metadata called as expected when no error raised"""

        # SETUP
        session = MagicMock()
        metadata = "test_metadata"

        # CALL
        datasets_api.validate_metadata(session, metadata)

        # ASSERT
        session.post_request.assert_called_once_with(
            url=f"{NID_API_URL}/nid/validate/",
            json={"metadata": metadata},
        )

    def test_validate_metadata_when_DAFNIError(self):
        """Tests that validate_metadata raises a ValidationError when DAFNIError raised on post request"""

        # SETUP
        session = MagicMock()
        session.post_request.side_effect = DAFNIError
        metadata = "test_metadata"

        # CALL + ASSERT
        with self.assertRaises(ValidationError):
            datasets_api.validate_metadata(session, metadata)

    def test_get_all_datasets(self):
        """Tests that get_all_datasets works as expected"""

        # SETUP
        session = MagicMock()
        filters = {
            "search_text": "Some search text",
            "date_range": {"begin": "Start Date", "end": "End Date"},
        }

        # CALL
        result = datasets_api.get_all_datasets(session, filters)

        # ASSERT
        session.post_request.assert_called_once_with(
            url=f"{SEARCH_AND_DISCOVERY_API_URL}/catalogue/",
            json={"offset": {"start": 0, "size": 1000}, "sort_by": "recent", **filters},
            allow_redirect=True,
        )
        self.assertEqual(result, session.post_request.return_value)

    def test_get_latest_dataset_metadata(self):
        """Tests that get_latest_dataset_metadata works as expected"""

        # SETUP
        session = MagicMock()
        version_id = "some-version-id"

        # CALL
        result = datasets_api.get_latest_dataset_metadata(session, version_id)

        # ASSERT
        session.get_request.assert_called_once_with(
            url=f"{NID_API_URL}/nid/metadata/{version_id}",
            allow_redirect=True,
        )
        self.assertEqual(result, session.get_request.return_value)

    def test_get_latest_dataset_metadata_raises_resource_not_found(self):
        """Tests that get_latest_dataset_metadata handles an
        EndpointNotFoundError as expected"""

        # SETUP
        session = MagicMock()
        version_id = "some-version-id"
        session.get_request.side_effect = EndpointNotFoundError(
            "Some 404 error message"
        )

        # CALL
        with self.assertRaises(ResourceNotFoundError) as err:
            datasets_api.get_latest_dataset_metadata(session, version_id)

        # ASSERT
        self.assertEqual(
            str(err.exception),
            f"Unable to find a dataset with version_id '{version_id}'",
        )

    def test_upload_dataset_metadata_error_message_func_when_error_found(self):
        """Tests that upload_dataset_metadata_error_message_func functions as
        expected when the session object returns an error message"""

        # SETUP
        session = MagicMock()
        session.get_error_message = MagicMock()
        error_message_func = datasets_api._upload_dataset_metadata_error_message_func(
            session
        )
        mock_response = create_mock_metadata_errors_response()

        # CALL
        error_message = error_message_func(mock_response)

        # ASSERT
        self.assertEqual(error_message, session.get_error_message.return_value)

    def test_upload_dataset_metadata_error_message_func_metadata_error(self):
        """Tests that upload_dataset_metadata_error_message_func functions as
        expected when errors are returned under 'metadata' and are not found
        by the session object"""

        # SETUP
        session = MagicMock()
        session.get_error_message = MagicMock(return_value=None)
        error_message_func = datasets_api._upload_dataset_metadata_error_message_func(
            session
        )
        mock_response = create_mock_metadata_errors_response()
        expected_errors = mock_response.json()["metadata"]

        # CALL
        error_message = error_message_func(mock_response)

        # ASSERT
        self.assertEqual(
            error_message,
            "Found errors in metadata:\n" f"{expected_errors[0]}\n{expected_errors[1]}",
        )

    def test_upload_dataset_metadata_error_message_func_handles_decode_error(self):
        """Tests _upload_dataset_metadata_error_message_func when JSON decoding fails"""

        # SETUP
        session = MagicMock()
        session.get_error_message = MagicMock(return_value=None)
        error_message_func = datasets_api._upload_dataset_metadata_error_message_func(
            session
        )
        mock_response = create_mock_metadata_errors_response()
        mock_response.json.side_effect = requests.JSONDecodeError("", "", 0)

        # CALL
        error_message = error_message_func(mock_response)

        # ASSERT
        self.assertEqual(error_message, None)

    @patch("dafni_cli.api.datasets_api._upload_dataset_metadata_error_message_func")
    def test_upload_dataset_metadata(self, mock_error_message_func):
        """Tests that upload_dataset_metadata works as expected using
        default values"""

        # SETUP
        session = MagicMock()
        temp_bucket_id = "temp-bucket-id"
        metadata = {"test": "dictionary"}

        # CALL
        result = datasets_api.upload_dataset_metadata(session, temp_bucket_id, metadata)

        # ASSERT
        mock_error_message_func.assert_called_once_with(session)
        session.post_request.assert_called_once_with(
            url=f"{NID_API_URL}/nid/dataset/",
            json={"bucketId": temp_bucket_id, "metadata": metadata},
            error_message_func=mock_error_message_func.return_value,
        )
        self.assertEqual(result, session.post_request.return_value)

    @patch("dafni_cli.api.datasets_api._upload_dataset_metadata_error_message_func")
    def test_upload_dataset_metadata_with_dataset_id(self, mock_error_message_func):
        """Tests that upload_dataset_metadata works as expected when given
        a dataset_id"""

        # SETUP
        session = MagicMock()
        temp_bucket_id = "temp-bucket-id"
        metadata = {"test": "dictionary"}
        dataset_id = "some-dataset-id"

        # CALL
        result = datasets_api.upload_dataset_metadata(
            session, temp_bucket_id, metadata, dataset_id=dataset_id
        )

        # ASSERT
        mock_error_message_func.assert_called_once_with(session)
        session.post_request.assert_called_once_with(
            url=f"{NID_API_URL}/nid/dataset/{dataset_id}",
            json={"bucketId": temp_bucket_id, "metadata": metadata},
            error_message_func=mock_error_message_func.return_value,
        )
        self.assertEqual(result, session.post_request.return_value)

    @patch("dafni_cli.api.datasets_api._upload_dataset_metadata_error_message_func")
    def test_upload_dataset_metadata_version(self, mock_error_message_func):
        """Tests that upload_dataset_metadata_version works as expected using
        default values"""

        # SETUP
        session = MagicMock()
        dataset_id = "dataset-id"
        version_id = "version-id"
        metadata = {"test": "dictionary"}

        # CALL
        result = datasets_api.upload_dataset_metadata_version(
            session, dataset_id, version_id, metadata
        )

        # ASSERT
        mock_error_message_func.assert_called_once_with(session)
        session.post_request.assert_called_once_with(
            url=f"{NID_API_URL}/nid/metadata/{dataset_id}/{version_id}",
            json={"metadata": metadata},
            error_message_func=mock_error_message_func.return_value,
        )
        self.assertEqual(result, session.post_request.return_value)

    def test_delete_dataset(self):
        """Tests that delete_dataset works as expected"""

        # SETUP
        session = MagicMock()
        dataset_id = "dataset-id"

        # CALL
        result = datasets_api.delete_dataset(session, dataset_id=dataset_id)

        # ASSERT
        session.delete_request.assert_called_once_with(
            f"{NID_API_URL}/nid/dataset/{dataset_id}",
        )
        self.assertEqual(result, session.delete_request.return_value)

    def test_delete_dataset_version(self):
        """Tests that delete_dataset_version works as expected"""

        # SETUP
        session = MagicMock()
        version_id = "version-id"

        # CALL
        result = datasets_api.delete_dataset_version(session, version_id=version_id)

        # ASSERT
        session.delete_request.assert_called_once_with(
            f"{NID_API_URL}/nid/version/{version_id}/",
        )
        self.assertEqual(result, session.delete_request.return_value)

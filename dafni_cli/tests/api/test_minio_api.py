from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, mock_open, patch

from dafni_cli.api import minio_api
from dafni_cli.consts import (
    MINIO_API_URL,
    MINIO_DOWNLOAD_REDIRECT_API_URL,
    NID_API_URL,
    DSS_API_URL,
    MINIO_UPLOAD_CT,
)


class TestMinioAPI(TestCase):
    """Test class to test the functions in minio_api.py"""

    @patch("builtins.open", new_callable=mock_open, read_data="definition file")
    def test_upload_file_to_minio(self, open_mock):
        """Tests that upload_file_to_minio works as expected"""

        # SETUP
        session = MagicMock()
        url = "example.url"
        file_path = Path("path/to/file")

        # CALL
        result = minio_api.upload_file_to_minio(session, url, file_path)

        # ASSERT
        open_mock.assert_called_once_with(file_path, "rb")
        session.put_request.assert_called_once_with(
            url=url, content_type=MINIO_UPLOAD_CT, data=open(Path(file_path), "rb")
        )
        self.assertEqual(result, session.put_request.return_value)

    def test_create_temp_bucket(self):
        """Tests that create_temp_bucket works as expected"""

        # SETUP
        session = MagicMock()

        # CALL
        result = minio_api.create_temp_bucket(session)

        # ASSERT
        session.post_request.assert_called_once_with(
            url=f"{NID_API_URL}/nid/upload/", allow_redirect=True
        )
        self.assertEqual(result, session.post_request.return_value)

    def test_delete_temp_bucket(self):
        """Tests that delete_temp_bucket works as expected"""

        # SETUP
        session = MagicMock()
        temp_bucket_id = "temp-some-id"

        # CALL
        result = minio_api.delete_temp_bucket(session, temp_bucket_id)

        # ASSERT
        session.delete_request.assert_called_once_with(
            url=f"{DSS_API_URL}/assets/some-id"
        )
        self.assertEqual(result, session.delete_request.return_value)

    def test_get_data_upload_urls(self):
        """Tests that get_data_upload_urls works as expected"""

        # SETUP
        session = MagicMock()
        temp_bucket_id = "temp-some-id"
        file_names = ["file_1.txt", "file_2.txt", "file_3.txt"]

        # CALL
        result = minio_api.get_data_upload_urls(session, temp_bucket_id, file_names)

        # ASSERT
        session.patch_request.assert_called_once_with(
            url=f"{NID_API_URL}/nid/upload/",
            json={"bucketId": temp_bucket_id, "datafiles": file_names},
            allow_redirect=True,
        )
        self.assertEqual(result, session.patch_request.return_value)

    def test_minio_get_request(self):
        """Tests that minio_get_request works as expected"""

        # SETUP
        session = MagicMock()
        url = f"{MINIO_API_URL}/example_file.zip"
        content = MagicMock()

        # CALL
        result = minio_api.minio_get_request(session, url, content)

        # ASSERT
        session.get_request.assert_called_once_with(
            url=f"{MINIO_DOWNLOAD_REDIRECT_API_URL}/example_file.zip",
            content_type="application/json",
            allow_redirect=False,
            content=content,
        )
        self.assertEqual(result, session.get_request.return_value)

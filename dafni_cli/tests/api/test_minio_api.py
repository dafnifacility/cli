from unittest import TestCase
from unittest.mock import ANY, MagicMock, mock_open, patch

from dafni_cli.api import minio_api
from dafni_cli.consts import (
    DSS_API_URL,
    MINIO_UPLOAD_CT,
    NID_API_URL,
)


class TestMinioAPI(TestCase):
    """Test class to test the functions in minio_api.py"""

    @patch("builtins.open", new_callable=mock_open, read_data="definition file")
    @patch("dafni_cli.api.minio_api.create_file_progress_bar")
    @patch("dafni_cli.api.minio_api.CallbackIOWrapper")
    def test_upload_file_to_minio(
        self, mock_CallbackIOWrapper, mock_create_file_progress_bar, open_mock
    ):
        """Tests that upload_file_to_minio works as expected"""

        # SETUP
        session = MagicMock()
        url = "example.url"
        file_path = MagicMock(name="file_name", stat=lambda: MagicMock(st_size=1000))
        progress_bar_value = MagicMock()

        # Cause the refresh callback to be called
        put_request_return_value = MagicMock()

        def put_request_side_effect(url, content_type, data, retry_callback):
            retry_callback()
            return put_request_return_value

        session.put_request = MagicMock(side_effect=put_request_side_effect)

        # Mock the progress bar object returned by `with create_file_progress_bar'
        mock_progress_bar = MagicMock()
        mock_create_file_progress_bar.return_value.__enter__.return_value = (
            mock_progress_bar
        )

        # CALL
        result = minio_api.upload_file_to_minio(
            session, url, file_path, progress_bar=progress_bar_value
        )

        # ASSERT
        open_mock.assert_called_once_with(file_path, "rb")
        mock_create_file_progress_bar.assert_called_once_with(
            description=file_path.name,
            total=file_path.stat().st_size,
            disable=False,
        )
        mock_CallbackIOWrapper.assert_called_once_with(
            mock_progress_bar.update, open_mock.return_value, "read"
        )
        session.put_request.assert_called_once_with(
            url=url,
            content_type=MINIO_UPLOAD_CT,
            data=mock_CallbackIOWrapper.return_value,
            retry_callback=ANY,
        )

        # retry_callback
        open_mock.return_value.seek.assert_called_once_with(0)
        mock_progress_bar.reset.assert_called_once()

        self.assertEqual(result, put_request_return_value)

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

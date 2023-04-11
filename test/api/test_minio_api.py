from mock import patch, mock_open
from pathlib import Path

from dafni_cli.consts import MINIO_UPLOAD_CT, DATA_UPLOAD_API_URL
from dafni_cli.api import minio_api
from test.fixtures.dataset_fixtures import upload_metadata_fixture


@patch("dafni_cli.api.minio_api.dafni_put_request")
@patch("builtins.open", new_callable=mock_open, read_data="definition file")
class TestUploadFileToMinio:
    """Test class to test the upload_file_to_minio functionality"""

    def test_put_request_and_open_called_with_correct_arguments(
        self, open_mock, mock_put
    ):
        # SETUP
        jwt = "JWT"
        url = "example.url"
        file_path = Path("path/to/file")

        # CALL
        minio_api.upload_file_to_minio(jwt, url, file_path)

        # ASSERT
        open_mock.assert_called_once_with(file_path, "rb")
        mock_put.assert_called_once_with(
            url, jwt, open(Path(file_path), "rb"), MINIO_UPLOAD_CT
        )


@patch("dafni_cli.api.minio_api.dafni_post_request")
class TestGetDataUploadId:
    """Test class to test the get_data_upload_id functionality"""

    def test_post_request_called_with_correct_values(self, mock_post):
        # SETUP
        mock_post.return_value = {"key": "value"}
        jwt = "JWT"

        # setup expected call values
        url = f"{DATA_UPLOAD_API_URL}/nid/upload/"
        data = {"cancelToken": {"promise": {}}}

        # CALL
        result = minio_api.get_data_upload_id(jwt)

        # ASSERT
        mock_post.assert_called_once_with(url, jwt, data, allow_redirect=True)
        assert result == {"key": "value"}


@patch("dafni_cli.api.minio_api.dafni_patch_request")
class TestGetDataUploadUrls:
    """Test class to test the get_data_upload_urls functionality"""

    def test_patch_request_called_with_correct_values(self, mock_patch):
        # SETUP
        mock_patch.return_value = {"key": "value"}
        # setup data for call
        jwt = "JWT"
        upload_id = "upload-id"
        file_names = ["file_1.txt", "file_2.txt", "file_3.txt"]

        # setup expected call values
        url = f"{DATA_UPLOAD_API_URL}/nid/upload/"
        data = {"bucketId": upload_id, "datafiles": file_names}

        # CALL
        result = minio_api.get_data_upload_urls(jwt, upload_id, file_names)

        # ASSERT
        mock_patch.assert_called_once_with(url, jwt, data, allow_redirect=True)
        assert result == {"key": "value"}


@patch("dafni_cli.api.minio_api.dafni_post_request")
class TestUploadDatasetMetadata:
    """Test class to test the upload_dataset_metadata functionality"""

    def test_post_request_called_with_correct_values(
        self, mock_post, upload_metadata_fixture
    ):
        # SETUP
        mock_post.return_value = {"key": "value"}
        jwt = "JWT"

        # setup expected call values
        url = f"{DATA_UPLOAD_API_URL}/nid/dataset/"
        upload_id = "upload-id"
        data = {"bucketId": upload_id, "metadata": upload_metadata_fixture}

        # CALL
        result = minio_api.upload_dataset_metadata(
            jwt, upload_id, upload_metadata_fixture
        )

        # ASSERT
        mock_post.assert_called_once_with(url, jwt, data, raise_status=False)
        assert result == {"key": "value"}

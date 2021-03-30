from mock import patch, mock_open
from pathlib import Path

from dafni_cli.consts import MINIO_UPLOAD_CT
from dafni_cli.api import minio_api


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

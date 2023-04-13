import json
import os

import pytest
from mock import MagicMock, call, patch
from requests.exceptions import HTTPError

from dafni_cli.consts import CONSOLE_WIDTH
from dafni_cli.datasets import dataset_upload as upload

from test.fixtures.dataset_fixtures import upload_metadata_fixture


@patch("dafni_cli.datasets.dataset_upload.click")
@patch("dafni_cli.datasets.dataset_upload.upload_metadata")
@patch("dafni_cli.datasets.dataset_upload.upload_files")
class TestUploadNewDatasetFiles:
    """Test class for testing the upload_new_dataset_files functionality"""

    def test_helper_functions_called_correctly(self, mock_files, mock_meta, mock_click):
        # SETUP
        upload_id = "upload_id"
        definition = "metadata.json"
        files = ["file_1.txt", "file_2.txt"]
        details = {
            "datasetId": "dataset-id",
            "versionId": "version-id",
            "metadataId": "metadata-id",
        }
        jwt = "JWT"

        mock_files.return_value = upload_id
        mock_meta.return_value = details

        # CALL
        upload.upload_new_dataset_files(jwt, definition, files)

        # ASSERT
        mock_files.assert_called_once_with(jwt, files)
        mock_meta.assert_called_once_with(jwt, definition, upload_id)

    def test_the_correct_details_are_outputted_on_success(
        self, mock_files, mock_meta, mock_click
    ):
        # SETUP
        upload_id = "upload_id"
        definition = "metadata.json"
        files = ["file_1.txt", "file_2.txt"]
        details = {
            "datasetId": "dataset-id",
            "versionId": "version-id",
            "metadataId": "metadata-id",
        }
        jwt = "JWT"

        mock_files.return_value = upload_id
        mock_meta.return_value = details

        # CALL
        upload.upload_new_dataset_files(jwt, definition, files)

        # ASSERT
        assert mock_click.echo.call_args_list == [
            call("\nUpload Successful"),
            call(f"Dataset ID: {details['datasetId']}"),
            call(f"Version ID: {details['versionId']}"),
            call(f"Metadata ID: {details['metadataId']}"),
        ]


@patch("dafni_cli.datasets.dataset_upload.click")
@patch("dafni_cli.datasets.dataset_upload.upload_file_to_minio")
@patch("dafni_cli.datasets.dataset_upload.get_data_upload_urls")
@patch("dafni_cli.datasets.dataset_upload.get_data_upload_id")
class TestUploadFiles:
    """Test class to test the upload_files functionality"""

    @pytest.mark.parametrize(
        "files", [["file_1.txt"], ["file_1.txt", "file_2.txt", "file_3.txt"]]
    )
    def test_upload_functions_called_correctly(
        self, mock_id, mock_urls, mock_upload, mock_click, files
    ):
        # SETUP
        # setup data
        upload_id = "upload_id"
        file_paths = [f"path\\to\\file\\{file_name}" for file_name in files]
        urls = [f"upload/url/{file_name}" for file_name in files]
        upload_urls = {"URLs": {files[idx]: url for idx, url in enumerate(urls)}}
        jwt = "JWT"
        # setup return values for functions
        mock_id.return_value = upload_id
        mock_urls.return_value = upload_urls

        # CALL
        upload.upload_files(jwt, file_paths)

        # ASSERT
        mock_id.assert_called_once_with(jwt)
        mock_urls.assert_called_once_with(jwt, upload_id, files)
        assert mock_upload.call_args_list == [
            call(jwt, url, file_paths[idx]) for idx, url in enumerate(urls)
        ]

    def test_correct_messages_outputted_by_click(
        self, mock_id, mock_urls, mock_upload, mock_click
    ):
        # SETUP
        # setup data
        upload_id = "upload_id"
        files = ["file_1.txt", "file_2.txt", "file_3.txt"]
        file_paths = [f"path\\to\\file\\{file_name}" for file_name in files]
        urls = [f"upload/url/{file_name}" for file_name in files]
        upload_urls = {"URLs": {files[idx]: url for idx, url in enumerate(urls)}}
        jwt = "JWT"
        # setup return values for functions
        mock_id.return_value = upload_id
        mock_urls.return_value = upload_urls

        # CALL
        upload.upload_files(jwt, file_paths)

        # ASSERT
        assert mock_click.echo.call_args_list == [
            call("\nRetrieving Temporary Upload ID"),
            call("Retrieving File Upload URls"),
            call("Uploading Files"),
        ]


@patch("dafni_cli.datasets.dataset_upload.click")
@patch("dafni_cli.datasets.dataset_upload.prose_print")
@patch("dafni_cli.datasets.dataset_upload.upload_dataset_metadata")
class TestUploadMetadata:
    """Test class to test the upload_metadata functionality"""

    def test_correct_response_returned_on_success(
        self, mock_upload, mock_prose, mock_click, tmp_path, upload_metadata_fixture
    ):
        # SETUP
        # create definition file
        file_name = "meta_data.json"
        file_path = os.path.join(tmp_path, file_name)
        with open(file_path, "w") as meta_file:
            meta_file.write(json.dumps(upload_metadata_fixture))

        # setup data
        upload_id = "upload-id"
        response = MagicMock()
        response.raise_for_status.return_value = None
        response.json.return_value = "Json success"
        jwt = "JWT"

        # setup mocks
        mock_upload.return_value = response

        # CALL
        result = upload.upload_metadata(jwt, file_path, upload_id)

        # ASSERT
        assert result == "Json success"

        mock_prose.assert_not_called()
        mock_upload.assert_called_once_with(jwt, upload_id, upload_metadata_fixture)

        response.raise_for_status.assert_called_once()
        mock_click.echo.assert_called_once_with("Uploading Metadata File")

    def test_correct_response_returned_on_failure(
        self, mock_upload, mock_prose, mock_click, tmp_path, upload_metadata_fixture
    ):
        # SETUP
        # create definition file
        file_name = "meta_data.json"
        file_path = os.path.join(tmp_path, file_name)
        with open(file_path, "w") as meta_file:
            meta_file.write(json.dumps(upload_metadata_fixture))

        # setup data
        upload_id = "upload-id"
        response = MagicMock()
        response.raise_for_status.side_effect = HTTPError("400 error")
        errors = ["error 1", "error 2", "error 3"]
        response.json.return_value = errors
        jwt = "JWT"

        # setup mocks
        mock_upload.return_value = response

        # CALL
        with pytest.raises(SystemExit, match="1"):
            upload.upload_metadata(jwt, file_path, upload_id)

        # ASSERT
        mock_prose.assert_called_once_with("\n".join(errors), CONSOLE_WIDTH)
        mock_upload.assert_called_once_with(jwt, upload_id, upload_metadata_fixture)

        response.raise_for_status.assert_called_once()

        assert mock_click.echo.call_args_list == [
            call("Uploading Metadata File"),
            call("\nMetadata Upload Failed"),
        ]

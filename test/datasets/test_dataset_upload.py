from unittest import TestCase
from unittest.mock import MagicMock, call, mock_open, patch

from requests import HTTPError

from dafni_cli.api.exceptions import DAFNIError
from dafni_cli.datasets import dataset_upload


@patch("dafni_cli.datasets.dataset_upload.click")
class TestDatasetUpload(TestCase):
    """Test class to test the functions in dataset_upload.py"""

    @patch("dafni_cli.datasets.dataset_upload.upload_files")
    @patch("dafni_cli.datasets.dataset_upload.upload_metadata")
    @patch("dafni_cli.datasets.dataset_upload.create_temp_bucket")
    def test_upload_new_dataset_files(
        self,
        mock_create_temp_bucket,
        mock_upload_metadata,
        mock_upload_files,
        mock_click,
    ):
        """Tests that upload_new_dataset_files works as expected"""
        # SETUP
        session = MagicMock()
        definition_path = "path/to/file"
        file_paths = ["file_1.txt", "file_2.txt"]
        temp_bucket_id = "some-temp-bucket"
        details = {
            "datasetId": "dataset-id",
            "versionId": "version-id",
            "metadataId": "metadata-id",
        }

        mock_create_temp_bucket.return_value = temp_bucket_id
        mock_upload_metadata.return_value = details

        # CALL
        dataset_upload.upload_new_dataset_files(session, definition_path, file_paths)

        # ASSERT
        mock_create_temp_bucket.assert_called_once_with(session)
        mock_upload_files.assert_called_once_with(
            session,
            temp_bucket_id,
            file_paths,
        )
        mock_upload_metadata.assert_called_once_with(
            session, definition_path, temp_bucket_id
        )

        mock_click.echo.assert_has_calls(
            [
                call("\nRetrieving temporary bucket ID"),
                call("\nUpload successful"),
                call(f"Dataset ID: {details['datasetId']}"),
                call(f"Version ID: {details['versionId']}"),
                call(f"Metadata ID: {details['metadataId']}"),
            ]
        )

    @patch("dafni_cli.datasets.dataset_upload.upload_files")
    @patch("dafni_cli.datasets.dataset_upload.upload_metadata")
    @patch("dafni_cli.datasets.dataset_upload.create_temp_bucket")
    @patch("dafni_cli.datasets.dataset_upload.delete_temp_bucket")
    def test_upload_new_dataset_files_deletes_bucket_on_error(
        self,
        mock_delete_temp_bucket,
        mock_create_temp_bucket,
        mock_upload_metadata,
        mock_upload_files,
        mock_click,
    ):
        """Tests that upload_new_dataset_files deletes the temporary bucket
        when an error occurs"""
        # SETUP
        session = MagicMock()
        definition_path = "path/to/file"
        file_paths = ["file_1.txt", "file_2.txt"]
        temp_bucket_id = "some-temp-bucket"

        mock_create_temp_bucket.return_value = temp_bucket_id
        mock_upload_metadata.side_effect = HTTPError(400)

        # CALL
        with self.assertRaises(HTTPError):
            dataset_upload.upload_new_dataset_files(
                session, definition_path, file_paths
            )

        # ASSERT
        mock_create_temp_bucket.assert_called_once_with(session)
        mock_upload_files.assert_called_once_with(
            session,
            temp_bucket_id,
            file_paths,
        )
        mock_upload_metadata.assert_called_once_with(
            session, definition_path, temp_bucket_id
        )
        mock_delete_temp_bucket.assert_called_once_with(session, temp_bucket_id)

        mock_click.echo.assert_has_calls(
            [
                call("\nRetrieving temporary bucket ID"),
                call("Deleting temporary bucket"),
            ]
        )

    @patch("dafni_cli.datasets.dataset_upload.upload_files")
    @patch("dafni_cli.datasets.dataset_upload.upload_metadata")
    @patch("dafni_cli.datasets.dataset_upload.create_temp_bucket")
    @patch("dafni_cli.datasets.dataset_upload.delete_temp_bucket")
    def test_upload_new_dataset_files_deletes_bucket_on_system_exit(
        self,
        mock_delete_temp_bucket,
        mock_create_temp_bucket,
        mock_upload_metadata,
        mock_upload_files,
        mock_click,
    ):
        """Tests that upload_new_dataset_files deletes the temporary bucket
        when an SystemExit is triggered"""
        # SETUP
        session = MagicMock()
        definition_path = "path/to/file"
        file_paths = ["file_1.txt", "file_2.txt"]
        temp_bucket_id = "some-temp-bucket"

        mock_create_temp_bucket.return_value = temp_bucket_id
        mock_upload_metadata.side_effect = SystemExit(1)

        # CALL
        with self.assertRaises(SystemExit):
            dataset_upload.upload_new_dataset_files(
                session, definition_path, file_paths
            )

        # ASSERT
        mock_create_temp_bucket.assert_called_once_with(session)
        mock_upload_files.assert_called_once_with(
            session,
            temp_bucket_id,
            file_paths,
        )
        mock_upload_metadata.assert_called_once_with(
            session, definition_path, temp_bucket_id
        )
        mock_delete_temp_bucket.assert_called_once_with(session, temp_bucket_id)

        mock_click.echo.assert_has_calls(
            [
                call("\nRetrieving temporary bucket ID"),
                call("Deleting temporary bucket"),
            ]
        )

    @patch("dafni_cli.datasets.dataset_upload.get_data_upload_urls")
    @patch("dafni_cli.datasets.dataset_upload.upload_file_to_minio")
    def test_upload_files(
        self,
        mock_upload_file_to_minio,
        mock_get_data_upload_urls,
        mock_click,
    ):
        """Tests that upload_files works as expected"""
        # SETUP
        session = MagicMock()
        temp_bucket_id = "some-temp-bucket"
        file_paths = ["file_1.txt", "file_2.txt"]
        urls = [f"upload/url/{file_name}" for file_name in file_paths]
        upload_urls = {"URLs": {file_paths[idx]: url for idx, url in enumerate(urls)}}

        mock_get_data_upload_urls.return_value = upload_urls

        # CALL
        dataset_upload.upload_files(session, temp_bucket_id, file_paths)

        # ASSERT
        mock_get_data_upload_urls.assert_called_once_with(
            session, temp_bucket_id, file_paths
        )
        mock_upload_file_to_minio.assert_has_calls(
            [call(session, url, file_paths[idx]) for idx, url in enumerate(urls)]
        )

        mock_click.echo.assert_has_calls(
            [
                call("Retrieving file upload URls"),
                call("Uploading files"),
            ]
        )

    @patch("builtins.open", new_callable=mock_open, read_data='{"some": "json_data"}')
    @patch("dafni_cli.datasets.dataset_upload.upload_dataset_metadata")
    def test_upload_metadata(
        self,
        mock_upload_dataset_metadata,
        open_mock,
        mock_click,
    ):
        """Tests that upload_metadata works as expected"""
        # SETUP
        session = MagicMock()
        definition_path = "path/to/file"
        temp_bucket_id = "some-temp-bucket"

        # CALL
        result = dataset_upload.upload_metadata(
            session, definition_path, temp_bucket_id
        )

        # ASSERT
        open_mock.assert_called_once_with(definition_path, "r", encoding="utf-8")
        mock_upload_dataset_metadata.assert_called_with(
            session, temp_bucket_id, {"some": "json_data"}
        )

        mock_click.echo.assert_has_calls(
            [
                call("Uploading metadata file"),
            ]
        )
        self.assertEqual(result, mock_upload_dataset_metadata.return_value)

    @patch("builtins.open", new_callable=mock_open, read_data='{"some": "json_data"}')
    @patch("dafni_cli.datasets.dataset_upload.upload_dataset_metadata")
    def test_upload_metadata_exits_on_error(
        self,
        mock_upload_dataset_metadata,
        open_mock,
        mock_click,
    ):
        """Tests that upload_metadata calls SystemExit(1) when an error occurs"""
        # SETUP
        session = MagicMock()
        definition_path = "path/to/file"
        temp_bucket_id = "some-temp-bucket"

        error = DAFNIError("Some error message")
        mock_upload_dataset_metadata.side_effect = error

        # CALL
        with self.assertRaises(SystemExit):
            dataset_upload.upload_metadata(session, definition_path, temp_bucket_id)

        # ASSERT
        open_mock.assert_called_once_with(definition_path, "r", encoding="utf-8")

        mock_click.echo.assert_has_calls(
            [
                call("Uploading metadata file"),
                call(f"\nMetadata upload failed: {error}"),
            ]
        )

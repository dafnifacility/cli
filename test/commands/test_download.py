import os

from click.testing import CliRunner
from mock import MagicMock, PropertyMock, patch

from dafni_cli.commands.download import download

from test.fixtures.dataset_fixtures import dataset_metadata_fixture
from test.fixtures.jwt_fixtures import processed_jwt_fixture

class TestDownload:
    """test class to test the download() command functionality"""

    @patch("dafni_cli.commands.download.DatasetMetadata")
    @patch("dafni_cli.commands.download.get_latest_dataset_metadata")
    @patch("dafni_cli.commands.download.check_for_jwt_file")
    class TestInit:
        """Test class to test the get() group processing of the
        JWT
        """

        def test_jwt_retrieved_and_set_on_context(
            self,
            mock_jwt,
            mock_get,
            mock_dataset,
            processed_jwt_fixture,
            dataset_metadata_fixture,
        ):
            # SETUP
            mock_get.return_value = dataset_metadata_fixture
            mock_jwt.return_value = processed_jwt_fixture, False

            mock_instance = MagicMock()
            mock_instance.files.return_value = []
            mock_dataset.return_value = mock_instance

            runner = CliRunner()
            ctx = {}

            # CALL
            result = runner.invoke(download, ["dataset", "id", "version-id"], obj=ctx)

            # ASSERT
            mock_jwt.assert_called_once()

            assert ctx["jwt"] == processed_jwt_fixture["jwt"]
            assert result.exit_code == 0

    @patch("dafni_cli.commands.download.DatasetMetadata")
    @patch("dafni_cli.commands.download.get_latest_dataset_metadata")
    @patch("dafni_cli.commands.download.check_for_jwt_file")
    class TestDataset:
        """Test class to test the download dataset command"""

        def test_message_outputted_if_no_files_found(
            self,
            mock_jwt,
            mock_get,
            mock_dataset,
            processed_jwt_fixture,
            dataset_metadata_fixture,
        ):
            # SETUP
            mock_get.return_value = dataset_metadata_fixture
            mock_jwt.return_value = processed_jwt_fixture, False

            mock_instance = MagicMock()
            files = PropertyMock(return_value=[])
            type(mock_instance).files = files

            mock_dataset.return_value = mock_instance

            runner = CliRunner()

            # CALL
            result = runner.invoke(download, ["dataset", "id", "version-id"])

            # ASSERT
            assert (
                result.stdout
                == "\nThere are no files currently associated with the Dataset to download\n"
            )

            assert result.exit_code == 0

        @patch("dafni_cli.commands.download.os.getcwd")
        @patch("dafni_cli.commands.download.write_files_to_zip")
        def test_file_details_processed_correctly_for_default_directory(
            self,
            mock_zip,
            mock_os,
            mock_jwt,
            mock_get,
            mock_dataset,
            processed_jwt_fixture,
            dataset_metadata_fixture,
        ):
            # SETUP
            mock_get.return_value = dataset_metadata_fixture
            mock_jwt.return_value = processed_jwt_fixture, False
            directory = "path/to/cwd"
            mock_os.return_value = directory

            # Setup DatasetMetadata mock instance
            mock_instance = MagicMock()
            files = PropertyMock(return_value=["files"])
            type(mock_instance).files = files

            file_names = ["file_1.txt", "file_2.pdf", "file_3.csv"]
            file_contents = [b"file 1", b"file 2", b"file 3"]
            mock_instance.download_dataset_files.return_value = (
                file_names,
                file_contents,
            )

            mock_dataset.return_value = mock_instance

            # Setup data for call
            data_id = "dataset id"
            version_id = "version id"

            # Setup data for results
            zip_name = f"Dataset_{data_id}_{version_id}.zip"
            path = os.path.join(directory, zip_name)

            runner = CliRunner()

            # CALL
            result = runner.invoke(download, ["dataset", data_id, version_id])

            # ASSERT
            mock_instance.download_dataset_files.assert_called_once_with(
                processed_jwt_fixture["jwt"]
            )

            mock_zip.assert_called_once_with(path, file_names, file_contents)

            mock_instance.output_datafiles_table.assert_called_once()

            assert result.exit_code == 0

        @patch("dafni_cli.commands.download.os.getcwd")
        @patch("dafni_cli.commands.download.write_files_to_zip")
        def test_file_details_processed_correctly_in_given_directory(
            self,
            mock_zip,
            mock_os,
            mock_jwt,
            mock_get,
            mock_dataset,
            processed_jwt_fixture,
            dataset_metadata_fixture,
        ):
            # SETUP
            mock_get.return_value = dataset_metadata_fixture
            mock_jwt.return_value = processed_jwt_fixture, False
            directory = "test"
            mock_os.return_value = directory

            # Setup DatasetMetadata mock instance
            mock_instance = MagicMock()
            files = PropertyMock(return_value=["files"])
            type(mock_instance).files = files

            file_names = ["file_1.txt", "file_2.pdf", "file_3.csv"]
            file_contents = [b"file 1", b"file 2", b"file 3"]
            mock_instance.download_dataset_files.return_value = (
                file_names,
                file_contents,
            )

            mock_dataset.return_value = mock_instance

            # Setup data for call
            data_id = "dataset id"
            version_id = "version id"

            # Setup data fro results
            zip_name = f"Dataset_{data_id}_{version_id}.zip"
            path = os.path.join(directory, zip_name)

            runner = CliRunner()

            # CALL
            with runner.isolated_filesystem():
                # Make directory for write zip file to
                os.mkdir(directory)

                result = runner.invoke(
                    download, ["dataset", data_id, version_id, "--directory", directory]
                )

            # ASSERT
            mock_instance.download_dataset_files.assert_called_once_with(
                processed_jwt_fixture["jwt"]
            )

            mock_zip.assert_called_once_with(path, file_names, file_contents)

            mock_instance.output_datafiles_table.assert_called_once()

            assert result.stdout == (
                "\nThe dataset files have been downloaded to: \ntest\\Dataset_dataset id_version id.zip\n"
            )

            assert result.exit_code == 0

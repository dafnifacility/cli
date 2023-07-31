from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from dafni_cli.commands import download


@patch("dafni_cli.commands.download.DAFNISession")
class TestDownload(TestCase):
    """Test class to test the download command"""

    @patch("dafni_cli.commands.download.parse_dataset_metadata")
    def test_session_retrieved_and_set_on_context(self, _, mock_DAFNISession):
        """Tests that the session is created in the click context"""
        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        ctx = {}

        # CALL
        result = runner.invoke(download.download, ["dataset", "version-id"], obj=ctx)

        # ASSERT
        mock_DAFNISession.assert_called_once()

        self.assertEqual(ctx["session"], session)
        self.assertEqual(result.exit_code, 0)


@patch("dafni_cli.commands.download.DAFNISession")
@patch("dafni_cli.commands.download.cli_get_latest_dataset_metadata")
@patch("dafni_cli.commands.download.parse_dataset_metadata")
@patch("dafni_cli.commands.download.download_dataset")
class TestDownloadDataset(TestCase):
    """Test class to test the download dataset command"""

    def test_download_dataset(
        self,
        mock_download_dataset,
        mock_parse_dataset_metadata,
        mock_cli_get_latest_dataset_metadata,
        mock_DAFNISession,
    ):
        """Tests that the 'download dataset' command works correctly (with no
        optional arguments)"""
        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()

        version_id = "version-id"
        file_names = ["file_name1", "file_name2"]
        file_contents = ["file_contents1", "file_contents2"]
        metadata = MagicMock()
        metadata.dataset_id = "dataset-id"
        metadata.files = [MagicMock(), MagicMock()]
        metadata.download_dataset_files = MagicMock()
        metadata.download_dataset_files.return_value = (
            file_names,
            file_contents,
        )
        mock_parse_dataset_metadata.return_value = metadata

        # CALL
        result = runner.invoke(download.download, ["dataset", version_id])

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_cli_get_latest_dataset_metadata.assert_called_once_with(
            session, version_id
        )
        mock_parse_dataset_metadata.assert_called_once_with(
            mock_cli_get_latest_dataset_metadata.return_value
        )

        mock_download_dataset.assert_called_once_with(
            session,
            metadata.files,
            None,
        )

        self.assertEqual(result.exit_code, 0)

    def test_download_dataset_with_specific_directory(
        self,
        mock_download_dataset,
        mock_parse_dataset_metadata,
        mock_cli_get_latest_dataset_metadata,
        mock_DAFNISession,
    ):
        """Tests that the 'download dataset' command works correctly with a
        specific directory specified"""
        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()

        version_id = "version-id"
        file_names = ["file_name1", "file_name2"]
        file_contents = [b"file_contents1", b"file_contents2"]
        directory = "some_folder"
        metadata = MagicMock()
        metadata.dataset_id = "dataset-id"
        metadata.files = [MagicMock(), MagicMock()]
        metadata.download_dataset_files = MagicMock()
        metadata.download_dataset_files.return_value = (
            file_names,
            file_contents,
        )
        mock_parse_dataset_metadata.return_value = metadata

        # CALL
        with runner.isolated_filesystem():
            Path(directory).mkdir()

            result = runner.invoke(
                download.download,
                ["dataset", version_id, "--directory", directory],
            )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_cli_get_latest_dataset_metadata.assert_called_once_with(
            session, version_id
        )
        mock_parse_dataset_metadata.assert_called_once_with(
            mock_cli_get_latest_dataset_metadata.return_value
        )

        mock_download_dataset.assert_called_once_with(
            session,
            metadata.files,
            Path(directory),
        )

        self.assertEqual(result.exit_code, 0)

    def test_download_dataset_with_no_files(
        self,
        mock_download_dataset,
        mock_parse_dataset_metadata,
        mock_cli_get_latest_dataset_metadata,
        mock_DAFNISession,
    ):
        """Tests that the 'download dataset' command works correctly when
        there are no files to download"""
        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        metadata = MagicMock()
        metadata.dataset_id = "dataset-id"
        metadata.files = []
        mock_parse_dataset_metadata.return_value = metadata

        # CALL
        result = runner.invoke(download.download, ["dataset", "version-id"])

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_cli_get_latest_dataset_metadata.assert_called_once_with(
            session, "version-id"
        )
        mock_parse_dataset_metadata.assert_called_once_with(
            mock_cli_get_latest_dataset_metadata.return_value
        )
        mock_download_dataset.assert_not_called()

        self.assertEqual(
            result.output,
            "There are no files currently associated with the Dataset to download\n",
        )

        self.assertEqual(result.exit_code, 0)

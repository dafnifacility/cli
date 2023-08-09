from pathlib import Path
from typing import List, Optional
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


class TestDownloadDataset(TestCase):
    """Test class to test the download dataset command"""

    def setUp(self) -> None:
        super().setUp()

        self.mock_DAFNISession = patch(
            "dafni_cli.commands.download.DAFNISession"
        ).start()
        self.mock_cli_get_latest_dataset_metadata = patch(
            "dafni_cli.commands.download.cli_get_latest_dataset_metadata"
        ).start()
        self.mock_cli_select_dataset_files = patch(
            "dafni_cli.commands.download.cli_select_dataset_files"
        ).start()
        self.mock_parse_dataset_metadata = patch(
            "dafni_cli.commands.download.parse_dataset_metadata"
        ).start()
        self.mock_download_dataset = patch(
            "dafni_cli.commands.download.download_dataset"
        ).start()

        self.mock_session = MagicMock()
        self.mock_DAFNISession.return_value = self.mock_session

        # Mock metadata and files
        self.version_id = "version-id"
        file_names = ["file_name1", "file_name2"]
        file_contents = ["file_contents1", "file_contents2"]
        self.metadata = MagicMock()
        self.metadata.dataset_id = "dataset-id"
        self.metadata.files = [MagicMock(), MagicMock()]
        self.metadata.download_dataset_files = MagicMock()
        self.metadata.download_dataset_files.return_value = (
            file_names,
            file_contents,
        )
        self.selected_dataset_files = [MagicMock() for file in self.metadata.files]
        self.mock_parse_dataset_metadata.return_value = self.metadata
        self.mock_cli_select_dataset_files.return_value = self.selected_dataset_files

        self.addCleanup(patch.stopall)

    def _run_command(
        self,
        directory: str,
        file_names: Optional[List[str]],
        file_regex: Optional[str],
    ):
        """Executes the 'download dataset' command and returns the result"""
        runner = CliRunner()

        with runner.isolated_filesystem():
            args = ["dataset", self.version_id]
            if directory:
                args.extend(["--directory", directory])
                Path(directory).mkdir()
            if file_names:
                for file_name in file_names:
                    args.extend(["--file", file_name])
            if file_regex:
                args.extend(["--regex", file_regex])

            result = runner.invoke(download.download, args)

        return result

    def test_download_dataset(
        self,
    ):
        """Tests that the 'download dataset' command works correctly (with no
        optional arguments)"""

        # CALL
        result = self._run_command(directory=None, file_names=None, file_regex=None)

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_cli_get_latest_dataset_metadata.assert_called_once_with(
            self.mock_session, self.version_id
        )
        self.mock_parse_dataset_metadata.assert_called_once_with(
            self.mock_cli_get_latest_dataset_metadata.return_value
        )
        self.mock_cli_select_dataset_files.assert_called_once_with(
            self.metadata, file_names=None, file_regex=None
        )

        self.mock_download_dataset.assert_called_once_with(
            self.mock_session,
            self.selected_dataset_files,
            None,
        )

        self.assertEqual(result.exit_code, 0)

    def test_download_dataset_with_specific_directory(
        self,
    ):
        """Tests that the 'download dataset' command works correctly with a
        specific directory specified"""

        # SETUP
        directory = "some_folder"

        # CALL
        result = self._run_command(
            directory=directory, file_names=None, file_regex=None
        )

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_cli_get_latest_dataset_metadata.assert_called_once_with(
            self.mock_session, self.version_id
        )
        self.mock_parse_dataset_metadata.assert_called_once_with(
            self.mock_cli_get_latest_dataset_metadata.return_value
        )
        self.mock_cli_select_dataset_files.assert_called_once_with(
            self.metadata, file_names=None, file_regex=None
        )

        self.mock_download_dataset.assert_called_once_with(
            self.mock_session,
            self.selected_dataset_files,
            Path(directory),
        )

        self.assertEqual(result.exit_code, 0)

    def test_download_dataset_with_no_files(
        self,
    ):
        """Tests that the 'download dataset' command works correctly when
        there are no files to download"""

        # SETUP
        self.metadata.files = []

        # CALL
        result = self._run_command(directory=None, file_names=None, file_regex=None)

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_cli_get_latest_dataset_metadata.assert_called_once_with(
            self.mock_session, self.version_id
        )
        self.mock_parse_dataset_metadata.assert_called_once_with(
            self.mock_cli_get_latest_dataset_metadata.return_value
        )
        self.mock_cli_select_dataset_files.assert_not_called()
        self.mock_download_dataset.assert_not_called()

        self.assertEqual(
            result.output,
            "There are no files currently associated with the Dataset to download\n",
        )

        self.assertEqual(result.exit_code, 0)

    def test_download_dataset_with_file_names_and_regex_given(
        self,
    ):
        """Tests that the 'download dataset' command works correctly (when given
        a list of file names and regex to match to)"""

        # CALL
        file_names = ["filename1.zip", "filename2.zip"]
        file_regex = r"^.+\.csv"
        result = self._run_command(
            directory=None, file_names=file_names, file_regex=file_regex
        )

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_cli_get_latest_dataset_metadata.assert_called_once_with(
            self.mock_session, self.version_id
        )
        self.mock_parse_dataset_metadata.assert_called_once_with(
            self.mock_cli_get_latest_dataset_metadata.return_value
        )
        self.mock_cli_select_dataset_files.assert_called_once_with(
            self.metadata, file_names=tuple(file_names), file_regex=file_regex
        )

        self.mock_download_dataset.assert_called_once_with(
            self.mock_session,
            self.selected_dataset_files,
            None,
        )

        self.assertEqual(result.exit_code, 0)

    def test_download_dataset_with_no_selected_files(
        self,
    ):
        """Tests that the 'download dataset' command works correctly when
        there are no selected files to download"""

        # SETUP
        self.selected_dataset_files = []
        self.mock_cli_select_dataset_files.return_value = self.selected_dataset_files

        # CALL
        result = self._run_command(directory=None, file_names=None, file_regex=None)

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_cli_get_latest_dataset_metadata.assert_called_once_with(
            self.mock_session, self.version_id
        )
        self.mock_parse_dataset_metadata.assert_called_once_with(
            self.mock_cli_get_latest_dataset_metadata.return_value
        )
        self.mock_cli_select_dataset_files.assert_called_once_with(
            self.metadata, file_names=None, file_regex=None
        )
        self.mock_download_dataset.assert_not_called()

        self.assertEqual(
            result.output,
            "No files selected to download\n",
        )

        self.assertEqual(result.exit_code, 0)

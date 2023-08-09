from pathlib import Path
from typing import Optional
from unittest import TestCase
from unittest.mock import MagicMock, call, mock_open, patch

import dafni_cli.datasets.dataset_download as dataset_download
from dafni_cli.api.parser import ParserBaseObject
from dafni_cli.consts import DOWNLOAD_CHUNK_SIZE
from dafni_cli.datasets.dataset_metadata import DataFile
from dafni_cli.tests.fixtures.dataset_metadata import TEST_DATASET_METADATA_DATAFILE


class TestDownloadDataset(TestCase):
    """Test class to test download_dataset works as expected"""

    def setUp(self) -> None:
        super().setUp()

        self.mock_click = patch("dafni_cli.datasets.dataset_download.click").start()
        self.mock_OverallFileProgressBar = patch(
            "dafni_cli.datasets.dataset_download.OverallFileProgressBar"
        ).start()
        self.mock_minio_get_request = patch(
            "dafni_cli.datasets.dataset_download.minio_get_request"
        ).start()
        self.open_mock = patch("builtins.open", new_callable=mock_open).start()
        self.mock_tqdm = patch("dafni_cli.datasets.dataset_download.tqdm").start()

        self.addCleanup(patch.stopall)

    def _test_download_dataset(self, directory: Optional[Path]):
        """Tests that download_dataset works as expected when given a
        particular value of 'directory'"""

        # SETUP
        session = MagicMock()
        files = [
            ParserBaseObject.parse_from_dict(DataFile, TEST_DATASET_METADATA_DATAFILE),
            ParserBaseObject.parse_from_dict(DataFile, TEST_DATASET_METADATA_DATAFILE),
        ]
        # Ensure second file has a different name
        files[1].name = "test.csv"

        mock_file_size = files[0].size
        mock_download_response = MagicMock()
        mock_download_response.headers.get = MagicMock(return_value=mock_file_size)
        mock_download_response_chunks = [MagicMock(), MagicMock()]
        mock_download_response.iter_content.return_value = mock_download_response_chunks

        self.mock_minio_get_request.return_value.__enter__.return_value = (
            mock_download_response
        )

        expected_total_file_size = sum(file.size for file in files)
        if directory is None:
            expected_directory = Path.cwd()
        else:
            expected_directory = directory

        # CALL
        dataset_download.download_dataset(
            session=session, files=files, directory=directory
        )

        # ASSERT
        self.mock_OverallFileProgressBar.assert_called_once_with(
            len(files), expected_total_file_size
        )
        self.mock_OverallFileProgressBar.return_value.__enter__.assert_called_once()
        self.assertEqual(
            self.mock_minio_get_request.call_args_list,
            [call(session, file.download_url, stream=True) for file in files],
        )
        self.assertEqual(
            mock_download_response.headers.get.call_args_list,
            [call("content-length", 0) for file in files],
        )
        self.assertEqual(
            self.open_mock.call_args_list,
            [call(expected_directory / file.name, "wb") for file in files],
        )
        self.assertEqual(
            self.mock_tqdm.wrapattr.call_args_list,
            [
                call(
                    self.open_mock.return_value.__enter__.return_value,
                    "write",
                    desc=file.name,
                    miniters=1,
                    total=mock_file_size,
                )
                for file in files
            ],
        )
        self.assertEqual(
            mock_download_response.iter_content.call_args_list,
            [call(chunk_size=DOWNLOAD_CHUNK_SIZE) for file in files],
        )
        self.assertEqual(
            self.mock_tqdm.wrapattr.return_value.__enter__.return_value.write.call_args_list,
            [call(chunk) for file in files for chunk in mock_download_response_chunks],
        )
        self.assertEqual(
            self.mock_click.echo.call_args_list,
            [
                call("Downloading files..."),
                call(),
                call(),
                call(f"Downloaded files to '{expected_directory}'"),
            ],
        )

    def test_download_dataset(self):
        """Tests that download_dataset works as expected when no directory
        is given"""
        self._test_download_dataset(directory=None)

    def test_download_dataset_given_directory(self):
        """Tests that download_dataset works as expected when a directory is
        given"""
        self._test_download_dataset(directory=Path("some/test/directory"))

import pytest
from mock import patch, call

from dafni_cli.datasets.dataset_metadata import DataFile, DatasetMeta
from dafni_cli.consts import CONSOLE_WIDTH, DATA_FORMATS


class TestDataFile:
    "Test class to test the DataFile Class"

    @patch("dafni_cli.datasets.dataset_metadata.process_file_size")
    @patch("dafni_cli.datasets.dataset_metadata.check_key_in_dict")
    class TestInit:
        """Test class to test the DataFile.init functionality"""

        def test_attributes_set_correctly(self, mock_check, mock_process):
            # SETUP
            mock_check.return_value = "Mock Check"
            mock_process.return_value = "Mock Size"

            file_dict = {"key": "value"}

            # CALL
            instance = DataFile(file_dict)

            # ASSERT
            assert instance.name == "Mock Check"
            assert instance.size == "Mock Size"
            assert instance.format == ""

        def test_util_functions_called_correctly(self, mock_check, mock_process):
            # SETUP
            mock_check.return_value = "Mock Check"
            mock_process.return_value = "Mock Size"

            file_dict = {"key": "value"}

            # CALL
            DataFile(file_dict)

            # ASSERT
            assert mock_check.call_args_list == [
                call(file_dict, "spdx:fileName"),
                call(file_dict, "dcat:byteSize", default=None),
                call(file_dict, "dcat:mediaType"),
            ]
            mock_process.assert_called_once_with("Mock Check")

        @pytest.mark.parametrize(
            "file_format, expected",
            [
                ("application/octet-stream", "Binary"),
                ("application/pdf", "PDF"),
                ("application/vnd.ms-excel", "Excel"),
                (
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "Excel",
                ),
                ("application/zip", "ZIP"),
                ("text/csv", "CSV"),
                ("text/plain", "Text"),
            ],
        )
        def test_format_mapped_correctly(
            self, mock_check, mock_process, file_format, expected
        ):
            # SETUP
            mock_check.side_effect = ("mock name", "mock size", file_format)
            mock_process.return_value = "Mock Size"

            file_dict = {"key": "value"}

            # CALL
            instance = DataFile(file_dict)

            # ASSERT
            assert instance.format == expected


class TestDatasetMeta:
    """Test class for the DatasetMeta class"""

    class TestInit:
        "Test class for the DatasetMeta.__init__() function"

        def test_the_correct_attributes_are_created(self):
            # SETUP
            none_keys = [
                "created",
                "creator",
                "contact",
                "description",
                "identifier",
                "location",
                "start_date",
                "end_date",
                "themes",
                "publisher",
                "issued",
                "rights",
                "language",
                "standard",
                "update",
            ]
            array_keys = ["files", "keywords"]

            # CALL
            instance = DatasetMeta()

            # ASSERT
            assert all(getattr(instance, key) is None for key in none_keys)
            assert all(getattr(instance, key) == [] for key in array_keys)

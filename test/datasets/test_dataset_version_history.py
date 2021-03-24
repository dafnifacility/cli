import pytest
from mock import patch, call

from dafni_cli.datasets.dataset_version_history import DatasetVersionHistory
from dafni_cli.datasets.dataset_metadata import DatasetMetadata
from dafni_cli.consts import CONSOLE_WIDTH, DATA_FORMATS, TAB_SPACE

from test.fixtures.jwt_fixtures import JWT
from test.fixtures.dataset_fixtures import (
    dataset_metadata_fixture,
    datafile_mock,
    dataset_meta_mock,
)


class TestDatasetVersionHistory:
    """Test class to test the DatasetVersionHistory Class"""

    class TestInit:
        """Test class to test the DataFile constructor"""

        def test_dataset_version_history_has_expected_attributes(self):
            # SETUP
            expected_attributes = ["jwt", "dataset_id", "versions", "version_ids"]
            # CALL
            instance = DatasetVersionHistory()
            # ASSERT
            assert all(
                getattr(instance, value) is None for value in expected_attributes
            )

        @patch.object(DatasetVersionHistory, "set_details_from_dict")
        def test_helper_functions_called_correctly(
            self, mock_set, dataset_metadata_fixture
        ):
            # SETUP
            jwt = JWT
            metadata = dataset_metadata_fixture
            # CALL
            instance = DatasetVersionHistory(jwt, metadata)
            # ASSERT
            assert instance.jwt == jwt
            mock_set.assert_called_once_with(metadata)

    class TestSetDetailsFromDict:
        """Test class to test the set_details_from_dict functionality"""

        @patch("dafni_cli.datasets.dataset_version_history.check_key_in_dict")
        def test_helper_functions_called_correctly(
            self, mock_check, dataset_metadata_fixture
        ):
            # SETUP
            mock_check.side_effect = ("Dataset", ["Version_1"], "Version ID")

            instance = DatasetVersionHistory()

            # CALL
            instance.set_details_from_dict(dataset_metadata_fixture)

            # ASSERT
            assert mock_check.call_args_list == [
                call(dataset_metadata_fixture, ["version_history", "dataset_uuid"]),
                call(
                    dataset_metadata_fixture,
                    ["version_history", "versions"],
                    default=[],
                ),
                call("Version_1", ["version_uuid"], default=None),
            ]

        def test_attributes_set_correctly_with_valid_metadata(
            self, dataset_metadata_fixture
        ):
            # SETUP
            instance = DatasetVersionHistory()
            # CALL
            instance.set_details_from_dict(dataset_metadata_fixture)
            # ASSERT

            assert (
                instance.dataset_id
                == dataset_metadata_fixture["version_history"]["dataset_uuid"]
            )
            assert (
                instance.versions
                == dataset_metadata_fixture["version_history"]["versions"]
            )
            assert instance.version_ids == [
                dataset_metadata_fixture["version_history"]["versions"][0][
                    "version_uuid"
                ]
            ]

    @patch.object(DatasetMetadata, "output_version_details")
    @patch.object(DatasetMetadata, "__init__")
    @patch("dafni_cli.datasets.dataset_version_history.get_latest_dataset_metadata")
    class TestProcessVersionHistory:
        """Test class to test the process_version_history functionality"""

        @pytest.mark.parametrize(
            "version_ids", [[], ["version_1"], ["version_1", "version_2"]]
        )
        def test_helper_functions_called_correctly(
            self, mock_get, mock_init, mock_output, version_ids
        ):
            # SETUP
            mock_init.return_value = None
            mock_get.return_value = "Meta data"

            instance = DatasetVersionHistory()

            instance.version_ids = version_ids
            instance.jwt = JWT
            instance.dataset_id = "dataset id"

            # CALL
            instance.process_version_history()

            # ASSERT
            assert mock_get.call_args_list == [
                call(instance.jwt, instance.dataset_id, version_id)
                for version_id in version_ids
            ]
            assert mock_output.call_count == len(version_ids)
            assert mock_init.call_args_list == [
                call("Meta data", version_id=version_id) for version_id in version_ids
            ]
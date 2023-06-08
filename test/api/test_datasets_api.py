from unittest import TestCase
from unittest.mock import MagicMock

from dafni_cli.api import datasets_api
from dafni_cli.api.exceptions import EndpointNotFoundError, ResourceNotFoundError
from dafni_cli.consts import NID_API_URL, SEARCH_AND_DISCOVERY_API_URL


class TestDatasetsAPI(TestCase):
    """Test class to test the functions in datasets_api.py"""

    def test_get_all_datasets(self):
        """Tests that get_all_datasets works as expected"""

        # SETUP
        session = MagicMock()
        filters = {
            "search_text": "Some search text",
            "date_range": {"begin": "Start Date", "end": "End Date"},
        }

        # CALL
        result = datasets_api.get_all_datasets(session, filters)

        # ASSERT
        session.post_request.assert_called_once_with(
            url=f"{SEARCH_AND_DISCOVERY_API_URL}/catalogue/",
            json={"offset": {"start": 0, "size": 1000}, "sort_by": "recent", **filters},
            allow_redirect=True,
        )
        self.assertEqual(result, session.post_request.return_value)

    def test_get_latest_dataset_metadata(self):
        """Tests that get_latest_dataset_metadata works as expected"""

        # SETUP
        session = MagicMock()
        version_id = "some-version-id"

        # CALL
        result = datasets_api.get_latest_dataset_metadata(session, version_id)

        # ASSERT
        session.get_request.assert_called_once_with(
            url=f"{SEARCH_AND_DISCOVERY_API_URL}/metadata/{version_id}",
            allow_redirect=True,
        )
        self.assertEqual(result, session.get_request.return_value)

    def test_get_latest_dataset_metadata_raises_resource_not_found(self):
        """Tests that get_latest_dataset_metadata handles an
        EndpointNotFoundError as expected"""

        # SETUP
        session = MagicMock()
        version_id = "some-version-id"
        session.get_request.side_effect = EndpointNotFoundError(
            "Some 404 error message"
        )

        # CALL
        with self.assertRaises(ResourceNotFoundError) as err:
            datasets_api.get_latest_dataset_metadata(session, version_id)

        # ASSERT
        self.assertEqual(
            str(err.exception),
            f"Unable to find a dataset with version_id '{version_id}'",
        )

    def test_delete_dataset(self):
        """Tests that delete_dataset works as expected"""

        # SETUP
        session = MagicMock()
        dataset_id = "dataset-id"

        # CALL
        result = datasets_api.delete_dataset(session, dataset_id=dataset_id)

        # ASSERT
        session.delete_request.assert_called_once_with(
            f"{NID_API_URL}/nid/dataset/{dataset_id}",
        )
        self.assertEqual(result, session.delete_request.return_value)

    def test_delete_dataset_version(self):
        """Tests that delete_dataset_version works as expected"""

        # SETUP
        session = MagicMock()
        dataset_id = "dataset-id"
        version_id = "version-id"

        # CALL
        result = datasets_api.delete_dataset_version(
            session, dataset_id=dataset_id, version_id=version_id
        )

        # ASSERT
        session.delete_request.assert_called_once_with(
            f"{NID_API_URL}/nid/dataset/{dataset_id}/{version_id}",
        )
        self.assertEqual(result, session.delete_request.return_value)

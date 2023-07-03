from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, mock_open, patch

from dafni_cli.api import workflows_api
from dafni_cli.api.exceptions import EndpointNotFoundError, ResourceNotFoundError
from dafni_cli.consts import NIMS_API_URL


class TestWorkflowsAPI(TestCase):
    """Test class to test the functions in workflows_api.py"""

    def test_get_all_workflows(self):
        """Tests that get_all_workflows works as expected"""

        # SETUP
        session = MagicMock()

        # CALL
        result = workflows_api.get_all_workflows(session)

        # ASSERT
        session.get_request.assert_called_once_with(
            f"{NIMS_API_URL}/workflows/",
        )
        self.assertEqual(result, session.get_request.return_value)

    def test_get_workflow(self):
        """Tests that get_workflow works as expected"""

        # SETUP
        session = MagicMock()
        version_id = "some-workflow-version-id"

        # CALL
        result = workflows_api.get_workflow(session, version_id=version_id)

        # ASSERT
        session.get_request.assert_called_once_with(
            f"{NIMS_API_URL}/workflows/{version_id}/",
        )
        self.assertEqual(result, session.get_request.return_value)

    def test_get_workflow_raises_resource_not_found(self):
        """Tests that get_workflow handles an EndpointNotFoundError as
        expected"""

        # SETUP
        session = MagicMock()
        version_id = "some-workflow-version-id"
        session.get_request.side_effect = EndpointNotFoundError(
            "Some 404 error message"
        )

        # CALL
        with self.assertRaises(ResourceNotFoundError) as err:
            workflows_api.get_workflow(session, version_id=version_id)

        # ASSERT
        self.assertEqual(
            str(err.exception),
            f"Unable to find a workflow with version id '{version_id}'",
        )

    def test_get_workflow_instance(self):
        """Tests that get_workflow_instance works as expected"""

        # SETUP
        session = MagicMock()
        instance_id = "some-instance-id"

        # CALL
        result = workflows_api.get_workflow_instance(session, instance_id=instance_id)

        # ASSERT
        session.get_request.assert_called_once_with(
            f"{NIMS_API_URL}/workflows/instances/{instance_id}/",
        )
        self.assertEqual(result, session.get_request.return_value)

    def test_get_workflow_instance_raises_resource_not_found(self):
        """Tests that get_workflow_instance handles an EndpointNotFoundError as
        expected"""

        # SETUP
        session = MagicMock()
        instance_id = "some-instance-id"
        session.get_request.side_effect = EndpointNotFoundError(
            "Some 404 error message"
        )

        # CALL
        with self.assertRaises(ResourceNotFoundError) as err:
            workflows_api.get_workflow_instance(session, instance_id=instance_id)

        # ASSERT
        self.assertEqual(
            str(err.exception),
            f"Unable to find a workflow instance with instance id '{instance_id}'",
        )

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""
        {
            \"test_data\": \"test_data\"
        }""",
    )
    def test_upload_workflow(
        self,
        open_mock,
    ):
        """Tests that upload_workflow works as expected without a parent"""
        # SETUP
        session = MagicMock()
        file_path = Path("path/to/file")
        version_message = "Version message"

        # CALL
        result = workflows_api.upload_workflow(
            session, file_path=file_path, version_message=version_message
        )

        # ASSERT
        open_mock.assert_called_once_with(file_path, "r", encoding="utf-8")
        session.post_request.assert_called_once_with(
            url=f"{NIMS_API_URL}/workflows/upload/",
            json={
                "version_message": version_message,
                "definition": {
                    "test_data": "test_data",
                },
            },
        )
        self.assertEqual(result, session.post_request.return_value)

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""
        {
            \"test_data\": \"test_data\"
        }""",
    )
    def test_upload_workflow_with_parent(
        self,
        open_mock,
    ):
        """Tests that upload_workflow works as expected with a parent"""
        # SETUP
        session = MagicMock()
        file_path = Path("path/to/file")
        version_message = "Version message"
        parent_id = "parent-id"

        # CALL
        result = workflows_api.upload_workflow(
            session,
            file_path=file_path,
            version_message=version_message,
            parent_id=parent_id,
        )

        # ASSERT
        open_mock.assert_called_once_with(file_path, "r", encoding="utf-8")
        session.post_request.assert_called_once_with(
            url=f"{NIMS_API_URL}/workflows/{parent_id}/upload/",
            json={
                "version_message": version_message,
                "definition": {
                    "test_data": "test_data",
                },
            },
        )
        self.assertEqual(result, session.post_request.return_value)

    def test_delete_workflow_version(self):
        """Tests that delete_workflow_version works as expected"""

        # SETUP
        session = MagicMock()
        version_id = "version-id"

        # CALL
        result = workflows_api.delete_workflow_version(session, version_id=version_id)

        # ASSERT
        session.delete_request.assert_called_once_with(
            f"{NIMS_API_URL}/workflows/{version_id}",
        )
        self.assertEqual(result, session.delete_request.return_value)

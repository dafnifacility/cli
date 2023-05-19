from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, mock_open, patch

from dafni_cli.api import workflows_api
from dafni_cli.api.exceptions import EndpointNotFoundError, ResourceNotFoundError
from dafni_cli.consts import WORKFLOWS_API_URL


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
            f"{WORKFLOWS_API_URL}/workflows/",
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
            f"{WORKFLOWS_API_URL}/workflows/{version_id}/",
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

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""
        {
            \"version_message\": \"initial version message\",
            \"other_data\": \"other_data\"
        }""",
    )
    def test_upload_workflow(
        self,
        open_mock,
    ):
        """Tests that upload_workflow works as expected without a parent or
        overridden version_message"""
        # SETUP
        session = MagicMock()
        file_path = Path("path/to/file")

        # CALL
        result = workflows_api.upload_workflow(session, file_path=file_path)

        # ASSERT
        open_mock.assert_called_once_with(file_path, "r", encoding="utf-8")
        session.post_request.assert_called_once_with(
            url=f"{WORKFLOWS_API_URL}/workflows/upload/",
            json={
                "version_message": "initial version message",
                "other_data": "other_data",
            },
        )
        self.assertEqual(result, session.post_request.return_value)

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""
        {
            \"version_message\": \"initial version message\",
            \"other_data\": \"other_data\"
        }""",
    )
    def test_upload_workflow_with_overridden_version_message(
        self,
        open_mock,
    ):
        """Tests that upload_workflow works as expected with an overridden
        version_message and no parent"""
        # SETUP
        session = MagicMock()
        version_message = "Version message"
        file_path = Path("path/to/file")

        # CALL
        result = workflows_api.upload_workflow(
            session, file_path=file_path, version_message=version_message
        )

        # ASSERT
        open_mock.assert_called_once_with(file_path, "r", encoding="utf-8")
        session.post_request.assert_called_once_with(
            url=f"{WORKFLOWS_API_URL}/workflows/upload/",
            json={
                "version_message": version_message,
                "other_data": "other_data",
            },
        )
        self.assertEqual(result, session.post_request.return_value)

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""
        {
            \"version_message\": \"initial version message\",
            \"other_data\": \"other_data\"
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
        parent_id = "parent-id"

        # CALL
        result = workflows_api.upload_workflow(
            session, file_path=file_path, parent_id=parent_id
        )

        # ASSERT
        open_mock.assert_called_once_with(file_path, "r", encoding="utf-8")
        session.post_request.assert_called_once_with(
            url=f"{WORKFLOWS_API_URL}/workflows/{parent_id}/upload/",
            json={
                "version_message": "initial version message",
                "other_data": "other_data",
            },
        )
        self.assertEqual(result, session.post_request.return_value)

    def test_delete_workflow(self):
        """Tests that delete_workflow works as expected"""

        # SETUP
        session = MagicMock()
        version_id = "version-id"

        # CALL
        result = workflows_api.delete_workflow(session, version_id=version_id)

        # ASSERT
        session.delete_request.assert_called_once_with(
            f"{WORKFLOWS_API_URL}/workflows/{version_id}",
        )
        self.assertEqual(result, session.delete_request.return_value)

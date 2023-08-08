from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, mock_open, patch

import requests

from dafni_cli.api import workflows_api
from dafni_cli.api.exceptions import (
    DAFNIError,
    EndpointNotFoundError,
    ResourceNotFoundError,
    ValidationError,
)
from dafni_cli.consts import NIMS_API_URL
from dafni_cli.tests.fixtures.session import (
    create_mock_error_response,
    create_mock_response,
)
from dafni_cli.utils import construct_validation_errors_from_dict


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
            f"{NIMS_API_URL}/workflows/{version_id}/",
        )
        self.assertEqual(result, session.delete_request.return_value)

    def test_validate_parameter_set_definition_error_message_func_when_error_found(
        self,
    ):
        """Tests that _validate_parameter_set_definition_error_message_func
        functions as expected when the session object returns an error message"""

        # SETUP
        session = MagicMock()
        session.get_error_message = MagicMock()
        error_message_func = (
            workflows_api._validate_parameter_set_definition_error_message_func(session)
        )
        mock_response = create_mock_error_response()

        # CALL
        error_message = error_message_func(mock_response)

        # ASSERT
        self.assertEqual(error_message, session.get_error_message.return_value)

    def test_validate_parameter_set_definition_error_message_func_validation_error(
        self,
    ):
        """Tests that _validate_parameter_set_definition_error_message_func
        functions as expected when validation errors are returned under a
        dictionary similar to the definition that would have been uploaded
        """

        # SETUP
        session = MagicMock()
        session.get_error_message = MagicMock(return_value=None)
        error_message_func = (
            workflows_api._validate_parameter_set_definition_error_message_func(session)
        )
        mock_response = create_mock_response(
            400,
            {
                "api_version": ["This field is required."],
                "kind": ["This field is required."],
                "metadata": ["This field is required."],
            },
        )

        # CALL
        error_message = error_message_func(mock_response)

        # ASSERT
        self.assertEqual(
            error_message,
            "Found the following errors in the definition:\n"
            + "\n".join(construct_validation_errors_from_dict(mock_response.json())),
        )

    def test_validate_parameter_set_definition_error_message_func_handles_decode_error(
        self,
    ):
        """Tests _validate_parameter_set_definition_error_message_func when
        JSON decoding fails"""

        # SETUP
        session = MagicMock()
        session.get_error_message = MagicMock(return_value=None)
        error_message_func = (
            workflows_api._validate_parameter_set_definition_error_message_func(session)
        )
        mock_response = create_mock_error_response()
        mock_response.json.side_effect = requests.JSONDecodeError("", "", 0)

        # CALL
        error_message = error_message_func(mock_response)

        # ASSERT
        self.assertEqual(error_message, None)

    @patch("builtins.open", new_callable=mock_open, read_data="definition file")
    @patch(
        "dafni_cli.api.workflows_api._validate_parameter_set_definition_error_message_func"
    )
    def test_validate_parameter_set_definition(
        self, mock_error_message_func, open_mock
    ):
        """Tests that validate_parameter_set_definition works as expected
        when the definition is found to be valid"""

        # SETUP
        session = MagicMock()
        parameter_set_definition_path = Path("path/to/file")
        session.post_request.return_value = create_mock_response(200)

        # CALL
        workflows_api.validate_parameter_set_definition(
            session, parameter_set_definition_path=parameter_set_definition_path
        )

        # ASSERT
        open_mock.assert_called_once_with(parameter_set_definition_path, "rb")
        session.post_request.assert_called_once_with(
            url=f"{NIMS_API_URL}/workflows/parameter-set/validate/",
            data=open(parameter_set_definition_path, "rb"),
            error_message_func=mock_error_message_func.return_value,
        )

    @patch("builtins.open", new_callable=mock_open, read_data="definition file")
    @patch(
        "dafni_cli.api.workflows_api._validate_parameter_set_definition_error_message_func"
    )
    def test_validate_parameter_set_definition_when_def_invalid(
        self, mock_error_message_func, open_mock
    ):
        """Tests that validate_parameter_set_definition works as expected
        when the definition is found to be invalid"""

        # SETUP
        session = MagicMock()
        parameter_set_definition_path = Path("path/to/file")
        error = DAFNIError("Some error message")
        session.post_request.side_effect = error

        # CALL
        with self.assertRaises(ValidationError) as err:
            workflows_api.validate_parameter_set_definition(
                session, parameter_set_definition_path=parameter_set_definition_path
            )

        # ASSERT
        open_mock.assert_called_once_with(parameter_set_definition_path, "rb")
        session.post_request.assert_called_once_with(
            url=f"{NIMS_API_URL}/workflows/parameter-set/validate/",
            data=open(parameter_set_definition_path, "rb"),
            error_message_func=mock_error_message_func.return_value,
        )
        self.assertEqual(
            str(err.exception),
            "Parameter set definition validation failed with the following "
            f"message:\n\n{str(error)}",
        )

    @patch("builtins.open", new_callable=mock_open, read_data="definition file")
    @patch(
        "dafni_cli.api.workflows_api._validate_parameter_set_definition_error_message_func"
    )
    def test_upload_parameter_set(self, mock_error_message_func, open_mock):
        """Tests that upload_parameter_set works as expected"""

        # SETUP
        session = MagicMock()
        parameter_set_definition_path = Path("path/to/file")

        # CALL
        workflows_api.upload_parameter_set(
            session, parameter_set_definition_path=parameter_set_definition_path
        )

        # ASSERT
        open_mock.assert_called_once_with(parameter_set_definition_path, "rb")
        session.post_request.assert_called_once_with(
            url=f"{NIMS_API_URL}/workflows/parameter-set/upload/",
            data=open(parameter_set_definition_path, "rb"),
            error_message_func=mock_error_message_func.return_value,
        )

from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from dafni_cli.api.exceptions import DAFNIError, ValidationError
from dafni_cli.tests.fixtures.workflow_parameter_set import TEST_WORKFLOW_PARAMETER_SET
from dafni_cli.tests.fixtures.workflows import TEST_WORKFLOW
from dafni_cli.workflows import upload


class TestWorkflowUpload(TestCase):
    """Test class to test the upload_workflow function"""

    def setUp(self) -> None:
        super().setUp()

        self.mock_workflows_api = patch(
            "dafni_cli.workflows.upload.workflows_api"
        ).start()
        self.mock_print_json = patch("dafni_cli.workflows.upload.print_json").start()
        self.mock_optional_echo = patch(
            "dafni_cli.workflows.upload.optional_echo"
        ).start()
        self.mock_click = patch("dafni_cli.workflows.upload.click").start()

        self.addCleanup(patch.stopall)

    def _test_upload_workflow(self, json: bool):
        """Tests that upload_workflow works as expected with a given json
        value"""
        # SETUP
        session = MagicMock()
        definition_path = Path("path/to/definition")
        version_message = MagicMock()
        parent_id = MagicMock()
        details = TEST_WORKFLOW

        self.mock_workflows_api.upload_workflow.return_value = details

        # CALL
        upload.upload_workflow(
            session, definition_path, version_message, parent_id, json=json
        )

        # ASSERT
        self.mock_optional_echo.assert_called_with("Uploading workflow", json)
        self.mock_workflows_api.upload_workflow.assert_called_once_with(
            session, definition_path, version_message, parent_id
        )

        if json:
            self.mock_print_json.assert_called_once_with(details)
            self.mock_click.echo.assert_not_called()
        else:
            self.mock_print_json.assert_not_called()
            self.assertEqual(
                self.mock_click.echo.call_args_list,
                [call("\nUpload successful"), call(f"Version ID: {details['id']}")],
            )

    def test_upload_workflow(self):
        """Tests that upload_workflow works as expected when json = False"""
        self._test_upload_workflow(json=False)

    def test_upload_workflow_json(self):
        """Tests that upload_workflow works as expected when json = True"""
        self._test_upload_workflow(json=True)


class TestParameterSetUpload(TestCase):
    """Test class to test the upload_parameter_set function"""

    def setUp(self) -> None:
        super().setUp()

        self.mock_workflows_api = patch(
            "dafni_cli.workflows.upload.workflows_api"
        ).start()
        self.mock_print_json = patch("dafni_cli.workflows.upload.print_json").start()
        self.mock_optional_echo = patch(
            "dafni_cli.workflows.upload.optional_echo"
        ).start()
        self.mock_click = patch("dafni_cli.workflows.upload.click").start()

        self.addCleanup(patch.stopall)

    def _test_upload_parameter_set(self, json: bool):
        """Tests that upload_parameter_set works as expected with a given value
        of json"""
        # SETUP
        session = MagicMock()
        definition_path = Path("path/to/definition")
        details = TEST_WORKFLOW_PARAMETER_SET

        self.mock_workflows_api.upload_parameter_set.return_value = details

        # CALL
        upload.upload_parameter_set(session, definition_path, json=json)

        # ASSERT
        self.mock_workflows_api.validate_parameter_set_definition.assert_called_once_with(
            session, definition_path
        )
        self.assertEqual(
            self.mock_optional_echo.call_args_list,
            [
                call("Validating parameter set definition", json),
                call("Uploading parameter set", json),
            ],
        )
        self.mock_workflows_api.upload_parameter_set.assert_called_once_with(
            session, definition_path
        )

        if json:
            self.mock_print_json.assert_called_once_with(details)
            self.mock_click.echo.assert_not_called()
        else:
            self.mock_print_json.assert_not_called()
            self.assertEqual(
                self.mock_click.echo.call_args_list,
                [
                    call("\nUpload successful"),
                    call(f"Parameter set ID: {details['id']}"),
                ],
            )

    def test_upload_parameter_set(self):
        """Tests that upload_parameter_set works as expected with json = False"""
        self._test_upload_parameter_set(json=False)

    def test_upload_parameter_set_json(self):
        """Tests that upload_parameter_set works as expected with json = True"""
        self._test_upload_parameter_set(json=True)

    def _test_upload_parameter_set_exits_for_validation_error(self, json: bool):
        """Tests that upload_parameter_set works as expected when there is a
        validation error with a given value of json"""
        # SETUP
        session = MagicMock()
        definition_path = Path("path/to/definition")

        self.mock_workflows_api.validate_parameter_set_definition.side_effect = (
            ValidationError("Some validation error message")
        )

        # CALL & ASSERT
        with self.assertRaises(SystemExit) as err:
            upload.upload_parameter_set(session, definition_path, json=json)

        # ASSERT
        self.mock_optional_echo.assert_called_once_with(
            "Validating parameter set definition", json
        )
        self.mock_workflows_api.validate_parameter_set_definition.assert_called_once_with(
            session, definition_path
        )
        self.assertEqual(err.exception.code, 1)
        self.mock_workflows_api.upload_parameter_set.assert_not_called()
        self.mock_print_json.assert_not_called()

        self.mock_click.echo.assert_called_once_with(
            self.mock_workflows_api.validate_parameter_set_definition.side_effect
        )

    def test_upload_parameter_set_exits_for_validation_error(self):
        """Tests that upload_parameter_set works as expected when there is a
        validation error and json = False"""
        self._test_upload_parameter_set_exits_for_validation_error(json=False)

    def test_upload_parameter_set_exits_for_validation_error_json(self):
        """Tests that upload_parameter_set works as expected when there is a
        validation error and json = True"""
        self._test_upload_parameter_set_exits_for_validation_error(json=True)

    def _test_upload_parameter_set_exits_for_dafni_error(self, json: bool):
        """Tests that upload_parameter_set works as expected when there is a
        dafni error with a given value of json"""
        # SETUP
        session = MagicMock()
        definition_path = Path("path/to/definition")

        self.mock_workflows_api.upload_parameter_set.side_effect = DAFNIError(
            "Some ingestion error message"
        )

        # CALL & ASSERT
        with self.assertRaises(SystemExit) as err:
            upload.upload_parameter_set(session, definition_path, json=json)

        # ASSERT
        self.assertEqual(
            self.mock_optional_echo.call_args_list,
            [
                call("Validating parameter set definition", json),
                call("Uploading parameter set", json),
            ],
        )

        self.mock_workflows_api.validate_parameter_set_definition.assert_called_once_with(
            session, definition_path
        )

        self.mock_workflows_api.upload_parameter_set.assert_called_once_with(
            session, definition_path
        )

        self.assertEqual(err.exception.code, 1)
        self.mock_print_json.assert_not_called()

        self.mock_click.echo.assert_called_once_with(
            self.mock_workflows_api.upload_parameter_set.side_effect
        )

    def test_upload_parameter_set_exits_for_dafni_error(self):
        """Tests that upload_parameter_set works as expected when there is a
        dafni error and json = False"""
        self._test_upload_parameter_set_exits_for_dafni_error(json=False)

    def test_upload_parameter_set_exits_for_dafni_error_json(self):
        """Tests that upload_parameter_set works as expected when there is a
        dafni error and json = True"""
        self._test_upload_parameter_set_exits_for_dafni_error(json=True)

from unittest import TestCase
from unittest.mock import MagicMock, patch

from dafni_cli.api.exceptions import ResourceNotFoundError
from dafni_cli.commands import helpers


@patch("dafni_cli.commands.helpers.get_model")
@patch("dafni_cli.commands.helpers.click")
class TestCliGetModel(TestCase):
    """Test class to test cli_get_model"""

    def test_returns_correctly(self, mock_click, mock_get_model):
        """Tests the function returns the model when found"""
        # SETUP
        mock_session = MagicMock()
        version_id = MagicMock()
        model_dict = MagicMock()
        mock_get_model.return_value = model_dict

        # CALL
        result = helpers.cli_get_model(mock_session, version_id)

        # ASSERT
        mock_get_model.assert_called_once_with(mock_session, version_id)
        self.assertEqual(result, model_dict)
        mock_click.echo.assert_not_called()

    def test_resource_not_found(self, mock_click, mock_get_model):
        """Tests the function prints an error message if the model is not
        found"""
        # SETUP
        mock_session = MagicMock()
        version_id = MagicMock()
        error = ResourceNotFoundError("Some error message")
        mock_get_model.side_effect = error

        # CALL
        with self.assertRaises(SystemExit) as err:
            helpers.cli_get_model(mock_session, version_id)

        # ASSERT
        mock_get_model.assert_called_once_with(mock_session, version_id)
        mock_click.echo.assert_called_once_with(error)
        self.assertEqual(err.exception.code, 1)


@patch("dafni_cli.commands.helpers.get_latest_dataset_metadata")
@patch("dafni_cli.commands.helpers.click")
class TestCliGetLatestDatasetMetadata(TestCase):
    """Test class to test cli_get_latest_dataset_metadata"""

    def test_returns_correctly(self, mock_click, mock_get_latest_dataset_metadata):
        """Tests the function returns the dataset metadata when found"""
        # SETUP
        mock_session = MagicMock()
        version_id = MagicMock()
        dataset_metadata_dict = MagicMock()
        mock_get_latest_dataset_metadata.return_value = dataset_metadata_dict

        # CALL
        result = helpers.cli_get_latest_dataset_metadata(mock_session, version_id)

        # ASSERT
        mock_get_latest_dataset_metadata.assert_called_once_with(
            mock_session, version_id
        )
        self.assertEqual(result, dataset_metadata_dict)
        mock_click.echo.assert_not_called()

    def test_resource_not_found(self, mock_click, mock_get_latest_dataset_metadata):
        """Tests the function prints an error message if the dataset metadata
        is not found"""
        # SETUP
        mock_session = MagicMock()
        version_id = MagicMock()
        error = ResourceNotFoundError("Some error message")
        mock_get_latest_dataset_metadata.side_effect = error

        # CALL
        with self.assertRaises(SystemExit) as err:
            helpers.cli_get_latest_dataset_metadata(mock_session, version_id)

        # ASSERT
        mock_get_latest_dataset_metadata.assert_called_once_with(
            mock_session, version_id
        )
        mock_click.echo.assert_called_once_with(error)
        self.assertEqual(err.exception.code, 1)


@patch("dafni_cli.commands.helpers.get_workflow")
@patch("dafni_cli.commands.helpers.click")
class TestCliGetWorkflow(TestCase):
    """Test class to test cli_get_workflow"""

    def test_returns_correctly(self, mock_click, mock_get_workflow):
        """Tests the function returns the workflow when found"""
        # SETUP
        mock_session = MagicMock()
        version_id = MagicMock()
        workflow_dict = MagicMock()
        mock_get_workflow.return_value = workflow_dict

        # CALL
        result = helpers.cli_get_workflow(mock_session, version_id)

        # ASSERT
        mock_get_workflow.assert_called_once_with(mock_session, version_id)
        self.assertEqual(result, workflow_dict)
        mock_click.echo.assert_not_called()

    def test_resource_not_found(self, mock_click, mock_get_workflow):
        """Tests the function prints an error message if the workflow is not
        found"""
        # SETUP
        mock_session = MagicMock()
        version_id = MagicMock()
        error = ResourceNotFoundError("Some error message")
        mock_get_workflow.side_effect = error

        # CALL
        with self.assertRaises(SystemExit) as err:
            helpers.cli_get_workflow(mock_session, version_id)

        # ASSERT
        mock_get_workflow.assert_called_once_with(mock_session, version_id)
        mock_click.echo.assert_called_once_with(error)
        self.assertEqual(err.exception.code, 1)


@patch("dafni_cli.commands.helpers.get_workflow_instance")
@patch("dafni_cli.commands.helpers.click")
class TestCliGetWorkflowInstance(TestCase):
    """Test class to test cli_get_workflow_instance"""

    def test_returns_correctly(self, mock_click, mock_get_workflow_instance):
        """Tests the function returns the workflow instance when found"""
        # SETUP
        mock_session = MagicMock()
        version_id = MagicMock()
        workflow_dict = MagicMock()
        mock_get_workflow_instance.return_value = workflow_dict

        # CALL
        result = helpers.cli_get_workflow_instance(mock_session, version_id)

        # ASSERT
        mock_get_workflow_instance.assert_called_once_with(mock_session, version_id)
        self.assertEqual(result, workflow_dict)
        mock_click.echo.assert_not_called()

    def test_resource_not_found(self, mock_click, mock_get_workflow_instance):
        """Tests the function prints an error message if the workflow instance
        is not found"""
        # SETUP
        mock_session = MagicMock()
        version_id = MagicMock()
        error = ResourceNotFoundError("Some error message")
        mock_get_workflow_instance.side_effect = error

        # CALL
        with self.assertRaises(SystemExit) as err:
            helpers.cli_get_workflow_instance(mock_session, version_id)

        # ASSERT
        mock_get_workflow_instance.assert_called_once_with(mock_session, version_id)
        mock_click.echo.assert_called_once_with(error)
        self.assertEqual(err.exception.code, 1)


@patch("dafni_cli.commands.helpers.parse_workflow")
@patch("dafni_cli.commands.helpers.cli_get_workflow")
@patch("dafni_cli.commands.helpers.click")
class TestCliGetWorkflowParameterSet(TestCase):
    """Test class to test cli_get_workflow_parameter_set"""

    def test_returns_correctly(
        self, mock_click, mock_cli_get_workflow, mock_parse_workflow
    ):
        """Tests the function returns the workflow parameter set when found"""
        # SETUP
        mock_session = MagicMock()
        workflow_version_id = MagicMock()
        parameter_set_id = MagicMock()
        workflow_dict = MagicMock()
        workflow = MagicMock()
        mock_cli_get_workflow.return_value = workflow_dict
        mock_parse_workflow.return_value = workflow

        # CALL
        result = helpers.cli_get_workflow_parameter_set(
            mock_session, workflow_version_id, parameter_set_id
        )

        # ASSERT
        mock_cli_get_workflow.assert_called_once_with(mock_session, workflow_version_id)
        mock_parse_workflow.assert_called_once_with(workflow_dict)
        workflow.get_parameter_set.assert_called_once_with(parameter_set_id)
        self.assertEqual(result, workflow.get_parameter_set.return_value)
        mock_click.echo.assert_not_called()

    def test_resource_not_found(
        self, mock_click, mock_cli_get_workflow, mock_parse_workflow
    ):
        """Tests the function prints an error message if the workflow parameter
        set is not found"""
        # SETUP
        mock_session = MagicMock()
        workflow_version_id = MagicMock()
        parameter_set_id = MagicMock()
        workflow_dict = MagicMock()
        workflow = MagicMock()
        error = ResourceNotFoundError("Some error message")
        workflow.get_parameter_set.side_effect = error
        mock_cli_get_workflow.return_value = workflow_dict
        mock_parse_workflow.return_value = workflow

        # CALL
        with self.assertRaises(SystemExit) as err:
            helpers.cli_get_workflow_parameter_set(
                mock_session, workflow_version_id, parameter_set_id
            )

        # ASSERT
        mock_cli_get_workflow.assert_called_once_with(mock_session, workflow_version_id)
        mock_parse_workflow.assert_called_once_with(workflow_dict)
        workflow.get_parameter_set.assert_called_once_with(parameter_set_id)
        mock_click.echo.assert_called_once_with(error)
        self.assertEqual(err.exception.code, 1)

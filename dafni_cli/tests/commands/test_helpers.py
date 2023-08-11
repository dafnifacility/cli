from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from dafni_cli.api.exceptions import ResourceNotFoundError
from dafni_cli.commands import helpers
from dafni_cli.datasets.dataset_metadata import DataFile


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


class TestCliSelectDatasetFiles(TestCase):
    """Test class to test cli_select_dataset_files"""

    def setUp(self) -> None:
        super().setUp()

        self.file_names = ["file1.csv", "file2.zip", "file3.csv"]
        self.dataset_metadata = MagicMock(
            files=[DataFile(name=file_name, size=0) for file_name in self.file_names]
        )

    def test_all_optionals_none_returns_whole_list(self):
        """Tests that the entire list of files is returned when the given list
        of files is None"""
        # CALL
        result = helpers.cli_select_dataset_files(self.dataset_metadata, files=None)

        # ASSERT
        self.assertEqual(result, self.dataset_metadata.files)

    def test_given_exact_file_names_selects_correct_files(self):
        """Tests that only files found in the given list of files are returned"""
        # CALL
        result = helpers.cli_select_dataset_files(
            self.dataset_metadata,
            files=["file1.csv", "file2.zip"],
        )

        # ASSERT
        self.assertEqual(
            result, [self.dataset_metadata.files[0], self.dataset_metadata.files[1]]
        )

    def test_given_file_wildcard_selects_correct_files(self):
        """Tests that only files with names matching the given glob-like file
        name is returned when given"""
        # CALL
        result = helpers.cli_select_dataset_files(
            self.dataset_metadata,
            files=["*.csv"],
        )

        # ASSERT
        self.assertEqual(
            result, [self.dataset_metadata.files[0], self.dataset_metadata.files[2]]
        )

    def test_given_file_name_and_wildcard_selects_correct_files(self):
        """Tests that only files with names found explicitly given or that match
        the a separate glob-like filename are returned when both are given"""
        # CALL
        result = helpers.cli_select_dataset_files(
            self.dataset_metadata,
            files=["*.csv", "file2.zip"],
        )

        # ASSERT
        self.assertEqual(result, self.dataset_metadata.files)


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
        self.assertEqual(result, (workflow, workflow.get_parameter_set.return_value))
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

from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from click.testing import CliRunner

from dafni_cli.commands import delete


@patch("dafni_cli.commands.delete.cli_get_model")
@patch("dafni_cli.commands.delete.parse_model")
class TestCollateModelVersionDetails(TestCase):
    """Test class to test the collate_model_version_details function"""

    def test_single_model_with_valid_permissions_returns_single_model_details(
        self, mock_parse_model, mock_cli_get_model
    ):
        """Tests collate_model_version_details works correctly for a single
        model with delete permissions"""

        # SETUP
        session = MagicMock()
        version_id = "version-id"
        version_ids = (version_id,)

        model_mock = MagicMock()
        model_mock.auth.destroy = True

        mock_parse_model.return_value = model_mock

        # CALL
        result = delete.collate_model_version_details(session, version_ids)

        # ASSERT
        mock_cli_get_model.assert_called_once_with(session, version_id)
        mock_parse_model.assert_called_once_with(mock_cli_get_model.return_value)
        self.assertEqual(result, [model_mock.get_version_details.return_value])

    @patch("dafni_cli.commands.delete.click")
    def test_single_model_without_valid_permissions_exits(
        self, mock_click, mock_parse_model, mock_cli_get_model
    ):
        """Tests collate_model_version_details works correctly for a single
        model without delete permissions"""

        # SETUP
        session = MagicMock()
        version_id = "version-id"
        version_ids = (version_id,)

        model_mock = MagicMock()
        model_mock.auth.destroy = False

        mock_parse_model.return_value = model_mock

        # CALL
        with self.assertRaises(SystemExit):
            delete.collate_model_version_details(session, version_ids)

        # ASSERT
        mock_cli_get_model.assert_called_once_with(session, version_id)
        mock_parse_model.assert_called_once_with(mock_cli_get_model.return_value)
        mock_click.echo.assert_has_calls(
            [
                call("You do not have sufficient permissions to delete model version:"),
                call(model_mock.get_version_details.return_value),
            ]
        )

    def test_multiple_models_with_valid_permissions_returns_multiple_model_details(
        self, mock_parse_model, mock_cli_get_model
    ):
        """Tests collate_model_version_details works correctly for a list
        of models with delete permissions"""

        # SETUP
        session = MagicMock()
        version_id1 = "version-id-1"
        version_id2 = "version-id-2"
        version_ids = (version_id1, version_id2)

        model_mock1 = MagicMock()
        model_mock1.auth.destroy = True
        model_mock2 = MagicMock()
        model_mock2.auth.destroy = True

        mock_parse_model.side_effect = [model_mock1, model_mock2]

        # CALL
        result = delete.collate_model_version_details(session, version_ids)

        # ASSERT
        mock_cli_get_model.assert_has_calls(
            [call(session, version_id1), call(session, version_id2)]
        )
        mock_parse_model.assert_has_calls(
            [
                call(mock_cli_get_model.return_value),
                call(mock_cli_get_model.return_value),
            ]
        )
        self.assertEqual(
            result,
            [
                model_mock1.get_version_details.return_value,
                model_mock2.get_version_details.return_value,
            ],
        )

    @patch("dafni_cli.commands.delete.click")
    def test_first_model_with_permissions_but_second_without_exits_and_shows_model_without_permissions(
        self, mock_click, mock_parse_model, mock_cli_get_model
    ):
        """Tests collate_model_version_details works correctly for a list
        of models where the first has delete permissions and the second does not"""

        # SETUP
        session = MagicMock()
        version_id1 = "version-id-1"
        version_id2 = "version-id-2"
        version_ids = [version_id1, version_id2]

        model_mock1 = MagicMock()
        model_mock1.auth.destroy = True
        model_mock2 = MagicMock()
        model_mock2.auth.destroy = False

        mock_parse_model.side_effect = [model_mock1, model_mock2]

        # CALL
        with self.assertRaises(SystemExit):
            delete.collate_model_version_details(session, version_ids)

        # ASSERT
        mock_cli_get_model.assert_has_calls(
            [call(session, version_id1), call(session, version_id2)]
        )
        mock_parse_model.assert_has_calls(
            [
                call(mock_cli_get_model.return_value),
                call(mock_cli_get_model.return_value),
            ]
        )
        self.assertEqual(
            mock_click.echo.call_args_list,
            [
                call("You do not have sufficient permissions to delete model version:"),
                call(model_mock2.get_version_details.return_value),
            ],
        )


@patch("dafni_cli.commands.delete.cli_get_latest_dataset_metadata")
@patch("dafni_cli.commands.delete.parse_dataset_metadata")
class TestCollateDatasetDetails(TestCase):
    """Test class to test the collate_dataset_details function"""

    def test_single_dataset_with_valid_permissions_returns_single_dataset_details(
        self, mock_parse_dataset_metadata, mock_cli_get_latest_dataset_metadata
    ):
        """Tests collate_dataset_details works correctly for a single dataset
        with delete permissions"""

        # SETUP
        session = MagicMock()
        version_id = "version-id"
        version_ids = (version_id,)

        dataset_mock = MagicMock()
        dataset_mock.dataset_id = "dataset-id"
        dataset_mock.auth.destroy = True

        mock_parse_dataset_metadata.return_value = dataset_mock

        # CALL
        result = delete.collate_dataset_details(session, version_ids)

        # ASSERT
        mock_cli_get_latest_dataset_metadata.assert_called_once_with(
            session, version_id
        )
        mock_parse_dataset_metadata.assert_called_once_with(
            mock_cli_get_latest_dataset_metadata.return_value
        )
        self.assertEqual(
            result,
            (
                [dataset_mock.get_details.return_value],
                [dataset_mock.dataset_id],
            ),
        )

    @patch("dafni_cli.commands.delete.click")
    def test_single_dataset_without_valid_permissions_exits(
        self,
        mock_click,
        mock_parse_dataset_metadata,
        mock_cli_get_latest_dataset_metadata,
    ):
        """Tests collate_dataset_details works correctly for a single dataset
        without delete permissions"""

        # SETUP
        session = MagicMock()
        version_id = "version-id"
        version_ids = (version_id,)

        dataset_mock = MagicMock()
        dataset_mock.dataset_id = "dataset-id"
        dataset_mock.auth.destroy = False

        mock_parse_dataset_metadata.return_value = dataset_mock

        # CALL
        with self.assertRaises(SystemExit):
            delete.collate_dataset_details(session, version_ids)

        # ASSERT
        mock_cli_get_latest_dataset_metadata.assert_called_once_with(
            session, version_id
        )
        mock_parse_dataset_metadata.assert_called_once_with(
            mock_cli_get_latest_dataset_metadata.return_value
        )
        mock_click.echo.assert_has_calls(
            [
                call("You do not have sufficient permissions to delete dataset:"),
                call(dataset_mock.get_details.return_value),
            ]
        )

    def test_multiple_datasets_with_valid_permissions_returns_multiple_dataset_details(
        self, mock_parse_dataset_metadata, mock_cli_get_latest_dataset_metadata
    ):
        """Tests collate_dataset_details works correctly for a list
        of datasets with delete permissions"""

        # SETUP
        session = MagicMock()
        version_id1 = "version-id-1"
        version_id2 = "version-id-2"
        version_ids = (version_id1, version_id2)

        dataset_mock1 = MagicMock()
        dataset_mock1.dataset_id = "dataset-id-1"
        dataset_mock1.auth.destroy = True
        dataset_mock2 = MagicMock()
        dataset_mock2.dataset_id = "dataset-id-2"
        dataset_mock2.auth.destroy = True

        mock_parse_dataset_metadata.side_effect = [dataset_mock1, dataset_mock2]

        # CALL
        result = delete.collate_dataset_details(session, version_ids)

        # ASSERT
        mock_cli_get_latest_dataset_metadata.assert_has_calls(
            [call(session, version_id1), call(session, version_id2)]
        )
        mock_parse_dataset_metadata.assert_has_calls(
            [
                call(mock_cli_get_latest_dataset_metadata.return_value),
                call(mock_cli_get_latest_dataset_metadata.return_value),
            ]
        )
        self.assertEqual(
            result,
            (
                [
                    dataset_mock1.get_details.return_value,
                    dataset_mock2.get_details.return_value,
                ],
                [dataset_mock1.dataset_id, dataset_mock2.dataset_id],
            ),
        )

    @patch("dafni_cli.commands.delete.click")
    def test_first_dataset_with_permissions_but_second_without_exits_and_shows_dataset_without_permissions(
        self,
        mock_click,
        mock_parse_dataset_metadata,
        mock_cli_get_latest_dataset_metadata,
    ):
        """Tests collate_dataset_details works correctly for a list of
        datasets where the first has delete permissions and the second does
        not"""

        # SETUP
        session = MagicMock()
        version_id1 = "version-id-1"
        version_id2 = "version-id-2"
        version_ids = (version_id1, version_id2)

        dataset_mock1 = MagicMock()
        dataset_mock1.dataset_id = "dataset-id-1"
        dataset_mock1.auth.destroy = True
        dataset_mock2 = MagicMock()
        dataset_mock2.dataset_id = "dataset-id-2"
        dataset_mock2.auth.destroy = False

        mock_parse_dataset_metadata.side_effect = [dataset_mock1, dataset_mock2]

        # CALL
        with self.assertRaises(SystemExit):
            delete.collate_dataset_details(session, version_ids)

        # ASSERT
        mock_cli_get_latest_dataset_metadata.assert_has_calls(
            [call(session, version_id1), call(session, version_id2)]
        )
        mock_parse_dataset_metadata.assert_has_calls(
            [
                call(mock_cli_get_latest_dataset_metadata.return_value),
                call(mock_cli_get_latest_dataset_metadata.return_value),
            ]
        )
        self.assertEqual(
            mock_click.echo.call_args_list,
            [
                call("You do not have sufficient permissions to delete dataset:"),
                call(dataset_mock2.get_details.return_value),
            ],
        )


@patch("dafni_cli.commands.delete.cli_get_latest_dataset_metadata")
@patch("dafni_cli.commands.delete.parse_dataset_metadata")
class TestCollateDatasetVersionDetails(TestCase):
    """Test class to test the collate_dataset_version_details function"""

    def test_single_dataset_version_with_valid_permissions_returns_single_dataset_details(
        self, mock_parse_dataset_metadata, mock_cli_get_latest_dataset_metadata
    ):
        """Tests collate_dataset_version_details works correctly for a single
        dataset version with delete permissions"""

        # SETUP
        session = MagicMock()
        version_id = "version-id"
        version_ids = (version_id,)

        dataset_mock = MagicMock()
        dataset_mock.dataset_id = "dataset-id"
        dataset_mock.auth.destroy = True

        mock_parse_dataset_metadata.return_value = dataset_mock

        # CALL
        result = delete.collate_dataset_version_details(session, version_ids)

        # ASSERT
        mock_cli_get_latest_dataset_metadata.assert_called_once_with(
            session, version_id
        )
        mock_parse_dataset_metadata.assert_called_once_with(
            mock_cli_get_latest_dataset_metadata.return_value
        )
        self.assertEqual(
            result,
            (
                [dataset_mock.get_version_details.return_value],
                [dataset_mock.dataset_id],
            ),
        )

    @patch("dafni_cli.commands.delete.click")
    def test_single_dataset_version_without_valid_permissions_exits(
        self,
        mock_click,
        mock_parse_dataset_metadata,
        mock_cli_get_latest_dataset_metadata,
    ):
        """Tests collate_dataset_version_details works correctly for a single
        dataset without delete permissions"""

        # SETUP
        session = MagicMock()
        version_id = "version-id"
        version_ids = (version_id,)

        dataset_mock = MagicMock()
        dataset_mock.dataset_id = "dataset-id"
        dataset_mock.auth.destroy = False

        mock_parse_dataset_metadata.return_value = dataset_mock

        # CALL
        with self.assertRaises(SystemExit):
            delete.collate_dataset_version_details(session, version_ids)

        # ASSERT
        mock_cli_get_latest_dataset_metadata.assert_called_once_with(
            session, version_id
        )
        mock_parse_dataset_metadata.assert_called_once_with(
            mock_cli_get_latest_dataset_metadata.return_value
        )
        mock_click.echo.assert_has_calls(
            [
                call(
                    "You do not have sufficient permissions to delete dataset version:"
                ),
                call(dataset_mock.get_version_details.return_value),
            ]
        )

    def test_multiple_dataset_versions_with_valid_permissions_returns_multiple_dataset_details(
        self, mock_parse_dataset_metadata, mock_cli_get_latest_dataset_metadata
    ):
        """Tests collate_dataset_version_details works correctly for a list
        of dataset versions with delete permissions"""

        # SETUP
        session = MagicMock()
        version_id1 = "version-id-1"
        version_id2 = "version-id-2"
        version_ids = (version_id1, version_id2)

        dataset_mock1 = MagicMock()
        dataset_mock1.dataset_id = "dataset-id-1"
        dataset_mock1.auth.destroy = True
        dataset_mock2 = MagicMock()
        dataset_mock2.dataset_id = "dataset-id-2"
        dataset_mock2.auth.destroy = True

        mock_parse_dataset_metadata.side_effect = [dataset_mock1, dataset_mock2]

        # CALL
        result = delete.collate_dataset_version_details(session, version_ids)

        # ASSERT
        mock_cli_get_latest_dataset_metadata.assert_has_calls(
            [call(session, version_id1), call(session, version_id2)]
        )
        mock_parse_dataset_metadata.assert_has_calls(
            [
                call(mock_cli_get_latest_dataset_metadata.return_value),
                call(mock_cli_get_latest_dataset_metadata.return_value),
            ]
        )
        self.assertEqual(
            result,
            (
                [
                    dataset_mock1.get_version_details.return_value,
                    dataset_mock2.get_version_details.return_value,
                ],
                [dataset_mock1.dataset_id, dataset_mock2.dataset_id],
            ),
        )

    @patch("dafni_cli.commands.delete.click")
    def test_first_dataset_version_with_permissions_but_second_without_exits_and_shows_dataset_without_permissions(
        self,
        mock_click,
        mock_parse_dataset_metadata,
        mock_cli_get_latest_dataset_metadata,
    ):
        """Tests collate_dataset_version_details works correctly for a list of
        dataset versions where the first has delete permissions and the second
        does not"""

        # SETUP
        session = MagicMock()
        version_id1 = "version-id-1"
        version_id2 = "version-id-2"
        version_ids = (version_id1, version_id2)

        dataset_mock1 = MagicMock()
        dataset_mock1.dataset_id = "dataset-id-1"
        dataset_mock1.auth.destroy = True
        dataset_mock2 = MagicMock()
        dataset_mock2.dataset_id = "dataset-id-2"
        dataset_mock2.auth.destroy = False

        mock_parse_dataset_metadata.side_effect = [dataset_mock1, dataset_mock2]

        # CALL
        with self.assertRaises(SystemExit):
            delete.collate_dataset_version_details(session, version_ids)

        # ASSERT
        mock_cli_get_latest_dataset_metadata.assert_has_calls(
            [call(session, version_id1), call(session, version_id2)]
        )
        mock_parse_dataset_metadata.assert_has_calls(
            [
                call(mock_cli_get_latest_dataset_metadata.return_value),
                call(mock_cli_get_latest_dataset_metadata.return_value),
            ]
        )
        self.assertEqual(
            mock_click.echo.call_args_list,
            [
                call(
                    "You do not have sufficient permissions to delete dataset version:"
                ),
                call(dataset_mock2.get_version_details.return_value),
            ],
        )


@patch("dafni_cli.commands.delete.cli_get_workflow")
@patch("dafni_cli.commands.delete.parse_workflow")
class TestCollateWorkflowVersionDetails(TestCase):
    """Test class to test the collate_workflow_version_details function"""

    def test_single_workflow_with_valid_permissions_returns_single_model_details(
        self, mock_parse_workflow, mock_cli_get_workflow
    ):
        """Tests collate_workflow_version_details works correctly for a single
        workflow with delete permissions"""

        # SETUP
        session = MagicMock()
        version_id = "version-id"
        version_ids = (version_id,)

        workflow_mock = MagicMock()
        workflow_mock.auth.destroy = True

        mock_parse_workflow.return_value = workflow_mock

        # CALL
        result = delete.collate_workflow_version_details(session, version_ids)

        # ASSERT
        mock_cli_get_workflow.assert_called_once_with(session, version_id)
        mock_parse_workflow.assert_called_once_with(mock_cli_get_workflow.return_value)
        self.assertEqual(result, [workflow_mock.get_version_details.return_value])

    @patch("dafni_cli.commands.delete.click")
    def test_single_workflow_without_valid_permissions_exits(
        self, mock_click, mock_parse_workflow, mock_cli_get_workflow
    ):
        """Tests collate_workflow_version_details works correctly for a single
        model without delete permissions"""

        # SETUP
        session = MagicMock()
        version_id = "version-id"
        version_ids = (version_id,)

        workflow_mock = MagicMock()
        workflow_mock.auth.destroy = False

        mock_parse_workflow.return_value = workflow_mock

        # CALL
        with self.assertRaises(SystemExit):
            delete.collate_workflow_version_details(session, version_ids)

        # ASSERT
        mock_cli_get_workflow.assert_called_once_with(session, version_id)
        mock_parse_workflow.assert_called_once_with(mock_cli_get_workflow.return_value)
        mock_click.echo.assert_has_calls(
            [
                call(
                    "You do not have sufficient permissions to delete workflow version:"
                ),
                call(workflow_mock.get_version_details.return_value),
            ]
        )

    def test_multiple_workflow_with_valid_permissions_returns_multiple_workflow_details(
        self, mock_parse_workflow, mock_cli_get_workflow
    ):
        """Tests collate_model_version_details works correctly for a list
        of models with delete permissions"""

        # SETUP
        session = MagicMock()
        version_id1 = "version-id-1"
        version_id2 = "version-id-2"
        version_ids = (version_id1, version_id2)

        workflow_mock1 = MagicMock()
        workflow_mock1.auth.destroy = True
        workflow_mock2 = MagicMock()
        workflow_mock2.auth.destroy = True

        mock_parse_workflow.side_effect = [workflow_mock1, workflow_mock2]

        # CALL
        result = delete.collate_workflow_version_details(session, version_ids)

        # ASSERT
        mock_cli_get_workflow.assert_has_calls(
            [call(session, version_id1), call(session, version_id2)]
        )
        mock_parse_workflow.assert_has_calls(
            [
                call(mock_cli_get_workflow.return_value),
                call(mock_cli_get_workflow.return_value),
            ]
        )
        self.assertEqual(
            result,
            [
                workflow_mock1.get_version_details.return_value,
                workflow_mock2.get_version_details.return_value,
            ],
        )

    @patch("dafni_cli.commands.delete.click")
    def test_first_workflow_with_permissions_but_second_without_exits_and_shows_workflow_without_permissions(
        self, mock_click, mock_parse_workflow, mock_cli_get_workflow
    ):
        """Tests collate_workflow_version_details works correctly for a list
        of workflows where the first has delete permissions and the second does not"""

        # SETUP
        session = MagicMock()
        version_id1 = "version-id-1"
        version_id2 = "version-id-2"
        version_ids = (version_id1, version_id2)

        workflow_mock1 = MagicMock()
        workflow_mock1.auth.destroy = True
        workflow_mock2 = MagicMock()
        workflow_mock2.auth.destroy = False

        mock_parse_workflow.side_effect = [workflow_mock1, workflow_mock2]

        # CALL
        with self.assertRaises(SystemExit):
            delete.collate_workflow_version_details(session, version_ids)

        # ASSERT
        mock_cli_get_workflow.assert_has_calls(
            [call(session, version_id1), call(session, version_id2)]
        )
        mock_parse_workflow.assert_has_calls(
            [
                call(mock_cli_get_workflow.return_value),
                call(mock_cli_get_workflow.return_value),
            ]
        )
        self.assertEqual(
            mock_click.echo.call_args_list,
            [
                call(
                    "You do not have sufficient permissions to delete workflow version:"
                ),
                call(workflow_mock2.get_version_details.return_value),
            ],
        )


@patch("dafni_cli.commands.delete.DAFNISession")
class TestDelete(TestCase):
    """Test class to test the delete command"""

    @patch("dafni_cli.commands.delete.collate_model_version_details")
    def test_session_retrieved_and_set_on_context(self, _, mock_DAFNISession):
        """Tests that the session is created in the click context"""
        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        ctx = {}

        # CALL
        result = runner.invoke(
            delete.delete, ["model-version", "version-id"], input="y", obj=ctx
        )

        # ASSERT
        mock_DAFNISession.assert_called_once()

        self.assertEqual(ctx["session"], session)
        self.assertEqual(result.exit_code, 0)

    # ----------------- MODEL

    @patch("dafni_cli.commands.delete.collate_model_version_details")
    @patch("dafni_cli.commands.delete.delete_model_version")
    def test_delete_model_version(
        self,
        mock_delete_model_version,
        mock_collate_model_version_details,
        mock_DAFNISession,
    ):
        """Tests that the 'delete model-version' command works correctly with a single
        version id"""
        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        ctx = {}
        version_ids = ("version-id",)
        mock_collate_model_version_details.return_value = ["Model 1 details"]

        # CALL
        result = runner.invoke(
            delete.delete, ["model-version"] + list(version_ids), input="y", obj=ctx
        )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_collate_model_version_details.assert_called_once_with(session, version_ids)
        mock_delete_model_version.assert_called_with(session, version_ids[0])

        self.assertEqual(
            result.output,
            "Model 1 details\nConfirm deletion of model versions? [y/N]: y\nModel versions deleted\n",
        )
        self.assertEqual(result.exit_code, 0)

    @patch("dafni_cli.commands.delete.collate_model_version_details")
    @patch("dafni_cli.commands.delete.delete_model_version")
    def test_delete_model_multiple_versions(
        self,
        mock_delete_model_version,
        mock_collate_model_version_details,
        mock_DAFNISession,
    ):
        """Tests that the 'delete model-version' command works correctly with multiple
        version ids"""
        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        ctx = {}
        version_ids = ("version-id-1", "version-id-2")
        mock_collate_model_version_details.return_value = [
            "Model 1 details",
            "Model 2 details",
        ]

        # CALL
        result = runner.invoke(
            delete.delete, ["model-version"] + list(version_ids), input="y", obj=ctx
        )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_collate_model_version_details.assert_called_once_with(session, version_ids)
        self.assertEqual(
            mock_delete_model_version.call_args_list,
            [call(session, version_ids[0]), call(session, version_ids[1])],
        )

        self.assertEqual(
            result.output,
            "Model 1 details\nModel 2 details\nConfirm deletion of model versions? [y/N]: y\nModel versions deleted\n",
        )
        self.assertEqual(result.exit_code, 0)

    @patch("dafni_cli.commands.delete.collate_model_version_details")
    @patch("dafni_cli.commands.delete.delete_model_version")
    def test_delete_model_cancels_when_requested(
        self,
        mock_delete_model_version,
        mock_collate_model_version_details,
        mock_DAFNISession,
    ):
        """Tests that the 'delete model-version' can be canceled after printing the
        model info"""
        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        ctx = {}
        version_ids = ("version-id",)
        mock_collate_model_version_details.return_value = ["Model 1 details"]

        # CALL
        result = runner.invoke(
            delete.delete, ["model-version"] + list(version_ids), input="n", obj=ctx
        )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_collate_model_version_details.assert_called_once_with(session, version_ids)
        mock_delete_model_version.assert_not_called()

        self.assertEqual(
            result.output,
            "Model 1 details\nConfirm deletion of model versions? [y/N]: n\nAborted!\n",
        )
        self.assertEqual(result.exit_code, 1)

    # ----------------- DATASET

    @patch("dafni_cli.commands.delete.collate_dataset_details")
    @patch("dafni_cli.commands.delete.delete_dataset")
    def test_delete_dataset(
        self, mock_delete_dataset, mock_collate_dataset_details, mock_DAFNISession
    ):
        """Tests that the 'delete dataset' command works correctly with a single
        version id"""
        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        ctx = {}
        dataset_ids = ("dataset-id",)
        version_ids = ("version-id",)
        mock_collate_dataset_details.return_value = (
            ["Dataset 1 details"],
            list(dataset_ids),
        )

        # CALL
        result = runner.invoke(
            delete.delete, ["dataset"] + list(version_ids), input="y", obj=ctx
        )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_collate_dataset_details.assert_called_once_with(session, version_ids)
        mock_delete_dataset.assert_called_with(session, dataset_ids[0])

        self.assertEqual(
            result.output,
            "Dataset 1 details\nConfirm deletion of datasets? [y/N]: y\nDatasets deleted\n",
        )
        self.assertEqual(result.exit_code, 0)

    @patch("dafni_cli.commands.delete.collate_dataset_details")
    @patch("dafni_cli.commands.delete.delete_dataset")
    def test_delete_dataset_multiple(
        self, mock_delete_dataset, mock_collate_dataset_details, mock_DAFNISession
    ):
        """Tests that the 'delete dataset' command works correctly with multiple
        version ids"""
        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        ctx = {}
        dataset_ids = ("dataset-id-1", "dataset-id-1")
        version_ids = ("version-id-1", "version-id-2")
        mock_collate_dataset_details.return_value = (
            [
                "Dataset 1 details",
                "Dataset 2 details",
            ],
            list(dataset_ids),
        )

        # CALL
        result = runner.invoke(
            delete.delete, ["dataset"] + list(version_ids), input="y", obj=ctx
        )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_collate_dataset_details.assert_called_once_with(session, version_ids)
        self.assertEqual(
            mock_delete_dataset.call_args_list,
            [call(session, dataset_ids[0]), call(session, dataset_ids[1])],
        )

        self.assertEqual(
            result.output,
            "Dataset 1 details\nDataset 2 details\nConfirm deletion of datasets? [y/N]: y\nDatasets deleted\n",
        )
        self.assertEqual(result.exit_code, 0)

    @patch("dafni_cli.commands.delete.collate_dataset_details")
    @patch("dafni_cli.commands.delete.delete_dataset")
    def test_delete_dataset_cancels_when_requested(
        self, mock_delete_dataset, mock_collate_dataset_details, mock_DAFNISession
    ):
        """Tests that the 'delete dataset' can be canceled after printing the
        dataset info"""
        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        ctx = {}
        dataset_ids = ("dataset-id",)
        version_ids = ("version-id",)
        mock_collate_dataset_details.return_value = (
            ["Dataset 1 details"],
            list(dataset_ids),
        )

        # CALL
        result = runner.invoke(
            delete.delete, ["dataset"] + list(version_ids), input="n", obj=ctx
        )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_collate_dataset_details.assert_called_once_with(session, version_ids)
        mock_delete_dataset.assert_not_called()

        self.assertEqual(
            result.output,
            "Dataset 1 details\nConfirm deletion of datasets? [y/N]: n\nAborted!\n",
        )
        self.assertEqual(result.exit_code, 1)

    # ----------------- DATASET VERSION

    @patch("dafni_cli.commands.delete.collate_dataset_version_details")
    @patch("dafni_cli.commands.delete.delete_dataset_version")
    def test_delete_dataset_version(
        self,
        mock_delete_dataset_version,
        mock_collate_dataset_version_details,
        mock_DAFNISession,
    ):
        """Tests that the 'delete dataset-version' command works correctly
        with a single version id"""
        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        ctx = {}
        dataset_ids = ("dataset-id",)
        version_ids = ("version-id",)
        mock_collate_dataset_version_details.return_value = (
            ["Dataset 1 details"],
            list(dataset_ids),
        )

        # CALL
        result = runner.invoke(
            delete.delete, ["dataset-version"] + list(version_ids), input="y", obj=ctx
        )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_collate_dataset_version_details.assert_called_once_with(
            session, version_ids
        )
        mock_delete_dataset_version.assert_called_with(
            session, version_id=version_ids[0]
        )

        self.assertEqual(
            result.output,
            "Dataset 1 details\nConfirm deletion of dataset versions? [y/N]: y\nDataset versions deleted\n",
        )
        self.assertEqual(result.exit_code, 0)

    @patch("dafni_cli.commands.delete.collate_dataset_version_details")
    @patch("dafni_cli.commands.delete.delete_dataset_version")
    def test_delete_dataset_version_multiple(
        self,
        mock_delete_dataset_version,
        mock_collate_dataset_version_details,
        mock_DAFNISession,
    ):
        """Tests that the 'delete dataset-version' command works correctly
        with multiple version ids"""
        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        ctx = {}
        dataset_ids = ("dataset-id-1", "dataset-id-2")
        version_ids = ("version-id-1", "version-id-2")
        mock_collate_dataset_version_details.return_value = (
            [
                "Dataset 1 details",
                "Dataset 2 details",
            ],
            list(dataset_ids),
        )

        # CALL
        result = runner.invoke(
            delete.delete, ["dataset-version"] + list(version_ids), input="y", obj=ctx
        )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_collate_dataset_version_details.assert_called_once_with(
            session, version_ids
        )
        self.assertEqual(
            mock_delete_dataset_version.call_args_list,
            [
                call(session, version_id=version_ids[0]),
                call(session, version_id=version_ids[1]),
            ],
        )

        self.assertEqual(
            result.output,
            "Dataset 1 details\nDataset 2 details\nConfirm deletion of dataset versions? [y/N]: y\nDataset versions deleted\n",
        )
        self.assertEqual(result.exit_code, 0)

    @patch("dafni_cli.commands.delete.collate_dataset_version_details")
    @patch("dafni_cli.commands.delete.delete_dataset_version")
    def test_delete_dataset_version_cancels_when_requested(
        self,
        mock_delete_dataset_version,
        mock_collate_dataset_version_details,
        mock_DAFNISession,
    ):
        """Tests that the 'delete dataset-version' can be canceled after
        printing the dataset version info"""
        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        ctx = {}
        dataset_ids = ("dataset-id",)
        version_ids = ("version-id",)
        mock_collate_dataset_version_details.return_value = (
            ["Dataset 1 details"],
            list(dataset_ids),
        )

        # CALL
        result = runner.invoke(
            delete.delete, ["dataset-version"] + list(version_ids), input="n", obj=ctx
        )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_collate_dataset_version_details.assert_called_once_with(
            session, version_ids
        )
        mock_delete_dataset_version.assert_not_called()

        self.assertEqual(
            result.output,
            "Dataset 1 details\nConfirm deletion of dataset versions? [y/N]: n\nAborted!\n",
        )
        self.assertEqual(result.exit_code, 1)

    # ----------------- WORKFLOW

    @patch("dafni_cli.commands.delete.collate_workflow_version_details")
    @patch("dafni_cli.commands.delete.delete_workflow_version")
    def test_delete_workflow_version(
        self,
        mock_delete_workflow_version,
        mock_collate_workflow_version_details,
        mock_DAFNISession,
    ):
        """Tests that the 'delete workflow-version' command works correctly with a single
        version id"""
        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        ctx = {}
        version_ids = ("version-id",)
        mock_collate_workflow_version_details.return_value = ["Workflow 1 details"]

        # CALL
        result = runner.invoke(
            delete.delete, ["workflow-version"] + list(version_ids), input="y", obj=ctx
        )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_collate_workflow_version_details.assert_called_once_with(
            session, version_ids
        )
        mock_delete_workflow_version.assert_called_with(session, version_ids[0])

        self.assertEqual(
            result.output,
            "Workflow 1 details\nConfirm deletion of workflow versions? [y/N]: y\nWorkflow versions deleted\n",
        )
        self.assertEqual(result.exit_code, 0)

    @patch("dafni_cli.commands.delete.collate_workflow_version_details")
    @patch("dafni_cli.commands.delete.delete_workflow_version")
    def test_delete_workflow_version_multiple_versions(
        self,
        mock_delete_workflow_version,
        mock_collate_workflow_version_details,
        mock_DAFNISession,
    ):
        """Tests that the 'delete workflow-version' command works correctly with multiple
        version ids"""
        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        ctx = {}
        version_ids = ("version-id-1", "version-id-2")
        mock_collate_workflow_version_details.return_value = [
            "Workflow 1 details",
            "Workflow 2 details",
        ]

        # CALL
        result = runner.invoke(
            delete.delete, ["workflow-version"] + list(version_ids), input="y", obj=ctx
        )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_collate_workflow_version_details.assert_called_once_with(
            session, version_ids
        )
        self.assertEqual(
            mock_delete_workflow_version.call_args_list,
            [call(session, version_ids[0]), call(session, version_ids[1])],
        )

        self.assertEqual(
            result.output,
            "Workflow 1 details\nWorkflow 2 details\nConfirm deletion of workflow versions? [y/N]: y\nWorkflow versions deleted\n",
        )
        self.assertEqual(result.exit_code, 0)

    @patch("dafni_cli.commands.delete.collate_workflow_version_details")
    @patch("dafni_cli.commands.delete.delete_workflow_version")
    def test_delete_workflow_version_cancels_when_requested(
        self,
        mock_delete_workflow_version,
        mock_collate_workflow_version_details,
        mock_DAFNISession,
    ):
        """Tests that the 'delete workflow-version' can be canceled after printing the
        workflow info"""
        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        ctx = {}
        version_ids = ("version-id",)
        mock_collate_workflow_version_details.return_value = ["Workflow 1 details"]

        # CALL
        result = runner.invoke(
            delete.delete, ["workflow-version"] + list(version_ids), input="n", obj=ctx
        )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_collate_workflow_version_details.assert_called_once_with(
            session, version_ids
        )
        mock_delete_workflow_version.assert_not_called()

        self.assertEqual(
            result.output,
            "Workflow 1 details\nConfirm deletion of workflow versions? [y/N]: n\nAborted!\n",
        )
        self.assertEqual(result.exit_code, 1)

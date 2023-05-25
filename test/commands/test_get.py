from unittest import TestCase
from unittest.mock import ANY, MagicMock, patch

from click.testing import CliRunner

from dafni_cli.commands import get


@patch("dafni_cli.commands.get.DAFNISession")
class TestGet(TestCase):
    """Test class to test the get command"""

    def test_session_retrieved_and_set_on_context(self, mock_DAFNISession):
        """Tests that the session is created in the click context"""
        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        ctx = {}

        # CALL
        result = runner.invoke(get.get, ["models"], obj=ctx)

        # ASSERT
        mock_DAFNISession.assert_called_once()

        self.assertEqual(ctx["session"], session)
        self.assertEqual(result.exit_code, 0)

    # ----------------- MODELS

    @patch("dafni_cli.commands.get.get_all_models")
    @patch("dafni_cli.commands.get.parse_models")
    @patch("dafni_cli.commands.get.print_json")
    def test_get_models(
        self, mock_print_json, mock_parse_models, mock_get_all_models, mock_DAFNISession
    ):
        """Tests that the 'get models' command works correctly (with no
        optional arguments)"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        models = [MagicMock(), MagicMock()]
        mock_get_all_models.return_value = models
        mock_parse_models.return_value = models

        # CALL
        result = runner.invoke(get.get, ["models"])

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_get_all_models.assert_called_with(session)
        for model in models:
            model.output_details.assert_called_with(False)
        mock_print_json.assert_not_called()

        self.assertEqual(result.exit_code, 0)

    @patch("dafni_cli.commands.get.get_all_models")
    @patch("dafni_cli.commands.get.parse_models")
    @patch("dafni_cli.commands.get.print_json")
    def test_get_models_with_long_true(
        self, mock_print_json, mock_parse_models, mock_get_all_models, mock_DAFNISession
    ):
        """Tests that the 'get models' command works correctly (with long
        True)"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        models = [MagicMock(), MagicMock()]
        mock_get_all_models.return_value = models
        mock_parse_models.return_value = models

        # CALL
        result = runner.invoke(get.get, ["models", "--long"])

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_get_all_models.assert_called_with(session)
        for model in models:
            model.output_details.assert_called_with(True)
        mock_print_json.assert_not_called()

        self.assertEqual(result.exit_code, 0)

    @patch("dafni_cli.commands.get.get_all_models")
    @patch("dafni_cli.commands.get.parse_models")
    @patch("dafni_cli.commands.get.print_json")
    def test_get_models_with_json_true(
        self, mock_print_json, mock_parse_models, mock_get_all_models, mock_DAFNISession
    ):
        """Tests that the 'get models' command works correctly (with json
        True)"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        models = [MagicMock(), MagicMock()]
        mock_get_all_models.return_value = models
        mock_parse_models.return_value = models

        # CALL
        result = runner.invoke(get.get, ["models", "--json"])

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_get_all_models.assert_called_with(session)
        for model in models:
            model.output_details.assert_not_called()
        mock_print_json.assert_called_with(models)

        self.assertEqual(result.exit_code, 0)

    def _test_get_models_with_date_filter(
        self,
        mock_print_json,
        mock_parse_models,
        mock_get_all_models,
        mock_DAFNISession,
        date_filter_options,
        long,
    ):
        """Helper method for testing that the 'get models' command works
        correctly with the given date filters"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        models = [MagicMock(), MagicMock()]

        # Make the first model filter but the second not
        models[0].filter_by_date = MagicMock(return_value=True)
        models[1].filter_by_date = MagicMock(return_value=False)

        mock_get_all_models.return_value = models
        mock_parse_models.return_value = models

        # CALL
        options = ["models", date_filter_options[0], "01/01/2023"]
        if long:
            options.append("--long")
        result = runner.invoke(get.get, options)

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_get_all_models.assert_called_with(session)
        models[0].filter_by_date.assert_called_with(date_filter_options[1], ANY)
        models[0].output_details.assert_called_with(long)
        models[1].output_details.assert_not_called()

        mock_print_json.assert_not_called()

        self.assertEqual(result.exit_code, 0)

    @patch("dafni_cli.commands.get.get_all_models")
    @patch("dafni_cli.commands.get.parse_models")
    @patch("dafni_cli.commands.get.print_json")
    def test_get_models_with_creation_date_filter(
        self,
        mock_print_json,
        mock_parse_models,
        mock_get_all_models,
        mock_DAFNISession,
    ):
        """Tests that the 'get models' command works correctly (while
        filtering by creation date)"""

        self._test_get_models_with_date_filter(
            mock_print_json,
            mock_parse_models,
            mock_get_all_models,
            mock_DAFNISession,
            ("--creation-date", "creation"),
            False,
        )

    @patch("dafni_cli.commands.get.get_all_models")
    @patch("dafni_cli.commands.get.parse_models")
    @patch("dafni_cli.commands.get.print_json")
    def test_get_models_with_publication_date_filter(
        self,
        mock_print_json,
        mock_parse_models,
        mock_get_all_models,
        mock_DAFNISession,
    ):
        """Tests that the 'get models' command works correctly (while
        filtering by publication date)"""

        self._test_get_models_with_date_filter(
            mock_print_json,
            mock_parse_models,
            mock_get_all_models,
            mock_DAFNISession,
            ("--publication-date", "publication"),
            False,
        )

    @patch("dafni_cli.commands.get.get_all_models")
    @patch("dafni_cli.commands.get.parse_models")
    @patch("dafni_cli.commands.get.print_json")
    def test_get_models_with_creation_date_filter_and_long_true(
        self,
        mock_print_json,
        mock_parse_models,
        mock_get_all_models,
        mock_DAFNISession,
    ):
        """Tests that the 'get models' command works correctly (while
        filtering by creation date and long=True)"""

        self._test_get_models_with_date_filter(
            mock_print_json,
            mock_parse_models,
            mock_get_all_models,
            mock_DAFNISession,
            ("--creation-date", "creation"),
            True,
        )

    @patch("dafni_cli.commands.get.get_all_models")
    @patch("dafni_cli.commands.get.parse_models")
    @patch("dafni_cli.commands.get.print_json")
    def test_get_models_with_publication_date_filter_and_long_true(
        self,
        mock_print_json,
        mock_parse_models,
        mock_get_all_models,
        mock_DAFNISession,
    ):
        """Tests that the 'get models' command works correctly (while
        filtering by publication date and long=True)"""

        self._test_get_models_with_date_filter(
            mock_print_json,
            mock_parse_models,
            mock_get_all_models,
            mock_DAFNISession,
            ("--publication-date", "publication"),
            True,
        )

    def _test_get_models_with_date_filter_json(
        self,
        mock_print_json,
        mock_parse_models,
        mock_get_all_models,
        mock_DAFNISession,
        date_filter_options,
    ):
        """Helper method for testing that the 'get models' command works
        correctly with the given date filters"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        models = [MagicMock(), MagicMock()]

        # Make the first model filter but the second not
        models[0].filter_by_date = MagicMock(return_value=True)
        models[1].filter_by_date = MagicMock(return_value=False)

        mock_get_all_models.return_value = models
        mock_parse_models.return_value = models

        # CALL
        options = ["models", date_filter_options[0], "01/01/2023", "--json"]
        result = runner.invoke(get.get, options)

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_get_all_models.assert_called_with(session)
        models[0].filter_by_date.assert_called_with(date_filter_options[1], ANY)
        models[0].output_details.assert_not_called()
        models[1].output_details.assert_not_called()

        mock_print_json.assert_called_with([models[0]])

        self.assertEqual(result.exit_code, 0)

    @patch("dafni_cli.commands.get.get_all_models")
    @patch("dafni_cli.commands.get.parse_models")
    @patch("dafni_cli.commands.get.print_json")
    def test_get_models_with_creation_date_filter_json(
        self,
        mock_print_json,
        mock_parse_models,
        mock_get_all_models,
        mock_DAFNISession,
    ):
        """Tests that the 'get models' command works correctly (while
        filtering by creation date and printing json)"""

        self._test_get_models_with_date_filter_json(
            mock_print_json,
            mock_parse_models,
            mock_get_all_models,
            mock_DAFNISession,
            ("--creation-date", "creation"),
        )

    @patch("dafni_cli.commands.get.get_all_models")
    @patch("dafni_cli.commands.get.parse_models")
    @patch("dafni_cli.commands.get.print_json")
    def test_get_models_with_publication_date_filter_json(
        self,
        mock_print_json,
        mock_parse_models,
        mock_get_all_models,
        mock_DAFNISession,
    ):
        """Tests that the 'get models' command works correctly (while
        filtering by publication date and printing json)"""

        self._test_get_models_with_date_filter_json(
            mock_print_json,
            mock_parse_models,
            mock_get_all_models,
            mock_DAFNISession,
            ("--publication-date", "publication"),
        )

    # ----------------- MODEL

    @patch("dafni_cli.commands.get.get_model")
    @patch("dafni_cli.commands.get.parse_model")
    def test_get_model(self, mock_parse_model, mock_get_model, mock_DAFNISession):
        """Tests that the 'get model' command works correctly (with no
        optional arguments)"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        model = MagicMock()
        mock_get_model.return_value = model
        mock_parse_model.return_value = model

        # CALL
        result = runner.invoke(get.get, ["model", "some_version_id"])

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_get_model.assert_called_with(session, "some_version_id")
        model.output_info.assert_called_once()

        self.assertEqual(result.exit_code, 0)

    @patch("dafni_cli.commands.get.get_model")
    @patch("dafni_cli.commands.get.parse_model")
    @patch("dafni_cli.commands.get.print_json")
    def test_get_model_json(
        self, mock_print_json, mock_parse_model, mock_get_model, mock_DAFNISession
    ):
        """Tests that the 'get model' command works correctly (with --json)"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        model = MagicMock()
        mock_get_model.return_value = model
        mock_parse_model.return_value = model

        # CALL
        result = runner.invoke(get.get, ["model", "some_version_id", "--json"])

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_get_model.assert_called_with(session, "some_version_id")
        model.output_info.assert_not_called()
        mock_print_json.assert_called_once_with(model)

        self.assertEqual(result.exit_code, 0)

    @patch("dafni_cli.commands.get.get_model")
    @patch("dafni_cli.commands.get.parse_model")
    @patch("dafni_cli.commands.get.print_json")
    def test_get_model_version_history(
        self, mock_print_json, mock_parse_model, mock_get_model, mock_DAFNISession
    ):
        """Tests that the 'get model' command works correctly (with
        --version-history)"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        model = MagicMock()
        mock_get_model.return_value = model
        mock_parse_model.return_value = model

        # CALL
        result = runner.invoke(
            get.get, ["model", "some_version_id", "--version-history"]
        )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_get_model.assert_called_with(session, "some_version_id")
        model.output_version_history.assert_called_once()
        mock_print_json.assert_not_called()

        self.assertEqual(result.exit_code, 0)

    @patch("dafni_cli.commands.get.get_model")
    @patch("dafni_cli.commands.get.parse_model")
    @patch("dafni_cli.commands.get.print_json")
    def test_get_model_version_history_json(
        self, mock_print_json, mock_parse_model, mock_get_model, mock_DAFNISession
    ):
        """Tests that the 'get model' command works correctly (with --json
        and --version-history)"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        model = MagicMock()
        version_history = MagicMock()
        mock_get_model.return_value = {"version_history": [version_history]}
        mock_parse_model.return_value = model

        # CALL
        result = runner.invoke(
            get.get, ["model", "some_version_id", "--version-history", "--json"]
        )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_get_model.assert_called_with(session, "some_version_id")
        model.output_version_history.assert_not_called()
        mock_print_json.assert_called_once_with(version_history)

        self.assertEqual(result.exit_code, 0)

    # ----------------- DATASETS

    @patch("dafni_cli.commands.get.get_all_datasets")
    @patch("dafni_cli.commands.get.parse_datasets")
    @patch("dafni_cli.commands.get.print_json")
    def test_get_datasets(
        self,
        mock_print_json,
        mock_parse_datasets,
        mock_get_all_datasets,
        mock_DAFNISession,
    ):
        """Tests that the 'get datasets' command works correctly (with no
        optional arguments)"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        datasets = [MagicMock(), MagicMock()]
        mock_get_all_datasets.return_value = datasets
        mock_parse_datasets.return_value = datasets

        # CALL
        result = runner.invoke(get.get, ["datasets"])

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_get_all_datasets.assert_called_with(session, {})
        for dataset in datasets:
            dataset.output_dataset_details.assert_called_once()
        mock_print_json.assert_not_called()

        self.assertEqual(result.exit_code, 0)

    @patch("dafni_cli.commands.get.get_all_datasets")
    @patch("dafni_cli.commands.get.parse_datasets")
    @patch("dafni_cli.commands.get.print_json")
    def test_get_datasets_with_json_true(
        self,
        mock_print_json,
        mock_parse_datasets,
        mock_get_all_datasets,
        mock_DAFNISession,
    ):
        """Tests that the 'get datasets' command works correctly (with json
        True)"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        datasets = [MagicMock(), MagicMock()]
        mock_get_all_datasets.return_value = datasets
        mock_parse_datasets.return_value = datasets

        # CALL
        result = runner.invoke(get.get, ["datasets", "--json"])

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_get_all_datasets.assert_called_with(session, {})
        for dataset in datasets:
            dataset.output_details.assert_not_called()
        mock_print_json.assert_called_with(datasets)

        self.assertEqual(result.exit_code, 0)

    def _test_get_datasets_with_date_filter(
        self,
        mock_print_json,
        mock_parse_datasets,
        mock_get_all_datasets,
        mock_DAFNISession,
        date_filter_options,
    ):
        """Helper method for testing that the 'get datasets' command works
        correctly with the given date filters"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        datasets = [MagicMock(), MagicMock()]

        mock_get_all_datasets.return_value = datasets
        mock_parse_datasets.return_value = datasets

        # CALL
        options = ["datasets", date_filter_options[0], "01/01/2023"]
        result = runner.invoke(get.get, options)

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_get_all_datasets.assert_called_with(session, date_filter_options[1])
        datasets[0].output_dataset_details.assert_called_once()
        datasets[1].output_dataset_details.assert_called_once()
        mock_print_json.assert_not_called()

        self.assertEqual(result.exit_code, 0)

    @patch("dafni_cli.commands.get.get_all_datasets")
    @patch("dafni_cli.commands.get.parse_datasets")
    @patch("dafni_cli.commands.get.print_json")
    def test_get_datasets_with_start_date_filter(
        self,
        mock_print_json,
        mock_parse_datasets,
        mock_get_all_datasets,
        mock_DAFNISession,
    ):
        """Tests that the 'get datasets' command works correctly (while
        filtering by start date)"""

        self._test_get_datasets_with_date_filter(
            mock_print_json,
            mock_parse_datasets,
            mock_get_all_datasets,
            mock_DAFNISession,
            (
                "--start-date",
                {
                    "date_range": {
                        "data_with_no_date": False,
                        "begin": "2023-01-01T00:00:00",
                    }
                },
            ),
        )

    @patch("dafni_cli.commands.get.get_all_datasets")
    @patch("dafni_cli.commands.get.parse_datasets")
    @patch("dafni_cli.commands.get.print_json")
    def test_get_datasets_with_end_date_filter(
        self,
        mock_print_json,
        mock_parse_datasets,
        mock_get_all_datasets,
        mock_DAFNISession,
    ):
        """Tests that the 'get datasets' command works correctly (while
        filtering by end date)"""

        self._test_get_datasets_with_date_filter(
            mock_print_json,
            mock_parse_datasets,
            mock_get_all_datasets,
            mock_DAFNISession,
            (
                "--end-date",
                {
                    "date_range": {
                        "data_with_no_date": False,
                        "end": "2023-01-01T00:00:00",
                    }
                },
            ),
        )

    # ----------------- DATASET

    @patch("dafni_cli.commands.get.get_latest_dataset_metadata")
    @patch("dafni_cli.commands.get.parse_dataset_metadata")
    @patch("dafni_cli.commands.get.print_json")
    def test_get_dataset(
        self,
        mock_print_json,
        mock_parse_dataset_metadata,
        mock_get_latest_dataset_metadata,
        mock_DAFNISession,
    ):
        """Tests that the 'get dataset' command works correctly (with no
        optional arguments)"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        dataset = MagicMock()
        mock_get_latest_dataset_metadata.return_value = dataset
        mock_parse_dataset_metadata.return_value = dataset

        # CALL
        result = runner.invoke(get.get, ["dataset", "some_version_id"])

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_get_latest_dataset_metadata.assert_called_with(session, "some_version_id")
        dataset.output_metadata_details.assert_called_once()
        mock_print_json.assert_not_called()

        self.assertEqual(result.exit_code, 0)

    @patch("dafni_cli.commands.get.get_latest_dataset_metadata")
    @patch("dafni_cli.commands.get.parse_dataset_metadata")
    @patch("dafni_cli.commands.get.print_json")
    def test_get_dataset_json(
        self,
        mock_print_json,
        mock_parse_dataset_metadata,
        mock_get_latest_dataset_metadata,
        mock_DAFNISession,
    ):
        """Tests that the 'get dataset' command works correctly (with --json)"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        dataset = MagicMock()
        mock_get_latest_dataset_metadata.return_value = dataset
        mock_parse_dataset_metadata.return_value = dataset

        # CALL
        result = runner.invoke(get.get, ["dataset", "some_version_id", "--json"])

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_get_latest_dataset_metadata.assert_called_with(session, "some_version_id")
        dataset.output_metadata_details.assert_not_called()
        mock_print_json.assert_called_once_with(dataset)

        self.assertEqual(result.exit_code, 0)

    @patch("dafni_cli.commands.get.get_latest_dataset_metadata")
    @patch("dafni_cli.commands.get.parse_dataset_metadata")
    @patch("dafni_cli.commands.get.print_json")
    def test_get_dataset_version_history(
        self,
        mock_print_json,
        mock_parse_dataset_metadata,
        mock_get_latest_dataset_metadata,
        mock_DAFNISession,
    ):
        """Tests that the 'get dataset' command works correctly (with
        --version-history)"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        dataset = MagicMock()
        dataset.version_history = MagicMock()
        mock_get_latest_dataset_metadata.return_value = dataset
        mock_parse_dataset_metadata.return_value = dataset

        # CALL
        result = runner.invoke(
            get.get, ["dataset", "some_version_id", "--version-history"]
        )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_get_latest_dataset_metadata.assert_called_with(session, "some_version_id")
        dataset.version_history.process_and_output_version_history.assert_called_once_with(
            session, False
        )
        mock_print_json.assert_not_called()

        self.assertEqual(result.exit_code, 0)

    @patch("dafni_cli.commands.get.get_latest_dataset_metadata")
    @patch("dafni_cli.commands.get.parse_dataset_metadata")
    @patch("dafni_cli.commands.get.print_json")
    def test_get_dataset_version_history_json(
        self,
        mock_print_json,
        mock_parse_dataset_metadata,
        mock_get_latest_dataset_metadata,
        mock_DAFNISession,
    ):
        """Tests that the 'get dataset' command works correctly (with --json
        and --version-history)"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        dataset = MagicMock()
        dataset.version_history = MagicMock()
        mock_get_latest_dataset_metadata.return_value = dataset
        mock_parse_dataset_metadata.return_value = dataset

        # CALL
        result = runner.invoke(
            get.get,
            ["dataset", "some_version_id", "--version-history", "--json"],
        )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_get_latest_dataset_metadata.assert_called_with(session, "some_version_id")
        dataset.version_history.process_and_output_version_history.assert_called_once_with(
            session, True
        )
        mock_print_json.assert_not_called()

        self.assertEqual(result.exit_code, 0)

    # ----------------- WORKFLOWS

    @patch("dafni_cli.commands.get.get_all_workflows")
    @patch("dafni_cli.commands.get.parse_workflows")
    @patch("dafni_cli.commands.get.print_json")
    def test_get_workflows(
        self,
        mock_print_json,
        mock_parse_workflows,
        mock_get_all_workflows,
        mock_DAFNISession,
    ):
        """Tests that the 'get workflows' command works correctly (with no
        optional arguments)"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        workflows = [MagicMock(), MagicMock()]
        mock_get_all_workflows.return_value = workflows
        mock_parse_workflows.return_value = workflows

        # CALL
        result = runner.invoke(get.get, ["workflows"])

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_get_all_workflows.assert_called_with(session)
        for workflow in workflows:
            workflow.output_details.assert_called_with(False)
        mock_print_json.assert_not_called()

        self.assertEqual(result.exit_code, 0)

    @patch("dafni_cli.commands.get.get_all_workflows")
    @patch("dafni_cli.commands.get.parse_workflows")
    @patch("dafni_cli.commands.get.print_json")
    def test_get_workflows_with_long_true(
        self,
        mock_print_json,
        mock_parse_workflows,
        mock_get_all_workflows,
        mock_DAFNISession,
    ):
        """Tests that the 'get workflows' command works correctly (with long
        True)"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        workflows = [MagicMock(), MagicMock()]
        mock_get_all_workflows.return_value = workflows
        mock_parse_workflows.return_value = workflows

        # CALL
        result = runner.invoke(get.get, ["workflows", "--long"])

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_get_all_workflows.assert_called_with(session)
        for workflow in workflows:
            workflow.output_details.assert_called_with(True)
        mock_print_json.assert_not_called()

        self.assertEqual(result.exit_code, 0)

    @patch("dafni_cli.commands.get.get_all_workflows")
    @patch("dafni_cli.commands.get.parse_workflows")
    @patch("dafni_cli.commands.get.print_json")
    def test_get_workflows_with_json_true(
        self,
        mock_print_json,
        mock_parse_workflows,
        mock_get_all_workflows,
        mock_DAFNISession,
    ):
        """Tests that the 'get workflows' command works correctly (with json
        True)"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        workflows = [MagicMock(), MagicMock()]
        mock_get_all_workflows.return_value = workflows
        mock_parse_workflows.return_value = workflows

        # CALL
        result = runner.invoke(get.get, ["workflows", "--json"])

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_get_all_workflows.assert_called_with(session)
        for workflow in workflows:
            workflow.output_details.assert_not_called()
        mock_print_json.assert_called_with(workflows)

        self.assertEqual(result.exit_code, 0)

    def _test_get_workflows_with_date_filter(
        self,
        mock_print_json,
        mock_parse_workflows,
        mock_get_all_workflows,
        mock_DAFNISession,
        date_filter_options,
        long,
    ):
        """Helper method for testing that the 'get workflows' command works
        correctly with the given date filters"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        workflows = [MagicMock(), MagicMock()]

        # Make the first model filter but the second not
        workflows[0].filter_by_date = MagicMock(return_value=True)
        workflows[1].filter_by_date = MagicMock(return_value=False)

        mock_get_all_workflows.return_value = workflows
        mock_parse_workflows.return_value = workflows

        # CALL
        options = ["workflows", date_filter_options[0], "01/01/2023"]
        if long:
            options.append("--long")
        result = runner.invoke(get.get, options)

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_get_all_workflows.assert_called_with(session)
        workflows[0].filter_by_date.assert_called_with(date_filter_options[1], ANY)
        workflows[0].output_details.assert_called_with(long)
        workflows[1].output_details.assert_not_called()
        mock_print_json.assert_not_called()

        self.assertEqual(result.exit_code, 0)

    @patch("dafni_cli.commands.get.get_all_workflows")
    @patch("dafni_cli.commands.get.parse_workflows")
    @patch("dafni_cli.commands.get.print_json")
    def test_get_workflows_with_creation_date_filter(
        self,
        mock_print_json,
        mock_parse_workflows,
        mock_get_all_workflows,
        mock_DAFNISession,
    ):
        """Tests that the 'get workflows' command works correctly (while
        filtering by creation date)"""

        self._test_get_workflows_with_date_filter(
            mock_print_json,
            mock_parse_workflows,
            mock_get_all_workflows,
            mock_DAFNISession,
            ("--creation-date", "creation"),
            False,
        )

    @patch("dafni_cli.commands.get.get_all_workflows")
    @patch("dafni_cli.commands.get.parse_workflows")
    @patch("dafni_cli.commands.get.print_json")
    def test_get_workflows_with_publication_date_filter(
        self,
        mock_print_json,
        mock_parse_workflows,
        mock_get_all_workflows,
        mock_DAFNISession,
    ):
        """Tests that the 'get workflows' command works correctly (while
        filtering by publication date)"""

        self._test_get_workflows_with_date_filter(
            mock_print_json,
            mock_parse_workflows,
            mock_get_all_workflows,
            mock_DAFNISession,
            ("--publication-date", "publication"),
            False,
        )

    @patch("dafni_cli.commands.get.get_all_workflows")
    @patch("dafni_cli.commands.get.parse_workflows")
    @patch("dafni_cli.commands.get.print_json")
    def test_get_workflows_with_creation_date_filter_and_long_true(
        self,
        mock_print_json,
        mock_parse_workflows,
        mock_get_all_workflows,
        mock_DAFNISession,
    ):
        """Tests that the 'get workflows' command works correctly (while
        filtering by creation date and long=True)"""

        self._test_get_workflows_with_date_filter(
            mock_print_json,
            mock_parse_workflows,
            mock_get_all_workflows,
            mock_DAFNISession,
            ("--creation-date", "creation"),
            True,
        )

    @patch("dafni_cli.commands.get.get_all_workflows")
    @patch("dafni_cli.commands.get.parse_workflows")
    @patch("dafni_cli.commands.get.print_json")
    def test_get_workflows_with_publication_date_filter_and_long_true(
        self,
        mock_print_json,
        mock_parse_workflows,
        mock_get_all_workflows,
        mock_DAFNISession,
    ):
        """Tests that the 'get workflows' command works correctly (while
        filtering by publication date and long=True)"""

        self._test_get_workflows_with_date_filter(
            mock_print_json,
            mock_parse_workflows,
            mock_get_all_workflows,
            mock_DAFNISession,
            ("--publication-date", "publication"),
            True,
        )

    def _test_get_workflows_with_date_filter_json(
        self,
        mock_print_json,
        mock_parse_workflows,
        mock_get_all_workflows,
        mock_DAFNISession,
        date_filter_options,
    ):
        """Helper method for testing that the 'get workflows' command works
        correctly with the given date filters and the --json flag"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        workflows = [MagicMock(), MagicMock()]

        # Make the first model filter but the second not
        workflows[0].filter_by_date = MagicMock(return_value=True)
        workflows[1].filter_by_date = MagicMock(return_value=False)

        mock_get_all_workflows.return_value = workflows
        mock_parse_workflows.return_value = workflows

        # CALL
        options = ["workflows", date_filter_options[0], "01/01/2023", "--json"]
        result = runner.invoke(get.get, options)

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_get_all_workflows.assert_called_with(session)
        workflows[0].filter_by_date.assert_called_with(date_filter_options[1], ANY)
        workflows[0].output_details.assert_not_called()
        workflows[1].output_details.assert_not_called()
        mock_print_json.assert_called_with([workflows[0]])

        self.assertEqual(result.exit_code, 0)

    @patch("dafni_cli.commands.get.get_all_workflows")
    @patch("dafni_cli.commands.get.parse_workflows")
    @patch("dafni_cli.commands.get.print_json")
    def test_get_workflows_with_creation_date_filter_json(
        self,
        mock_print_json,
        mock_parse_workflows,
        mock_get_all_workflows,
        mock_DAFNISession,
    ):
        """Tests that the 'get workflows' command works correctly (while
        filtering by creation date and printing json)"""

        self._test_get_workflows_with_date_filter_json(
            mock_print_json,
            mock_parse_workflows,
            mock_get_all_workflows,
            mock_DAFNISession,
            ("--creation-date", "creation"),
        )

    @patch("dafni_cli.commands.get.get_all_workflows")
    @patch("dafni_cli.commands.get.parse_workflows")
    @patch("dafni_cli.commands.get.print_json")
    def test_get_workflows_with_publication_date_filter_json(
        self,
        mock_print_json,
        mock_parse_workflows,
        mock_get_all_workflows,
        mock_DAFNISession,
    ):
        """Tests that the 'get workflows' command works correctly (while
        filtering by publication date and printing json)"""

        self._test_get_workflows_with_date_filter_json(
            mock_print_json,
            mock_parse_workflows,
            mock_get_all_workflows,
            mock_DAFNISession,
            ("--publication-date", "publication"),
        )

    # ----------------- WORKFLOW

    @patch("dafni_cli.commands.get.get_workflow")
    @patch("dafni_cli.commands.get.parse_workflow")
    @patch("dafni_cli.commands.get.print_json")
    def test_get_workflow(
        self, mock_print_json, mock_parse_workflow, mock_get_workflow, mock_DAFNISession
    ):
        """Tests that the 'get workflow' command works correctly (with no
        optional arguments)"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        workflow = MagicMock()
        mock_get_workflow.return_value = workflow
        mock_parse_workflow.return_value = workflow

        # CALL
        result = runner.invoke(get.get, ["workflow", "some_version_id"])

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_get_workflow.assert_called_with(session, "some_version_id")
        workflow.output_info.assert_called_once()
        mock_print_json.assert_not_called()

        self.assertEqual(result.exit_code, 0)

    @patch("dafni_cli.commands.get.get_workflow")
    @patch("dafni_cli.commands.get.parse_workflow")
    @patch("dafni_cli.commands.get.print_json")
    def test_get_workflow_json(
        self, mock_print_json, mock_parse_workflow, mock_get_workflow, mock_DAFNISession
    ):
        """Tests that the 'get workflow' command works correctly (with --json)"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        workflow = MagicMock()
        mock_get_workflow.return_value = workflow
        mock_parse_workflow.return_value = workflow

        # CALL
        result = runner.invoke(get.get, ["workflow", "some_version_id", "--json"])

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_get_workflow.assert_called_with(session, "some_version_id")
        workflow.output_info.assert_not_called()
        mock_print_json.assert_called_once_with(workflow)

        self.assertEqual(result.exit_code, 0)

    @patch("dafni_cli.commands.get.get_workflow")
    @patch("dafni_cli.commands.get.parse_workflow")
    @patch("dafni_cli.commands.get.print_json")
    def test_get_workflow_version_history(
        self, mock_print_json, mock_parse_workflow, mock_get_workflow, mock_DAFNISession
    ):
        """Tests that the 'get workflow' command works correctly (with
        --version-history)"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        workflow = MagicMock()
        mock_get_workflow.return_value = workflow
        mock_parse_workflow.return_value = workflow

        # CALL
        result = runner.invoke(
            get.get, ["workflow", "some_version_id", "--version-history"]
        )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_get_workflow.assert_called_with(session, "some_version_id")
        workflow.output_version_history.assert_called_once()
        mock_print_json.assert_not_called()

        self.assertEqual(result.exit_code, 0)

    @patch("dafni_cli.commands.get.get_workflow")
    @patch("dafni_cli.commands.get.parse_workflow")
    @patch("dafni_cli.commands.get.print_json")
    def test_get_workflow_version_history_json(
        self, mock_print_json, mock_parse_workflow, mock_get_workflow, mock_DAFNISession
    ):
        """Tests that the 'get workflow' command works correctly (with --json
        and --version-history)"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        workflow = MagicMock()
        version_history = MagicMock()
        mock_get_workflow.return_value = {"version_history": [version_history]}
        mock_parse_workflow.return_value = workflow

        # CALL
        result = runner.invoke(
            get.get, ["workflow", "some_version_id", "--version-history", "--json"]
        )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_get_workflow.assert_called_with(session, "some_version_id")
        workflow.output_version_history.assert_not_called()
        mock_print_json.assert_called_once_with(version_history)

        self.assertEqual(result.exit_code, 0)

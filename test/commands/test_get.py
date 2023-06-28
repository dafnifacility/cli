from datetime import datetime
from unittest import TestCase
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from dafni_cli.api.exceptions import ResourceNotFoundError
from dafni_cli.commands import get
from dafni_cli.consts import DATE_INPUT_FORMAT

from test.fixtures.dataset_metadata import TEST_DATASET_METADATA


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


class TestGetModels(TestCase):
    """Test class to test the get models command"""

    def setUp(
        self,
    ) -> None:
        super().setUp()

        self.mock_DAFNISession = patch("dafni_cli.commands.get.DAFNISession").start()
        self.mock_get_all_models = patch(
            "dafni_cli.commands.get.get_all_models"
        ).start()
        self.mock_parse_models = patch("dafni_cli.commands.get.parse_models").start()
        self.mock_print_json = patch("dafni_cli.commands.get.print_json").start()
        self.mock_text_filter = patch("dafni_cli.commands.get.text_filter").start()
        self.mock_creation_date_filter = patch(
            "dafni_cli.commands.get.creation_date_filter"
        ).start()
        self.mock_publication_date_filter = patch(
            "dafni_cli.commands.get.publication_date_filter"
        ).start()
        self.mock_filter_multiple = patch(
            "dafni_cli.commands.get.filter_multiple"
        ).start()

        self.addCleanup(patch.stopall)

    def test_get_models(self):
        """Tests that the 'get models' command works correctly (with no
        optional arguments)"""

        # SETUP
        session = MagicMock()
        self.mock_DAFNISession.return_value = session
        runner = CliRunner()
        model_dicts = [MagicMock(), MagicMock()]
        models = [MagicMock(), MagicMock()]
        self.mock_get_all_models.return_value = model_dicts
        self.mock_parse_models.return_value = models

        # No filtering
        self.mock_filter_multiple.return_value = models, model_dicts

        # CALL
        result = runner.invoke(get.get, ["models"])

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_get_all_models.assert_called_with(session)
        self.mock_filter_multiple.assert_called_with([], models, model_dicts)
        for model in models:
            model.output_details.assert_called_with(False)
        self.mock_print_json.assert_not_called()

        self.assertEqual(result.exit_code, 0)

    def test_get_models_with_long_true(self):
        """Tests that the 'get models' command works correctly (with long
        True)"""

        # SETUP
        session = MagicMock()
        self.mock_DAFNISession.return_value = session
        runner = CliRunner()
        model_dicts = [MagicMock(), MagicMock()]
        models = [MagicMock(), MagicMock()]
        self.mock_get_all_models.return_value = model_dicts
        self.mock_parse_models.return_value = models

        # No filtering
        self.mock_filter_multiple.return_value = models, model_dicts

        # CALL
        result = runner.invoke(get.get, ["models", "--long"])

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_get_all_models.assert_called_with(session)
        self.mock_filter_multiple.assert_called_with([], models, model_dicts)
        for model in models:
            model.output_details.assert_called_with(True)
        self.mock_print_json.assert_not_called()

        self.assertEqual(result.exit_code, 0)

    def test_get_models_with_json_true(self):
        """Tests that the 'get models' command works correctly (with json
        True)"""

        # SETUP
        session = MagicMock()
        self.mock_DAFNISession.return_value = session
        runner = CliRunner()
        model_dicts = [MagicMock(), MagicMock()]
        models = [MagicMock(), MagicMock()]
        self.mock_get_all_models.return_value = model_dicts
        self.mock_parse_models.return_value = models

        # No filtering
        self.mock_filter_multiple.return_value = models, model_dicts

        # CALL
        result = runner.invoke(get.get, ["models", "--json"])

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_get_all_models.assert_called_with(session)
        self.mock_filter_multiple.assert_called_with([], models, model_dicts)
        for model in models:
            model.output_details.assert_not_called()
        self.mock_print_json.assert_called_with(model_dicts)

        self.assertEqual(result.exit_code, 0)

    def test_get_models_with_text_filter(
        self,
    ):
        """Tests that the 'get models' command works correctly with a
        search text filter"""

        # SETUP
        session = MagicMock()
        self.mock_DAFNISession.return_value = session
        runner = CliRunner()
        model_dicts = [MagicMock(), MagicMock()]
        models = [MagicMock(), MagicMock()]
        search_text = "Test"

        self.mock_get_all_models.return_value = model_dicts
        self.mock_parse_models.return_value = models

        # Make the first model filter but the second not
        self.mock_filter_multiple.return_value = [models[0]], [model_dicts[0]]

        # CALL
        options = ["models", "--search", search_text]
        result = runner.invoke(get.get, options)

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_get_all_models.assert_called_with(session)
        self.mock_text_filter.assert_called_once_with(search_text)
        self.mock_creation_date_filter.assert_not_called()
        self.mock_publication_date_filter.assert_not_called()
        self.mock_filter_multiple.assert_called_with(
            [self.mock_text_filter.return_value], models, model_dicts
        )

        models[0].output_details.assert_called_with(False)
        models[1].output_details.assert_not_called()
        self.mock_print_json.assert_not_called()

        self.assertEqual(result.exit_code, 0)

    def _test_get_models_with_date_filter(
        self,
        date_filter_options,
        mock_date_filter,
        long,
    ):
        """Helper method for testing that the 'get models' command works
        correctly with the given date filters"""

        # SETUP
        session = MagicMock()
        self.mock_DAFNISession.return_value = session
        runner = CliRunner()
        model_dicts = [MagicMock(), MagicMock()]
        models = [MagicMock(), MagicMock()]
        date = datetime(2023, 1, 1)

        self.mock_get_all_models.return_value = model_dicts
        self.mock_parse_models.return_value = models

        # Make the first model filter but the second not
        self.mock_filter_multiple.return_value = [models[0]], [model_dicts[0]]

        # CALL
        options = ["models", date_filter_options[0], date.strftime(DATE_INPUT_FORMAT)]
        if long:
            options.append("--long")
        result = runner.invoke(get.get, options)

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_get_all_models.assert_called_with(session)
        mock_date_filter.assert_called_once_with(date)
        self.mock_filter_multiple.assert_called_with(
            [mock_date_filter.return_value], models, model_dicts
        )
        models[0].output_details.assert_called_with(long)
        models[1].output_details.assert_not_called()

        self.mock_print_json.assert_not_called()

        self.assertEqual(result.exit_code, 0)

    def test_get_models_with_creation_date_filter(
        self,
    ):
        """Tests that the 'get models' command works correctly (while
        filtering by creation date)"""

        self._test_get_models_with_date_filter(
            ("--creation-date", "creation"),
            self.mock_creation_date_filter,
            False,
        )

    def test_get_models_with_publication_date_filter(
        self,
    ):
        """Tests that the 'get models' command works correctly (while
        filtering by publication date)"""

        self._test_get_models_with_date_filter(
            ("--publication-date", "publication"),
            self.mock_publication_date_filter,
            False,
        )

    def test_get_models_with_creation_date_filter_and_long_true(
        self,
    ):
        """Tests that the 'get models' command works correctly (while
        filtering by creation date and long=True)"""

        self._test_get_models_with_date_filter(
            ("--creation-date", "creation"),
            self.mock_creation_date_filter,
            True,
        )

    def test_get_models_with_publication_date_filter_and_long_true(
        self,
    ):
        """Tests that the 'get models' command works correctly (while
        filtering by publication date and long=True)"""

        self._test_get_models_with_date_filter(
            ("--publication-date", "publication"),
            self.mock_publication_date_filter,
            True,
        )

    def _test_get_models_with_date_filter_json(
        self,
        date_filter_options,
        mock_date_filter,
    ):
        """Helper method for testing that the 'get models' command works
        correctly with the given date filters"""

        # SETUP
        session = MagicMock()
        self.mock_DAFNISession.return_value = session
        runner = CliRunner()
        model_dicts = [MagicMock(), MagicMock()]
        models = [MagicMock(), MagicMock()]
        date = datetime(2023, 1, 1)

        self.mock_get_all_models.return_value = model_dicts
        self.mock_parse_models.return_value = models

        # Make the first model filter but the second not
        self.mock_filter_multiple.return_value = [models[0]], [model_dicts[0]]

        # CALL
        options = [
            "models",
            date_filter_options[0],
            date.strftime(DATE_INPUT_FORMAT),
            "--json",
        ]
        result = runner.invoke(get.get, options)

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_get_all_models.assert_called_with(session)
        mock_date_filter.assert_called_once_with(date)
        self.mock_filter_multiple.assert_called_with(
            [mock_date_filter.return_value], models, model_dicts
        )
        models[0].output_details.assert_not_called()
        models[1].output_details.assert_not_called()

        self.mock_print_json.assert_called_with([model_dicts[0]])

        self.assertEqual(result.exit_code, 0)

    def test_get_models_with_creation_date_filter_json(
        self,
    ):
        """Tests that the 'get models' command works correctly (while
        filtering by creation date and printing json)"""

        self._test_get_models_with_date_filter_json(
            ("--creation-date", "creation"), self.mock_creation_date_filter
        )

    def test_get_models_with_publication_date_filter_json(
        self,
    ):
        """Tests that the 'get models' command works correctly (while
        filtering by publication date and printing json)"""

        self._test_get_models_with_date_filter_json(
            ("--publication-date", "publication"), self.mock_publication_date_filter
        )


@patch("dafni_cli.commands.get.DAFNISession")
@patch("dafni_cli.commands.get.cli_get_model")
@patch("dafni_cli.commands.get.parse_model")
@patch("dafni_cli.commands.get.print_json")
class TestGetModel(TestCase):
    """Test class to test the get model command"""

    def test_get_model(
        self, mock_print_json, mock_parse_model, mock_cli_get_model, mock_DAFNISession
    ):
        """Tests that the 'get model' command works correctly (with no
        optional arguments)"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        model = MagicMock()
        mock_cli_get_model.return_value = model
        mock_parse_model.return_value = model

        # CALL
        result = runner.invoke(get.get, ["model", "some_version_id"])

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_cli_get_model.assert_called_with(session, "some_version_id")
        model.output_info.assert_called_once()
        mock_print_json.assert_not_called()

        self.assertEqual(result.exit_code, 0)

    def test_get_model_json(
        self, mock_print_json, mock_parse_model, mock_cli_get_model, mock_DAFNISession
    ):
        """Tests that the 'get model' command works correctly (with --json)"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        model = MagicMock()
        mock_cli_get_model.return_value = model
        mock_parse_model.return_value = model

        # CALL
        result = runner.invoke(get.get, ["model", "some_version_id", "--json"])

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_cli_get_model.assert_called_with(session, "some_version_id")
        model.output_info.assert_not_called()
        mock_print_json.assert_called_once_with(model)

        self.assertEqual(result.exit_code, 0)

    def test_get_model_version_history(
        self, mock_print_json, mock_parse_model, mock_cli_get_model, mock_DAFNISession
    ):
        """Tests that the 'get model' command works correctly (with
        --version-history)"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        model = MagicMock()
        mock_cli_get_model.return_value = model
        mock_parse_model.return_value = model

        # CALL
        result = runner.invoke(
            get.get, ["model", "some_version_id", "--version-history"]
        )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_cli_get_model.assert_called_with(session, "some_version_id")
        model.output_version_history.assert_called_once()
        mock_print_json.assert_not_called()

        self.assertEqual(result.exit_code, 0)

    def test_get_model_version_history_json(
        self, mock_print_json, mock_parse_model, mock_cli_get_model, mock_DAFNISession
    ):
        """Tests that the 'get model' command works correctly (with --json
        and --version-history)"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        model = MagicMock()
        version_history = MagicMock()
        mock_cli_get_model.return_value = {"version_history": [version_history]}
        mock_parse_model.return_value = model

        # CALL
        result = runner.invoke(
            get.get, ["model", "some_version_id", "--version-history", "--json"]
        )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_cli_get_model.assert_called_with(session, "some_version_id")
        model.output_version_history.assert_not_called()
        mock_print_json.assert_called_once_with(version_history)

        self.assertEqual(result.exit_code, 0)


@patch("dafni_cli.commands.get.DAFNISession")
@patch("dafni_cli.commands.get.get_all_datasets")
@patch("dafni_cli.commands.get.parse_datasets")
@patch("dafni_cli.commands.get.print_json")
class TestGetDatasets(TestCase):
    """Test class to test the get datasets command"""

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
            dataset.output_brief_details.assert_called_once()
        mock_print_json.assert_not_called()

        self.assertEqual(result.exit_code, 0)

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
        options = ["datasets", date_filter_options[0], "2023-01-01"]
        result = runner.invoke(get.get, options)

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_get_all_datasets.assert_called_with(session, date_filter_options[1])
        datasets[0].output_brief_details.assert_called_once()
        datasets[1].output_brief_details.assert_called_once()
        mock_print_json.assert_not_called()

        self.assertEqual(result.exit_code, 0)

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


@patch("dafni_cli.commands.get.DAFNISession")
@patch("dafni_cli.commands.get.cli_get_latest_dataset_metadata")
@patch("dafni_cli.commands.get.parse_dataset_metadata")
@patch("dafni_cli.commands.get.print_json")
class TestGetDataset(TestCase):
    """Test class to test the get dataset command"""

    def test_get_dataset(
        self,
        mock_print_json,
        mock_parse_dataset_metadata,
        mock_cli_get_latest_dataset_metadata,
        mock_DAFNISession,
    ):
        """Tests that the 'get dataset' command works correctly (with no
        optional arguments)"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        dataset = MagicMock()
        mock_cli_get_latest_dataset_metadata.return_value = dataset
        mock_parse_dataset_metadata.return_value = dataset

        # CALL
        result = runner.invoke(get.get, ["dataset", "some_version_id"])

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_cli_get_latest_dataset_metadata.assert_called_with(
            session, "some_version_id"
        )
        dataset.output_details.assert_called_once()
        mock_print_json.assert_not_called()

        self.assertEqual(result.exit_code, 0)

    def test_get_dataset_json(
        self,
        mock_print_json,
        mock_parse_dataset_metadata,
        mock_cli_get_latest_dataset_metadata,
        mock_DAFNISession,
    ):
        """Tests that the 'get dataset' command works correctly (with --json)"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        dataset = MagicMock()
        mock_cli_get_latest_dataset_metadata.return_value = dataset
        mock_parse_dataset_metadata.return_value = dataset

        # CALL
        result = runner.invoke(get.get, ["dataset", "some_version_id", "--json"])

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_cli_get_latest_dataset_metadata.assert_called_with(
            session, "some_version_id"
        )
        dataset.output_details.assert_not_called()
        mock_print_json.assert_called_once_with(dataset)

        self.assertEqual(result.exit_code, 0)

    def test_get_dataset_version_history(
        self,
        mock_print_json,
        mock_parse_dataset_metadata,
        mock_cli_get_latest_dataset_metadata,
        mock_DAFNISession,
    ):
        """Tests that the 'get dataset' command works correctly with
        --version-history"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        dataset = MagicMock()
        dataset.version_history = MagicMock()
        mock_cli_get_latest_dataset_metadata.return_value = TEST_DATASET_METADATA
        mock_parse_dataset_metadata.return_value = dataset

        # CALL
        result = runner.invoke(
            get.get, ["dataset", "some_version_id", "--version-history"]
        )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_cli_get_latest_dataset_metadata.assert_called_with(
            session, "some_version_id"
        )
        dataset.version_history.output_version_history.assert_called_once()
        mock_print_json.assert_not_called()

        self.assertEqual(result.exit_code, 0)

    def test_get_dataset_version_history_json(
        self,
        mock_print_json,
        mock_parse_dataset_metadata,
        mock_cli_get_latest_dataset_metadata,
        mock_DAFNISession,
    ):
        """Tests that the 'get dataset' command works correctly with --json
        and --version-history"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        dataset = MagicMock()
        dataset.version_history = MagicMock()
        mock_cli_get_latest_dataset_metadata.return_value = TEST_DATASET_METADATA
        mock_parse_dataset_metadata.return_value = dataset

        # CALL
        result = runner.invoke(
            get.get,
            ["dataset", "some_version_id", "--version-history", "--json"],
        )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_cli_get_latest_dataset_metadata.assert_called_with(
            session, "some_version_id"
        )
        dataset.version_history.output_version_history.assert_not_called()
        mock_print_json.assert_called_once_with(
            TEST_DATASET_METADATA["version_history"]
        )

        self.assertEqual(result.exit_code, 0)


class TestGetWorkflows(TestCase):
    """Test class to test the get workflows command"""

    def setUp(
        self,
    ) -> None:
        super().setUp()

        self.mock_DAFNISession = patch("dafni_cli.commands.get.DAFNISession").start()
        self.mock_get_all_workflows = patch(
            "dafni_cli.commands.get.get_all_workflows"
        ).start()
        self.mock_parse_workflows = patch(
            "dafni_cli.commands.get.parse_workflows"
        ).start()
        self.mock_print_json = patch("dafni_cli.commands.get.print_json").start()
        self.mock_text_filter = patch("dafni_cli.commands.get.text_filter").start()
        self.mock_creation_date_filter = patch(
            "dafni_cli.commands.get.creation_date_filter"
        ).start()
        self.mock_publication_date_filter = patch(
            "dafni_cli.commands.get.publication_date_filter"
        ).start()
        self.mock_filter_multiple = patch(
            "dafni_cli.commands.get.filter_multiple"
        ).start()

        self.addCleanup(patch.stopall)

    def test_get_workflows(self):
        """Tests that the 'get workflows' command works correctly (with no
        optional arguments)"""

        # SETUP
        session = MagicMock()
        self.mock_DAFNISession.return_value = session
        runner = CliRunner()
        workflow_dicts = [MagicMock(), MagicMock()]
        workflows = [MagicMock(), MagicMock()]
        self.mock_get_all_workflows.return_value = workflow_dicts
        self.mock_parse_workflows.return_value = workflows

        # No filtering
        self.mock_filter_multiple.return_value = workflows, workflow_dicts

        # CALL
        result = runner.invoke(get.get, ["workflows"])

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_get_all_workflows.assert_called_with(session)
        self.mock_filter_multiple.assert_called_with([], workflows, workflow_dicts)
        for workflow in workflows:
            workflow.output_details.assert_called_with(False)
        self.mock_print_json.assert_not_called()

        self.assertEqual(result.exit_code, 0)

    def test_get_workflows_with_long_true(self):
        """Tests that the 'get workflows' command works correctly (with long
        True)"""

        # SETUP
        session = MagicMock()
        self.mock_DAFNISession.return_value = session
        runner = CliRunner()
        workflow_dicts = [MagicMock(), MagicMock()]
        workflows = [MagicMock(), MagicMock()]
        self.mock_get_all_workflows.return_value = workflow_dicts
        self.mock_parse_workflows.return_value = workflows

        # No filtering
        self.mock_filter_multiple.return_value = workflows, workflow_dicts

        # CALL
        result = runner.invoke(get.get, ["workflows", "--long"])

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_get_all_workflows.assert_called_with(session)
        self.mock_filter_multiple.assert_called_with([], workflows, workflow_dicts)
        for workflow in workflows:
            workflow.output_details.assert_called_with(True)
        self.mock_print_json.assert_not_called()

        self.assertEqual(result.exit_code, 0)

    def test_get_workflows_with_json_true(
        self,
    ):
        """Tests that the 'get workflows' command works correctly (with json
        True)"""

        # SETUP
        session = MagicMock()
        self.mock_DAFNISession.return_value = session
        runner = CliRunner()
        workflow_dicts = [MagicMock(), MagicMock()]
        workflows = [MagicMock(), MagicMock()]
        self.mock_get_all_workflows.return_value = workflow_dicts
        self.mock_parse_workflows.return_value = workflows

        # No filtering
        self.mock_filter_multiple.return_value = workflows, workflow_dicts

        # CALL
        result = runner.invoke(get.get, ["workflows", "--json"])

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_get_all_workflows.assert_called_with(session)
        self.mock_filter_multiple.assert_called_with([], workflows, workflow_dicts)
        for workflow in workflows:
            workflow.output_details.assert_not_called()
        self.mock_print_json.assert_called_with(workflow_dicts)

        self.assertEqual(result.exit_code, 0)

    def test_get_workflows_with_text_filter(
        self,
    ):
        """Tests that the 'get workflows' command works correctly with a
        search text filter"""

        # SETUP
        session = MagicMock()
        self.mock_DAFNISession.return_value = session
        runner = CliRunner()
        workflow_dicts = [MagicMock(), MagicMock()]
        workflows = [MagicMock(), MagicMock()]
        search_text = "Test"

        self.mock_get_all_workflows.return_value = workflow_dicts
        self.mock_parse_workflows.return_value = workflows

        # Make the first model filter but the second not
        self.mock_filter_multiple.return_value = [workflows[0]], [workflow_dicts[0]]

        # CALL
        options = ["workflows", "--search", search_text]
        result = runner.invoke(get.get, options)

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_get_all_workflows.assert_called_with(session)
        self.mock_text_filter.assert_called_once_with(search_text)
        self.mock_creation_date_filter.assert_not_called()
        self.mock_publication_date_filter.assert_not_called()
        self.mock_filter_multiple.assert_called_with(
            [self.mock_text_filter.return_value], workflows, workflow_dicts
        )

        workflows[0].output_details.assert_called_with(False)
        workflows[1].output_details.assert_not_called()
        self.mock_print_json.assert_not_called()

        self.assertEqual(result.exit_code, 0)

    def _test_get_workflows_with_date_filter(
        self,
        date_filter_options,
        mock_date_filter,
        long,
    ):
        """Helper method for testing that the 'get workflows' command works
        correctly with the given date filters"""

        # SETUP
        session = MagicMock()
        self.mock_DAFNISession.return_value = session
        runner = CliRunner()
        workflow_dicts = [MagicMock(), MagicMock()]
        workflows = [MagicMock(), MagicMock()]
        date = datetime(2023, 1, 1)

        self.mock_get_all_workflows.return_value = workflow_dicts
        self.mock_parse_workflows.return_value = workflows

        # Make the first workflow filter but the second not
        self.mock_filter_multiple.return_value = [workflows[0]], [workflow_dicts[0]]

        # CALL
        options = [
            "workflows",
            date_filter_options[0],
            date.strftime(DATE_INPUT_FORMAT),
        ]
        if long:
            options.append("--long")
        result = runner.invoke(get.get, options)

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_get_all_workflows.assert_called_with(session)
        mock_date_filter.assert_called_once_with(date)
        self.mock_filter_multiple.assert_called_with(
            [mock_date_filter.return_value], workflows, workflow_dicts
        )

        workflows[0].output_details.assert_called_with(long)
        workflows[1].output_details.assert_not_called()
        self.mock_print_json.assert_not_called()

        self.assertEqual(result.exit_code, 0)

    def test_get_workflows_with_creation_date_filter(
        self,
    ):
        """Tests that the 'get workflows' command works correctly (while
        filtering by creation date)"""

        self._test_get_workflows_with_date_filter(
            ("--creation-date", "creation"),
            self.mock_creation_date_filter,
            False,
        )

    def test_get_workflows_with_publication_date_filter(
        self,
    ):
        """Tests that the 'get workflows' command works correctly (while
        filtering by publication date)"""

        self._test_get_workflows_with_date_filter(
            ("--publication-date", "publication"),
            self.mock_publication_date_filter,
            False,
        )

    def test_get_workflows_with_creation_date_filter_and_long_true(
        self,
    ):
        """Tests that the 'get workflows' command works correctly (while
        filtering by creation date and long=True)"""

        self._test_get_workflows_with_date_filter(
            ("--creation-date", "creation"),
            self.mock_creation_date_filter,
            True,
        )

    def test_get_workflows_with_publication_date_filter_and_long_true(
        self,
    ):
        """Tests that the 'get workflows' command works correctly (while
        filtering by publication date and long=True)"""

        self._test_get_workflows_with_date_filter(
            ("--publication-date", "publication"),
            self.mock_publication_date_filter,
            True,
        )

    def _test_get_workflows_with_date_filter_json(
        self,
        date_filter_options,
        mock_date_filter,
    ):
        """Helper method for testing that the 'get workflows' command works
        correctly with the given date filters and the --json flag"""

        # SETUP
        session = MagicMock()
        self.mock_DAFNISession.return_value = session
        runner = CliRunner()
        workflow_dicts = [MagicMock(), MagicMock()]
        workflows = [MagicMock(), MagicMock()]
        date = datetime(2023, 1, 1)

        self.mock_get_all_workflows.return_value = workflow_dicts
        self.mock_parse_workflows.return_value = workflows

        # Make the first workflow filter but the second not
        self.mock_filter_multiple.return_value = [workflows[0]], [workflow_dicts[0]]

        # CALL
        options = [
            "workflows",
            date_filter_options[0],
            date.strftime(DATE_INPUT_FORMAT),
            "--json",
        ]
        result = runner.invoke(get.get, options)

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_get_all_workflows.assert_called_with(session)
        mock_date_filter.assert_called_once_with(date)
        self.mock_filter_multiple.assert_called_with(
            [mock_date_filter.return_value], workflows, workflow_dicts
        )
        workflows[0].output_details.assert_not_called()
        workflows[1].output_details.assert_not_called()
        self.mock_print_json.assert_called_with([workflow_dicts[0]])

        self.assertEqual(result.exit_code, 0)

    def test_get_workflows_with_creation_date_filter_json(
        self,
    ):
        """Tests that the 'get workflows' command works correctly (while
        filtering by creation date and printing json)"""

        self._test_get_workflows_with_date_filter_json(
            ("--creation-date", "creation"),
            self.mock_creation_date_filter,
        )

    def test_get_workflows_with_publication_date_filter_json(
        self,
    ):
        """Tests that the 'get workflows' command works correctly (while
        filtering by publication date and printing json)"""

        self._test_get_workflows_with_date_filter_json(
            ("--publication-date", "publication"), self.mock_publication_date_filter
        )

    def test_get_workflows_with_all_filters(
        self,
    ):
        """Tests that the 'get workflows' command works correctly with a
        one of each filter"""

        # SETUP
        session = MagicMock()
        self.mock_DAFNISession.return_value = session
        runner = CliRunner()
        workflow_dicts = [MagicMock(), MagicMock()]
        workflows = [MagicMock(), MagicMock()]
        search_text = "Test"
        creation_date = datetime(2022, 6, 28)
        publication_date = datetime(2022, 12, 11)

        self.mock_get_all_workflows.return_value = workflow_dicts
        self.mock_parse_workflows.return_value = workflows

        # Make the first model filter but the second not
        self.mock_filter_multiple.return_value = [workflows[0]], [workflow_dicts[0]]

        # CALL
        options = [
            "workflows",
            "--search",
            search_text,
            "--creation-date",
            creation_date,
            "--publication-date",
            publication_date,
        ]
        result = runner.invoke(get.get, options)

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_get_all_workflows.assert_called_with(session)
        self.mock_text_filter.assert_called_once_with(search_text)
        self.mock_creation_date_filter.assert_called_once_with(creation_date)
        self.mock_publication_date_filter.assert_called_once_with(publication_date)
        self.mock_filter_multiple.assert_called_with(
            [
                self.mock_text_filter.return_value,
                self.mock_creation_date_filter.return_value,
                self.mock_publication_date_filter.return_value,
            ],
            workflows,
            workflow_dicts,
        )

        workflows[0].output_details.assert_called_with(False)
        workflows[1].output_details.assert_not_called()
        self.mock_print_json.assert_not_called()

        self.assertEqual(result.exit_code, 0)


@patch("dafni_cli.commands.get.DAFNISession")
@patch("dafni_cli.commands.get.cli_get_workflow")
@patch("dafni_cli.commands.get.parse_workflow")
@patch("dafni_cli.commands.get.print_json")
class TestGetWorkflow(TestCase):
    """Test class to test the get workflow command"""

    def test_get_workflow(
        self,
        mock_print_json,
        mock_parse_workflow,
        mock_cli_get_workflow,
        mock_DAFNISession,
    ):
        """Tests that the 'get workflow' command works correctly (with no
        optional arguments)"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        workflow = MagicMock()
        mock_cli_get_workflow.return_value = workflow
        mock_parse_workflow.return_value = workflow

        # CALL
        result = runner.invoke(get.get, ["workflow", "some_version_id"])

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_cli_get_workflow.assert_called_with(session, "some_version_id")
        workflow.output_info.assert_called_once()
        mock_print_json.assert_not_called()

        self.assertEqual(result.exit_code, 0)

    def test_get_workflow_json(
        self,
        mock_print_json,
        mock_parse_workflow,
        mock_cli_get_workflow,
        mock_DAFNISession,
    ):
        """Tests that the 'get workflow' command works correctly (with --json)"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        workflow = MagicMock()
        mock_cli_get_workflow.return_value = workflow
        mock_parse_workflow.return_value = workflow

        # CALL
        result = runner.invoke(get.get, ["workflow", "some_version_id", "--json"])

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_cli_get_workflow.assert_called_with(session, "some_version_id")
        workflow.output_info.assert_not_called()
        mock_print_json.assert_called_once_with(workflow)

        self.assertEqual(result.exit_code, 0)

    def test_get_workflow_version_history(
        self,
        mock_print_json,
        mock_parse_workflow,
        mock_cli_get_workflow,
        mock_DAFNISession,
    ):
        """Tests that the 'get workflow' command works correctly (with
        --version-history)"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        workflow = MagicMock()
        mock_cli_get_workflow.return_value = workflow
        mock_parse_workflow.return_value = workflow

        # CALL
        result = runner.invoke(
            get.get, ["workflow", "some_version_id", "--version-history"]
        )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_cli_get_workflow.assert_called_with(session, "some_version_id")
        workflow.output_version_history.assert_called_once()
        mock_print_json.assert_not_called()

        self.assertEqual(result.exit_code, 0)

    def test_get_workflow_version_history_json(
        self,
        mock_print_json,
        mock_parse_workflow,
        mock_cli_get_workflow,
        mock_DAFNISession,
    ):
        """Tests that the 'get workflow' command works correctly (with --json
        and --version-history)"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        workflow = MagicMock()
        version_history = MagicMock()
        mock_cli_get_workflow.return_value = {"version_history": [version_history]}
        mock_parse_workflow.return_value = workflow

        # CALL
        result = runner.invoke(
            get.get, ["workflow", "some_version_id", "--version-history", "--json"]
        )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_cli_get_workflow.assert_called_with(session, "some_version_id")
        workflow.output_version_history.assert_not_called()
        mock_print_json.assert_called_once_with(version_history)

        self.assertEqual(result.exit_code, 0)


class TestGetWorkflowInstances(TestCase):
    """Test class to test the get workflow-instances command"""

    def setUp(
        self,
    ) -> None:
        super().setUp()

        self.mock_DAFNISession = patch("dafni_cli.commands.get.DAFNISession").start()
        self.mock_cli_get_workflow = patch(
            "dafni_cli.commands.get.cli_get_workflow"
        ).start()
        self.mock_parse_workflow = patch(
            "dafni_cli.commands.get.parse_workflow"
        ).start()
        self.mock_print_json = patch("dafni_cli.commands.get.print_json").start()
        self.mock_click = patch("dafni_cli.commands.get.click").start()

        self.addCleanup(patch.stopall)

    def test_get_workflows(self):
        """Tests that the 'get workflows' command works correctly (with no
        optional arguments)"""

        # SETUP
        session = MagicMock()
        self.mock_DAFNISession.return_value = session
        runner = CliRunner()
        version_id = "version_id"
        workflow_dict = {"instances": MagicMock()}
        workflow = MagicMock()
        self.mock_cli_get_workflow.return_value = workflow_dict
        self.mock_parse_workflow.return_value = workflow

        # CALL
        result = runner.invoke(get.get, ["workflow-instances", version_id])

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_cli_get_workflow.assert_called_once_with(session, version_id)
        self.mock_parse_workflow.assert_called_once_with(workflow_dict)
        self.mock_print_json.assert_not_called()
        workflow.format_instances.assert_called_once()
        self.mock_click.echo.assert_called_once_with(
            workflow.format_instances.return_value
        )

        self.assertEqual(result.exit_code, 0)

    def test_get_workflows_with_json_true(
        self,
    ):
        """Tests that the 'get workflows' command works correctly (with json
        True)"""

        # SETUP
        session = MagicMock()
        self.mock_DAFNISession.return_value = session
        runner = CliRunner()
        version_id = "version_id"
        workflow_dict = {"instances": MagicMock()}
        workflow = MagicMock()
        self.mock_cli_get_workflow.return_value = workflow_dict
        self.mock_parse_workflow.return_value = workflow

        # CALL
        result = runner.invoke(get.get, ["workflow-instances", version_id, "--json"])

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_cli_get_workflow.assert_called_once_with(session, version_id)
        self.mock_parse_workflow.assert_called_once_with(workflow_dict)
        self.mock_print_json.assert_called_once_with(workflow_dict["instances"])
        workflow.format_instances.assert_not_called()
        self.mock_click.echo.assert_not_called()

        self.assertEqual(result.exit_code, 0)

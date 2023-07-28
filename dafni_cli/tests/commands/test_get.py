from datetime import datetime
from typing import List
from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from click.testing import CliRunner

from dafni_cli.commands import get
from dafni_cli.consts import (
    DATE_INPUT_FORMAT,
    TABLE_ACCESS_HEADER,
    TABLE_DISPLAY_NAME_MAX_COLUMN_WIDTH,
    TABLE_FINISHED_HEADER,
    TABLE_ID_HEADER,
    TABLE_NAME_HEADER,
    TABLE_PARAMETER_SET_HEADER,
    TABLE_PUBLICATION_DATE_HEADER,
    TABLE_STARTED_HEADER,
    TABLE_STATUS_HEADER,
    TABLE_SUMMARY_HEADER,
    TABLE_SUMMARY_MAX_COLUMN_WIDTH,
    TABLE_VERSION_ID_HEADER,
    TABLE_WORKFLOW_VERSION_ID_HEADER,
)
from dafni_cli.tests.fixtures.dataset_metadata import TEST_DATASET_METADATA


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
        self.mock_click = patch("dafni_cli.commands.get.click").start()
        self.mock_format_table = patch("dafni_cli.commands.get.format_table").start()

        self.addCleanup(patch.stopall)

    def _test_get_models_with_filters(
        self, filter_arguments: List, expected_filters: List, json: bool
    ):
        """Helper method for testing that the 'get models' command
        works correctly for some given filters"""

        # SETUP
        session = MagicMock()
        self.mock_DAFNISession.return_value = session
        runner = CliRunner()
        model_dicts = [MagicMock(), MagicMock()]
        models = [MagicMock(), MagicMock()]
        self.mock_get_all_models.return_value = model_dicts
        self.mock_parse_models.return_value = models

        # Make the first model filter but the second not
        self.mock_filter_multiple.return_value = (
            [models[0]],
            [model_dicts[0]],
        )

        # CALL
        options = ["models"]
        options.extend(filter_arguments)
        if json:
            options.append("--json")
        result = runner.invoke(get.get, options)

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_get_all_models.assert_called_with(session)
        self.mock_parse_models.assert_called_once_with(model_dicts)
        self.mock_filter_multiple.assert_called_once_with(
            expected_filters, models, model_dicts
        )

        # Different outputs depending on json flag
        if json:
            self.mock_print_json.assert_called_with([model_dicts[0]])
            for model in models:
                model.get_brief_details.assert_not_called()
            self.mock_format_table.assert_not_called()
            self.mock_click.echo.assert_not_called()
        else:
            self.mock_print_json.assert_not_called()

            models[0].get_brief_details.assert_called_once()
            models[1].get_brief_details.assert_not_called()

            self.mock_format_table.assert_called_once_with(
                headers=[
                    TABLE_NAME_HEADER,
                    TABLE_VERSION_ID_HEADER,
                    TABLE_STATUS_HEADER,
                    TABLE_ACCESS_HEADER,
                    TABLE_PUBLICATION_DATE_HEADER,
                    TABLE_SUMMARY_HEADER,
                ],
                rows=[models[0].get_brief_details.return_value],
                max_column_widths=[
                    TABLE_DISPLAY_NAME_MAX_COLUMN_WIDTH,
                    None,
                    None,
                    None,
                    None,
                    TABLE_SUMMARY_MAX_COLUMN_WIDTH,
                ],
            )
            self.mock_click.echo.assert_called_once_with(
                self.mock_format_table.return_value
            )

        self.assertEqual(result.exit_code, 0)

    def test_get_models(self):
        """Tests that the 'get models' command works correctly (with no
        optional arguments)"""

        self._test_get_models_with_filters(
            filter_arguments=[], expected_filters=[], json=False
        )

    def test_get_models_json(self):
        """Tests that the 'get models' command works correctly (with json
        True)"""

        self._test_get_models_with_filters(
            filter_arguments=[], expected_filters=[], json=True
        )

    def test_get_models_with_text_filter(
        self,
    ):
        """Tests that the 'get models' command works correctly with a
        search text filter"""

        # SETUP
        search_text = "Test"

        # CALL & ASSERT
        self._test_get_models_with_filters(
            filter_arguments=["--search", search_text],
            expected_filters=[self.mock_text_filter.return_value],
            json=False,
        )
        self.mock_text_filter.assert_called_once_with(search_text)

    def test_get_models_with_text_filter_json(
        self,
    ):
        """Tests that the 'get models' command works correctly with a
        search text filter (with json=True)"""

        # SETUP
        search_text = "Test"

        # CALL & ASSERT
        self._test_get_models_with_filters(
            filter_arguments=["--search", search_text],
            expected_filters=[self.mock_text_filter.return_value],
            json=True,
        )
        self.mock_text_filter.assert_called_once_with(search_text)

    def _test_get_models_with_date_filter(
        self,
        filter_argument: str,
        mock_date_filter,
        json: bool,
    ):
        """Helper method for testing that the 'get models' command
        works correctly with a given date filter"""

        # SETUP
        date = datetime(2023, 1, 1)

        # CALL & ASSERT
        self._test_get_models_with_filters(
            filter_arguments=[filter_argument, date.strftime(DATE_INPUT_FORMAT)],
            expected_filters=[mock_date_filter.return_value],
            json=json,
        )
        mock_date_filter.assert_called_once_with(date)

    def test_get_models_with_creation_date_filter(
        self,
    ):
        """Tests that the 'get models' command works correctly (while
        filtering by creation date)"""

        self._test_get_models_with_date_filter(
            filter_argument="--creation-date",
            mock_date_filter=self.mock_creation_date_filter,
            json=False,
        )

    def test_get_models_with_creation_date_filter_json(
        self,
    ):
        """Tests that the 'get models' command works correctly (while
        filtering by creation date and json=True)"""

        self._test_get_models_with_date_filter(
            filter_argument="--creation-date",
            mock_date_filter=self.mock_creation_date_filter,
            json=True,
        )

    def test_get_models_with_publication_date_filter(
        self,
    ):
        """Tests that the 'get models' command works correctly (while
        filtering by publication date)"""

        self._test_get_models_with_date_filter(
            filter_argument="--publication-date",
            mock_date_filter=self.mock_publication_date_filter,
            json=False,
        )

    def test_get_models_with_publication_date_filter_json(
        self,
    ):
        """Tests that the 'get models' command works correctly (while
        filtering by publication date and json=True)"""

        self._test_get_models_with_date_filter(
            filter_argument="--publication-date",
            mock_date_filter=self.mock_publication_date_filter,
            json=True,
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
        model.output_details.assert_called_once()
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
        model.output_details.assert_not_called()
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


class TestGetDatasets(TestCase):
    """Test class to test the get datasets command"""

    def setUp(
        self,
    ) -> None:
        super().setUp()

        self.mock_DAFNISession = patch("dafni_cli.commands.get.DAFNISession").start()
        self.mock_get_all_datasets = patch(
            "dafni_cli.commands.get.get_all_datasets"
        ).start()
        self.mock_parse_datasets = patch(
            "dafni_cli.commands.get.parse_datasets"
        ).start()
        self.mock_print_json = patch("dafni_cli.commands.get.print_json").start()

        self.addCleanup(patch.stopall)

    def test_get_datasets(
        self,
    ):
        """Tests that the 'get datasets' command works correctly (with no
        optional arguments)"""

        # SETUP
        session = MagicMock()
        self.mock_DAFNISession.return_value = session
        runner = CliRunner()
        datasets = [MagicMock(), MagicMock()]
        self.mock_get_all_datasets.return_value = datasets
        self.mock_parse_datasets.return_value = datasets

        # CALL
        result = runner.invoke(get.get, ["datasets"])

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_get_all_datasets.assert_called_with(session, {})
        for dataset in datasets:
            dataset.output_brief_details.assert_called_once()
        self.mock_print_json.assert_not_called()

        self.assertEqual(result.exit_code, 0)

    def test_get_datasets_json(
        self,
    ):
        """Tests that the 'get datasets' command works correctly (with json
        True)"""

        # SETUP
        session = MagicMock()
        self.mock_DAFNISession.return_value = session
        runner = CliRunner()
        datasets = [MagicMock(), MagicMock()]
        self.mock_get_all_datasets.return_value = datasets
        self.mock_parse_datasets.return_value = datasets

        # CALL
        result = runner.invoke(get.get, ["datasets", "--json"])

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_get_all_datasets.assert_called_with(session, {})
        for dataset in datasets:
            dataset.output_details.assert_not_called()
        self.mock_print_json.assert_called_with(datasets)

        self.assertEqual(result.exit_code, 0)

    def _test_get_datasets_with_date_filter(
        self,
        date_filter_options,
    ):
        """Helper method for testing that the 'get datasets' command works
        correctly with the given date filters"""

        # SETUP
        session = MagicMock()
        self.mock_DAFNISession.return_value = session
        runner = CliRunner()
        datasets = [MagicMock(), MagicMock()]

        self.mock_get_all_datasets.return_value = datasets
        self.mock_parse_datasets.return_value = datasets

        # CALL
        options = ["datasets", date_filter_options[0], "2023-01-01"]
        result = runner.invoke(get.get, options)

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_get_all_datasets.assert_called_with(session, date_filter_options[1])
        datasets[0].output_brief_details.assert_called_once()
        datasets[1].output_brief_details.assert_called_once()
        self.mock_print_json.assert_not_called()

        self.assertEqual(result.exit_code, 0)

    def test_get_datasets_with_start_date_filter(
        self,
    ):
        """Tests that the 'get datasets' command works correctly (while
        filtering by start date)"""

        self._test_get_datasets_with_date_filter(
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
    ):
        """Tests that the 'get datasets' command works correctly (while
        filtering by end date)"""

        self._test_get_datasets_with_date_filter(
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
        self.mock_click = patch("dafni_cli.commands.get.click").start()
        self.mock_format_table = patch("dafni_cli.commands.get.format_table").start()

        self.addCleanup(patch.stopall)

    def _test_get_workflows_with_filters(
        self,
        filter_arguments: List,
        expected_filters: List,
        json: bool,
    ):
        """Helper method for testing that the 'get workflows' command
        works correctly for some given filters"""

        # SETUP
        session = MagicMock()
        self.mock_DAFNISession.return_value = session
        runner = CliRunner()
        workflow_dicts = [MagicMock(), MagicMock()]
        workflows = [MagicMock(), MagicMock()]
        self.mock_get_all_workflows.return_value = workflow_dicts
        self.mock_parse_workflows.return_value = workflows

        # Make the first workflow filter but the second not
        self.mock_filter_multiple.return_value = (
            [workflows[0]],
            [workflow_dicts[0]],
        )

        # CALL
        options = [
            "workflows",
        ]
        options.extend(filter_arguments)
        if json:
            options.append("--json")
        result = runner.invoke(get.get, options)

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_get_all_workflows.assert_called_with(session)
        self.mock_parse_workflows.assert_called_once_with(workflow_dicts)
        self.mock_filter_multiple.assert_called_once_with(
            expected_filters,
            workflows,
            workflow_dicts,
        )

        # Different outputs depending on json flag
        if json:
            self.mock_print_json.assert_called_once_with([workflow_dicts[0]])
            for workflow_instance in workflows:
                workflow_instance.get_brief_details.assert_not_called()
            self.mock_format_table.assert_not_called()
            self.mock_click.echo.assert_not_called()
        else:
            self.mock_print_json.assert_not_called()

            workflows[0].get_brief_details.assert_called_once()
            workflows[1].get_brief_details.assert_not_called()

            self.mock_format_table.assert_called_once_with(
                headers=[
                    TABLE_NAME_HEADER,
                    TABLE_VERSION_ID_HEADER,
                    TABLE_PUBLICATION_DATE_HEADER,
                    TABLE_SUMMARY_HEADER,
                ],
                rows=[workflows[0].get_brief_details.return_value],
                max_column_widths=[
                    TABLE_DISPLAY_NAME_MAX_COLUMN_WIDTH,
                    None,
                    None,
                    TABLE_SUMMARY_MAX_COLUMN_WIDTH,
                ],
            )
            self.mock_click.echo.assert_called_once_with(
                self.mock_format_table.return_value
            )

        self.assertEqual(result.exit_code, 0)

    def test_get_workflows(self):
        """Tests that the 'get workflows' command works correctly (with no
        optional arguments)"""

        self._test_get_workflows_with_filters(
            filter_arguments=[], expected_filters=[], json=False
        )

    def test_get_workflows_json(
        self,
    ):
        """Tests that the 'get workflows' command works correctly (with json
        True)"""

        self._test_get_workflows_with_filters(
            filter_arguments=[], expected_filters=[], json=True
        )

    def test_get_workflows_with_text_filter(
        self,
    ):
        """Tests that the 'get workflows' command works correctly with a
        search text filter"""

        # SETUP
        search_text = "Test"

        # CALL & ASSERT
        self._test_get_workflows_with_filters(
            filter_arguments=["--search", search_text],
            expected_filters=[self.mock_text_filter.return_value],
            json=False,
        )
        self.mock_text_filter.assert_called_once_with(search_text)

    def test_get_workflows_with_text_filter_json(
        self,
    ):
        """Tests that the 'get workflows' command works correctly with a
        search text filter (and json=True)"""

        # SETUP
        search_text = "Test"

        # CALL & ASSERT
        self._test_get_workflows_with_filters(
            filter_arguments=["--search", search_text],
            expected_filters=[self.mock_text_filter.return_value],
            json=True,
        )
        self.mock_text_filter.assert_called_once_with(search_text)

    def _test_get_workflows_with_date_filter(
        self,
        filter_argument: str,
        mock_date_filter,
        json: bool,
    ):
        """Helper method for testing that the 'get workflows' command works
        correctly with the given date filter"""

        # SETUP
        date = datetime(2023, 1, 1)

        # CALL & ASSERT
        self._test_get_workflows_with_filters(
            filter_arguments=[filter_argument, date.strftime(DATE_INPUT_FORMAT)],
            expected_filters=[mock_date_filter.return_value],
            json=json,
        )
        mock_date_filter.assert_called_once_with(date)

    def test_get_workflows_with_creation_date_filter(
        self,
    ):
        """Tests that the 'get workflows' command works correctly (while
        filtering by creation date)"""

        self._test_get_workflows_with_date_filter(
            filter_argument="--creation-date",
            mock_date_filter=self.mock_creation_date_filter,
            json=False,
        )

    def test_get_workflows_with_creation_date_filter_json(
        self,
    ):
        """Tests that the 'get workflows' command works correctly (while
        filtering by creation date and json=True)"""

        self._test_get_workflows_with_date_filter(
            filter_argument="--creation-date",
            mock_date_filter=self.mock_creation_date_filter,
            json=True,
        )

    def test_get_workflows_with_publication_date_filter(
        self,
    ):
        """Tests that the 'get workflows' command works correctly (while
        filtering by publication date)"""

        self._test_get_workflows_with_date_filter(
            filter_argument="--publication-date",
            mock_date_filter=self.mock_publication_date_filter,
            json=False,
        )

    def test_get_workflows_with_publication_date_filter_json(
        self,
    ):
        """Tests that the 'get workflows' command works correctly (while
        filtering by publication date and json=True)"""

        self._test_get_workflows_with_date_filter(
            filter_argument="--publication-date",
            mock_date_filter=self.mock_publication_date_filter,
            json=True,
        )

    def test_get_workflows_with_all_filters(
        self,
    ):
        """Tests that the 'get workflows' command works correctly while
        filtering by everything at once"""

        # SETUP
        search_text = "Test"
        creation_date = datetime(2022, 6, 28)
        publication_date = datetime(2022, 12, 11)

        # CALL & ASSERT
        self._test_get_workflows_with_filters(
            filter_arguments=[
                "--search",
                search_text,
                "--creation-date",
                creation_date.strftime(DATE_INPUT_FORMAT),
                "--publication-date",
                publication_date.strftime(DATE_INPUT_FORMAT),
            ],
            expected_filters=[
                self.mock_text_filter.return_value,
                self.mock_creation_date_filter.return_value,
                self.mock_publication_date_filter.return_value,
            ],
            json=False,
        )


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
        workflow.output_details.assert_called_once()
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
        workflow.output_details.assert_not_called()
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
        self.mock_start_filter = patch("dafni_cli.commands.get.start_filter").start()
        self.mock_end_filter = patch("dafni_cli.commands.get.end_filter").start()
        self.mock_status_filter = patch("dafni_cli.commands.get.status_filter").start()
        self.mock_filter_multiple = patch(
            "dafni_cli.commands.get.filter_multiple"
        ).start()
        self.mock_print_json = patch("dafni_cli.commands.get.print_json").start()
        self.mock_click = patch("dafni_cli.commands.get.click").start()
        self.mock_format_table = patch("dafni_cli.commands.get.format_table").start()

        self.addCleanup(patch.stopall)

    def _test_get_workflow_instances_with_filters(
        self,
        filter_arguments: List,
        expected_filters: List,
        json: bool,
    ):
        """Helper method for testing that the 'get workflow-instances' command
        works correctly for some given filters"""

        # SETUP
        session = MagicMock()
        self.mock_DAFNISession.return_value = session
        runner = CliRunner()
        version_id = "version_id"
        workflow_instance_dicts = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        workflow_instances = [
            MagicMock(finished_time=datetime(2023, 7, 12, 11, 11, 42)),
            MagicMock(finished_time=datetime(2021, 7, 12, 11, 11, 42)),
            MagicMock(finished_time=datetime(2022, 7, 12, 11, 11, 42)),
            MagicMock(finished_time=datetime(2023, 7, 12, 11, 11, 42)),
        ]
        workflow_dict = {"instances": workflow_instance_dicts}
        workflow = MagicMock(instances=workflow_instances)
        self.mock_cli_get_workflow.return_value = workflow_dict
        self.mock_parse_workflow.return_value = workflow

        # Make the first workflow instance filter but the second not
        self.mock_filter_multiple.return_value = (
            workflow_instances[:3],
            workflow_instance_dicts[:3],
        )

        # CALL
        options = [
            "workflow-instances",
            version_id,
        ]
        options.extend(filter_arguments)
        if json:
            options.append("--json")
        result = runner.invoke(get.get, options)

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_cli_get_workflow.assert_called_once_with(session, version_id)
        self.mock_parse_workflow.assert_called_once_with(workflow_dict)
        self.mock_filter_multiple.assert_called_once_with(
            expected_filters,
            workflow_instances,
            workflow_instance_dicts,
        )

        # Different outputs depending on json flag
        if json:
            self.mock_print_json.assert_called_once_with(
                workflow_instance_dicts[:3],
            )
            for workflow_instance in workflow_instances:
                workflow_instance.get_brief_details.assert_not_called()
            self.mock_format_table.assert_not_called()
            self.mock_click.echo.assert_not_called()
        else:
            self.mock_print_json.assert_not_called()

            workflow_instances[0].get_brief_details.assert_called_once()
            workflow_instances[1].get_brief_details.assert_called_once()
            workflow_instances[2].get_brief_details.assert_called_once()
            workflow_instances[3].get_brief_details.assert_not_called()

            self.mock_format_table.assert_called_once_with(
                headers=[
                    TABLE_ID_HEADER,
                    TABLE_WORKFLOW_VERSION_ID_HEADER,
                    TABLE_PARAMETER_SET_HEADER,
                    TABLE_STARTED_HEADER,
                    TABLE_FINISHED_HEADER,
                    TABLE_STATUS_HEADER,
                ],
                rows=[
                    # Should have been sorted
                    workflow_instances[1].get_brief_details.return_value,
                    workflow_instances[2].get_brief_details.return_value,
                    workflow_instances[0].get_brief_details.return_value,
                ],
            )
            self.mock_click.echo.assert_called_once_with(
                self.mock_format_table.return_value
            )

        self.assertEqual(result.exit_code, 0)

    def test_get_workflow_instances(self):
        """Tests that the 'get workflow-instances' command works correctly (with no
        optional arguments)"""

        self._test_get_workflow_instances_with_filters(
            filter_arguments=[], expected_filters=[], json=False
        )

    def test_get_workflow_instances_with_json_true(
        self,
    ):
        """Tests that the 'get workflow-instances' command works correctly (with json
        True)"""

        self._test_get_workflow_instances_with_filters(
            filter_arguments=[], expected_filters=[], json=True
        )

    def _test_get_workflow_instances_with_datetime_filter(
        self,
        filter_argument: str,
        mock_datetime_filter,
        json: bool,
    ):
        """Helper method for testing that the 'get workflow-instances' command
        works correctly with a given datetime filter"""

        # SETUP
        date = datetime(2023, 1, 1)

        # CALL & ASSERT
        self._test_get_workflow_instances_with_filters(
            filter_arguments=[filter_argument, date.strftime(DATE_INPUT_FORMAT)],
            expected_filters=[mock_datetime_filter.return_value],
            json=json,
        )
        mock_datetime_filter.assert_called_once_with(date)

    def test_get_workflow_instances_with_start_filter(
        self,
    ):
        """Tests that the 'get workflow-instances' command works correctly
        (while filtering by start date/time)"""

        self._test_get_workflow_instances_with_datetime_filter(
            filter_argument="--start",
            mock_datetime_filter=self.mock_start_filter,
            json=False,
        )

    def test_get_workflow_instances_with_start_filter_json(
        self,
    ):
        """Tests that the 'get workflow-instances' command works correctly
        (while filtering by start date/time and json=True)"""

        self._test_get_workflow_instances_with_datetime_filter(
            filter_argument="--start",
            mock_datetime_filter=self.mock_start_filter,
            json=True,
        )

    def test_get_workflow_instances_with_end_filter(
        self,
    ):
        """Tests that the 'get workflow-instances' command works correctly
        (while filtering by end date/time)"""

        self._test_get_workflow_instances_with_datetime_filter(
            filter_argument="--end",
            mock_datetime_filter=self.mock_end_filter,
            json=False,
        )

    def test_get_workflow_instances_with_end_filter_json(
        self,
    ):
        """Tests that the 'get workflow-instances' command works correctly
        (while filtering by end date/time and json=True)"""

        self._test_get_workflow_instances_with_datetime_filter(
            filter_argument="--end",
            mock_datetime_filter=self.mock_end_filter,
            json=True,
        )

    def _test_get_workflow_instances_with_status_filter(
        self, filter_argument: str, status: str, json: bool
    ):
        """Tests that the 'get workflow-instances' command works correctly
        (while filtering based on some status)"""

        self._test_get_workflow_instances_with_filters(
            filter_arguments=[filter_argument],
            expected_filters=[self.mock_status_filter.return_value],
            json=json,
        )
        self.mock_status_filter.assert_called_once_with(status)

    # The following uncommented tests each tests that the
    # 'get workflow-instances' command works correctly while filtering by
    # each potential status either with or without json flags
    def test_get_workflow_instances_with_cancelled_filter(self):
        self._test_get_workflow_instances_with_status_filter(
            "--cancelled", "Cancelled", json=False
        )

    def test_get_workflow_instances_with_cancelled_filter_json(self):
        self._test_get_workflow_instances_with_status_filter(
            "--cancelled", "Cancelled", json=True
        )

    def test_get_workflow_instances_with_error_filter(self):
        self._test_get_workflow_instances_with_status_filter(
            "--error", "Error", json=False
        )

    def test_get_workflow_instances_with_error_filter_json(self):
        self._test_get_workflow_instances_with_status_filter(
            "--error", "Error", json=True
        )

    def test_get_workflow_instances_with_failed_filter(self):
        self._test_get_workflow_instances_with_status_filter(
            "--failed", "Failed", json=False
        )

    def test_get_workflow_instances_with_failed_filter_json(self):
        self._test_get_workflow_instances_with_status_filter(
            "--failed", "Failed", json=True
        )

    def test_get_workflow_instances_with_omitted_filter(self):
        self._test_get_workflow_instances_with_status_filter(
            "--omitted", "Omitted", json=False
        )

    def test_get_workflow_instances_with_omitted_filter_json(self):
        self._test_get_workflow_instances_with_status_filter(
            "--omitted", "Omitted", json=True
        )

    def test_get_workflow_instances_with_pending_filter(self):
        self._test_get_workflow_instances_with_status_filter(
            "--pending", "Pending", json=False
        )

    def test_get_workflow_instances_with_pending_filter_json(self):
        self._test_get_workflow_instances_with_status_filter(
            "--pending", "Pending", json=True
        )

    def test_get_workflow_instances_with_running_filter(self):
        self._test_get_workflow_instances_with_status_filter(
            "--running", "Running", json=False
        )

    def test_get_workflow_instances_with_running_filter_json(self):
        self._test_get_workflow_instances_with_status_filter(
            "--running", "Running", json=True
        )

    def test_get_workflow_instances_with_succeeded_filter(self):
        self._test_get_workflow_instances_with_status_filter(
            "--succeeded", "Succeeded", json=False
        )

    def test_get_workflow_instances_with_succeeded_filter_json(self):
        self._test_get_workflow_instances_with_status_filter(
            "--succeeded", "Succeeded", json=True
        )

    def test_get_workflow_instances_with_all_filters(self):
        """Tests that the 'get workflow-instances' command works correctly
        while filtering by everything at once"""

        # SETUP
        start = datetime(2022, 6, 28)
        end = datetime(2022, 12, 11)

        # CALL & ASSERT
        self._test_get_workflow_instances_with_filters(
            filter_arguments=[
                "--start",
                start.strftime(DATE_INPUT_FORMAT),
                "--end",
                end.strftime(DATE_INPUT_FORMAT),
                "--cancelled",
                "--error",
                "--failed",
                "--omitted",
                "--pending",
                "--running",
                "--succeeded",
            ],
            expected_filters=[
                self.mock_start_filter.return_value,
                self.mock_end_filter.return_value,
                self.mock_status_filter.return_value,
                self.mock_status_filter.return_value,
                self.mock_status_filter.return_value,
                self.mock_status_filter.return_value,
                self.mock_status_filter.return_value,
                self.mock_status_filter.return_value,
                self.mock_status_filter.return_value,
            ],
            json=False,
        )
        self.mock_start_filter.assert_called_once_with(start)
        self.mock_end_filter.assert_called_once_with(end)
        self.assertEqual(
            self.mock_status_filter.mock_calls,
            [
                call("Cancelled"),
                call("Error"),
                call("Failed"),
                call("Omitted"),
                call("Pending"),
                call("Running"),
                call("Succeeded"),
            ],
        )


@patch("dafni_cli.commands.get.DAFNISession")
@patch("dafni_cli.commands.get.cli_get_workflow_instance")
@patch("dafni_cli.commands.get.parse_workflow_instance")
@patch("dafni_cli.commands.get.print_json")
class TestGetWorkflowInstance(TestCase):
    """Test class to test the get workflow-instance command"""

    def test_get_workflow_instance(
        self,
        mock_print_json,
        mock_parse_workflow_instance,
        mock_cli_get_workflow_instance,
        mock_DAFNISession,
    ):
        """Tests that the 'get workflow-instance' command works correctly"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        workflow_instance_dict = MagicMock()
        workflow_instance = MagicMock()
        mock_cli_get_workflow_instance.return_value = workflow_instance_dict
        mock_parse_workflow_instance.return_value = workflow_instance

        # CALL
        result = runner.invoke(get.get, ["workflow-instance", "some_instance_id"])

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_cli_get_workflow_instance.assert_called_with(session, "some_instance_id")
        mock_print_json.assert_not_called()
        mock_parse_workflow_instance.assert_called_once_with(workflow_instance_dict)
        workflow_instance.output_details.assert_called_once()

        self.assertEqual(result.exit_code, 0)

    def test_get_workflow_instance_json(
        self,
        mock_print_json,
        mock_parse_workflow_instance,
        mock_cli_get_workflow_instance,
        mock_DAFNISession,
    ):
        """Tests that the 'get workflow-version' command works correctly (with --json)"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        workflow_instance_dict = MagicMock()
        workflow_instance = MagicMock()
        mock_cli_get_workflow_instance.return_value = workflow_instance_dict
        mock_parse_workflow_instance.return_value = workflow_instance

        # CALL
        result = runner.invoke(
            get.get, ["workflow-instance", "some_instance_id", "--json"]
        )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_cli_get_workflow_instance.assert_called_with(session, "some_instance_id")
        mock_print_json.assert_called_once_with(workflow_instance_dict)
        mock_parse_workflow_instance.assert_not_called()
        workflow_instance.output_details.assert_not_called()

        self.assertEqual(result.exit_code, 0)


@patch("dafni_cli.commands.get.DAFNISession")
@patch("dafni_cli.commands.get.cli_get_workflow_parameter_set")
@patch("dafni_cli.commands.get.print_json")
class TestGetWorkflowParameterSet(TestCase):
    """Test class to test the get workflow-parameter-set command"""

    def test_get_workflow_parameter_set(
        self,
        mock_print_json,
        mock_cli_get_workflow_parameter_set,
        mock_DAFNISession,
    ):
        """Tests that the 'get workflow-parameter-set' command works correctly"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        workflow_inst = MagicMock()
        parameter_set = MagicMock()
        mock_cli_get_workflow_parameter_set.return_value = (
            workflow_inst,
            parameter_set,
        )

        # CALL
        result = runner.invoke(
            get.get,
            ["workflow-parameter-set", "workflow-version-id", "parameter-set-id"],
        )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_cli_get_workflow_parameter_set.assert_called_with(
            session, "workflow-version-id", "parameter-set-id"
        )
        mock_print_json.assert_not_called()
        parameter_set.output_details.assert_called_once_with(workflow_inst.spec)

        self.assertEqual(result.exit_code, 0)

    def test_get_workflow_parameter_set_json(
        self,
        mock_print_json,
        mock_cli_get_workflow_parameter_set,
        mock_DAFNISession,
    ):
        """Tests that the 'get workflow-parameter-set' command works correctly (with --json)"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        workflow_inst = MagicMock()
        parameter_set = MagicMock()
        mock_cli_get_workflow_parameter_set.return_value = (
            workflow_inst,
            parameter_set,
        )

        # CALL
        result = runner.invoke(
            get.get,
            [
                "workflow-parameter-set",
                "workflow-version-id",
                "parameter-set-id",
                "--json",
            ],
        )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_cli_get_workflow_parameter_set.assert_called_with(
            session, "workflow-version-id", "parameter-set-id"
        )
        mock_print_json.assert_called_once_with(parameter_set.dictionary)
        parameter_set.output_details.assert_not_called()

        self.assertEqual(result.exit_code, 0)

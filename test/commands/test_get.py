import pytest
from mock import patch, call
from click.testing import CliRunner

from dafni_cli.commands import get
from dafni_cli.model import (
    model,
    version_history,
)
from dafni_cli.datasets import dataset, dataset_metadata, dataset_version_history
from test.fixtures.jwt_fixtures import processed_jwt_fixture
from test.fixtures.model_fixtures import get_models_list_fixture
from test.fixtures.dataset_fixtures import (
    get_dataset_list_fixture,
    dataset_metadata_fixture,
)
from test.fixtures.model_fixtures import get_model_metadata_fixture


class TestGet:
    """test class to test the get() command functionality"""

    @patch("dafni_cli.commands.get.get_models_dicts")
    @patch("dafni_cli.commands.get.check_for_jwt_file")
    class TestInit:
        """Test class to test the get() group processing of the
        JWT
        """

        def test_jwt_retrieved_and_set_on_context(
            self, mock_jwt, mock_models, processed_jwt_fixture
        ):
            # SETUP
            mock_models.return_value = []
            mock_jwt.return_value = processed_jwt_fixture, False
            runner = CliRunner()
            ctx = {}

            # CALL
            result = runner.invoke(get.get, ["models"], obj=ctx)

            # ASSERT
            mock_jwt.assert_called_once()

            assert ctx["jwt"] == processed_jwt_fixture["jwt"]

            assert result.exit_code == 0

    @patch.object(model.Model, "filter_by_date")
    @patch.object(model.Model, "output_details")
    @patch("dafni_cli.commands.get.get_models_dicts")
    @patch("dafni_cli.commands.get.check_for_jwt_file")
    class TestModels:
        """Test class to test the get.models command"""

        @patch("dafni_cli.commands.get.process_response_to_class_list")
        def test_get_models_dict_called_with_jwt_from_context(
            self,
            mock_list,
            mock_jwt,
            mock_get,
            mock_output,
            mock_filter,
            processed_jwt_fixture,
            get_models_list_fixture,
        ):
            # SETUP
            # setup get group command
            mock_jwt.return_value = processed_jwt_fixture, False
            # setup get_models_dicts call
            models = get_models_list_fixture
            mock_get.return_value = models
            # setup create_model_list call
            mock_list.return_value = []
            # Setup click
            runner = CliRunner()

            # CALL
            result = runner.invoke(get.get, ["models"])

            # ASSERT
            mock_get.assert_called_once_with(processed_jwt_fixture["jwt"])
            mock_list.assert_called_once_with(models, model.Model)

            assert result.exit_code == 0

        def test_output_model_details_called_on_all_models_if_no_option_given(
            self,
            mock_jwt,
            mock_get,
            mock_output,
            mock_filter,
            processed_jwt_fixture,
            get_models_list_fixture,
        ):
            # SETUP
            # setup get group command
            mock_jwt.return_value = processed_jwt_fixture, False
            # setup get_models_dicts call
            models = get_models_list_fixture
            mock_get.return_value = models
            # Setup click
            runner = CliRunner()

            # CALL
            result = runner.invoke(get.get, ["models"])

            # ASSERT
            assert mock_output.call_count == len(models)
            mock_filter.assert_not_called()

            assert result.exit_code == 0

        @pytest.mark.parametrize(
            "option, value",
            [("--creation-date", "creation"), ("--publication-date", "publication")],
        )
        def test_output_model_details_called_on_no_models_if_filter_options_return_no_models(
            self,
            mock_jwt,
            mock_get,
            mock_output,
            mock_filter,
            option,
            value,
            processed_jwt_fixture,
            get_models_list_fixture,
        ):
            # SETUP
            date = "01/02/2021"
            # setup get group command
            mock_jwt.return_value = processed_jwt_fixture, False
            # setup get_models_dicts call
            models = get_models_list_fixture
            mock_get.return_value = models
            # setup filter_by_date return so that no models are displayed
            mock_filter.return_value = False
            # Setup click
            runner = CliRunner()

            # CALL
            result = runner.invoke(get.get, ["models", option, date])

            # ASSERT
            assert mock_output.call_count == 0
            assert mock_filter.call_args_list == [call(value, date), call(value, date)]
            assert result.exit_code == 0

        @pytest.mark.parametrize(
            "option, value",
            [("--creation-date", "creation"), ("--publication-date", "publication")],
        )
        def test_output_model_details_called_on_a_model_if_filter_options_return_models(
            self,
            mock_jwt,
            mock_get,
            mock_output,
            mock_filter,
            option,
            value,
            processed_jwt_fixture,
            get_models_list_fixture,
        ):
            # SETUP
            date = "01/02/2021"
            # setup get group command
            mock_jwt.return_value = processed_jwt_fixture, False
            # setup get_models_dicts call
            models = get_models_list_fixture
            mock_get.return_value = models
            # setup filter_by_date return so that the second model is displayed
            mock_filter.side_effect = False, True
            # Setup click
            runner = CliRunner()

            # CALL
            result = runner.invoke(get.get, ["models", option, date])

            # ASSERT
            assert mock_output.call_count == 1
            assert mock_filter.call_args_list == [call(value, date), call(value, date)]
            assert result.exit_code == 0

    @patch.object(model.Model, "get_details_from_id")
    @patch.object(model.Model, "get_metadata")
    @patch.object(model.Model, "output_metadata")
    @patch("dafni_cli.model.model.get_model_metadata_dict")
    @patch("dafni_cli.model.model.get_single_model_dict")
    @patch("dafni_cli.commands.get.check_for_jwt_file")
    class TestModel:
        """Test class to test the get.models command"""

        def test_model_methods_each_called_once_when_one_version_id_given(
            self,
            mock_jwt,
            mock_get,
            mock_set_metadata,
            mock_output,
            mock_get_metadata,
            mock_details,
            processed_jwt_fixture,
            get_models_list_fixture,
            get_model_metadata_fixture,
        ):
            # SETUP
            # setup get jwt
            mock_jwt.return_value = processed_jwt_fixture, False
            # setup retrieving
            mock_get.return_value = get_models_list_fixture[0]
            version_id = get_models_list_fixture[0]["id"]
            # setup setting metadata
            mock_set_metadata.return_value = get_model_metadata_fixture
            # Setup click
            runner = CliRunner()

            # CALL
            result = runner.invoke(get.get, ["model", version_id])

            # ASSERT
            mock_details.assert_called_once_with(
                processed_jwt_fixture["jwt"], version_id
            )
            mock_get_metadata.assert_called_once_with(processed_jwt_fixture["jwt"])
            mock_output.assert_called_once()
            assert result.exit_code == 0

        def test_model_methods_each_called_twice_when_two_version_ids_given(
            self,
            mock_jwt,
            mock_get,
            mock_set_metadata,
            mock_output,
            mock_get_metadata,
            mock_details,
            processed_jwt_fixture,
            get_models_list_fixture,
            get_model_metadata_fixture,
        ):
            # SETUP
            # setup get jwt
            mock_jwt.return_value = processed_jwt_fixture, False
            # setup retrieving
            mock_get.side_effect = get_models_list_fixture
            version_id_1 = get_models_list_fixture[0]["id"]
            version_id_2 = get_models_list_fixture[1]["id"]
            # setup setting metadata
            mock_set_metadata.return_value = get_model_metadata_fixture
            # Setup click
            runner = CliRunner()

            # CALL
            result = runner.invoke(get.get, ["model", version_id_1, version_id_2])

            # ASSERT
            assert mock_details.call_args_list == [
                call(processed_jwt_fixture["jwt"], version_id_1),
                call(processed_jwt_fixture["jwt"], version_id_2),
            ]
            assert mock_get_metadata.call_args_list == [
                call(processed_jwt_fixture["jwt"]),
                call(processed_jwt_fixture["jwt"]),
            ]
            assert mock_output.call_args_list == [call(), call()]
            assert result.exit_code == 0

        @patch.object(version_history.ModelVersionHistory, "output_version_history")
        @patch.object(version_history.ModelVersionHistory, "__init__")
        def test_version_history_methods_each_called_once_when_one_version_id_given(
            self,
            mock_initialise,
            mock_output_version_history,
            mock_jwt,
            mock_get,
            mock_set_metadata,
            mock_output,
            mock_get_metadata,
            mock_details,
            processed_jwt_fixture,
            get_models_list_fixture,
            get_model_metadata_fixture,
        ):
            # SETUP
            # setup get jwt
            mock_jwt.return_value = processed_jwt_fixture, False
            # setup retrieving
            mock_get.side_effect = get_models_list_fixture
            version_id = get_models_list_fixture[0]["id"]
            # Setup click
            runner = CliRunner()
            mock_initialise.return_value = None

            # CALL
            result = runner.invoke(get.get, ["model", version_id, "--version-history"])

            # ASSERT
            assert mock_details.called_once_with(
                processed_jwt_fixture["jwt"], version_id
            )
            assert mock_initialise.called_once_with(
                processed_jwt_fixture["jwt"], model.Model(version_id)
            )
            mock_output_version_history.assert_called_once()
            assert result.exit_code == 0

        @patch.object(version_history.ModelVersionHistory, "output_version_history")
        @patch.object(version_history.ModelVersionHistory, "__init__")
        def test_version_history_methods_each_called_twice_when_two_version_ids_given(
            self,
            mock_initialise,
            mock_output_version_history,
            mock_jwt,
            mock_get,
            mock_set_metadata,
            mock_output,
            mock_get_metadata,
            mock_details,
            processed_jwt_fixture,
            get_models_list_fixture,
            get_model_metadata_fixture,
        ):
            # SETUP
            # setup get jwt
            mock_jwt.return_value = processed_jwt_fixture, False
            # setup retrieving
            mock_get.side_effect = get_models_list_fixture
            version_id_1 = get_models_list_fixture[0]["id"]
            version_id_2 = get_models_list_fixture[1]["id"]
            # setup setting metadata
            mock_set_metadata.return_value = get_model_metadata_fixture
            # Setup click
            runner = CliRunner()
            mock_initialise.return_value = None

            # CALL
            result = runner.invoke(
                get.get, ["model", version_id_1, version_id_2, "--version-history"]
            )

            # ASSERT
            assert mock_details.call_args_list == [
                call(processed_jwt_fixture["jwt"], version_id_1),
                call(processed_jwt_fixture["jwt"], version_id_2),
            ]
            assert mock_initialise.call_count == 2
            assert mock_output_version_history.call_args_list == [call(), call()]
            assert result.exit_code == 0

        @patch("dafni_cli.commands.get.click")
        def test_message_printed_when_no_id_provided(
            self,
            mock_click,
            mock_jwt,
            mock_get,
            mock_set_metadata,
            mock_output,
            mock_get_metadata,
            mock_details,
        ):
            # SETUP
            # Setup click
            runner = CliRunner()

            # CALL
            result = runner.invoke(get.get, ["model"])

            # ASSERT
            mock_details.assert_not_called()
            mock_get_metadata.assert_not_called()
            mock_output.assert_not_called()
            assert result.exception
            assert result.exit_code == 1

    @patch.object(dataset.Dataset, "output_dataset_details")
    @patch("dafni_cli.commands.get.get_all_datasets")
    @patch("dafni_cli.datasets.dataset_filtering.process_datasets_filters")
    @patch("dafni_cli.commands.get.check_for_jwt_file")
    class TestDatasets:
        """Test class to test the get group datasets command"""

        @patch("dafni_cli.commands.get.process_response_to_class_list")
        def test_get_all_datasets_called_with_jwt_from_context(
            self,
            mock_create,
            mock_jwt,
            mock_filter,
            mock_get,
            mock_output,
            processed_jwt_fixture,
            get_dataset_list_fixture,
        ):
            # SETUP
            # setup get group command to set the context containing a JWT
            mock_jwt.return_value = processed_jwt_fixture, False
            # setup filters
            filters = {}
            mock_filter.return_value = filters
            # setup get_all_datasets call
            response = get_dataset_list_fixture
            mock_get.return_value = response
            # setup process_response_to_class_list
            mock_create.return_value = []
            # Setup click
            runner = CliRunner()

            # CALL
            result = runner.invoke(get.get, ["datasets"])

            # ASSERT
            mock_filter.assert_called_once_with(None, None, None)
            mock_get.assert_called_once_with(processed_jwt_fixture["jwt"], filters)
            mock_create.assert_called_once_with(response["metadata"], dataset.Dataset)

            assert result.exit_code == 0

        def test_output_dataset_details_called_for_each_dataset(
            self,
            mock_jwt,
            mock_filter,
            mock_get,
            mock_output,
            processed_jwt_fixture,
            get_dataset_list_fixture,
        ):
            # SETUP
            # setup get group command to set the context containing a JWT
            mock_jwt.return_value = processed_jwt_fixture, False
            # setup filters
            filters = {}
            mock_filter.return_value = filters
            # setup get_all_datasets call
            response = get_dataset_list_fixture
            mock_get.return_value = response
            # Setup click
            runner = CliRunner()

            # CALL
            result = runner.invoke(get.get, ["datasets"])

            # ASSERT
            assert mock_output.call_count == len(response["metadata"])

            assert result.exit_code == 0

        @pytest.mark.parametrize(
            "filter_args, search, start, end",
            [
                (["--search", "DAFNI passport"], "DAFNI passport", None, None),
                (["--start-date", "21/1/2021"], None, "21/1/2021", None),
                (["--end-date", "21/1/2021"], None, None, "21/1/2021"),
                (
                    ["--start-date", "21/1/2021", "--end-date", "22/2/2021"],
                    None,
                    "21/1/2021",
                    "22/2/2021",
                ),
                (
                    [
                        "--search",
                        "DAFNI passport",
                        "--start-date",
                        "21/1/2021",
                        "--end-date",
                        "22/2/2021",
                    ],
                    "DAFNI passport",
                    "21/1/2021",
                    "22/2/2021",
                ),
            ],
            ids=[
                "Case 1 - Only search terms used",
                "Case 2 - Only Start date defined",
                "Case 3 - Only End date defined",
                "Case 4 - Start & End date defined",
                "Case 5 - Search term & date range defined",
            ],
        )
        def test_filter_options_passed_correctly_to_process_dataset_filters(
            self,
            mock_jwt,
            mock_filter,
            mock_get,
            mock_output,
            filter_args,
            search,
            start,
            end,
            processed_jwt_fixture,
            get_dataset_list_fixture,
        ):
            # SETUP
            # setup get group command
            mock_jwt.return_value = processed_jwt_fixture, False
            # setup filters
            filters = {}
            mock_filter.return_value = filters
            # setup get_all_datasets call
            response = get_dataset_list_fixture
            mock_get.return_value = response
            # Setup click
            runner = CliRunner()

            # CALL
            runner.invoke(get.get, ["datasets", *filter_args])

            # ASSERT
            mock_filter.assert_called_once_with(search, start, end)

    @patch("dafni_cli.commands.get.get_latest_dataset_metadata")
    @patch("dafni_cli.commands.get.check_for_jwt_file")
    class TestDataset:
        """Test class to test the get group dataset command"""

        @patch.object(dataset_metadata.DatasetMetadata, "output_metadata_details")
        @patch.object(dataset_metadata.DatasetMetadata, "__init__")
        def test_get_dataset_called_with_jwt_from_context_with_default_long_and_version_flag_value(
            self,
            mock_init,
            mock_output,
            mock_jwt,
            mock_get,
            processed_jwt_fixture,
            dataset_metadata_fixture,
        ):
            # SETUP
            # setup get group command to set the context containing a JWT
            mock_jwt.return_value = processed_jwt_fixture, False
            # setup get_latest_dataset_metadata call
            response = dataset_metadata_fixture
            mock_get.return_value = response
            # setup DatasetMetadata class
            mock_init.return_value = None
            mock_output.return_value = "Output"

            # setup data
            dataset_id = "0a0a0a0a-0a00-0a00-a000-0a0a0000000a"
            version_id = "0a0a0a0a-0a00-0a00-a000-0a0a0000000b"

            # Setup click
            runner = CliRunner()

            # CALL
            result = runner.invoke(get.get, ["dataset", dataset_id, version_id])

            # ASSERT
            mock_get.assert_called_once_with(
                processed_jwt_fixture["jwt"], dataset_id, version_id
            )
            mock_init.assert_called_once_with(response)
            mock_output.assert_called_once_with(False)

            assert result.exit_code == 0

        @pytest.mark.parametrize("metadata", ["--metadata","-m"])
        @pytest.mark.parametrize(
            "option, long",
            [("--short", False), ("-s", False), ("-l", True), ("--long", True)],
        )
        @patch.object(dataset_metadata.DatasetMetadata, "output_metadata_details")
        @patch.object(dataset_metadata.DatasetMetadata, "__init__")
        def test_dataset_metadata_called_with_given_long_value_when_version_history_is_false(
            self,
            mock_init,
            mock_output,
            mock_jwt,
            mock_get,
            option,
            long,
            metadata,
            processed_jwt_fixture,
            dataset_metadata_fixture,
        ):
            # SETUP
            # setup get group command to set the context containing a JWT
            mock_jwt.return_value = processed_jwt_fixture, False
            # setup get_latest_dataset_metadata call
            response = dataset_metadata_fixture
            mock_get.return_value = response
            # setup DatasetMetadata class
            mock_init.return_value = None
            mock_output.return_value = "Output"

            # setup data
            dataset_id = "0a0a0a0a-0a00-0a00-a000-0a0a0000000a"
            version_id = "0a0a0a0a-0a00-0a00-a000-0a0a0000000b"

            # Setup click
            runner = CliRunner()

            # CALL
            result = runner.invoke(
                get.get,
                ["dataset", dataset_id, version_id, option, metadata],
            )
            print(result.stdout)
            print(result.exc_info)
            # ASSERT
            mock_get.assert_called_once_with(
                processed_jwt_fixture["jwt"], dataset_id, version_id
            )
            mock_init.assert_called_once_with(response)
            mock_output.assert_called_once_with(long)

            assert result.exit_code == 0

        @pytest.mark.parametrize("version_history", ["--version-history", "-v"])
        @patch.object(
            dataset_version_history.DatasetVersionHistory, "process_version_history"
        )
        @patch.object(dataset_version_history.DatasetVersionHistory, "__init__")
        def test_dataset_version_history_called_when_version_history_true(
            self,
            mock_init,
            mock_output,
            mock_jwt,
            mock_get,
            version_history,
            processed_jwt_fixture,
            dataset_metadata_fixture,
        ):
            # SETUP
            # setup get group command to set the context containing a JWT
            mock_jwt.return_value = processed_jwt_fixture, False
            # setup get_latest_dataset_metadata call
            response = dataset_metadata_fixture
            mock_get.return_value = response
            # setup DatasetMetadata class
            mock_init.return_value = None
            mock_output.return_value = "Output"

            # setup data
            dataset_id = "0a0a0a0a-0a00-0a00-a000-0a0a0000000a"
            version_id = "0a0a0a0a-0a00-0a00-a000-0a0a0000000b"

            # Setup click
            runner = CliRunner()

            # CALL
            result = runner.invoke(
                get.get,
                ["dataset", dataset_id, version_id, version_history],
            )

            # ASSERT
            mock_get.assert_called_once_with(
                processed_jwt_fixture["jwt"], dataset_id, version_id
            )
            mock_init.assert_called_once_with(processed_jwt_fixture["jwt"], response)
            mock_output.assert_called_once_with()

            assert result.exit_code == 0

import pytest
from mock import patch, call
from click.testing import CliRunner

from dafni_cli import get, model
from dafni_cli.datasets import dataset
from test.fixtures.jwt_fixtures import processed_jwt_fixture
from test.fixtures.model_fixtures import get_models_list_fixture
from test.fixtures.dataset_fixtures import get_dataset_list_fixture


class TestGet:
    """test class to test the get() command functionality"""

    @patch("dafni_cli.get.get_models_dicts")
    @patch("dafni_cli.get.check_for_jwt_file")
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
    @patch.object(model.Model, "output_model_details")
    @patch("dafni_cli.get.get_models_dicts")
    @patch("dafni_cli.get.check_for_jwt_file")
    class TestModels:
        """Test class to test the get.models command"""

        @patch("dafni_cli.get.process_response_to_class_list")
        def test_get_models_dict_called_with_jwt_from_context(
            self,
            mock_create,
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
            mock_create.return_value = []
            # Setup click
            runner = CliRunner()

            # CALL
            result = runner.invoke(get.get, ["models"])

            # ASSERT
            mock_get.assert_called_once_with(processed_jwt_fixture["jwt"])
            mock_create.assert_called_once_with(models, model.Model)

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

    @patch.object(dataset.Dataset, "output_dataset_details")
    @patch("dafni_cli.get.get_all_datasets")
    @patch("dafni_cli.get.check_for_jwt_file")
    class TestDatasets:
        """Test class to test the get group datasets command"""

        @patch("dafni_cli.get.process_response_to_class_list")
        def test_get_all_datasets_called_with_jwt_from_context(
            self,
            mock_create,
            mock_jwt,
            mock_get,
            mock_output,
            processed_jwt_fixture,
            get_dataset_list_fixture,
        ):
            # SETUP
            # setup get group command
            mock_jwt.return_value = processed_jwt_fixture, False
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
            mock_get.assert_called_once_with(processed_jwt_fixture["jwt"])
            mock_create.assert_called_once_with(response["metadata"], dataset.Dataset)

            assert result.exit_code == 0

        def test_output_dataset_details_called_for_each_dataset(
            self,
            mock_jwt,
            mock_get,
            mock_output,
            processed_jwt_fixture,
            get_dataset_list_fixture,
        ):
            # SETUP
            # setup get group command
            mock_jwt.return_value = processed_jwt_fixture, False
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
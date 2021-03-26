import pytest
from mock import patch, call, MagicMock, PropertyMock, create_autospec
from click.testing import CliRunner

from dafni_cli.commands import delete
from test.fixtures.jwt_fixtures import processed_jwt_fixture
from dafni_cli.model import model


@patch.object(model.Model, "get_details_from_id")
@patch.object(model.Model, "output_version_details")
@patch("dafni_cli.auth.Auth.destroy", new_callable=PropertyMock)
class TestCollateModelVersionDetails:
    """Test class to test the collate_model_version_details method"""

    def test_single_model_with_valid_permissions_returns_single_model_details(
            self, mock_destroy, mock_output, mock_get
    ):
        # SETUP
        mock_output.return_value = "Model 1 details"
        mock_destroy.return_value = True
        jwt = "JWT"
        version_id = "version-id"
        version_id_list = [version_id]

        # CALL
        result = delete.collate_model_version_details(jwt, version_id_list)

        # ASSERT
        mock_get.assert_called_once_with(jwt, version_id)
        assert mock_output.called_once
        assert result == ["Model 1 details"]

    def test_multiple_models_both_with_valid_permissions_returns_multiple_model_details(
            self, mock_destroy, mock_output, mock_get
    ):
        # SETUP
        mock_output.side_effect = ["Model 1 details", "Model 2 details"]
        mock_destroy.return_value = True
        jwt = "JWT"
        version_id1 = "version-id-1"
        version_id2 = "version-id-2"
        version_id_list = [version_id1, version_id2]

        # CALL
        result = delete.collate_model_version_details(jwt, version_id_list)

        # ASSERT
        assert mock_get.call_args_list == [
            call(jwt, version_id1),
            call(jwt, version_id2)
        ]
        assert mock_output.call_count == 2
        assert result == ["Model 1 details", "Model 2 details"]

    @patch("dafni_cli.commands.delete.click")
    def test_single_model_without_permission_exits_with_code_1(
            self, mock_click, mock_destroy, mock_output, mock_get
    ):
        # SETUP
        mock_output.return_value = "Model 1 details"
        mock_destroy.return_value = False
        jwt = "JWT"
        version_id = "version-id"
        version_id_list = [version_id]

        # CALL
        with pytest.raises(SystemExit) as cn:
            result = delete.collate_model_version_details(jwt, version_id_list)

        # ASSERT
        mock_get.assert_called_once_with(jwt, version_id)
        mock_output.assert_called_once()
        assert mock_click.echo.call_args_list == [
            call("You do not have sufficient permissions to delete model version:"),
            call("Model 1 details")
        ]
        assert cn.value.code == 1

    @patch("dafni_cli.commands.delete.click")
    def test_first_model_with_permissions_but_second_without_exits_and_shows_model_without_permissions(
            self, mock_click, mock_destroy, mock_output, mock_get
    ):
        # SETUP
        mock_output.side_effect = ["Model 1 details", "Model 2 details"]
        mock_get.return_value = None
        # Is called once by model_version = Model(vid) and once by if statement => need 2 values per version ID.
        mock_destroy.side_effect = [True, True, False, False]
        jwt = "JWT"
        version_id1 = "version-id-1"
        version_id2 = "version-id-2"
        version_id_list = [version_id1, version_id2]

        # CALL
        with pytest.raises(SystemExit) as cn:
            result = delete.collate_model_version_details(jwt, version_id_list)

        # ASSERT
        print(mock_destroy.call_count)
        assert mock_get.call_args_list == [
            call(jwt, version_id1),
            call(jwt, version_id2)
        ]
        assert mock_output.call_count == 2
        assert mock_click.echo.call_args_list == [
            call("You do not have sufficient permissions to delete model version:"),
            call("Model 2 details")
        ]
        assert cn.value.code == 1


class TestDelete:
    """Test class to test the delete() command functionality"""

    class TestInit:
        """Test class to test the delete() group processing of the JWT"""

        @patch("dafni_cli.commands.delete.check_for_jwt_file")
        @patch("dafni_cli.commands.delete.click")
        @patch("dafni_cli.commands.delete.collate_model_version_details")
        @patch("dafni_cli.commands.delete.argument_confirmation")
        @patch("dafni_cli.commands.delete.delete_model")
        def test_jwt_retrieved_and_set_on_context(
                self,
                mock_model,
                mock_confirm,
                mock_collate,
                mock_click,
                mock_jwt,
                processed_jwt_fixture
        ):
            # SETUP
            mock_jwt.return_value = processed_jwt_fixture, False
            runner = CliRunner()
            ctx = {}

            # CALL
            result = runner.invoke(delete.delete, ["model", "version-id"], obj=ctx)

            # ASSERT
            mock_jwt.assert_called_once()
            assert ctx["jwt"] == processed_jwt_fixture["jwt"]
            assert result.exit_code == 0

    @patch("dafni_cli.commands.delete.check_for_jwt_file")
    @patch("dafni_cli.commands.delete.click")
    @patch("dafni_cli.commands.delete.collate_model_version_details")
    @patch("dafni_cli.commands.delete.argument_confirmation")
    @patch("dafni_cli.commands.delete.delete_model")
    class TestModel:
        """Test class to test the delete.model command"""

        def test_methods_called_once_each_for_single_model(
                self,
                mock_model,
                mock_confirm,
                mock_collate,
                mock_click,
                mock_jwt,
                processed_jwt_fixture
        ):
            # SETUP
            mock_jwt.return_value = processed_jwt_fixture, False
            mock_collate.return_value = ["model 1 details"]
            runner = CliRunner()
            version_id = "version-id"

            # CALL
            result = runner.invoke(delete.delete, ["model", version_id])

            # ASSERT
            assert result.exit_code == 0
            mock_collate.assert_called_once_with(
                processed_jwt_fixture["jwt"],
                (version_id,)
            )
            mock_confirm.assert_called_once_with(
                [],
                [],
                "Confirm deletion of models?",
                ["model 1 details"]
            )
            mock_model.assert_called_once_with(
                processed_jwt_fixture["jwt"],
                version_id
            )
            mock_click.echo.assert_called_once_with("Model versions deleted")

        def test_methods_called_once_each_other_than_delete_model_for_multiple_models(
                self,
                mock_model,
                mock_confirm,
                mock_collate,
                mock_click,
                mock_jwt,
                processed_jwt_fixture
        ):
            # SETUP
            mock_jwt.return_value = processed_jwt_fixture, False
            mock_collate.return_value = ["model 1 details", "model 2 details"]
            runner = CliRunner()
            version_id1 = "version-id-1"
            version_id2 = "version-id-2"

            # CALL
            result = runner.invoke(delete.delete, ["model", version_id1, version_id2])

            # ASSERT
            assert result.exit_code == 0
            mock_collate.assert_called_once_with(
                processed_jwt_fixture["jwt"],
                (version_id1, version_id2,)
            )
            mock_confirm.assert_called_once_with(
                [],
                [],
                "Confirm deletion of models?",
                ["model 1 details", "model 2 details"]
            )
            assert mock_model.call_args_list == [
                call(
                    processed_jwt_fixture["jwt"],
                    version_id1
                ),
                call(
                    processed_jwt_fixture["jwt"],
                    version_id2
                )
            ]
            mock_click.echo.assert_called_once_with("Model versions deleted")

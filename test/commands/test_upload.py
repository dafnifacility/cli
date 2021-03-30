import pytest
from mock import patch, call
from click.testing import CliRunner
from requests import HTTPError, Response
import json

from dafni_cli.commands import upload
from test.fixtures.jwt_fixtures import processed_jwt_fixture
from test.fixtures.model_fixtures import get_model_upload_urls_fixture
from test.fixtures.dataset_fixtures import upload_metadata_fixture


class TestUpload:
    """test class to test the upload() command functionality"""

    @patch("dafni_cli.commands.upload.model_version_ingest")
    @patch("dafni_cli.commands.upload.upload_file_to_minio")
    @patch("dafni_cli.commands.upload.get_model_upload_urls")
    @patch("dafni_cli.commands.upload.validate_model_definition")
    @patch("dafni_cli.commands.upload.argument_confirmation")
    @patch("dafni_cli.commands.upload.check_for_jwt_file")
    class TestInit:
        """Test class to test the get() group processing of the
        JWT
        """

        @pytest.mark.parametrize("version_message_flag", ["--version-message", "-m"])
        def test_jwt_retrieved_and_set_on_context(
            self,
            mock_jwt,
            mock_confirm,
            mock_validate,
            mock_urls,
            mock_minio,
            mock_ingest,
            version_message_flag,
            processed_jwt_fixture,
            get_model_upload_urls_fixture,
        ):
            # SETUP
            mock_jwt.return_value = processed_jwt_fixture, False
            mock_validate.return_value = (True, "")
            mock_urls.return_value = get_model_upload_urls_fixture

            runner = CliRunner()
            ctx = {}

            # CALL
            with runner.isolated_filesystem():
                with open("test_definition.yaml", "w") as f:
                    f.write("test definition file")
                with open("test_image.txt", "w") as f:
                    f.write("test image file")
                result = runner.invoke(
                    upload.upload,
                    [
                        "model",
                        "test_definition.yaml",
                        "test_image.txt",
                        version_message_flag,
                        "version message",
                    ],
                    obj=ctx,
                )

            # ASSERT
            mock_jwt.assert_called_once()
            assert ctx["jwt"] == processed_jwt_fixture["jwt"]
            assert result.exit_code == 0

    @patch("dafni_cli.commands.upload.check_for_jwt_file")
    @patch("dafni_cli.commands.upload.argument_confirmation")
    @patch("dafni_cli.commands.upload.click")
    @patch("dafni_cli.commands.upload.validate_model_definition")
    class TestModel:
        """test class to test the upload.model() command functionality"""

        @pytest.mark.parametrize("version_message_flag", ["--version-message", "-m"])
        def test_method_aborted_and_500_error_printed_if_500_response_from_validation_method(
            self,
            mock_validate,
            mock_click,
            mock_confirm,
            mock_jwt,
            version_message_flag,
            processed_jwt_fixture,
        ):
            # SETUP
            mock_jwt.return_value = processed_jwt_fixture, False
            error_response = Response()
            error_response.status_code = 500
            mock_validate.side_effect = HTTPError(response=error_response)
            runner = CliRunner()

            # CALL
            with runner.isolated_filesystem():
                with open("test_definition.yaml", "w") as f:
                    f.write("test definition file")
                with open("test_image.txt", "w") as f:
                    f.write("test image file")
                result = runner.invoke(
                    upload.upload,
                    [
                        "model",
                        "test_definition.yaml",
                        "test_image.txt",
                        version_message_flag,
                        "version message",
                    ],
                )

            # ASSERT
            assert result.exit_code == 1
            assert mock_click.echo.call_args_list == [
                call("Validating model definition"),
                call(
                    "Error validating the model definition. "
                    "See https://docs.secure.dafni.rl.ac.uk/docs/how-to/models/how-to-write-a-model-definition-file/"
                    " for guidance"
                ),
            ]

        @pytest.mark.parametrize("version_message_flag", ["--version-message", "-m"])
        def test_method_aborted_and_standard_error_printed_if_non_200_or_500_response_from_validation_method(
            self,
            mock_validate,
            mock_click,
            mock_confirm,
            mock_jwt,
            version_message_flag,
            processed_jwt_fixture,
        ):
            # SETUP
            mock_jwt.return_value = processed_jwt_fixture, False
            error_response = Response()
            error_response.status_code = 400
            error = HTTPError("error message", response=error_response)
            mock_validate.side_effect = error
            runner = CliRunner()

            # CALL
            with runner.isolated_filesystem():
                with open("test_definition.yaml", "w") as f:
                    f.write("test definition file")
                with open("test_image.txt", "w") as f:
                    f.write("test image file")
                result = runner.invoke(
                    upload.upload,
                    [
                        "model",
                        "test_definition.yaml",
                        "test_image.txt",
                        version_message_flag,
                        "version message",
                    ],
                )

            # ASSERT
            assert result.exit_code == 1
            assert mock_click.echo.call_args_list == [
                call("Validating model definition"),
                call(error),
            ]

        @pytest.mark.parametrize("version_message_flag", ["--version-message", "-m"])
        def test_method_aborted_and_error_printed_if_model_definition_is_not_valid(
            self,
            mock_validate,
            mock_click,
            mock_confirm,
            mock_jwt,
            version_message_flag,
            processed_jwt_fixture,
        ):
            # SETUP
            mock_jwt.return_value = processed_jwt_fixture, False
            mock_validate.return_value = (False, "Test validation error")
            runner = CliRunner()

            # CALL
            with runner.isolated_filesystem():
                with open("test_definition.yaml", "w") as f:
                    f.write("test definition file")
                with open("test_image.txt", "w") as f:
                    f.write("test image file")
                result = runner.invoke(
                    upload.upload,
                    [
                        "model",
                        "test_definition.yaml",
                        "test_image.txt",
                        version_message_flag,
                        "version message",
                    ],
                )

            # ASSERT
            assert result.exit_code == 1
            mock_confirm.assert_called_once_with(
                ["Model definition file path", "Image file path", "Version message"],
                ["test_definition.yaml", "test_image.txt", "version message"],
                "Confirm model upload?",
                ["No parent model: new model to be created"],
            )
            mock_validate.assert_called_once_with(
                processed_jwt_fixture["jwt"], "test_definition.yaml"
            )
            assert mock_click.echo.call_args_list == [
                call("Validating model definition"),
                call(
                    "Definition validation failed with the following errors: Test validation error"
                ),
            ]

        @patch("dafni_cli.commands.upload.get_model_upload_urls")
        @patch("dafni_cli.commands.upload.upload_file_to_minio")
        @patch("dafni_cli.commands.upload.model_version_ingest")
        @pytest.mark.parametrize(
            "upload_options, expected_argument, confirm_arg_1, confirm_arg_2, confirm_arg_3",
            [
                (
                    [
                        "model",
                        "test_definition.yaml",
                        "test_image.txt",
                        "--version-message",
                        "version message",
                    ],
                    None,
                    [
                        "Model definition file path",
                        "Image file path",
                        "Version message",
                    ],
                    ["test_definition.yaml", "test_image.txt", "version message"],
                    ["No parent model: new model to be created"],
                ),
                (
                    [
                        "model",
                        "test_definition.yaml",
                        "test_image.txt",
                        "--version-message",
                        "version message",
                        "--parent-model",
                        "parent-model-id",
                    ],
                    "parent-model-id",
                    [
                        "Model definition file path",
                        "Image file path",
                        "Version message",
                        "Parent model ID",
                    ],
                    [
                        "test_definition.yaml",
                        "test_image.txt",
                        "version message",
                        "parent-model-id",
                    ],
                    None,
                ),
            ],
            ids=["Case 1 - without parent model", "Case 2 - with parent model"],
        )
        def test_models_api_functions_called_with_expected_arguments(
            self,
            mock_ingest,
            mock_minio,
            mock_urls,
            mock_validate,
            mock_click,
            mock_confirm,
            mock_jwt,
            upload_options,
            expected_argument,
            confirm_arg_1,
            confirm_arg_2,
            confirm_arg_3,
            processed_jwt_fixture,
            get_model_upload_urls_fixture,
        ):
            # SETUP
            mock_jwt.return_value = processed_jwt_fixture, False
            mock_validate.return_value = (True, "")
            mock_urls.return_value = get_model_upload_urls_fixture
            upload_id, urls_dict = get_model_upload_urls_fixture
            runner = CliRunner()

            # CALL
            with runner.isolated_filesystem():
                with open("test_definition.yaml", "w") as f:
                    f.write("test definition file")
                with open("test_image.txt", "w") as f:
                    f.write("test image file")
                result = runner.invoke(upload.upload, upload_options)

            # ASSERT
            assert result.exit_code == 0
            mock_confirm.assert_called_once_with(
                confirm_arg_1, confirm_arg_2, "Confirm model upload?", confirm_arg_3
            )
            mock_validate.assert_called_once_with(
                processed_jwt_fixture["jwt"], "test_definition.yaml"
            )
            mock_urls.assert_called_once_with(processed_jwt_fixture["jwt"])
            assert mock_minio.call_args_list == [
                call(
                    processed_jwt_fixture["jwt"],
                    urls_dict["definition"],
                    "test_definition.yaml",
                ),
                call(
                    processed_jwt_fixture["jwt"], urls_dict["image"], "test_image.txt"
                ),
            ]
            mock_ingest.assert_called_once_with(
                processed_jwt_fixture["jwt"],
                upload_id,
                "version message",
                expected_argument,
            )
            assert mock_click.echo.call_args_list == [
                call("Validating model definition"),
                call("Getting urls"),
                call("Uploading model definition and image"),
                call("Ingesting model"),
                call("Model upload complete"),
            ]

    @patch("dafni_cli.commands.upload.upload_new_dataset_files")
    @patch("dafni_cli.commands.upload.argument_confirmation")
    @patch("dafni_cli.commands.upload.check_for_jwt_file")
    class TestDataset:
        """Test class to test the upload.dataset command"""

        @pytest.mark.parametrize(
            "files", [["file_1.txt"], ["file_1.txt", "file_2.txt", "file_3.txt"]]
        )
        def test_upload_does_not_take_place_if_confirmation_cancelled(
            self,
            mock_jwt,
            mock_confirm,
            mock_upload,
            files,
            processed_jwt_fixture,
            upload_metadata_fixture,
        ):
            # SETUP
            mock_jwt.return_value = processed_jwt_fixture, True
            mock_confirm.side_effect = SystemExit(1)

            # setup data for call
            definition = "meta_data.json"
            runner = CliRunner()

            # setup expected call values
            argument_names = ["Dataset definition file path"] + [
                "Dataset file path" for file_path in files
            ]
            arguments = [definition, *files]

            # CALL
            with runner.isolated_filesystem():
                with open(definition, "w") as f:
                    f.write(json.dumps(upload_metadata_fixture))
                for file_name in files:
                    with open(file_name, "w") as f:
                        f.write(f"{file_name} content")

                result = runner.invoke(upload.upload, ["dataset", definition, *files])

            # ASSERT
            assert result.exit_code == 1
            mock_upload.assert_not_called()
            mock_confirm.assert_called_once_with(
                argument_names, arguments, "Confirm Dataset upload?"
            )

        @pytest.mark.parametrize(
            "files", [("file_1.txt",), ("file_1.txt", "file_2.txt", "file_3.txt")]
        )
        def test_upload_take_place_if_details_confirmed(
            self,
            mock_jwt,
            mock_confirm,
            mock_upload,
            files,
            processed_jwt_fixture,
            upload_metadata_fixture,
        ):
            # SETUP
            mock_jwt.return_value = processed_jwt_fixture, True
            mock_confirm.return_value = None

            # setup data for call
            definition = "meta_data.json"
            runner = CliRunner()

            # setup expected call values
            argument_names = ["Dataset definition file path"] + [
                "Dataset file path" for file_path in files
            ]
            arguments = [definition, *files]

            # CALL
            with runner.isolated_filesystem():
                with open(definition, "w") as f:
                    f.write(json.dumps(upload_metadata_fixture))
                for file_name in files:
                    with open(file_name, "w") as f:
                        f.write(f"{file_name} content")

                result = runner.invoke(upload.upload, ["dataset", definition, *files])

            # ASSERT
            assert result.exit_code == 0
            mock_upload.assert_called_once_with(
                processed_jwt_fixture["jwt"], definition, files
            )
            mock_confirm.assert_called_once_with(
                argument_names, arguments, "Confirm Dataset upload?"
            )
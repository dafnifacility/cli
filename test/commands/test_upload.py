from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from click.testing import CliRunner

from dafni_cli.api.exceptions import ValidationError
from dafni_cli.commands import upload
from dafni_cli.datasets.dataset_metadata import parse_dataset_metadata

from test.api.test_models_api import TEST_MODELS_UPLOAD_RESPONSE
from test.fixtures.dataset_metadata import TEST_DATASET_METADATA


@patch("dafni_cli.commands.upload.DAFNISession")
class TestUpload(TestCase):
    """Test class to test the upload command"""

    @patch("dafni_cli.commands.upload.upload_dataset")
    def test_session_retrieved_and_set_on_context(self, _, mock_DAFNISession):
        """Tests that the session is created in the click context"""
        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        ctx = {}

        # CALL
        with runner.isolated_filesystem():
            with open("test_definition.json", "w", encoding="utf-8") as f:
                f.write("{}")
            with open("test_image.txt", "w", encoding="utf-8") as f:
                f.write("test image file")
            result = runner.invoke(
                upload.upload,
                ["dataset", "test_definition.json", "test_image.txt"],
                input="y",
                obj=ctx,
            )

        # ASSERT
        mock_DAFNISession.assert_called_once()

        self.assertEqual(ctx["session"], session)
        self.assertEqual(result.exit_code, 0)

    # ----------------- MODELS

    @patch("dafni_cli.commands.upload.validate_model_definition")
    @patch("dafni_cli.commands.upload.get_model_upload_urls")
    @patch("dafni_cli.commands.upload.upload_file_to_minio")
    @patch("dafni_cli.commands.upload.model_version_ingest")
    def test_upload_model(
        self,
        mock_model_version_ingest,
        mock_upload_file_to_minio,
        mock_get_model_upload_urls,
        mock_validate_model_definition,
        mock_DAFNISession,
    ):
        """Tests that the 'upload model' command works correctly when
        no parent is given"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()

        mock_get_model_upload_urls.return_value = (
            TEST_MODELS_UPLOAD_RESPONSE["id"],
            TEST_MODELS_UPLOAD_RESPONSE["urls"],
        )

        # CALL
        with runner.isolated_filesystem():
            with open("test_definition.yaml", "w", encoding="utf-8") as file:
                file.write("test definition file")
            with open("test_image.txt", "w", encoding="utf-8") as file:
                file.write("test image file")
            result = runner.invoke(
                upload.upload,
                [
                    "model",
                    "test_definition.yaml",
                    "test_image.txt",
                    "--version-message",
                    "version_message",
                ],
                input="y",
            )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_validate_model_definition.assert_called_once_with(
            session, Path("test_definition.yaml")
        )
        mock_get_model_upload_urls.assert_called_once_with(session)
        mock_upload_file_to_minio.assert_has_calls(
            [
                call(
                    session,
                    TEST_MODELS_UPLOAD_RESPONSE["urls"]["definition"],
                    Path("test_definition.yaml"),
                ),
                call(
                    session,
                    TEST_MODELS_UPLOAD_RESPONSE["urls"]["image"],
                    Path("test_image.txt"),
                ),
            ]
        )
        mock_model_version_ingest.assert_called_once_with(
            session, TEST_MODELS_UPLOAD_RESPONSE["id"], "version_message", None
        )

        self.assertEqual(
            result.output,
            "Model definition file path: test_definition.yaml\n"
            "Image file path: test_image.txt\n"
            "Version message: version_message\n"
            "No parent model: New model to be created\n"
            "Confirm model upload? [y/N]: y\n"
            "Validating model definition\n"
            "Getting urls\n"
            "Uploading model definition and image\n"
            "Ingesting model\n"
            "Model upload complete\n",
        )
        self.assertEqual(result.exit_code, 0)

    @patch("dafni_cli.commands.upload.validate_model_definition")
    @patch("dafni_cli.commands.upload.get_model_upload_urls")
    @patch("dafni_cli.commands.upload.upload_file_to_minio")
    @patch("dafni_cli.commands.upload.model_version_ingest")
    def test_upload_model_with_parent(
        self,
        mock_model_version_ingest,
        mock_upload_file_to_minio,
        mock_get_model_upload_urls,
        mock_validate_model_definition,
        mock_DAFNISession,
    ):
        """Tests that the 'upload model' command works correctly when
        a parent is given"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()

        mock_get_model_upload_urls.return_value = (
            TEST_MODELS_UPLOAD_RESPONSE["id"],
            TEST_MODELS_UPLOAD_RESPONSE["urls"],
        )

        # CALL
        with runner.isolated_filesystem():
            with open("test_definition.yaml", "w", encoding="utf-8") as file:
                file.write("test definition file")
            with open("test_image.txt", "w", encoding="utf-8") as file:
                file.write("test image file")
            result = runner.invoke(
                upload.upload,
                [
                    "model",
                    "test_definition.yaml",
                    "test_image.txt",
                    "--version-message",
                    "version_message",
                    "--parent-id",
                    "parent-id",
                ],
                input="y",
            )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_validate_model_definition.assert_called_once_with(
            session, Path("test_definition.yaml")
        )
        mock_get_model_upload_urls.assert_called_once_with(session)
        mock_upload_file_to_minio.assert_has_calls(
            [
                call(
                    session,
                    TEST_MODELS_UPLOAD_RESPONSE["urls"]["definition"],
                    Path("test_definition.yaml"),
                ),
                call(
                    session,
                    TEST_MODELS_UPLOAD_RESPONSE["urls"]["image"],
                    Path("test_image.txt"),
                ),
            ]
        )
        mock_model_version_ingest.assert_called_once_with(
            session, TEST_MODELS_UPLOAD_RESPONSE["id"], "version_message", "parent-id"
        )

        self.assertEqual(
            result.output,
            "Model definition file path: test_definition.yaml\n"
            "Image file path: test_image.txt\n"
            "Version message: version_message\n"
            "Parent model ID: parent-id\n"
            "Confirm model upload? [y/N]: y\n"
            "Validating model definition\n"
            "Getting urls\n"
            "Uploading model definition and image\n"
            "Ingesting model\n"
            "Model upload complete\n",
        )
        self.assertEqual(result.exit_code, 0)

    @patch("dafni_cli.commands.upload.validate_model_definition")
    @patch("dafni_cli.commands.upload.get_model_upload_urls")
    @patch("dafni_cli.commands.upload.upload_file_to_minio")
    @patch("dafni_cli.commands.upload.model_version_ingest")
    def test_upload_model_with_validation_error(
        self,
        mock_model_version_ingest,
        mock_upload_file_to_minio,
        mock_get_model_upload_urls,
        mock_validate_model_definition,
        mock_DAFNISession,
    ):
        """Tests that the 'upload model' command exits correctly when
        a validation error occurs"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()

        mock_get_model_upload_urls.return_value = (
            TEST_MODELS_UPLOAD_RESPONSE["id"],
            TEST_MODELS_UPLOAD_RESPONSE["urls"],
        )
        mock_validate_model_definition.side_effect = ValidationError(
            "Some validation error message"
        )

        # CALL
        with runner.isolated_filesystem():
            with open("test_definition.yaml", "w", encoding="utf-8") as file:
                file.write("test definition file")
            with open("test_image.txt", "w", encoding="utf-8") as file:
                file.write("test image file")
            result = runner.invoke(
                upload.upload,
                [
                    "model",
                    "test_definition.yaml",
                    "test_image.txt",
                    "--version-message",
                    "version_message",
                ],
                input="y",
            )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_validate_model_definition.assert_called_once_with(
            session, Path("test_definition.yaml")
        )

        self.assertEqual(
            result.output,
            "Model definition file path: test_definition.yaml\n"
            "Image file path: test_image.txt\n"
            "Version message: version_message\n"
            "No parent model: New model to be created\n"
            "Confirm model upload? [y/N]: y\n"
            "Validating model definition\n"
            "Some validation error message\n",
        )
        self.assertEqual(result.exit_code, 1)

    @patch("dafni_cli.commands.upload.validate_model_definition")
    @patch("dafni_cli.commands.upload.get_model_upload_urls")
    @patch("dafni_cli.commands.upload.upload_file_to_minio")
    @patch("dafni_cli.commands.upload.model_version_ingest")
    def test_upload_model_cancel(
        self,
        mock_model_version_ingest,
        mock_upload_file_to_minio,
        mock_get_model_upload_urls,
        mock_validate_model_definition,
        mock_DAFNISession,
    ):
        """Tests that the 'upload model' command can be canceled"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()

        mock_get_model_upload_urls.return_value = (
            TEST_MODELS_UPLOAD_RESPONSE["id"],
            TEST_MODELS_UPLOAD_RESPONSE["urls"],
        )
        mock_validate_model_definition.side_effect = ValidationError(
            "Some validation error message"
        )

        # CALL
        with runner.isolated_filesystem():
            with open("test_definition.yaml", "w", encoding="utf-8") as file:
                file.write("test definition file")
            with open("test_image.txt", "w", encoding="utf-8") as file:
                file.write("test image file")
            result = runner.invoke(
                upload.upload,
                [
                    "model",
                    "test_definition.yaml",
                    "test_image.txt",
                    "--version-message",
                    "version_message",
                ],
                input="n",
            )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_validate_model_definition.assert_not_called()
        mock_get_model_upload_urls.assert_not_called()
        mock_upload_file_to_minio.assert_not_called()
        mock_model_version_ingest.assert_not_called()

        self.assertEqual(
            result.output,
            "Model definition file path: test_definition.yaml\n"
            "Image file path: test_image.txt\n"
            "Version message: version_message\n"
            "No parent model: New model to be created\n"
            "Confirm model upload? [y/N]: n\n"
            "Aborted!\n",
        )
        self.assertEqual(result.exit_code, 1)

    # ----------------- DATASET

    @patch("dafni_cli.commands.upload.upload_dataset")
    def test_upload_dataset(
        self,
        mock_upload_dataset,
        mock_DAFNISession,
    ):
        """Tests that the 'upload dataset' command works correctly"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()

        # CALL
        with runner.isolated_filesystem():
            with open("test_definition.json", "w", encoding="utf-8") as file:
                file.write("{}")
            with open("test_dataset.txt", "w", encoding="utf-8") as file:
                file.write("test dataset file")
            result = runner.invoke(
                upload.upload,
                [
                    "dataset",
                    "test_definition.json",
                    "test_dataset.txt",
                ],
                input="y",
            )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_upload_dataset.assert_called_once_with(
            session, {}, (Path("test_dataset.txt"),)
        )

        self.assertEqual(
            result.output,
            "Dataset definition file path: test_definition.json\n"
            "Dataset file path: test_dataset.txt\n"
            "Confirm dataset upload? [y/N]: y\n",
        )
        self.assertEqual(result.exit_code, 0)

    @patch("dafni_cli.commands.upload.upload_dataset")
    def test_upload_dataset_with_multiple_files(
        self,
        mock_upload_dataset,
        mock_DAFNISession,
    ):
        """Tests that the 'upload dataset' command works correctly when
        multiple files are given"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()

        # CALL
        with runner.isolated_filesystem():
            with open("test_definition.json", "w", encoding="utf-8") as file:
                file.write("{}")
            with open("test_dataset1.txt", "w", encoding="utf-8") as file:
                file.write("test dataset file1")
            with open("test_dataset2.txt", "w", encoding="utf-8") as file:
                file.write("test dataset file2")
            result = runner.invoke(
                upload.upload,
                [
                    "dataset",
                    "test_definition.json",
                    "test_dataset1.txt",
                    "test_dataset2.txt",
                ],
                input="y",
            )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_upload_dataset.assert_called_once_with(
            session,
            {},
            (Path("test_dataset1.txt"), Path("test_dataset2.txt")),
        )

        self.assertEqual(
            result.output,
            "Dataset definition file path: test_definition.json\n"
            "Dataset file path: test_dataset1.txt\n"
            "Dataset file path: test_dataset2.txt\n"
            "Confirm dataset upload? [y/N]: y\n",
        )
        self.assertEqual(result.exit_code, 0)

    @patch("dafni_cli.commands.upload.upload_dataset")
    def test_upload_dataset_cancel(
        self,
        mock_upload_dataset,
        mock_DAFNISession,
    ):
        """Tests that the 'upload dataset' command can be canceled"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()

        # CALL
        with runner.isolated_filesystem():
            with open("test_definition.json", "w", encoding="utf-8") as file:
                file.write("{}")
            with open("test_dataset.txt", "w", encoding="utf-8") as file:
                file.write("test dataset file")
            result = runner.invoke(
                upload.upload,
                [
                    "dataset",
                    "test_definition.json",
                    "test_dataset.txt",
                ],
                input="n",
            )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_upload_dataset.assert_not_called()

        self.assertEqual(
            result.output,
            "Dataset definition file path: test_definition.json\n"
            "Dataset file path: test_dataset.txt\n"
            "Confirm dataset upload? [y/N]: n\n"
            "Aborted!\n",
        )
        self.assertEqual(result.exit_code, 1)

    # ----------------- DATASET-VERSION

    @patch("dafni_cli.commands.upload.upload_dataset")
    @patch("dafni_cli.commands.upload.get_latest_dataset_metadata")
    @patch("dafni_cli.commands.upload.modify_dataset_metadata_for_upload")
    def test_upload_dataset_version(
        self,
        mock_modify_dataset_metadata_for_upload,
        mock_get_latest_dataset_metadata,
        mock_upload_dataset,
        mock_DAFNISession,
    ):
        """Tests that the 'upload dataset-version' command works correctly"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        dataset_version_id = "some-existing-version-id"
        file_path = "test_dataset.txt"
        mock_get_latest_dataset_metadata.return_value = TEST_DATASET_METADATA
        metadata = parse_dataset_metadata(TEST_DATASET_METADATA)

        # CALL
        with runner.isolated_filesystem():
            with open("test_dataset.txt", "w", encoding="utf-8") as file:
                file.write("test dataset file")
            result = runner.invoke(
                upload.upload,
                [
                    "dataset-version",
                    dataset_version_id,
                    file_path,
                ],
                input="y",
            )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_get_latest_dataset_metadata.assert_called_once_with(
            session, dataset_version_id
        )
        mock_modify_dataset_metadata_for_upload.assert_called_once_with(
            existing_metadata=TEST_DATASET_METADATA,
            definition_path=None,
            version_message=None,
        )
        mock_upload_dataset.assert_called_once_with(
            session,
            dataset_id=metadata.dataset_id,
            metadata=mock_modify_dataset_metadata_for_upload.return_value,
            file_paths=(Path(file_path),),
        )

        self.assertEqual(
            result.output,
            f"Dataset Title: {metadata.title}\n"
            f"Dataset ID: {metadata.dataset_id}\n"
            f"Dataset Version ID: {metadata.version_id}\n"
            f"Dataset file path: {file_path}\n"
            "Confirm dataset upload? [y/N]: y\n",
        )
        self.assertEqual(result.exit_code, 0)

    @patch("dafni_cli.commands.upload.upload_dataset")
    @patch("dafni_cli.commands.upload.get_latest_dataset_metadata")
    @patch("dafni_cli.commands.upload.modify_dataset_metadata_for_upload")
    def test_upload_dataset_version_with_multiple_files(
        self,
        mock_modify_dataset_metadata_for_upload,
        mock_get_latest_dataset_metadata,
        mock_upload_dataset,
        mock_DAFNISession,
    ):
        """Tests that the 'upload dataset-version' command works correctly
        when multiple files are given"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        dataset_version_id = "some-existing-version-id"
        file_paths = ["test_dataset1.txt", "test_dataset2.txt"]
        mock_get_latest_dataset_metadata.return_value = TEST_DATASET_METADATA
        metadata = parse_dataset_metadata(TEST_DATASET_METADATA)

        # CALL
        with runner.isolated_filesystem():
            with open("test_dataset1.txt", "w", encoding="utf-8") as file:
                file.write("test dataset file")
            with open("test_dataset2.txt", "w", encoding="utf-8") as file:
                file.write("test dataset file")
            result = runner.invoke(
                upload.upload,
                ["dataset-version", dataset_version_id, file_paths[0], file_paths[1]],
                input="y",
            )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_get_latest_dataset_metadata.assert_called_once_with(
            session, dataset_version_id
        )
        mock_modify_dataset_metadata_for_upload.assert_called_once_with(
            existing_metadata=TEST_DATASET_METADATA,
            definition_path=None,
            version_message=None,
        )
        mock_upload_dataset.assert_called_once_with(
            session,
            dataset_id=metadata.dataset_id,
            metadata=mock_modify_dataset_metadata_for_upload.return_value,
            file_paths=(Path(file_paths[0]), Path(file_paths[1])),
        )

        self.assertEqual(
            result.output,
            f"Dataset Title: {metadata.title}\n"
            f"Dataset ID: {metadata.dataset_id}\n"
            f"Dataset Version ID: {metadata.version_id}\n"
            f"Dataset file path: {file_paths[0]}\n"
            f"Dataset file path: {file_paths[1]}\n"
            "Confirm dataset upload? [y/N]: y\n",
        )
        self.assertEqual(result.exit_code, 0)

    @patch("dafni_cli.commands.upload.upload_dataset")
    @patch("dafni_cli.commands.upload.get_latest_dataset_metadata")
    @patch("dafni_cli.commands.upload.modify_dataset_metadata_for_upload")
    def test_upload_dataset_version_cancel(
        self,
        mock_modify_dataset_metadata_for_upload,
        mock_get_latest_dataset_metadata,
        mock_upload_dataset,
        mock_DAFNISession,
    ):
        """Tests that the 'upload dataset-version' command can be canceled"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        dataset_version_id = "some-existing-version-id"
        file_path = "test_dataset.txt"
        mock_get_latest_dataset_metadata.return_value = TEST_DATASET_METADATA
        metadata = parse_dataset_metadata(TEST_DATASET_METADATA)

        # CALL
        with runner.isolated_filesystem():
            with open(file_path, "w", encoding="utf-8") as file:
                file.write("test dataset file")
            result = runner.invoke(
                upload.upload,
                [
                    "dataset-version",
                    dataset_version_id,
                    file_path,
                ],
                input="n",
            )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_get_latest_dataset_metadata.assert_called_once_with(
            session, dataset_version_id
        )
        mock_modify_dataset_metadata_for_upload.assert_called_once_with(
            existing_metadata=TEST_DATASET_METADATA,
            definition_path=None,
            version_message=None,
        )
        mock_upload_dataset.assert_not_called()

        self.assertEqual(
            result.output,
            f"Dataset Title: {metadata.title}\n"
            f"Dataset ID: {metadata.dataset_id}\n"
            f"Dataset Version ID: {metadata.version_id}\n"
            f"Dataset file path: {file_path}\n"
            "Confirm dataset upload? [y/N]: n\n"
            "Aborted!\n",
        )
        self.assertEqual(result.exit_code, 1)

    @patch("dafni_cli.commands.upload.upload_dataset")
    @patch("dafni_cli.commands.upload.get_latest_dataset_metadata")
    @patch("dafni_cli.commands.upload.modify_dataset_metadata_for_upload")
    def test_upload_dataset_version_with_definition_and_version_message(
        self,
        mock_modify_dataset_metadata_for_upload,
        mock_get_latest_dataset_metadata,
        mock_upload_dataset,
        mock_DAFNISession,
    ):
        """Tests that the 'upload dataset-version' command works correctly
        when a metadata and version message is given"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        dataset_version_id = "some-existing-version-id"
        file_path = "test_dataset.txt"
        definition_path = "defintion.json"
        version_message = "version_message"
        mock_get_latest_dataset_metadata.return_value = TEST_DATASET_METADATA
        metadata = parse_dataset_metadata(TEST_DATASET_METADATA)

        # CALL
        with runner.isolated_filesystem():
            with open(file_path, "w", encoding="utf-8") as file:
                file.write("test dataset file")
            with open(definition_path, "w", encoding="utf-8") as file:
                file.write("test definition file")
            result = runner.invoke(
                upload.upload,
                [
                    "dataset-version",
                    dataset_version_id,
                    file_path,
                    "--definition",
                    definition_path,
                    "--version-message",
                    version_message,
                ],
                input="y",
            )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_get_latest_dataset_metadata.assert_called_once_with(
            session, dataset_version_id
        )
        mock_modify_dataset_metadata_for_upload.assert_called_once_with(
            existing_metadata=TEST_DATASET_METADATA,
            definition_path=Path(definition_path),
            version_message=version_message,
        )
        mock_upload_dataset.assert_called_once_with(
            session,
            dataset_id=metadata.dataset_id,
            metadata=mock_modify_dataset_metadata_for_upload.return_value,
            file_paths=(Path(file_path),),
        )

        self.assertEqual(
            result.output,
            f"Dataset Title: {metadata.title}\n"
            f"Dataset ID: {metadata.dataset_id}\n"
            f"Dataset Version ID: {metadata.version_id}\n"
            f"Dataset file path: {file_path}\n"
            f"Dataset definition file path: {definition_path}\n"
            "Confirm dataset upload? [y/N]: y\n",
        )
        self.assertEqual(result.exit_code, 0)

    # ----------------- WORKFLOW

    @patch("dafni_cli.commands.upload.upload_workflow")
    def test_upload_workflow(
        self,
        mock_upload_workflow,
        mock_DAFNISession,
    ):
        """Tests that the 'upload workflow' command works correctly when
        no parent is given"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()

        # CALL
        with runner.isolated_filesystem():
            with open("test_definition.json", "w", encoding="utf-8") as file:
                file.write("test definition file")
            result = runner.invoke(
                upload.upload,
                [
                    "workflow",
                    "test_definition.json",
                ],
                input="y",
            )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_upload_workflow.assert_called_once_with(
            session, Path("test_definition.json"), None, None
        )

        self.assertEqual(
            result.output,
            "Workflow definition file path: test_definition.json\n"
            "Version message: None\n"
            "No parent workflow: new workflow to be created\n"
            "Confirm workflow upload? [y/N]: y\n"
            "Uploading workflow\n"
            "Workflow upload complete\n",
        )
        self.assertEqual(result.exit_code, 0)

    @patch("dafni_cli.commands.upload.upload_workflow")
    def test_upload_workflow_with_parent_and_version_message(
        self,
        mock_upload_workflow,
        mock_DAFNISession,
    ):
        """Tests that the 'upload workflow' command works correctly when
        a parent and version message is given"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()

        # CALL
        with runner.isolated_filesystem():
            with open("test_definition.json", "w", encoding="utf-8") as file:
                file.write("test definition file")
            result = runner.invoke(
                upload.upload,
                [
                    "workflow",
                    "test_definition.json",
                    "--version-message",
                    "version_message",
                    "--parent-id",
                    "parent-id",
                ],
                input="y",
            )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_upload_workflow.assert_called_once_with(
            session, Path("test_definition.json"), "version_message", "parent-id"
        )

        self.assertEqual(
            result.output,
            "Workflow definition file path: test_definition.json\n"
            "Version message: version_message\n"
            "Parent workflow ID: parent-id\n"
            "Confirm workflow upload? [y/N]: y\n"
            "Uploading workflow\n"
            "Workflow upload complete\n",
        )
        self.assertEqual(result.exit_code, 0)

    @patch("dafni_cli.commands.upload.upload_workflow")
    def test_upload_workflow_cancel(
        self,
        mock_upload_workflow,
        mock_DAFNISession,
    ):
        """Tests that the 'upload workflow' command can be canceled"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()

        # CALL
        with runner.isolated_filesystem():
            with open("test_definition.json", "w", encoding="utf-8") as file:
                file.write("test definition file")
            result = runner.invoke(
                upload.upload,
                [
                    "workflow",
                    "test_definition.json",
                ],
                input="n",
            )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_upload_workflow.assert_not_called()

        self.assertEqual(
            result.output,
            "Workflow definition file path: test_definition.json\n"
            "Version message: None\n"
            "No parent workflow: new workflow to be created\n"
            "Confirm workflow upload? [y/N]: n\n"
            "Aborted!\n",
        )
        self.assertEqual(result.exit_code, 1)

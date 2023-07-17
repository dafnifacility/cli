import json
from datetime import datetime
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from dafni_cli.commands import upload
from dafni_cli.datasets.dataset_metadata import parse_dataset_metadata

from test.commands.test_options import add_dataset_metadata_common_options
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


@patch("dafni_cli.commands.upload.DAFNISession")
@patch("dafni_cli.commands.upload.upload_model")
class TestUploadModel(TestCase):
    """Test class to test the upload model commands"""

    def test_upload_model(
        self,
        mock_upload_model,
        mock_DAFNISession,
    ):
        """Tests that the 'upload model' command works correctly when
        no parent id is given"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        definition_path = "test_definition.yaml"
        image_path = "test_image.txt"
        version_message = "version_message"

        # CALL
        with runner.isolated_filesystem():
            with open(definition_path, "w", encoding="utf-8") as file:
                file.write("test definition file")
            with open(image_path, "w", encoding="utf-8") as file:
                file.write("test image file")
            result = runner.invoke(
                upload.upload,
                [
                    "model",
                    definition_path,
                    image_path,
                    "--version-message",
                    version_message,
                ],
                input="y",
            )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_upload_model.assert_called_with(
            session,
            definition_path=Path(definition_path),
            image_path=Path(image_path),
            version_message=version_message,
            parent_id=None,
        )

        self.assertEqual(
            result.output,
            "Model definition file path: test_definition.yaml\n"
            "Image file path: test_image.txt\n"
            "Version message: version_message\n"
            "No parent model: New model to be created\n"
            "Confirm model upload? [y/N]: y\n",
        )
        self.assertEqual(result.exit_code, 0)

    def test_upload_model_with_parent(
        self,
        mock_upload_model,
        mock_DAFNISession,
    ):
        """Tests that the 'upload model' command works correctly when
        a parent is given"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        definition_path = "test_definition.yaml"
        image_path = "test_image.txt"
        version_message = "version_message"
        parent_id = "parent-id"

        # CALL
        with runner.isolated_filesystem():
            with open(definition_path, "w", encoding="utf-8") as file:
                file.write("test definition file")
            with open(image_path, "w", encoding="utf-8") as file:
                file.write("test image file")
            result = runner.invoke(
                upload.upload,
                [
                    "model",
                    definition_path,
                    image_path,
                    "--version-message",
                    version_message,
                    "--parent-id",
                    parent_id,
                ],
                input="y",
            )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_upload_model.assert_called_with(
            session,
            definition_path=Path(definition_path),
            image_path=Path(image_path),
            version_message=version_message,
            parent_id=parent_id,
        )

        self.assertEqual(
            result.output,
            "Model definition file path: test_definition.yaml\n"
            "Image file path: test_image.txt\n"
            "Version message: version_message\n"
            "Parent model ID: parent-id\n"
            "Confirm model upload? [y/N]: y\n",
        )
        self.assertEqual(result.exit_code, 0)

    def test_upload_model_skipping_confirmation(
        self,
        mock_upload_model,
        mock_DAFNISession,
    ):
        """Tests that the 'upload model' command works correctly when
        given a -y flag to skip the confirmation"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        definition_path = "test_definition.yaml"
        image_path = "test_image.txt"
        version_message = "version_message"

        # CALL
        with runner.isolated_filesystem():
            with open(definition_path, "w", encoding="utf-8") as file:
                file.write("test definition file")
            with open(image_path, "w", encoding="utf-8") as file:
                file.write("test image file")
            result = runner.invoke(
                upload.upload,
                [
                    "model",
                    definition_path,
                    image_path,
                    "--version-message",
                    version_message,
                    "-y",
                ],
            )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_upload_model.assert_called_with(
            session,
            definition_path=Path(definition_path),
            image_path=Path(image_path),
            version_message=version_message,
            parent_id=None,
        )

        self.assertEqual(result.output, "")
        self.assertEqual(result.exit_code, 0)

    def test_upload_model_cancel(
        self,
        mock_model_upload,
        mock_DAFNISession,
    ):
        """Tests that the 'upload model' command can be canceled"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        definition_path = "test_definition.yaml"
        image_path = "test_image.txt"
        version_message = "version_message"

        # CALL
        with runner.isolated_filesystem():
            with open(definition_path, "w", encoding="utf-8") as file:
                file.write("test definition file")
            with open(image_path, "w", encoding="utf-8") as file:
                file.write("test image file")
            result = runner.invoke(
                upload.upload,
                [
                    "model",
                    definition_path,
                    image_path,
                    "--version-message",
                    version_message,
                ],
                input="n",
            )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_model_upload.assert_not_called()

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


@patch("dafni_cli.commands.upload.DAFNISession")
@patch("dafni_cli.commands.upload.upload_dataset")
class TestUploadDataset(TestCase):
    """Test class to test the upload dataset commands"""

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
            with open("test_metadata.json", "w", encoding="utf-8") as file:
                file.write("{}")
            with open("test_dataset.txt", "w", encoding="utf-8") as file:
                file.write("test dataset file")
            result = runner.invoke(
                upload.upload,
                [
                    "dataset",
                    "test_metadata.json",
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
            "Dataset metadata file path: test_metadata.json\n"
            "Dataset file path: test_dataset.txt\n"
            "Confirm dataset upload? [y/N]: y\n",
        )
        self.assertEqual(result.exit_code, 0)

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
            with open("test_metadata.json", "w", encoding="utf-8") as file:
                file.write("{}")
            with open("test_dataset1.txt", "w", encoding="utf-8") as file:
                file.write("test dataset file1")
            with open("test_dataset2.txt", "w", encoding="utf-8") as file:
                file.write("test dataset file2")
            result = runner.invoke(
                upload.upload,
                [
                    "dataset",
                    "test_metadata.json",
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
            "Dataset metadata file path: test_metadata.json\n"
            "Dataset file path: test_dataset1.txt\n"
            "Dataset file path: test_dataset2.txt\n"
            "Confirm dataset upload? [y/N]: y\n",
        )
        self.assertEqual(result.exit_code, 0)

    def test_upload_dataset_skipping_confirmation(
        self,
        mock_upload_dataset,
        mock_DAFNISession,
    ):
        """Tests that the 'upload dataset' command works correctly when
        given a -y flag to skip the confirmation"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()

        # CALL
        with runner.isolated_filesystem():
            with open("test_metadata.json", "w", encoding="utf-8") as file:
                file.write("{}")
            with open("test_dataset.txt", "w", encoding="utf-8") as file:
                file.write("test dataset file")
            result = runner.invoke(
                upload.upload,
                ["dataset", "test_metadata.json", "test_dataset.txt", "-y"],
            )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_upload_dataset.assert_called_once_with(
            session, {}, (Path("test_dataset.txt"),)
        )

        self.assertEqual(result.output, "")
        self.assertEqual(result.exit_code, 0)

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
            with open("test_metadata.json", "w", encoding="utf-8") as file:
                file.write("{}")
            with open("test_dataset.txt", "w", encoding="utf-8") as file:
                file.write("test dataset file")
            result = runner.invoke(
                upload.upload,
                [
                    "dataset",
                    "test_metadata.json",
                    "test_dataset.txt",
                ],
                input="n",
            )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_upload_dataset.assert_not_called()

        self.assertEqual(
            result.output,
            "Dataset metadata file path: test_metadata.json\n"
            "Dataset file path: test_dataset.txt\n"
            "Confirm dataset upload? [y/N]: n\n"
            "Aborted!\n",
        )
        self.assertEqual(result.exit_code, 1)


@patch("dafni_cli.commands.upload.DAFNISession")
@patch("dafni_cli.commands.upload.upload_dataset")
@patch("dafni_cli.commands.upload.cli_get_latest_dataset_metadata")
@patch("dafni_cli.commands.upload.modify_dataset_metadata_for_upload")
class TestUploadDatasetVersion(TestCase):
    """Test class to test the upload dataset-version commands"""

    def test_upload_dataset_version(
        self,
        mock_modify_dataset_metadata_for_upload,
        mock_cli_get_latest_dataset_metadata,
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
        mock_cli_get_latest_dataset_metadata.return_value = TEST_DATASET_METADATA
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
        mock_cli_get_latest_dataset_metadata.assert_called_once_with(
            session, dataset_version_id
        )
        mock_modify_dataset_metadata_for_upload.assert_called_once_with(
            existing_metadata=TEST_DATASET_METADATA,
            metadata_path=None,
            title=None,
            description=None,
            subject=None,
            identifiers=None,
            themes=None,
            language=None,
            keywords=None,
            standard=None,
            start_date=None,
            end_date=None,
            organisation=None,
            people=None,
            created_date=None,
            update_frequency=None,
            publisher=None,
            contact=None,
            license=None,
            rights=None,
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

    def test_upload_dataset_version_with_multiple_files(
        self,
        mock_modify_dataset_metadata_for_upload,
        mock_cli_get_latest_dataset_metadata,
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
        mock_cli_get_latest_dataset_metadata.return_value = TEST_DATASET_METADATA
        metadata = parse_dataset_metadata(TEST_DATASET_METADATA)

        # CALL
        with runner.isolated_filesystem():
            with open(file_paths[0], "w", encoding="utf-8") as file:
                file.write("test dataset file")
            with open(file_paths[1], "w", encoding="utf-8") as file:
                file.write("test dataset file")
            result = runner.invoke(
                upload.upload,
                ["dataset-version", dataset_version_id, file_paths[0], file_paths[1]],
                input="y",
            )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_cli_get_latest_dataset_metadata.assert_called_once_with(
            session, dataset_version_id
        )
        mock_modify_dataset_metadata_for_upload.assert_called_once_with(
            existing_metadata=TEST_DATASET_METADATA,
            metadata_path=None,
            title=None,
            description=None,
            subject=None,
            identifiers=None,
            themes=None,
            language=None,
            keywords=None,
            standard=None,
            start_date=None,
            end_date=None,
            organisation=None,
            people=None,
            created_date=None,
            update_frequency=None,
            publisher=None,
            contact=None,
            license=None,
            rights=None,
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

    def test_upload_dataset_version_saving_existing_metadata(
        self,
        mock_modify_dataset_metadata_for_upload,
        mock_cli_get_latest_dataset_metadata,
        mock_upload_dataset,
        mock_DAFNISession,
    ):
        """Tests that the 'upload dataset-version' command works correctly
        with the --save option"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        dataset_version_id = "some-existing-version-id"
        file_path = "test_dataset.txt"
        mock_cli_get_latest_dataset_metadata.return_value = TEST_DATASET_METADATA
        mock_modify_dataset_metadata_for_upload.return_value = TEST_DATASET_METADATA
        metadata_save_path = "metadata_save_file.json"

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
                    "--save",
                    metadata_save_path,
                ],
            )

            with open(metadata_save_path, "r", encoding="utf-8") as file:
                saved_metadata = file.read()

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_cli_get_latest_dataset_metadata.assert_called_once_with(
            session, dataset_version_id
        )
        mock_modify_dataset_metadata_for_upload.assert_called_once_with(
            existing_metadata=TEST_DATASET_METADATA,
            metadata_path=None,
            title=None,
            description=None,
            subject=None,
            identifiers=None,
            themes=None,
            language=None,
            keywords=None,
            standard=None,
            start_date=None,
            end_date=None,
            organisation=None,
            people=None,
            created_date=None,
            update_frequency=None,
            publisher=None,
            contact=None,
            license=None,
            rights=None,
            version_message=None,
        )
        self.assertEqual(
            saved_metadata, json.dumps(TEST_DATASET_METADATA, indent=4, sort_keys=True)
        )
        mock_upload_dataset.assert_not_called()

        self.assertEqual(
            result.output, f"Saved existing dataset metadata to {metadata_save_path}\n"
        )
        self.assertEqual(result.exit_code, 0)

    def test_upload_dataset_version_skipping_confirmation(
        self,
        mock_modify_dataset_metadata_for_upload,
        mock_cli_get_latest_dataset_metadata,
        mock_upload_dataset,
        mock_DAFNISession,
    ):
        """Tests that the 'upload dataset-version' command works correctly when
        given a -y flag to skip the confirmation"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        dataset_version_id = "some-existing-version-id"
        file_path = "test_dataset.txt"
        mock_cli_get_latest_dataset_metadata.return_value = TEST_DATASET_METADATA
        metadata = parse_dataset_metadata(TEST_DATASET_METADATA)

        # CALL
        with runner.isolated_filesystem():
            with open("test_dataset.txt", "w", encoding="utf-8") as file:
                file.write("test dataset file")
            result = runner.invoke(
                upload.upload,
                ["dataset-version", dataset_version_id, file_path, "-y"],
            )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_cli_get_latest_dataset_metadata.assert_called_once_with(
            session, dataset_version_id
        )
        mock_modify_dataset_metadata_for_upload.assert_called_once_with(
            existing_metadata=TEST_DATASET_METADATA,
            metadata_path=None,
            title=None,
            description=None,
            subject=None,
            identifiers=None,
            themes=None,
            language=None,
            keywords=None,
            standard=None,
            start_date=None,
            end_date=None,
            organisation=None,
            people=None,
            created_date=None,
            update_frequency=None,
            publisher=None,
            contact=None,
            license=None,
            rights=None,
            version_message=None,
        )
        mock_upload_dataset.assert_called_once_with(
            session,
            dataset_id=metadata.dataset_id,
            metadata=mock_modify_dataset_metadata_for_upload.return_value,
            file_paths=(Path(file_path),),
        )

        self.assertEqual(result.output, "")
        self.assertEqual(result.exit_code, 0)

    def test_upload_dataset_version_cancel(
        self,
        mock_modify_dataset_metadata_for_upload,
        mock_cli_get_latest_dataset_metadata,
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
        mock_cli_get_latest_dataset_metadata.return_value = TEST_DATASET_METADATA
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
        mock_cli_get_latest_dataset_metadata.assert_called_once_with(
            session, dataset_version_id
        )
        mock_modify_dataset_metadata_for_upload.assert_called_once_with(
            existing_metadata=TEST_DATASET_METADATA,
            metadata_path=None,
            title=None,
            description=None,
            subject=None,
            identifiers=None,
            themes=None,
            language=None,
            keywords=None,
            standard=None,
            start_date=None,
            end_date=None,
            organisation=None,
            people=None,
            created_date=None,
            update_frequency=None,
            publisher=None,
            contact=None,
            license=None,
            rights=None,
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

    def test_upload_dataset_version_with_metadata_and_all_optional_modifications(
        self,
        mock_modify_dataset_metadata_for_upload,
        mock_cli_get_latest_dataset_metadata,
        mock_upload_dataset,
        mock_DAFNISession,
    ):
        """Tests that the 'upload dataset-version' command works correctly
        when a path to metadata and a version message is given"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        dataset_version_id = "some-existing-version-id"
        file_path = "test_dataset.txt"
        metadata_path = "definition.json"
        mock_cli_get_latest_dataset_metadata.return_value = TEST_DATASET_METADATA
        metadata = parse_dataset_metadata(TEST_DATASET_METADATA)

        options = {
            "title": "Dataset title",
            "description": "Dataset description",
            "identifiers": ("test", "identifiers"),
            "subject": "Farming",
            "themes": ("Buildings", "Hydrology"),
            "language": "en",
            "keywords": ("test", "another_test"),
            "standard": ("standard_name", "https://www.standard-url.com/"),
            "start_date": datetime(2022, 6, 28),
            "end_date": datetime(2022, 8, 10),
            "organisation": ("organisation_name", "https://www.organisaton-url.com/"),
            "people": (
                ("person-1-name", "http://www.person-1.com/"),
                ("person-2-name", "http://www.person-2.com/"),
            ),
            "created_date": datetime(2023, 6, 14),
            "update_frequency": "Annual",
            "publisher": ("publisher_name", "https://www.publisher-url.com/"),
            "contact": ("contact_point_name", "test@example.com"),
            "license": "http://www.license-url.com/",
            "rights": "Some rights",
            "version_message": "Some version message",
        }

        args = add_dataset_metadata_common_options(
            args=[
                "dataset-version",
                dataset_version_id,
                file_path,
                "--metadata",
                metadata_path,
            ],
            all_optional=True,
            dictionary=options,
            **options,
        )

        # CALL
        with runner.isolated_filesystem():
            with open(file_path, "w", encoding="utf-8") as file:
                file.write("test dataset file")
            with open(metadata_path, "w", encoding="utf-8") as file:
                file.write("test metadata file")
            result = runner.invoke(
                upload.upload,
                args,
                input="y",
            )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_cli_get_latest_dataset_metadata.assert_called_once_with(
            session, dataset_version_id
        )
        mock_modify_dataset_metadata_for_upload.assert_called_once_with(
            existing_metadata=TEST_DATASET_METADATA,
            metadata_path=Path(metadata_path),
            **options,
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
            f"Dataset metadata file path: {metadata_path}\n"
            "Confirm dataset upload? [y/N]: y\n",
        )
        self.assertEqual(result.exit_code, 0)


@patch("dafni_cli.commands.upload.DAFNISession")
@patch("dafni_cli.commands.upload.upload_dataset_metadata_version")
@patch("dafni_cli.commands.upload.cli_get_latest_dataset_metadata")
@patch("dafni_cli.commands.upload.modify_dataset_metadata_for_upload")
class TestUploadDatasetMetadata(TestCase):
    """Test class to test the upload dataset-metadata commands"""

    def test_upload_dataset_metadata(
        self,
        mock_modify_dataset_metadata_for_upload,
        mock_cli_get_latest_dataset_metadata,
        mock_upload_dataset_metadata_version,
        mock_DAFNISession,
    ):
        """Tests that the 'upload dataset-metadata' command works correctly"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        dataset_version_id = "some-existing-version-id"
        mock_cli_get_latest_dataset_metadata.return_value = TEST_DATASET_METADATA
        metadata = parse_dataset_metadata(TEST_DATASET_METADATA)

        # CALL
        with runner.isolated_filesystem():
            result = runner.invoke(
                upload.upload,
                [
                    "dataset-metadata",
                    dataset_version_id,
                ],
                input="y",
            )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_cli_get_latest_dataset_metadata.assert_called_once_with(
            session, dataset_version_id
        )
        mock_modify_dataset_metadata_for_upload.assert_called_once_with(
            existing_metadata=TEST_DATASET_METADATA,
            metadata_path=None,
            title=None,
            description=None,
            subject=None,
            identifiers=None,
            themes=None,
            language=None,
            keywords=None,
            standard=None,
            start_date=None,
            end_date=None,
            organisation=None,
            people=None,
            created_date=None,
            update_frequency=None,
            publisher=None,
            contact=None,
            license=None,
            rights=None,
            version_message=None,
        )
        mock_upload_dataset_metadata_version.assert_called_once_with(
            session,
            dataset_id=metadata.dataset_id,
            version_id=dataset_version_id,
            metadata=mock_modify_dataset_metadata_for_upload.return_value,
        )

        self.assertEqual(
            result.output,
            f"Dataset Title: {metadata.title}\n"
            f"Dataset ID: {metadata.dataset_id}\n"
            f"Dataset Version ID: {metadata.version_id}\n"
            "Confirm metadata upload? [y/N]: y\n",
        )
        self.assertEqual(result.exit_code, 0)

    def test_upload_dataset_metadata_saving_existing_metadata(
        self,
        mock_modify_dataset_metadata_for_upload,
        mock_cli_get_latest_dataset_metadata,
        mock_upload_dataset_metadata_version,
        mock_DAFNISession,
    ):
        """Tests that the 'upload dataset-metadata' command works correctly
        with the --save option"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        dataset_version_id = "some-existing-version-id"
        mock_cli_get_latest_dataset_metadata.return_value = TEST_DATASET_METADATA
        mock_modify_dataset_metadata_for_upload.return_value = TEST_DATASET_METADATA
        metadata_save_path = "metadata_save_file.json"

        # CALL
        with runner.isolated_filesystem():
            result = runner.invoke(
                upload.upload,
                [
                    "dataset-metadata",
                    dataset_version_id,
                    "--save",
                    metadata_save_path,
                ],
            )

            with open(metadata_save_path, "r", encoding="utf-8") as file:
                saved_metadata = file.read()

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_cli_get_latest_dataset_metadata.assert_called_once_with(
            session, dataset_version_id
        )
        mock_modify_dataset_metadata_for_upload.assert_called_once_with(
            existing_metadata=TEST_DATASET_METADATA,
            metadata_path=None,
            title=None,
            description=None,
            subject=None,
            identifiers=None,
            themes=None,
            language=None,
            keywords=None,
            standard=None,
            start_date=None,
            end_date=None,
            organisation=None,
            people=None,
            created_date=None,
            update_frequency=None,
            publisher=None,
            contact=None,
            license=None,
            rights=None,
            version_message=None,
        )
        self.assertEqual(
            saved_metadata, json.dumps(TEST_DATASET_METADATA, indent=4, sort_keys=True)
        )
        mock_upload_dataset_metadata_version.assert_not_called()

        self.assertEqual(
            result.output, f"Saved existing dataset metadata to {metadata_save_path}\n"
        )
        self.assertEqual(result.exit_code, 0)

    def test_upload_dataset_metadata_with_metadata_and_all_optional_modifications(
        self,
        mock_modify_dataset_metadata_for_upload,
        mock_cli_get_latest_dataset_metadata,
        mock_upload_dataset_metadata_version,
        mock_DAFNISession,
    ):
        """Tests that the 'upload dataset-metadata' command works correctly
        when a path to metadata and a version message is given"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        dataset_version_id = "some-existing-version-id"
        metadata_path = "metadata.json"
        mock_cli_get_latest_dataset_metadata.return_value = TEST_DATASET_METADATA
        metadata = parse_dataset_metadata(TEST_DATASET_METADATA)

        options = {
            "title": "Dataset title",
            "description": "Dataset description",
            "identifiers": ("test", "identifiers"),
            "subject": "Farming",
            "themes": ("Buildings", "Hydrology"),
            "language": "en",
            "keywords": ("test", "another_test"),
            "standard": ("standard_name", "https://www.standard-url.com/"),
            "start_date": datetime(2022, 6, 28),
            "end_date": datetime(2022, 8, 10),
            "organisation": ("organisation_name", "https://www.organisaton-url.com/"),
            "people": (
                ("person-1-name", "http://www.person-1.com/"),
                ("person-2-name", "http://www.person-2.com/"),
            ),
            "created_date": datetime(2023, 6, 14),
            "update_frequency": "Annual",
            "publisher": ("publisher_name", "https://www.publisher-url.com/"),
            "contact": ("contact_point_name", "test@example.com"),
            "license": "http://www.license-url.com/",
            "rights": "Some rights",
            "version_message": "Some version message",
        }

        args = add_dataset_metadata_common_options(
            args=[
                "dataset-metadata",
                dataset_version_id,
                "--metadata",
                metadata_path,
            ],
            all_optional=True,
            dictionary=options,
            **options,
        )

        # CALL
        with runner.isolated_filesystem():
            with open(metadata_path, "w", encoding="utf-8") as file:
                file.write("test metadata file")
            result = runner.invoke(
                upload.upload,
                args,
                input="y",
            )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_cli_get_latest_dataset_metadata.assert_called_once_with(
            session, dataset_version_id
        )
        mock_modify_dataset_metadata_for_upload.assert_called_once_with(
            existing_metadata=TEST_DATASET_METADATA,
            metadata_path=Path(metadata_path),
            **options,
        )
        mock_upload_dataset_metadata_version.assert_called_once_with(
            session,
            dataset_id=metadata.dataset_id,
            version_id=dataset_version_id,
            metadata=mock_modify_dataset_metadata_for_upload.return_value,
        )

        self.assertEqual(
            result.output,
            f"Dataset Title: {metadata.title}\n"
            f"Dataset ID: {metadata.dataset_id}\n"
            f"Dataset Version ID: {metadata.version_id}\n"
            f"Dataset metadata file path: {metadata_path}\n"
            "Confirm metadata upload? [y/N]: y\n",
        )
        self.assertEqual(result.exit_code, 0)

    def test_upload_dataset_metadata_skipping_confirmation(
        self,
        mock_modify_dataset_metadata_for_upload,
        mock_cli_get_latest_dataset_metadata,
        mock_upload_dataset_metadata_version,
        mock_DAFNISession,
    ):
        """Tests that the 'upload dataset-metadata' command works correctly when
        given a -y flag to skip the confirmation"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        dataset_version_id = "some-existing-version-id"
        mock_cli_get_latest_dataset_metadata.return_value = TEST_DATASET_METADATA
        metadata = parse_dataset_metadata(TEST_DATASET_METADATA)

        # CALL
        with runner.isolated_filesystem():
            result = runner.invoke(
                upload.upload,
                ["dataset-metadata", dataset_version_id, "-y"],
            )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_cli_get_latest_dataset_metadata.assert_called_once_with(
            session, dataset_version_id
        )
        mock_modify_dataset_metadata_for_upload.assert_called_once_with(
            existing_metadata=TEST_DATASET_METADATA,
            metadata_path=None,
            title=None,
            description=None,
            subject=None,
            identifiers=None,
            themes=None,
            language=None,
            keywords=None,
            standard=None,
            start_date=None,
            end_date=None,
            organisation=None,
            people=None,
            created_date=None,
            update_frequency=None,
            publisher=None,
            contact=None,
            license=None,
            rights=None,
            version_message=None,
        )
        mock_upload_dataset_metadata_version.assert_called_once_with(
            session,
            dataset_id=metadata.dataset_id,
            version_id=dataset_version_id,
            metadata=mock_modify_dataset_metadata_for_upload.return_value,
        )

        self.assertEqual(result.output, "")
        self.assertEqual(result.exit_code, 0)

    def test_upload_metadata_cancel(
        self,
        mock_modify_dataset_metadata_for_upload,
        mock_cli_get_latest_dataset_metadata,
        mock_upload_dataset_metadata_version,
        mock_DAFNISession,
    ):
        """Tests that the 'upload dataset-metadata' command can be canceled"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        dataset_version_id = "some-existing-version-id"
        mock_cli_get_latest_dataset_metadata.return_value = TEST_DATASET_METADATA
        metadata = parse_dataset_metadata(TEST_DATASET_METADATA)

        # CALL
        with runner.isolated_filesystem():
            result = runner.invoke(
                upload.upload,
                [
                    "dataset-metadata",
                    dataset_version_id,
                ],
                input="n",
            )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_cli_get_latest_dataset_metadata.assert_called_once_with(
            session, dataset_version_id
        )
        mock_modify_dataset_metadata_for_upload.assert_called_once_with(
            existing_metadata=TEST_DATASET_METADATA,
            metadata_path=None,
            title=None,
            description=None,
            subject=None,
            identifiers=None,
            themes=None,
            language=None,
            keywords=None,
            standard=None,
            start_date=None,
            end_date=None,
            organisation=None,
            people=None,
            created_date=None,
            update_frequency=None,
            publisher=None,
            contact=None,
            license=None,
            rights=None,
            version_message=None,
        )
        mock_upload_dataset_metadata_version.assert_not_called()

        self.assertEqual(
            result.output,
            f"Dataset Title: {metadata.title}\n"
            f"Dataset ID: {metadata.dataset_id}\n"
            f"Dataset Version ID: {metadata.version_id}\n"
            "Confirm metadata upload? [y/N]: n\n"
            "Aborted!\n",
        )
        self.assertEqual(result.exit_code, 1)


@patch("dafni_cli.commands.upload.DAFNISession")
@patch("dafni_cli.commands.upload.upload_workflow")
class TestUploadWorkflow(TestCase):
    """Test class to test the upload workflow commands"""

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
        version_message = "Initial version"
        version_id = "version-id"
        mock_upload_workflow.return_value = {"id": version_id}

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
                    version_message,
                ],
                input="y",
            )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_upload_workflow.assert_called_once_with(
            session, Path("test_definition.json"), version_message, None
        )

        self.assertEqual(
            result.output,
            "Workflow definition file path: test_definition.json\n"
            f"Version message: {version_message}\n"
            "No parent workflow: new workflow to be created\n"
            "Confirm workflow upload? [y/N]: y\n"
            "Uploading workflow\n"
            "\nUpload successful\n"
            f"Version ID: {version_id}\n",
        )
        self.assertEqual(result.exit_code, 0)

    def test_upload_workflow_with_parent(
        self,
        mock_upload_workflow,
        mock_DAFNISession,
    ):
        """Tests that the 'upload workflow' command works correctly when
        a parent is given"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        version_message = "Initial version"
        version_id = "version-id"
        mock_upload_workflow.return_value = {"id": version_id}

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
                    version_message,
                    "--parent-id",
                    "parent-id",
                ],
                input="y",
            )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_upload_workflow.assert_called_once_with(
            session, Path("test_definition.json"), version_message, "parent-id"
        )

        self.assertEqual(
            result.output,
            "Workflow definition file path: test_definition.json\n"
            f"Version message: {version_message}\n"
            "Parent workflow ID: parent-id\n"
            "Confirm workflow upload? [y/N]: y\n"
            "Uploading workflow\n"
            "\nUpload successful\n"
            f"Version ID: {version_id}\n",
        )
        self.assertEqual(result.exit_code, 0)

    def test_upload_workflow_skipping_confirmation(
        self,
        mock_upload_workflow,
        mock_DAFNISession,
    ):
        """Tests that the 'upload workflow' command works correctly when
        given a -y flag to skip the confirmation"""

        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        version_message = "Initial version"
        version_id = "version-id"
        mock_upload_workflow.return_value = {"id": version_id}

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
                    version_message,
                    "-y",
                ],
            )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_upload_workflow.assert_called_once_with(
            session, Path("test_definition.json"), version_message, None
        )

        self.assertEqual(
            result.output,
            "Uploading workflow\n"
            "\nUpload successful\n"
            f"Version ID: {version_id}\n",
        )
        self.assertEqual(result.exit_code, 0)

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
        version_message = "Initial version"
        version_id = "version-id"
        mock_upload_workflow.return_value = {"id": version_id}

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
                    version_message,
                ],
                input="n",
            )

        # ASSERT
        mock_DAFNISession.assert_called_once()
        mock_upload_workflow.assert_not_called()

        self.assertEqual(
            result.output,
            "Workflow definition file path: test_definition.json\n"
            f"Version message: {version_message}\n"
            "No parent workflow: new workflow to be created\n"
            "Confirm workflow upload? [y/N]: n\n"
            "Aborted!\n",
        )
        self.assertEqual(result.exit_code, 1)

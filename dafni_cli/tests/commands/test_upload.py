import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple
from unittest import TestCase
from unittest.mock import MagicMock, patch

from click.testing import CliRunner, Result

from dafni_cli.commands import upload
from dafni_cli.datasets.dataset_metadata import parse_dataset_metadata
from dafni_cli.tests.commands.test_options import add_dataset_metadata_common_options
from dafni_cli.tests.fixtures.dataset_metadata import TEST_DATASET_METADATA


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


class TestUploadModel(TestCase):
    """Test class to test the upload model commands"""

    def setUp(self) -> None:
        super().setUp()

        self.definition_path = "test_definition.yaml"
        self.image_path = "test_image.txt"
        self.version_message = "version_message"
        self.parent_id = "parent-id"

        self.mock_DAFNISession = patch("dafni_cli.commands.upload.DAFNISession").start()
        self.mock_session = MagicMock()
        self.mock_DAFNISession.return_value = self.mock_session

        self.mock_upload_model = patch("dafni_cli.commands.upload.upload_model").start()

        self.addCleanup(patch.stopall)

    def invoke_command(
        self,
        additional_args: Optional[List[str]] = None,
        input: Optional[str] = None,
    ) -> Result:
        """Invokes the upload model command with required arguments provided
        Args:
            additional_args (Optional[List[str]]): Any additional parameters to add
            input (Optional[str]): 'input' to pass to CliRunner's invoke function
        """
        if additional_args is None:
            additional_args = []

        runner = CliRunner()

        with runner.isolated_filesystem():
            with open(self.definition_path, "w", encoding="utf-8") as file:
                file.write("test definition file")
            with open(self.image_path, "w", encoding="utf-8") as file:
                file.write("test image file")
            result = runner.invoke(
                upload.upload,
                [
                    "model",
                    self.definition_path,
                    self.image_path,
                    "--version-message",
                    self.version_message,
                ]
                + additional_args,
                input=input,
            )
        return result

    def test_upload_model(
        self,
    ):
        """Tests that the 'upload model' command works correctly when
        no parent id is given"""

        # CALL
        result = self.invoke_command(
            input="y",
        )

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_upload_model.assert_called_with(
            self.mock_session,
            definition_path=Path(self.definition_path),
            image_path=Path(self.image_path),
            version_message=self.version_message,
            parent_id=None,
            json=False,
        )

        self.assertEqual(
            result.output,
            f"Model definition file path: {self.definition_path}\n"
            f"Image file path: {self.image_path}\n"
            f"Version message: {self.version_message}\n"
            "No parent model: New model to be created\n"
            "Confirm model upload? [y/N]: y\n",
        )
        self.assertEqual(result.exit_code, 0)

    def test_upload_model_with_parent(
        self,
    ):
        """Tests that the 'upload model' command works correctly when
        a parent is given"""

        # CALL
        result = self.invoke_command(
            additional_args=["--parent-id", self.parent_id],
            input="y",
        )

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_upload_model.assert_called_with(
            self.mock_session,
            definition_path=Path(self.definition_path),
            image_path=Path(self.image_path),
            version_message=self.version_message,
            parent_id=self.parent_id,
            json=False,
        )

        self.assertEqual(
            result.output,
            f"Model definition file path: {self.definition_path}\n"
            f"Image file path: {self.image_path}\n"
            f"Version message: {self.version_message}\n"
            f"Parent model ID: {self.parent_id}\n"
            "Confirm model upload? [y/N]: y\n",
        )
        self.assertEqual(result.exit_code, 0)

    def test_upload_model_skipping_confirmation(
        self,
    ):
        """Tests that the 'upload model' command works correctly when
        given a -y flag to skip the confirmation"""

        # CALL
        result = self.invoke_command(
            additional_args=["-y"],
        )

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_upload_model.assert_called_with(
            self.mock_session,
            definition_path=Path(self.definition_path),
            image_path=Path(self.image_path),
            version_message=self.version_message,
            parent_id=None,
            json=False,
        )

        self.assertEqual(result.output, "")
        self.assertEqual(result.exit_code, 0)

    def test_upload_model_json(
        self,
    ):
        """Tests that the 'upload model' command works correctly when
        given a --json flag"""

        # CALL
        result = self.invoke_command(
            additional_args=["--json"],
        )

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_upload_model.assert_called_with(
            self.mock_session,
            definition_path=Path(self.definition_path),
            image_path=Path(self.image_path),
            version_message=self.version_message,
            parent_id=None,
            json=True,
        )

        self.assertEqual(result.output, "")
        self.assertEqual(result.exit_code, 0)

    def test_upload_model_cancel(
        self,
    ):
        """Tests that the 'upload model' command can be canceled"""

        # CALL
        result = self.invoke_command(
            input="n",
        )

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_upload_model.assert_not_called()

        self.assertEqual(
            result.output,
            f"Model definition file path: {self.definition_path}\n"
            f"Image file path: {self.image_path}\n"
            f"Version message: {self.version_message}\n"
            "No parent model: New model to be created\n"
            "Confirm model upload? [y/N]: n\n"
            "Aborted!\n",
        )
        self.assertEqual(result.exit_code, 1)


class TestUploadDataset(TestCase):
    """Test class to test the upload dataset commands"""

    def setUp(self) -> None:
        super().setUp()

        self.metadata_path = "test_metadata.json"

        self.mock_DAFNISession = patch("dafni_cli.commands.upload.DAFNISession").start()
        self.mock_session = MagicMock()
        self.mock_DAFNISession.return_value = self.mock_session

        self.mock_upload_dataset = patch(
            "dafni_cli.commands.upload.upload_dataset"
        ).start()

        self.addCleanup(patch.stopall)

    def invoke_command(
        self,
        file_paths: List[str],
        additional_args: Optional[List[str]] = None,
        input: Optional[str] = None,
    ) -> Result:
        """Invokes the upload dataset command with most required arguments provided

        Args:
            file_paths (Optional[List]): List of file paths of the dataset files
                                         to upload (Added automatically to command
                                         parameters)
            additional_args (Optional[List[str]]): Any additional parameters to
                                                   add
            input (Optional[str]): 'input' to pass to CliRunner's invoke function
        """
        if additional_args is None:
            additional_args = []

        runner = CliRunner()

        with runner.isolated_filesystem():
            with open(self.metadata_path, "w", encoding="utf-8") as file:
                file.write("{}")
            for file_path in file_paths:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write("test dataset file")
            result = runner.invoke(
                upload.upload,
                [
                    "dataset",
                    self.metadata_path,
                ]
                + file_paths
                + additional_args,
                input=input,
            )
        return result

    def test_upload_dataset(
        self,
    ):
        """Tests that the 'upload dataset' command works correctly"""

        # SETUP
        dataset_file_path = "test_dataset.txt"

        # CALL
        result = self.invoke_command(file_paths=[dataset_file_path], input="y")

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_upload_dataset.assert_called_once_with(
            self.mock_session, {}, (Path(dataset_file_path),), json=False
        )

        self.assertEqual(
            result.output,
            f"Dataset metadata file path: {self.metadata_path}\n"
            f"Dataset file name: {dataset_file_path}\n"
            "Confirm dataset upload? [y/N]: y\n",
        )
        self.assertEqual(result.exit_code, 0)

    def test_upload_dataset_with_multiple_files(
        self,
    ):
        """Tests that the 'upload dataset' command works correctly when
        multiple files are given"""

        # SETUP
        dataset_file_paths = ["test_dataset1.txt", "test_dataset2.txt"]

        # CALL
        result = self.invoke_command(file_paths=dataset_file_paths, input="y")

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_upload_dataset.assert_called_once_with(
            self.mock_session,
            {},
            (Path(dataset_file_paths[0]), Path(dataset_file_paths[1])),
            json=False,
        )

        self.assertEqual(
            result.output,
            f"Dataset metadata file path: {self.metadata_path}\n"
            f"Dataset file name: {dataset_file_paths[0]}\n"
            f"Dataset file name: {dataset_file_paths[1]}\n"
            "Confirm dataset upload? [y/N]: y\n",
        )
        self.assertEqual(result.exit_code, 0)

    def test_upload_dataset_skipping_confirmation(
        self,
    ):
        """Tests that the 'upload dataset' command works correctly when
        given a -y flag to skip the confirmation"""

        # SETUP
        dataset_file_path = "test_dataset.txt"

        # CALL
        result = self.invoke_command(
            file_paths=[dataset_file_path], additional_args=["-y"], input="y"
        )

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_upload_dataset.assert_called_once_with(
            self.mock_session, {}, (Path(dataset_file_path),), json=False
        )

        self.assertEqual(result.output, "")
        self.assertEqual(result.exit_code, 0)

    def test_upload_dataset_json(
        self,
    ):
        """Tests that the 'upload dataset' command works correctly when given
        a --json flag"""

        # SETUP
        dataset_file_path = "test_dataset.txt"

        # CALL
        result = self.invoke_command(
            file_paths=[dataset_file_path], additional_args=["--json"]
        )

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_upload_dataset.assert_called_once_with(
            self.mock_session, {}, (Path(dataset_file_path),), json=True
        )

        self.assertEqual(result.output, "")
        self.assertEqual(result.exit_code, 0)

    def test_upload_dataset_cancel(
        self,
    ):
        """Tests that the 'upload dataset' command can be canceled"""

        # SETUP
        dataset_file_path = "test_dataset.txt"

        # CALL
        result = self.invoke_command(file_paths=[dataset_file_path], input="n")

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_upload_dataset.assert_not_called()

        self.assertEqual(
            result.output,
            f"Dataset metadata file path: {self.metadata_path}\n"
            f"Dataset file name: {dataset_file_path}\n"
            "Confirm dataset upload? [y/N]: n\n"
            "Aborted!\n",
        )
        self.assertEqual(result.exit_code, 1)


class TestUploadDatasetVersion(TestCase):
    """Test class to test the upload dataset-version commands"""

    def setUp(self) -> None:
        super().setUp()

        self.dataset_version_id = "some-existing-version-id"

        self.mock_DAFNISession = patch("dafni_cli.commands.upload.DAFNISession").start()
        self.mock_session = MagicMock()
        self.mock_DAFNISession.return_value = self.mock_session

        self.mock_cli_get_latest_dataset_metadata = patch(
            "dafni_cli.commands.upload.cli_get_latest_dataset_metadata"
        ).start()
        self.mock_modify_dataset_metadata_for_upload = patch(
            "dafni_cli.commands.upload.modify_dataset_metadata_for_upload"
        ).start()
        self.mock_upload_dataset = patch(
            "dafni_cli.commands.upload.upload_dataset"
        ).start()

        self.addCleanup(patch.stopall)

    def invoke_command(
        self,
        file_paths: List[str],
        additional_args: List[str],
        input: Optional[str] = None,
        file_paths_to_read: Optional[List[str]] = None,
    ) -> Tuple[Result, List[str]]:
        """Invokes the upload dataset-version  command with most required arguments
        provided

        Args:
            file_paths (Optional[List]): List of file paths of files to create prior
                                         to invoking the command
            additional_args (List[str]): Any additional parameters to add
            input (Optional[str]): 'input' to pass to CliRunner's invoke function
            file_paths_to_read (Optional[List[str]]): Paths to files to read (will
                                                    return the contents in a list)
        """
        runner = CliRunner()

        saved_file_data = []

        with runner.isolated_filesystem():
            for file_path in file_paths:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write("test dataset file")
            result = runner.invoke(
                upload.upload,
                [
                    "dataset-version",
                    self.dataset_version_id,
                ]
                + additional_args,
                input=input,
            )
            # Store the contents of any files created so they may be checked
            # later
            if file_paths_to_read:
                for file_path in file_paths_to_read:
                    with open(file_path, "r", encoding="utf-8") as file:
                        saved_file_data.append(file.read())

        return result, saved_file_data

    def test_upload_dataset_version(
        self,
    ):
        """Tests that the 'upload dataset-version' command works correctly"""

        # SETUP
        dataset_file_path = "test_dataset.txt"
        self.mock_cli_get_latest_dataset_metadata.return_value = TEST_DATASET_METADATA
        metadata = parse_dataset_metadata(TEST_DATASET_METADATA)

        # CALL
        result, _ = self.invoke_command(
            file_paths=[dataset_file_path],
            additional_args=[dataset_file_path],
            input="y",
        )

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_cli_get_latest_dataset_metadata.assert_called_once_with(
            self.mock_session, self.dataset_version_id
        )
        self.mock_modify_dataset_metadata_for_upload.assert_called_once_with(
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
        self.mock_upload_dataset.assert_called_once_with(
            self.mock_session,
            dataset_id=metadata.dataset_id,
            metadata=self.mock_modify_dataset_metadata_for_upload.return_value,
            paths=(Path(dataset_file_path),),
            json=False,
        )

        self.assertEqual(
            result.output,
            f"Dataset Title: {metadata.title}\n"
            f"Dataset ID: {metadata.dataset_id}\n"
            f"Dataset Version ID: {metadata.version_id}\n"
            f"Dataset file name: {dataset_file_path}\n"
            "Confirm dataset upload? [y/N]: y\n",
        )
        self.assertEqual(result.exit_code, 0)

    def test_upload_dataset_version_with_multiple_files(
        self,
    ):
        """Tests that the 'upload dataset-version' command works correctly
        when multiple files are given"""

        # SETUP
        dataset_file_paths = ["test_dataset1.txt", "test_dataset2.txt"]
        self.mock_cli_get_latest_dataset_metadata.return_value = TEST_DATASET_METADATA
        metadata = parse_dataset_metadata(TEST_DATASET_METADATA)

        # CALL
        result, _ = self.invoke_command(
            file_paths=dataset_file_paths,
            additional_args=dataset_file_paths,
            input="y",
        )

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_cli_get_latest_dataset_metadata.assert_called_once_with(
            self.mock_session, self.dataset_version_id
        )
        self.mock_modify_dataset_metadata_for_upload.assert_called_once_with(
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
        self.mock_upload_dataset.assert_called_once_with(
            self.mock_session,
            dataset_id=metadata.dataset_id,
            metadata=self.mock_modify_dataset_metadata_for_upload.return_value,
            paths=(Path(dataset_file_paths[0]), Path(dataset_file_paths[1])),
            json=False,
        )

        self.assertEqual(
            result.output,
            f"Dataset Title: {metadata.title}\n"
            f"Dataset ID: {metadata.dataset_id}\n"
            f"Dataset Version ID: {metadata.version_id}\n"
            f"Dataset file name: {dataset_file_paths[0]}\n"
            f"Dataset file name: {dataset_file_paths[1]}\n"
            "Confirm dataset upload? [y/N]: y\n",
        )
        self.assertEqual(result.exit_code, 0)

    def test_upload_dataset_version_saving_existing_metadata(
        self,
    ):
        """Tests that the 'upload dataset-version' command works correctly
        with the --save option"""

        # SETUP
        dataset_file_path = "test_dataset.txt"
        self.mock_cli_get_latest_dataset_metadata.return_value = TEST_DATASET_METADATA
        self.mock_modify_dataset_metadata_for_upload.return_value = (
            TEST_DATASET_METADATA
        )
        metadata_save_path = "metadata_save_file.json"

        # CALL
        result, saved_file_data = self.invoke_command(
            file_paths=[dataset_file_path],
            additional_args=[dataset_file_path, "--save", metadata_save_path],
            input="y",
            file_paths_to_read=[metadata_save_path],
        )

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_cli_get_latest_dataset_metadata.assert_called_once_with(
            self.mock_session, self.dataset_version_id
        )
        self.mock_modify_dataset_metadata_for_upload.assert_called_once_with(
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
            saved_file_data[0],
            json.dumps(TEST_DATASET_METADATA, indent=4, sort_keys=True),
        )
        self.mock_upload_dataset.assert_not_called()

        self.assertEqual(
            result.output, f"Saved existing dataset metadata to {metadata_save_path}\n"
        )
        self.assertEqual(result.exit_code, 0)

    def test_upload_dataset_version_skipping_confirmation(
        self,
    ):
        """Tests that the 'upload dataset-version' command works correctly when
        given a -y flag to skip the confirmation"""

        # SETUP
        dataset_file_path = "test_dataset.txt"
        self.mock_cli_get_latest_dataset_metadata.return_value = TEST_DATASET_METADATA
        metadata = parse_dataset_metadata(TEST_DATASET_METADATA)

        # CALL
        result, _ = self.invoke_command(
            file_paths=[dataset_file_path], additional_args=[dataset_file_path, "-y"]
        )

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_cli_get_latest_dataset_metadata.assert_called_once_with(
            self.mock_session, self.dataset_version_id
        )
        self.mock_modify_dataset_metadata_for_upload.assert_called_once_with(
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
        self.mock_upload_dataset.assert_called_once_with(
            self.mock_session,
            dataset_id=metadata.dataset_id,
            metadata=self.mock_modify_dataset_metadata_for_upload.return_value,
            paths=(Path(dataset_file_path),),
            json=False,
        )

        self.assertEqual(result.output, "")
        self.assertEqual(result.exit_code, 0)

    def test_upload_dataset_version_json(
        self,
    ):
        """Tests that the 'upload dataset-version' command works correctly
        when given a --json flag"""

        # SETUP
        dataset_file_path = "test_dataset.txt"
        self.mock_cli_get_latest_dataset_metadata.return_value = TEST_DATASET_METADATA
        metadata = parse_dataset_metadata(TEST_DATASET_METADATA)

        # CALL
        result, _ = self.invoke_command(
            file_paths=[dataset_file_path],
            additional_args=[dataset_file_path, "--json"],
        )

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_cli_get_latest_dataset_metadata.assert_called_once_with(
            self.mock_session, self.dataset_version_id
        )
        self.mock_modify_dataset_metadata_for_upload.assert_called_once_with(
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
        self.mock_upload_dataset.assert_called_once_with(
            self.mock_session,
            dataset_id=metadata.dataset_id,
            metadata=self.mock_modify_dataset_metadata_for_upload.return_value,
            paths=(Path(dataset_file_path),),
            json=True,
        )

        self.assertEqual(result.output, "")
        self.assertEqual(result.exit_code, 0)

    def test_upload_dataset_version_cancel(
        self,
    ):
        """Tests that the 'upload dataset-version' command can be canceled"""

        # SETUP
        dataset_file_path = "test_dataset.txt"
        self.mock_cli_get_latest_dataset_metadata.return_value = TEST_DATASET_METADATA
        metadata = parse_dataset_metadata(TEST_DATASET_METADATA)

        # CALL
        result, _ = self.invoke_command(
            file_paths=[dataset_file_path],
            additional_args=[dataset_file_path],
            input="n",
        )

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_cli_get_latest_dataset_metadata.assert_called_once_with(
            self.mock_session, self.dataset_version_id
        )
        self.mock_modify_dataset_metadata_for_upload.assert_called_once_with(
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
        self.mock_upload_dataset.assert_not_called()

        self.assertEqual(
            result.output,
            f"Dataset Title: {metadata.title}\n"
            f"Dataset ID: {metadata.dataset_id}\n"
            f"Dataset Version ID: {metadata.version_id}\n"
            f"Dataset file name: {dataset_file_path}\n"
            "Confirm dataset upload? [y/N]: n\n"
            "Aborted!\n",
        )
        self.assertEqual(result.exit_code, 1)

    def test_upload_dataset_version_with_metadata_and_all_optional_modifications(
        self,
    ):
        """Tests that the 'upload dataset-version' command works correctly
        when a path to metadata and a version message is given"""

        # SETUP
        dataset_file_path = "test_dataset.txt"
        metadata_path = "definition.json"
        self.mock_cli_get_latest_dataset_metadata.return_value = TEST_DATASET_METADATA
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

        additional_args = add_dataset_metadata_common_options(
            args=[
                dataset_file_path,
                "--metadata",
                metadata_path,
            ],
            all_optional=True,
            dictionary=options,
            **options,
        )

        # CALL
        result, _ = self.invoke_command(
            file_paths=[dataset_file_path, metadata_path],
            additional_args=additional_args,
            input="y",
        )

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_cli_get_latest_dataset_metadata.assert_called_once_with(
            self.mock_session, self.dataset_version_id
        )
        self.mock_modify_dataset_metadata_for_upload.assert_called_once_with(
            existing_metadata=TEST_DATASET_METADATA,
            metadata_path=Path(metadata_path),
            **options,
        )
        self.mock_upload_dataset.assert_called_once_with(
            self.mock_session,
            dataset_id=metadata.dataset_id,
            metadata=self.mock_modify_dataset_metadata_for_upload.return_value,
            paths=(Path(dataset_file_path),),
            json=False,
        )

        self.assertEqual(
            result.output,
            f"Dataset Title: {metadata.title}\n"
            f"Dataset ID: {metadata.dataset_id}\n"
            f"Dataset Version ID: {metadata.version_id}\n"
            f"Dataset file name: {dataset_file_path}\n"
            f"Dataset metadata file path: {metadata_path}\n"
            "Confirm dataset upload? [y/N]: y\n",
        )
        self.assertEqual(result.exit_code, 0)


class TestUploadDatasetMetadata(TestCase):
    """Test class to test the upload dataset-metadata commands"""

    def setUp(self) -> None:
        super().setUp()

        self.dataset_version_id = "some-existing-version-id"

        self.mock_DAFNISession = patch("dafni_cli.commands.upload.DAFNISession").start()
        self.mock_session = MagicMock()
        self.mock_DAFNISession.return_value = self.mock_session

        self.mock_cli_get_latest_dataset_metadata = patch(
            "dafni_cli.commands.upload.cli_get_latest_dataset_metadata"
        ).start()
        self.mock_modify_dataset_metadata_for_upload = patch(
            "dafni_cli.commands.upload.modify_dataset_metadata_for_upload"
        ).start()
        self.mock_upload_dataset_metadata_version = patch(
            "dafni_cli.commands.upload.upload_dataset_metadata_version"
        ).start()

    def invoke_command(
        self,
        file_paths: Optional[List[str]] = None,
        additional_args: Optional[List[str]] = None,
        input: Optional[str] = None,
        file_paths_to_read: Optional[List[str]] = None,
    ) -> Tuple[Result, List[str]]:
        """Invokes the upload dataset-metadata command with the required arguments
        provided

        Args:
            file_paths (Optional[List]): List of file paths of files to create prior
                                         to invoking the command
            additional_args (Optional[List[str]]): Any additional parameters to
                                                     add
            input (Optional[str]): 'input' to pass to CliRunner's invoke function
            file_paths_to_read (Optional[List[str]]): Paths to files to read (will
                                                    return the contents in a list)
        """
        if file_paths is None:
            file_paths = []
        if additional_args is None:
            additional_args = []

        runner = CliRunner()

        saved_file_data = []

        with runner.isolated_filesystem():
            for file_path in file_paths:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write("test dataset file")
            result = runner.invoke(
                upload.upload,
                [
                    "dataset-metadata",
                    self.dataset_version_id,
                ]
                + additional_args,
                input=input,
            )
            # Store the contents of any files created so they may be checked
            # later
            if file_paths_to_read:
                for file_path in file_paths_to_read:
                    with open(file_path, "r", encoding="utf-8") as file:
                        saved_file_data.append(file.read())

        return result, saved_file_data

    def test_upload_dataset_metadata(
        self,
    ):
        """Tests that the 'upload dataset-metadata' command works correctly"""

        # SETUP
        self.mock_cli_get_latest_dataset_metadata.return_value = TEST_DATASET_METADATA
        metadata = parse_dataset_metadata(TEST_DATASET_METADATA)

        # CALL
        result, _ = self.invoke_command(input="y")

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_cli_get_latest_dataset_metadata.assert_called_once_with(
            self.mock_session, self.dataset_version_id
        )
        self.mock_modify_dataset_metadata_for_upload.assert_called_once_with(
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
        self.mock_upload_dataset_metadata_version.assert_called_once_with(
            self.mock_session,
            dataset_id=metadata.dataset_id,
            version_id=self.dataset_version_id,
            metadata=self.mock_modify_dataset_metadata_for_upload.return_value,
            json=False,
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
    ):
        """Tests that the 'upload dataset-metadata' command works correctly
        with the --save option"""

        # SETUP
        self.mock_cli_get_latest_dataset_metadata.return_value = TEST_DATASET_METADATA
        self.mock_modify_dataset_metadata_for_upload.return_value = (
            TEST_DATASET_METADATA
        )
        metadata_save_path = "metadata_save_file.json"

        # CALL
        result, saved_file_data = self.invoke_command(
            additional_args=["--save", metadata_save_path],
            file_paths_to_read=[metadata_save_path],
        )

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_cli_get_latest_dataset_metadata.assert_called_once_with(
            self.mock_session, self.dataset_version_id
        )
        self.mock_modify_dataset_metadata_for_upload.assert_called_once_with(
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
            saved_file_data[0],
            json.dumps(TEST_DATASET_METADATA, indent=4, sort_keys=True),
        )
        self.mock_upload_dataset_metadata_version.assert_not_called()

        self.assertEqual(
            result.output, f"Saved existing dataset metadata to {metadata_save_path}\n"
        )
        self.assertEqual(result.exit_code, 0)

    def test_upload_dataset_metadata_with_metadata_and_all_optional_modifications(
        self,
    ):
        """Tests that the 'upload dataset-metadata' command works correctly
        when a path to metadata and a version message is given"""

        # SETUP
        metadata_path = "metadata.json"
        self.mock_cli_get_latest_dataset_metadata.return_value = TEST_DATASET_METADATA
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

        additional_args = add_dataset_metadata_common_options(
            args=[
                "--metadata",
                metadata_path,
            ],
            all_optional=True,
            dictionary=options,
            **options,
        )

        # CALL
        result, _ = self.invoke_command(
            file_paths=[metadata_path], additional_args=additional_args, input="y"
        )

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_cli_get_latest_dataset_metadata.assert_called_once_with(
            self.mock_session, self.dataset_version_id
        )
        self.mock_modify_dataset_metadata_for_upload.assert_called_once_with(
            existing_metadata=TEST_DATASET_METADATA,
            metadata_path=Path(metadata_path),
            **options,
        )
        self.mock_upload_dataset_metadata_version.assert_called_once_with(
            self.mock_session,
            dataset_id=metadata.dataset_id,
            version_id=self.dataset_version_id,
            metadata=self.mock_modify_dataset_metadata_for_upload.return_value,
            json=False,
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
    ):
        """Tests that the 'upload dataset-metadata' command works correctly when
        given a -y flag to skip the confirmation"""

        # SETUP
        self.mock_cli_get_latest_dataset_metadata.return_value = TEST_DATASET_METADATA
        metadata = parse_dataset_metadata(TEST_DATASET_METADATA)

        # CALL
        result, _ = self.invoke_command(additional_args=["-y"])

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_cli_get_latest_dataset_metadata.assert_called_once_with(
            self.mock_session, self.dataset_version_id
        )
        self.mock_modify_dataset_metadata_for_upload.assert_called_once_with(
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
        self.mock_upload_dataset_metadata_version.assert_called_once_with(
            self.mock_session,
            dataset_id=metadata.dataset_id,
            version_id=self.dataset_version_id,
            metadata=self.mock_modify_dataset_metadata_for_upload.return_value,
            json=False,
        )

        self.assertEqual(result.output, "")
        self.assertEqual(result.exit_code, 0)

    def test_upload_dataset_metadata_json(
        self,
    ):
        """Tests that the 'upload dataset-metadata' command works correctly
        when given a --json flag"""

        # SETUP
        self.mock_cli_get_latest_dataset_metadata.return_value = TEST_DATASET_METADATA
        metadata = parse_dataset_metadata(TEST_DATASET_METADATA)

        # CALL
        result, _ = self.invoke_command(additional_args=["--json"])

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_cli_get_latest_dataset_metadata.assert_called_once_with(
            self.mock_session, self.dataset_version_id
        )
        self.mock_modify_dataset_metadata_for_upload.assert_called_once_with(
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
        self.mock_upload_dataset_metadata_version.assert_called_once_with(
            self.mock_session,
            dataset_id=metadata.dataset_id,
            version_id=self.dataset_version_id,
            metadata=self.mock_modify_dataset_metadata_for_upload.return_value,
            json=True,
        )

        self.assertEqual(result.output, "")
        self.assertEqual(result.exit_code, 0)

    def test_upload_metadata_cancel(
        self,
    ):
        """Tests that the 'upload dataset-metadata' command can be canceled"""

        # SETUP
        self.mock_cli_get_latest_dataset_metadata.return_value = TEST_DATASET_METADATA
        metadata = parse_dataset_metadata(TEST_DATASET_METADATA)

        # CALL
        result, _ = self.invoke_command(input="n")

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_cli_get_latest_dataset_metadata.assert_called_once_with(
            self.mock_session, self.dataset_version_id
        )
        self.mock_modify_dataset_metadata_for_upload.assert_called_once_with(
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
        self.mock_upload_dataset_metadata_version.assert_not_called()

        self.assertEqual(
            result.output,
            f"Dataset Title: {metadata.title}\n"
            f"Dataset ID: {metadata.dataset_id}\n"
            f"Dataset Version ID: {metadata.version_id}\n"
            "Confirm metadata upload? [y/N]: n\n"
            "Aborted!\n",
        )
        self.assertEqual(result.exit_code, 1)


class TestUploadWorkflow(TestCase):
    """Test class to test the upload workflow commands"""

    def setUp(self) -> None:
        super().setUp()

        self.definition_path = "test_definition.json"
        self.version_message = "Initial version"

        self.mock_DAFNISession = patch("dafni_cli.commands.upload.DAFNISession").start()
        self.mock_session = MagicMock()
        self.mock_DAFNISession.return_value = self.mock_session

        self.mock_upload_workflow = patch(
            "dafni_cli.commands.upload.upload_workflow"
        ).start()

    def invoke_command(
        self,
        additional_args: Optional[List[str]] = None,
        input: Optional[str] = None,
    ) -> Result:
        """Invokes the upload dataset command with all required arguments provided

        Args:
            additional_args (Optional[List[str]]): Any additional parameters to
                                                     add
            input (Optional[str]): 'input' to pass to CliRunner's invoke function
        """
        if additional_args is None:
            additional_args = []

        runner = CliRunner()

        with runner.isolated_filesystem():
            with open(self.definition_path, "w", encoding="utf-8") as file:
                file.write("{}")
            result = runner.invoke(
                upload.upload,
                [
                    "workflow",
                    self.definition_path,
                    "--version-message",
                    self.version_message,
                ]
                + additional_args,
                input=input,
            )
        return result

    def test_upload_workflow(
        self,
    ):
        """Tests that the 'upload workflow' command works correctly when
        no parent is given"""

        # CALL
        result = self.invoke_command(input="y")

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_upload_workflow.assert_called_once_with(
            self.mock_session,
            Path(self.definition_path),
            self.version_message,
            None,
            json=False,
        )

        self.assertEqual(
            result.output,
            f"Workflow definition file path: {self.definition_path}\n"
            f"Version message: {self.version_message}\n"
            "No parent workflow: new workflow to be created\n"
            "Confirm workflow upload? [y/N]: y\n",
        )
        self.assertEqual(result.exit_code, 0)

    def test_upload_workflow_with_parent(
        self,
    ):
        """Tests that the 'upload workflow' command works correctly when
        a parent is given"""

        # SETUP
        parent_id = "parent-id"

        # CALL
        result = self.invoke_command(
            additional_args=["--parent-id", parent_id], input="y"
        )

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_upload_workflow.assert_called_once_with(
            self.mock_session,
            Path("test_definition.json"),
            self.version_message,
            parent_id,
            json=False,
        )

        self.assertEqual(
            result.output,
            f"Workflow definition file path: {self.definition_path}\n"
            f"Version message: {self.version_message}\n"
            f"Parent workflow ID: {parent_id}\n"
            "Confirm workflow upload? [y/N]: y\n",
        )
        self.assertEqual(result.exit_code, 0)

    def test_upload_workflow_skipping_confirmation(
        self,
    ):
        """Tests that the 'upload workflow' command works correctly when
        given a -y flag to skip the confirmation"""

        # CALL
        result = self.invoke_command(additional_args=["-y"])

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_upload_workflow.assert_called_once_with(
            self.mock_session,
            Path(self.definition_path),
            self.version_message,
            None,
            json=False,
        )

        self.assertEqual(result.output, "")
        self.assertEqual(result.exit_code, 0)

    def test_upload_workflow_json(
        self,
    ):
        """Tests that the 'upload workflow' command works correctly when
        given a --json flag"""

        # CALL
        result = self.invoke_command(additional_args=["--json"])

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_upload_workflow.assert_called_once_with(
            self.mock_session,
            Path(self.definition_path),
            self.version_message,
            None,
            json=True,
        )

        self.assertEqual(result.output, "")
        self.assertEqual(result.exit_code, 0)

    def test_upload_workflow_cancel(
        self,
    ):
        """Tests that the 'upload workflow' command can be canceled"""

        # CALL
        result = self.invoke_command(input="n")

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_upload_workflow.assert_not_called()

        self.assertEqual(
            result.output,
            f"Workflow definition file path: {self.definition_path}\n"
            f"Version message: {self.version_message}\n"
            "No parent workflow: new workflow to be created\n"
            "Confirm workflow upload? [y/N]: n\n"
            "Aborted!\n",
        )
        self.assertEqual(result.exit_code, 1)


class TestUploadWorkflowParameterSet(TestCase):
    """Test class to test the upload workflow-parameter-set commands"""

    def setUp(self) -> None:
        super().setUp()

        self.definition_path = "test_definition.json"

        self.mock_DAFNISession = patch("dafni_cli.commands.upload.DAFNISession").start()
        self.mock_session = MagicMock()
        self.mock_DAFNISession.return_value = self.mock_session

        self.mock_upload_parameter_set = patch(
            "dafni_cli.commands.upload.upload_parameter_set"
        ).start()

        self.addCleanup(patch.stopall)

    def invoke_command(
        self,
        additional_args: Optional[List[str]] = None,
        input: Optional[str] = None,
    ) -> Result:
        """Invokes the upload workflow-parameter-srt command with all required
        arguments provided

        Args:
            additional_args (Optional[List[str]]): Any additional parameters to
                                                   add
            input (Optional[str]): 'input' to pass to CliRunner's invoke function
        """
        if additional_args is None:
            additional_args = []

        runner = CliRunner()

        with runner.isolated_filesystem():
            with open(self.definition_path, "w", encoding="utf-8") as file:
                file.write("{}")
            result = runner.invoke(
                upload.upload,
                [
                    "workflow-parameter-set",
                    self.definition_path,
                ]
                + additional_args,
                input=input,
            )
        return result

    def test_upload_workflow_parameter_set(
        self,
    ):
        """Tests that the 'upload workflow-parameter-set' command works
        correctly"""

        # SETUP
        parameter_set_id = "parameter-set-id"
        self.mock_upload_parameter_set.return_value = {"id": parameter_set_id}

        # CALL
        result = self.invoke_command(input="y")

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_upload_parameter_set.assert_called_once_with(
            self.mock_session, Path(self.definition_path), json=False
        )

        self.assertEqual(
            result.output,
            f"Parameter set definition file path: {self.definition_path}\n"
            "Confirm parameter set upload? [y/N]: y\n",
        )
        self.assertEqual(result.exit_code, 0)

    def test_upload_workflow_parameter_set_skipping_confirmation(
        self,
    ):
        """Tests that the 'upload workflow-parameter-set' command works
        correctly when given a -y flag to skip the confirmation"""

        # CALL
        result = self.invoke_command(additional_args=["-y"])

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_upload_parameter_set.assert_called_once_with(
            self.mock_session, Path(self.definition_path), json=False
        )

        self.assertEqual(result.output, "")
        self.assertEqual(result.exit_code, 0)

    def test_upload_workflow_parameter_set_json(
        self,
    ):
        """Tests that the 'upload workflow-parameter-set' command works
        correctly when given a --json flag"""

        # SETUP
        parameter_set_id = "parameter-set-id"
        self.mock_upload_parameter_set.return_value = {"id": parameter_set_id}

        # CALL
        result = self.invoke_command(additional_args=["--json"])

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_upload_parameter_set.assert_called_once_with(
            self.mock_session, Path(self.definition_path), json=True
        )

        self.assertEqual(result.output, "")
        self.assertEqual(result.exit_code, 0)

    def test_upload_workflow_parameter_set_cancel(
        self,
    ):
        """Tests that the 'upload workflow-parameter-set' command can be canceled"""

        # CALL
        result = self.invoke_command(input="n")

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_upload_parameter_set.assert_not_called()

        self.assertEqual(
            result.output,
            f"Parameter set definition file path: {self.definition_path}\n"
            "Confirm parameter set upload? [y/N]: n\n"
            "Aborted!\n",
        )
        self.assertEqual(result.exit_code, 1)

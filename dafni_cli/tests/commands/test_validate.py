import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple
from unittest import TestCase
from unittest.mock import MagicMock, patch

from click.testing import CliRunner, Result

# from dafni_cli.commands import upload
from dafni_cli.commands import validate
from dafni_cli.datasets.dataset_metadata import parse_dataset_metadata
from dafni_cli.tests.commands.test_options import add_dataset_metadata_common_options
from dafni_cli.tests.fixtures.dataset_metadata import TEST_DATASET_METADATA


@patch("dafni_cli.commands.validate.DAFNISession")
class TestValidate(TestCase):
    """Test class to test the validate command"""

    @patch("dafni_cli.commands.validate.validate_metadata")
    def test_session_retrieved_and_set_on_context(self, _, mock_DAFNISession):
        """Tests that the session is created in the click context"""
        # SETUP
        session = MagicMock()
        mock_DAFNISession.return_value = session
        runner = CliRunner()
        ctx = {}

        # CALL
        with runner.isolated_filesystem():
            with open("test_metadata.json", "w", encoding="utf-8") as f:
                f.write("{}")
            result = runner.invoke(
                validate.validate,
                ["dataset-metadata", "test_metadata.json"],
                input="y",
                obj=ctx,
            )

        # ASSERT
        mock_DAFNISession.assert_called_once()

        self.assertEqual(ctx["session"], session)
        self.assertEqual(result.exit_code, 0)

class TestValidateDatasetMetadata(TestCase):
    """Test class to test the upload dataset commands"""

    def setUp(self) -> None:
        super().setUp()

        self.metadata_path = "test_metadata.json"

        self.mock_DAFNISession = patch("dafni_cli.commands.validate.DAFNISession").start()
        self.mock_session = MagicMock()
        self.mock_DAFNISession.return_value = self.mock_session

        self.mock_validate_metadata = patch(
            "dafni_cli.commands.validate.validate_metadata"
        ).start()

        self.addCleanup(patch.stopall)

    def invoke_command(
        self,
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
            result = runner.invoke(
                validate.validate,
                [
                    "dataset-metadata",
                    self.metadata_path,
                ]
                + additional_args,
                input=input,
            )
        return result

    def test_validate_metadata(
        self,
    ):
        """Tests that the 'validate_metadata' command works correctly"""

        # SETUP

        # CALL
        result = self.invoke_command(input="y")

        # ASSERT
        self.mock_DAFNISession.assert_called_once()
        self.mock_validate_metadata.assert_called_once_with(
            self.mock_session, {}
        )

        self.assertEqual(
            result.output,
            f"metadata path: {self.metadata_path}\n"
            "Confirm metadata validation check? [y/N]: y\n"
            "Validating metadata\n"
            "Metadata validation successfull\n",
        )
        self.assertEqual(result.exit_code, 0)

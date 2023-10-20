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

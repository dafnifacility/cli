import importlib
import json
from datetime import datetime
from pathlib import Path
from unittest import TestCase
from unittest.mock import ANY, patch

from click.testing import CliRunner

from dafni_cli.commands import create

from test.commands.test_optional import add_dataset_metadata_common_options


@patch("dafni_cli.commands.create.modify_dataset_metadata_for_upload")
class TestCreateDatasetMetadata(TestCase):
    """Test class to test the create dataset metadata command"""

    def test_with_required_values_only(
        self,
        mock_modify_dataset_metadata_for_upload,
    ):
        """Tests that the 'create dataset-metadata' command functions
        correctly when all required values are given"""

        # SETUP
        runner = CliRunner()
        metadata_path = "test_metadata.json"

        options = {
            "title": "Dataset title",
            "description": "Dataset description",
            "identifiers": None,
            "subject": "Farming",
            "themes": None,
            "language": "en",
            "keywords": ("test", "another_test"),
            "standard": None,
            "start_date": None,
            "end_date": None,
            "organisation": ("organisation_name", "organisation_url"),
            "people": None,
            "created_date": None,
            "update_frequency": None,
            "publisher": None,
            "contact": ("contact_point_name", "contact_point_email_address"),
            "license": None,
            "rights": None,
            "version_message": "Some version message",
        }

        template_metadata = json.loads(
            importlib.resources.read_text(
                "dafni_cli.data", "dataset_metadata_template.json"
            )
        )
        mock_modify_dataset_metadata_for_upload.return_value = template_metadata

        args = add_dataset_metadata_common_options(
            args=[
                "dataset-metadata",
                metadata_path,
            ],
            all_optional=False,
            dictionary=options,
            **options,
        )

        # CALL
        with runner.isolated_filesystem():
            result = runner.invoke(create.create, args)

            # ASSERT
            mock_modify_dataset_metadata_for_upload.assert_called_once_with(
                existing_metadata=template_metadata,
                **options,
            )

            self.assertEqual(
                result.output,
                f"Saved dataset metadata to {metadata_path}\n",
            )

            self.assertTrue(Path(metadata_path).is_file())

            self.assertEqual(result.exit_code, 0)

    def test_with_all_optional_values(
        self,
        mock_modify_dataset_metadata_for_upload,
    ):
        """Tests that the 'create dataset-metadata' command functions
        correctly when all optional values are given"""

        # SETUP
        runner = CliRunner()
        metadata_path = "test_metadata.json"

        options = {
            "title": "Dataset title",
            "description": "Dataset description",
            "identifiers": ("test", "identifiers"),
            "subject": "Farming",
            "themes": ("Buildings", "Hydrology"),
            "language": "en",
            "keywords": ("test", "another_test"),
            "standard": ("standard_name", "standard_url"),
            "start_date": datetime(2022, 6, 28),
            "end_date": datetime(2022, 8, 10),
            "organisation": ("organisation_name", "organisation_url"),
            "people": (
                ("person-1-name", "person-1-id"),
                ("person-2-name", "person-2-id"),
            ),
            "created_date": datetime(2023, 6, 14),
            "update_frequency": "Annual",
            "publisher": ("publisher_name", "publisher_id"),
            "contact": ("contact_point_name", "contact_point_email_address"),
            "license": "some/license/url",
            "rights": "Some rights",
            "version_message": "Some version message",
        }

        template_metadata = json.loads(
            importlib.resources.read_text(
                "dafni_cli.data", "dataset_metadata_template.json"
            )
        )
        mock_modify_dataset_metadata_for_upload.return_value = template_metadata

        args = add_dataset_metadata_common_options(
            args=[
                "dataset-metadata",
                metadata_path,
            ],
            all_optional=False,
            dictionary=options,
            **options,
        )

        # CALL
        with runner.isolated_filesystem():
            result = runner.invoke(create.create, args)

            # ASSERT
            mock_modify_dataset_metadata_for_upload.assert_called_once_with(
                existing_metadata=template_metadata, **options
            )

            self.assertEqual(
                result.output,
                f"Saved dataset metadata to {metadata_path}\n",
            )

            self.assertTrue(Path(metadata_path).is_file())

            self.assertEqual(result.exit_code, 0)

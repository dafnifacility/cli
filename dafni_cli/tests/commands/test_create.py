import importlib
import json
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from click.testing import CliRunner

from dafni_cli.commands import create
from dafni_cli.tests.commands.test_options import add_dataset_metadata_common_options


@patch("dafni_cli.commands.create.modify_dataset_metadata_for_upload")
class TestCreateDatasetMetadata(TestCase):
    """Test class to test the create dataset metadata command"""

    @contextmanager
    def _test_create_dataset_metadata(
        self,
        mock_modify_dataset_metadata_for_upload,
        metadata_path: str,
        options: dict,
        should_fail: bool,
    ):
        """Helper function that runs the create dataset metadata command in an
        isolated filesystem given a set of options and verifies that the
        modify_dataset_metadata_for_upload function was called correctly

        Args:
            mock_modify_dataset_metadata_for_upload: Mock
                                modify_dataset_metadata_for_upload function
            metadata_path (str): Path to create the metadata file
            options (dict): Dictionary of optional arguments for the command
            should_fail (bool): Whether the command should fail or not - if
                    True will assert modify_dataset_metadata_for_upload was
                    not called

        """

        # SETUP
        runner = CliRunner()

        template_metadata = json.loads(
            importlib.resources.files("dafni_cli.data")
            .joinpath("dataset_metadata_template.json")
            .read_text(encoding="utf-8")
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

        with runner.isolated_filesystem():
            # CALL
            result = runner.invoke(create.create, args)

            # ASSERT
            if should_fail:
                mock_modify_dataset_metadata_for_upload.assert_not_called()
            else:
                mock_modify_dataset_metadata_for_upload.assert_called_once_with(
                    existing_metadata=template_metadata,
                    **options,
                )

            yield result

    def test_with_required_values_only(
        self,
        mock_modify_dataset_metadata_for_upload,
    ):
        """Tests that the 'create dataset-metadata' command functions
        correctly when all required values are given"""

        # SETUP
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
            "organisation": ("organisation_name", "https://www.organisaton-url.com/"),
            "people": None,
            "created_date": None,
            "update_frequency": None,
            "publisher": None,
            "contact": ("contact_point_name", "test@example.com"),
            "license": None,
            "rights": None,
            "version_message": "Some version message",
        }

        # CALL
        with self._test_create_dataset_metadata(
            mock_modify_dataset_metadata_for_upload,
            metadata_path,
            options,
            should_fail=False,
        ) as result:
            # ASSERT
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
        metadata_path = "test_metadata.json"

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

        # CALL
        with self._test_create_dataset_metadata(
            mock_modify_dataset_metadata_for_upload,
            metadata_path,
            options,
            should_fail=False,
        ) as result:
            # ASSERT
            self.assertEqual(
                result.output,
                f"Saved dataset metadata to {metadata_path}\n",
            )

            self.assertTrue(Path(metadata_path).is_file())

            self.assertEqual(result.exit_code, 0)

    def test_with_empty_standard_name(
        self,
        mock_modify_dataset_metadata_for_upload,
    ):
        """Tests that the 'create dataset-metadata' command functions
        when a standard's name is given as an empty string"""

        # SETUP
        metadata_path = "test_metadata.json"

        options = {
            "title": "Dataset title",
            "description": "Dataset description",
            "identifiers": None,
            "subject": "Farming",
            "themes": None,
            "language": "en",
            "keywords": ("test", "another_test"),
            "standard": ("", "https://www.standard-url.com/"),
            "start_date": None,
            "end_date": None,
            "organisation": ("organisation_name", "https://www.organisaton-url.com/"),
            "people": None,
            "created_date": None,
            "update_frequency": None,
            "publisher": None,
            "contact": ("contact_point_name", "test@example.com"),
            "license": None,
            "rights": None,
            "version_message": "Some version message",
        }

        # CALL
        with self._test_create_dataset_metadata(
            mock_modify_dataset_metadata_for_upload,
            metadata_path,
            options,
            should_fail=False,
        ) as result:
            # ASSERT
            self.assertEqual(
                result.output,
                f"Saved dataset metadata to {metadata_path}\n",
            )

            self.assertTrue(Path(metadata_path).is_file())

            self.assertEqual(result.exit_code, 0)

    def test_with_empty_standard_url(
        self,
        mock_modify_dataset_metadata_for_upload,
    ):
        """Tests that the 'create dataset-metadata' command functions
        when a standard's url is given as an empty string"""

        # SETUP
        metadata_path = "test_metadata.json"

        options = {
            "title": "Dataset title",
            "description": "Dataset description",
            "identifiers": None,
            "subject": "Farming",
            "themes": None,
            "language": "en",
            "keywords": ("test", "another_test"),
            "standard": ("standard_name", ""),
            "start_date": None,
            "end_date": None,
            "organisation": ("organisation_name", "https://www.organisaton-url.com/"),
            "people": None,
            "created_date": None,
            "update_frequency": None,
            "publisher": None,
            "contact": ("contact_point_name", "test@example.com"),
            "license": None,
            "rights": None,
            "version_message": "Some version message",
        }

        # CALL
        with self._test_create_dataset_metadata(
            mock_modify_dataset_metadata_for_upload,
            metadata_path,
            options,
            should_fail=False,
        ) as result:
            # ASSERT
            self.assertEqual(
                result.output,
                f"Saved dataset metadata to {metadata_path}\n",
            )

            self.assertTrue(Path(metadata_path).is_file())

            self.assertEqual(result.exit_code, 0)

    def test_with_invalid_standard_url(
        self,
        mock_modify_dataset_metadata_for_upload,
    ):
        """Tests that the 'create dataset-metadata' command fails
        when a standard's url is invalid - this by extension tests all
        such URLs using the URLParamType"""

        # SETUP
        metadata_path = "test_metadata.json"

        options = {
            "title": "Dataset title",
            "description": "Dataset description",
            "identifiers": None,
            "subject": "Farming",
            "themes": None,
            "language": "en",
            "keywords": ("test", "another_test"),
            "standard": ("standard_name", "invalid url"),
            "start_date": None,
            "end_date": None,
            "organisation": ("organisation_name", "https://www.organisaton-url.com/"),
            "people": None,
            "created_date": None,
            "update_frequency": None,
            "publisher": None,
            "contact": ("contact_point_name", "test@example.com"),
            "license": None,
            "rights": None,
            "version_message": "Some version message",
        }

        # CALL
        with self._test_create_dataset_metadata(
            mock_modify_dataset_metadata_for_upload,
            metadata_path,
            options,
            should_fail=True,
        ) as result:
            # ASSERT
            self.assertEqual(
                result.output,
                "Usage: create dataset-metadata [OPTIONS] SAVE_PATH\n"
                "Try 'create dataset-metadata --help' for help.\n\n"
                "Error: Invalid value for '--standard': 'invalid url' is not a valid URL\n",
            )

            self.assertEqual(result.exit_code, 2)

    def test_with_empty_contact_email(
        self,
        mock_modify_dataset_metadata_for_upload,
    ):
        """Tests that the 'create dataset-metadata' command
        fails when the contact email is an empty string (or by extension
        invalid)"""

        # SETUP
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
            "organisation": ("organisation_name", "https://www.organisaton-url.com/"),
            "people": None,
            "created_date": None,
            "update_frequency": None,
            "publisher": None,
            "contact": ("contact_point_name", ""),
            "license": None,
            "rights": None,
            "version_message": "Some version message",
        }

        # CALL
        with self._test_create_dataset_metadata(
            mock_modify_dataset_metadata_for_upload,
            metadata_path,
            options,
            should_fail=True,
        ) as result:
            # ASSERT
            self.assertEqual(
                result.output,
                "Usage: create dataset-metadata [OPTIONS] SAVE_PATH\n"
                "Try 'create dataset-metadata --help' for help.\n\n"
                "Error: Invalid value for '--contact': '' is not a valid email address\n",
            )

            self.assertEqual(result.exit_code, 2)

    def test_with_empty_person_name(
        self,
        mock_modify_dataset_metadata_for_upload,
    ):
        """Tests that the 'create dataset-metadata' command functions
        when a person's name is given as an empty string"""

        # SETUP
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
            "organisation": ("organisation_name", "https://www.organisaton-url.com/"),
            "people": (("", "http://www.person-1.com/"),),
            "created_date": None,
            "update_frequency": None,
            "publisher": None,
            "contact": ("contact_point_name", "test@example.com"),
            "license": None,
            "rights": None,
            "version_message": "Some version message",
        }

        # CALL
        with self._test_create_dataset_metadata(
            mock_modify_dataset_metadata_for_upload,
            metadata_path,
            options,
            should_fail=False,
        ) as result:
            # ASSERT
            self.assertEqual(
                result.output,
                f"Saved dataset metadata to {metadata_path}\n",
            )

            self.assertTrue(Path(metadata_path).is_file())

            self.assertEqual(result.exit_code, 0)

    def test_with_empty_person_id(
        self,
        mock_modify_dataset_metadata_for_upload,
    ):
        """Tests that the 'create dataset-metadata' command functions
        when a person's id is given as an empty string"""

        # SETUP
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
            "organisation": ("organisation_name", "https://www.organisaton-url.com/"),
            "people": (("person-1-name", ""),),
            "created_date": None,
            "update_frequency": None,
            "publisher": None,
            "contact": ("contact_point_name", "test@example.com"),
            "license": None,
            "rights": None,
            "version_message": "Some version message",
        }

        # CALL
        with self._test_create_dataset_metadata(
            mock_modify_dataset_metadata_for_upload,
            metadata_path,
            options,
            should_fail=False,
        ) as result:
            # ASSERT
            self.assertEqual(
                result.output,
                f"Saved dataset metadata to {metadata_path}\n",
            )

            self.assertTrue(Path(metadata_path).is_file())

            self.assertEqual(result.exit_code, 0)

    def test_with_empty_publisher_name(
        self,
        mock_modify_dataset_metadata_for_upload,
    ):
        """Tests that the 'create dataset-metadata' command functions
        when a publisher's name is given as an empty string"""

        # SETUP
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
            "organisation": ("organisation_name", "https://www.organisaton-url.com/"),
            "people": None,
            "created_date": None,
            "update_frequency": None,
            "publisher": (None, "https://www.publisher-url.com/"),
            "contact": ("contact_point_name", "test@example.com"),
            "license": None,
            "rights": None,
            "version_message": "Some version message",
        }

        # CALL
        with self._test_create_dataset_metadata(
            mock_modify_dataset_metadata_for_upload,
            metadata_path,
            options,
            should_fail=False,
        ) as result:
            # ASSERT
            self.assertEqual(
                result.output,
                f"Saved dataset metadata to {metadata_path}\n",
            )

            self.assertTrue(Path(metadata_path).is_file())

            self.assertEqual(result.exit_code, 0)

    def test_with_empty_publisher_id(
        self,
        mock_modify_dataset_metadata_for_upload,
    ):
        """Tests that the 'create dataset-metadata' command functions
        when a publishers's id is given as an empty string"""

        # SETUP
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
            "organisation": ("organisation_name", "https://www.organisaton-url.com/"),
            "people": None,
            "created_date": None,
            "update_frequency": None,
            "publisher": ("publisher_name", None),
            "contact": ("contact_point_name", "test@example.com"),
            "license": None,
            "rights": None,
            "version_message": "Some version message",
        }

        # CALL
        with self._test_create_dataset_metadata(
            mock_modify_dataset_metadata_for_upload,
            metadata_path,
            options,
            should_fail=False,
        ) as result:
            # ASSERT
            self.assertEqual(
                result.output,
                f"Saved dataset metadata to {metadata_path}\n",
            )

            self.assertTrue(Path(metadata_path).is_file())

            self.assertEqual(result.exit_code, 0)

    def test_with_empty_license(
        self,
        mock_modify_dataset_metadata_for_upload,
    ):
        """Tests that the 'create dataset-metadata' command
        fails when license is given as an empty string"""

        # SETUP
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
            "organisation": ("organisation_name", "https://www.organisaton-url.com/"),
            "people": None,
            "created_date": None,
            "update_frequency": None,
            "publisher": None,
            "contact": ("contact_point_name", "test@example.com"),
            "license": "",
            "rights": None,
            "version_message": "Some version message",
        }

        # CALL
        with self._test_create_dataset_metadata(
            mock_modify_dataset_metadata_for_upload,
            metadata_path,
            options,
            should_fail=True,
        ) as result:
            # ASSERT
            self.assertEqual(
                result.output,
                "Usage: create dataset-metadata [OPTIONS] SAVE_PATH\n"
                "Try 'create dataset-metadata --help' for help.\n\n"
                "Error: Invalid value for '--license': Value cannot be an empty string\n",
            )

            self.assertEqual(result.exit_code, 2)

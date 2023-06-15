import importlib
import json
from datetime import datetime
from pathlib import Path
from unittest import TestCase
from unittest.mock import ANY, patch

from click.testing import CliRunner

from dafni_cli.commands import create
from dafni_cli.consts import DATE_INPUT_FORMAT


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
        title = "Dataset title"
        description = "Dataset description"
        subject = "Farming"
        language = "en"
        keywords = ("test", "another_test")
        organisation = ("organisation_name", "organisation_url")
        contact = ("contact_point_name", "contact_point_email_address")
        version_message = "Some version message"

        template_metadata = json.loads(
            importlib.resources.read_text(
                "dafni_cli.data", "dataset_metadata_template.json"
            )
        )
        mock_modify_dataset_metadata_for_upload.return_value = template_metadata

        args = [
            "dataset-metadata",
            metadata_path,
            "--title",
            title,
            "--description",
            description,
            "--subject",
            subject,
            "--language",
            language,
        ]
        for keyword in keywords:
            args.extend(["--keyword", keyword])
        args.extend(
            [
                "--organisation",
                organisation[0],
                organisation[1],
                "--contact",
                contact[0],
                contact[1],
                "--version-message",
                version_message,
            ]
        )

        # CALL
        with runner.isolated_filesystem():
            result = runner.invoke(create.create, args)

            # ASSERT
            mock_modify_dataset_metadata_for_upload.assert_called_once_with(
                existing_metadata=template_metadata,
                title=title,
                description=description,
                subject=subject,
                identifiers=None,
                themes=None,
                language=language,
                keywords=keywords,
                standard=None,
                start_date=None,
                end_date=None,
                organisation=organisation,
                people=None,
                created_date=ANY,
                update_frequency=None,
                publisher=None,
                contact=contact,
                license="https://creativecommons.org/licences/by/4.0/",
                rights=None,
                version_message=version_message,
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
        title = "Dataset title"
        description = "Dataset description"
        identifiers = ("test", "identifiers")
        subject = "Farming"
        themes = ("Buildings", "Hydrology")
        language = "en"
        keywords = ("test", "another_test")
        standard = ("standard_name", "standard_url")
        start_date = datetime(2022, 6, 28)
        end_date = datetime(2022, 8, 10)
        organisation = ("organisation_name", "organisation_url")
        people = (("person-1-name", "person-1-id"), ("person-2-name", "person-2-id"))
        created_date = datetime(2023, 6, 14)
        update_frequency = "Annual"
        publisher = ("publisher_name", "publisher_id")
        contact = ("contact_point_name", "contact_point_email_address")
        license = "some/license/url"
        rights = "Some rights"
        version_message = "Some version message"

        template_metadata = json.loads(
            importlib.resources.read_text(
                "dafni_cli.data", "dataset_metadata_template.json"
            )
        )
        mock_modify_dataset_metadata_for_upload.return_value = template_metadata

        args = [
            "dataset-metadata",
            metadata_path,
            "--title",
            title,
            "--description",
            description,
        ]
        for identifier in identifiers:
            args.extend(["--identifier", identifier])
        args.extend(
            [
                "--subject",
                subject,
            ]
        )
        for theme in themes:
            args.extend(["--theme", theme])
        args.extend(
            [
                "--language",
                language,
            ]
        )
        for keyword in keywords:
            args.extend(["--keyword", keyword])
        args.extend(
            [
                "--standard",
                standard[0],
                standard[1],
                "--start-date",
                start_date.strftime(DATE_INPUT_FORMAT),
                "--end-date",
                end_date.strftime(DATE_INPUT_FORMAT),
                "--organisation",
                organisation[0],
                organisation[1],
            ]
        )
        for person in people:
            args.extend(["--person", person[0], person[1]])
        args.extend(
            [
                "--created-date",
                created_date.strftime(DATE_INPUT_FORMAT),
                "--update-frequency",
                update_frequency,
                "--publisher",
                publisher[0],
                publisher[1],
                "--contact",
                contact[0],
                contact[1],
                "--license",
                license,
                "--rights",
                rights,
                "--version-message",
                version_message,
            ]
        )

        # CALL
        with runner.isolated_filesystem():
            result = runner.invoke(create.create, args)

            # ASSERT
            mock_modify_dataset_metadata_for_upload.assert_called_once_with(
                existing_metadata=template_metadata,
                title=title,
                description=description,
                subject=subject,
                identifiers=identifiers,
                themes=themes,
                language=language,
                keywords=keywords,
                standard=standard,
                start_date=start_date,
                end_date=end_date,
                organisation=organisation,
                people=people,
                created_date=created_date,
                update_frequency=update_frequency,
                publisher=publisher,
                contact=contact,
                license=license,
                rights=rights,
                version_message=version_message,
            )

            self.assertEqual(
                result.output,
                f"Saved dataset metadata to {metadata_path}\n",
            )

            self.assertTrue(Path(metadata_path).is_file())

            self.assertEqual(result.exit_code, 0)

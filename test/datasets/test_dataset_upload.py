import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, call, mock_open, patch

from requests import HTTPError

from dafni_cli.api.exceptions import DAFNIError
from dafni_cli.datasets import dataset_upload
from dafni_cli.datasets.dataset_metadata import (
    DATASET_METADATA_SUBJECTS,
    DATASET_METADATA_THEMES,
    DATASET_METADATA_UPDATE_FREQUENCIES,
)

from test.fixtures.dataset_metadata import TEST_DATASET_METADATA


class TestRemoveDatasetMetadataInvalidForUpload(TestCase):
    """Test class to test remove_dataset_metadata_invalid_for_upload works as
    expected"""

    def test_remove_dataset_metadata_invalid_for_upload(self):
        """Tests that remove_dataset_metadata_invalid_for_upload works as expected"""

        # SETUP
        original_metadata = deepcopy(TEST_DATASET_METADATA)
        metadata = deepcopy(original_metadata)

        # CALL
        dataset_upload.remove_dataset_metadata_invalid_for_upload(metadata)

        # ASSERT

        # Remove all keys that are present in the original, and check the only
        # ones left are the invalid ones
        for key in metadata.keys():
            del original_metadata[key]

        self.assertCountEqual(
            original_metadata.keys(), dataset_upload.METADATA_KEYS_INVALID_FOR_UPLOAD
        )


MOCK_DEFINITION_DATA = {"version_message": "existing_message"}
MOCK_DEFINITION_FILE = json.dumps(MOCK_DEFINITION_DATA)


@patch("dafni_cli.datasets.dataset_upload.remove_dataset_metadata_invalid_for_upload")
@patch("builtins.open", new_callable=mock_open, read_data=MOCK_DEFINITION_FILE)
class TestModifyDatasetMetadataForUpload(TestCase):
    """Test class to test modify_dataset_metadata_for_upload works as
    expected"""

    def test_with_only_existing_metadata(self, mock_open, mock_remove_invalid):
        """Tests that calling the function with only the existing metadata,
        returns the metadata with invalid parameters removed"""

        # SETUP
        metadata = deepcopy(TEST_DATASET_METADATA)

        # CALL
        result = dataset_upload.modify_dataset_metadata_for_upload(metadata, None, None)

        # ASSERT
        mock_open.assert_not_called()
        mock_remove_invalid.assert_called_once_with(metadata)
        self.assertEqual(result, TEST_DATASET_METADATA)

    def test_with_definition_path(self, mock_open, mock_remove_invalid):
        """Tests that calling the function with a definition path loads
        existing metadata from a file and returns it while deleting any
        invalid fields for upload"""

        # SETUP
        metadata = TEST_DATASET_METADATA
        definition_path = Path("some_definition_path")

        # CALL
        result = dataset_upload.modify_dataset_metadata_for_upload(
            metadata, definition_path, None
        )

        # ASSERT
        mock_open.assert_called_once_with(definition_path, "r", encoding="utf-8")
        mock_remove_invalid.assert_called_once_with(MOCK_DEFINITION_DATA)
        self.assertEqual(result, MOCK_DEFINITION_DATA)

    def test_with_all_optional_values(self, mock_open, mock_remove_invalid):
        """Tests that calling the function all parameters given replaces
        them in the returned metadata"""

        # SETUP
        metadata = TEST_DATASET_METADATA
        title = "New title"
        description = "New description"
        identifiers = ("some", "identifiers")
        subject = "Environment"
        themes = ("Addresses", "Geology")
        language = "new_language"
        keywords = ("some", "keywords")
        standard = ("standard_name", "standard_url")
        start_date = datetime(2023, 1, 10)
        end_date = datetime(2023, 4, 10)
        organisation = ("organisation_name", "organisation_id")
        people = (("person_1", "person_1_id"), ("person_2", "person_2_id"))
        created_date = datetime(2023, 5, 1)
        update_frequency = "Weekly"
        publisher = ("publisher_name", "publisher_id")
        contact = ("contact_name", "contact_email_address")
        license = "some/url"
        rights = "Rights"
        version_message = "new_version_message"

        # CALL
        result = dataset_upload.modify_dataset_metadata_for_upload(
            metadata,
            title=title,
            description=description,
            identifiers=identifiers,
            subject=subject,
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

        # ASSERT
        mock_open.assert_not_called()

        self.assertEqual(result["dct:title"], title)
        self.assertEqual(result["dct:description"], description)
        self.assertEqual(result["dct:identifier"], list(identifiers))
        self.assertEqual(result["dct:subject"], subject)
        self.assertEqual(result["dcat:theme"], list(themes))
        self.assertEqual(result["dct:language"], language)
        self.assertEqual(result["dcat:keyword"], list(keywords))
        self.assertEqual(result["dct:conformsTo"]["label"], standard[0])
        self.assertEqual(result["dct:conformsTo"]["@id"], standard[1])
        self.assertEqual(
            result["dct:PeriodOfTime"]["time:hasBeginning"], start_date.isoformat()
        )
        self.assertEqual(
            result["dct:PeriodOfTime"]["time:hasEnd"], end_date.isoformat()
        )
        result_organisation = result["dct:creator"][-(len(people) + 1)]
        self.assertEqual(
            result_organisation,
            {
                "@type": "foaf:Organization",
                "foaf:name": organisation[0],
                "@id": organisation[1],
                "internalID": None,
            },
        )
        for i, person in enumerate(people):
            result_person = result["dct:creator"][-(len(people) - i)]
            self.assertEqual(
                result_person,
                {
                    "@type": "foaf:Person",
                    "foaf:name": person[0],
                    "@id": person[1],
                    "internalID": None,
                },
            )
        self.assertEqual(result["dct:created"], created_date.isoformat())
        self.assertEqual(result["dct:accrualPeriodicity"], update_frequency)
        self.assertEqual(result["dct:publisher"]["foaf:name"], publisher[0])
        self.assertEqual(result["dct:publisher"]["@id"], publisher[1])
        self.assertEqual(result["dcat:contactPoint"]["vcard:fn"], contact[0])
        self.assertEqual(result["dcat:contactPoint"]["vcard:hasEmail"], contact[1])
        self.assertEqual(result["dct:license"]["@id"], license)
        self.assertEqual(result["dct:rights"], rights)

        # Since unittest is storing the reference it is further modified by
        # the version message so use result here instead of
        # metadata/TEST_DATASET_METADATA - also want to ensure the original
        # hasn't been accidentally modified so double check here
        mock_remove_invalid.assert_called_once_with(result)
        self.assertNotEqual(metadata["dafni_version_note"], version_message)
        self.assertEqual(result["dafni_version_note"], version_message)

    def test_with_invalid_subject_raises_error(self, mock_open, mock_remove_invalid):
        """Tests that calling the function when an invalid subject raises
        an appropriate ValueError"""

        # SETUP
        metadata = TEST_DATASET_METADATA

        # CALL & ASSERT
        with self.assertRaises(ValueError) as err:
            dataset_upload.modify_dataset_metadata_for_upload(
                metadata, subject="Invalid subject"
            )
        self.assertEqual(
            str(err.exception),
            f"Subject 'Invalid subject' is invalid, choose one from {''.join(DATASET_METADATA_SUBJECTS)}",
        )

    def test_with_invalid_theme_raises_error(self, mock_open, mock_remove_invalid):
        """Tests that calling the function when an invalid theme raises
        an appropriate ValueError"""

        # SETUP
        metadata = TEST_DATASET_METADATA

        # CALL & ASSERT
        with self.assertRaises(ValueError) as err:
            dataset_upload.modify_dataset_metadata_for_upload(
                metadata, themes=("Elevation", "Invalid theme")
            )
        self.assertEqual(
            str(err.exception),
            f"Theme 'Invalid theme' is invalid, choose one from {''.join(DATASET_METADATA_THEMES)}",
        )

    def test_with_invalid_update_frequency_raises_error(
        self, mock_open, mock_remove_invalid
    ):
        """Tests that calling the function when an invalid theme raises
        an appropriate ValueError"""

        # SETUP
        metadata = TEST_DATASET_METADATA

        # CALL & ASSERT
        with self.assertRaises(ValueError) as err:
            dataset_upload.modify_dataset_metadata_for_upload(
                metadata, update_frequency="Invalid frequency"
            )
        self.assertEqual(
            str(err.exception),
            f"Update frequency 'Invalid frequency' is invalid, choose one from {''.join(DATASET_METADATA_UPDATE_FREQUENCIES)}",
        )


@patch("dafni_cli.datasets.dataset_upload.click")
class TestDatasetUpload(TestCase):
    """Test class to test the functions in dataset_upload.py"""

    @patch("dafni_cli.datasets.dataset_upload.get_data_upload_urls")
    @patch("dafni_cli.datasets.dataset_upload.upload_file_to_minio")
    def test_upload_files(
        self,
        mock_upload_file_to_minio,
        mock_get_data_upload_urls,
        mock_click,
    ):
        """Tests that upload_files works as expected"""
        # SETUP
        session = MagicMock()
        temp_bucket_id = "some-temp-bucket"
        file_paths = [Path("file_1.txt"), Path("file_2.txt")]
        urls = [f"upload/url/{file_path.name}" for file_path in file_paths]
        upload_urls = {
            "URLs": {file_paths[idx].name: url for idx, url in enumerate(urls)}
        }

        mock_get_data_upload_urls.return_value = upload_urls

        # CALL
        dataset_upload.upload_files(session, temp_bucket_id, file_paths)

        # ASSERT
        mock_get_data_upload_urls.assert_called_once_with(
            session, temp_bucket_id, [file_path.name for file_path in file_paths]
        )
        mock_upload_file_to_minio.assert_has_calls(
            [call(session, url, file_paths[idx]) for idx, url in enumerate(urls)]
        )

        mock_click.echo.assert_has_calls(
            [
                call("Retrieving file upload URls"),
                call("Uploading files"),
            ]
        )

    @patch("dafni_cli.api.datasets_api.upload_dataset_metadata")
    def test_commit_metadata(
        self,
        mock_upload_dataset_metadata,
        mock_click,
    ):
        """Tests that _commit_metadata works as expected without a dataset_id"""
        # SETUP
        session = MagicMock()
        metadata = MOCK_DEFINITION_DATA
        temp_bucket_id = "some-temp-bucket"

        # CALL
        result = dataset_upload._commit_metadata(session, metadata, temp_bucket_id)

        # ASSERT
        mock_upload_dataset_metadata.assert_called_with(
            session, temp_bucket_id, metadata, dataset_id=None
        )

        mock_click.echo.assert_has_calls(
            [
                call("Uploading metadata file"),
            ]
        )
        self.assertEqual(result, mock_upload_dataset_metadata.return_value)

    @patch("dafni_cli.api.datasets_api.upload_dataset_metadata")
    def test_commit_metadata_with_dataset_id(
        self,
        mock_upload_dataset_metadata,
        mock_click,
    ):
        """Tests that _commit_metadata works as expected with a dataset_id"""
        # SETUP
        session = MagicMock()
        metadata = MOCK_DEFINITION_DATA
        temp_bucket_id = "some-temp-bucket"
        dataset_id = "some-dataset-id"

        # CALL
        result = dataset_upload._commit_metadata(
            session, metadata, temp_bucket_id, dataset_id=dataset_id
        )

        # ASSERT
        mock_upload_dataset_metadata.assert_called_with(
            session, temp_bucket_id, metadata, dataset_id=dataset_id
        )

        mock_click.echo.assert_has_calls(
            [
                call("Uploading metadata file"),
            ]
        )
        self.assertEqual(result, mock_upload_dataset_metadata.return_value)

    @patch("dafni_cli.api.datasets_api.upload_dataset_metadata")
    def test_commit_metadata_exits_on_error(
        self,
        mock_upload_dataset_metadata,
        mock_click,
    ):
        """Tests that _commit_metadata calls SystemExit(1) when an error occurs"""
        # SETUP
        session = MagicMock()
        metadata = MOCK_DEFINITION_DATA
        temp_bucket_id = "some-temp-bucket"

        error = DAFNIError("Some error message")
        mock_upload_dataset_metadata.side_effect = error

        # CALL
        with self.assertRaises(SystemExit):
            dataset_upload._commit_metadata(session, metadata, temp_bucket_id)

        # ASSERT
        mock_click.echo.assert_has_calls(
            [
                call("Uploading metadata file"),
                call(f"\nMetadata upload failed: {error}"),
            ]
        )

    @patch("dafni_cli.datasets.dataset_upload.upload_files")
    @patch("dafni_cli.datasets.dataset_upload._commit_metadata")
    @patch("dafni_cli.datasets.dataset_upload.create_temp_bucket")
    def test_upload_dataset(
        self,
        mock_create_temp_bucket,
        mock_commit_metadata,
        mock_upload_files,
        mock_click,
    ):
        """Tests that upload_dataset works as expected"""
        # SETUP
        session = MagicMock()
        metadata = MagicMock()
        file_paths = ["file_1.txt", "file_2.txt"]
        temp_bucket_id = "some-temp-bucket"
        dataset_id = MagicMock()
        details = {
            "datasetId": "dataset-id",
            "versionId": "version-id",
            "metadataId": "metadata-id",
        }

        mock_create_temp_bucket.return_value = temp_bucket_id
        mock_commit_metadata.return_value = details

        # CALL
        dataset_upload.upload_dataset(session, metadata, file_paths, dataset_id)

        # ASSERT
        mock_create_temp_bucket.assert_called_once_with(session)
        mock_upload_files.assert_called_once_with(
            session,
            temp_bucket_id,
            file_paths,
        )
        mock_commit_metadata.assert_called_once_with(
            session, metadata, temp_bucket_id, dataset_id=dataset_id
        )

        mock_click.echo.assert_has_calls(
            [
                call("\nRetrieving temporary bucket ID"),
                call("\nUpload successful"),
                call(f"Dataset ID: {details['datasetId']}"),
                call(f"Version ID: {details['versionId']}"),
                call(f"Metadata ID: {details['metadataId']}"),
            ]
        )

    @patch("dafni_cli.datasets.dataset_upload.upload_files")
    @patch("dafni_cli.datasets.dataset_upload._commit_metadata")
    @patch("dafni_cli.datasets.dataset_upload.create_temp_bucket")
    @patch("dafni_cli.datasets.dataset_upload.delete_temp_bucket")
    def test_upload_dataset_deletes_bucket_on_error(
        self,
        mock_delete_temp_bucket,
        mock_create_temp_bucket,
        mock_commit_metadata,
        mock_upload_files,
        mock_click,
    ):
        """Tests that upload_dataset deletes the temporary bucket when an
        error occurs"""
        # SETUP
        session = MagicMock()
        metadata = MagicMock()
        file_paths = ["file_1.txt", "file_2.txt"]
        temp_bucket_id = "some-temp-bucket"

        mock_create_temp_bucket.return_value = temp_bucket_id
        mock_commit_metadata.side_effect = HTTPError(400)

        # CALL
        with self.assertRaises(HTTPError):
            dataset_upload.upload_dataset(session, metadata, file_paths)

        # ASSERT
        mock_create_temp_bucket.assert_called_once_with(session)
        mock_upload_files.assert_called_once_with(
            session,
            temp_bucket_id,
            file_paths,
        )
        mock_commit_metadata.assert_called_once_with(
            session, metadata, temp_bucket_id, dataset_id=None
        )
        mock_delete_temp_bucket.assert_called_once_with(session, temp_bucket_id)

        mock_click.echo.assert_has_calls(
            [
                call("\nRetrieving temporary bucket ID"),
                call("Deleting temporary bucket"),
            ]
        )

    @patch("dafni_cli.datasets.dataset_upload.upload_files")
    @patch("dafni_cli.datasets.dataset_upload._commit_metadata")
    @patch("dafni_cli.datasets.dataset_upload.create_temp_bucket")
    @patch("dafni_cli.datasets.dataset_upload.delete_temp_bucket")
    def test_upload_dataset_deletes_bucket_on_system_exit(
        self,
        mock_delete_temp_bucket,
        mock_create_temp_bucket,
        mock_commit_metadata,
        mock_upload_files,
        mock_click,
    ):
        """Tests that upload_dataset deletes the temporary bucket when a
        SystemExit is triggered"""
        # SETUP
        session = MagicMock()
        metadata = MagicMock()
        file_paths = ["file_1.txt", "file_2.txt"]
        temp_bucket_id = "some-temp-bucket"

        mock_create_temp_bucket.return_value = temp_bucket_id
        mock_commit_metadata.side_effect = SystemExit(1)

        # CALL
        with self.assertRaises(SystemExit):
            dataset_upload.upload_dataset(session, metadata, file_paths)

        # ASSERT
        mock_create_temp_bucket.assert_called_once_with(session)
        mock_upload_files.assert_called_once_with(
            session,
            temp_bucket_id,
            file_paths,
        )
        mock_commit_metadata.assert_called_once_with(
            session, metadata, temp_bucket_id, dataset_id=None
        )
        mock_delete_temp_bucket.assert_called_once_with(session, temp_bucket_id)

        mock_click.echo.assert_has_calls(
            [
                call("\nRetrieving temporary bucket ID"),
                call("Deleting temporary bucket"),
            ]
        )

    @patch(
        "dafni_cli.datasets.dataset_upload.datasets_api.upload_dataset_metadata_version"
    )
    def test_upload_dataset_metadata_version(
        self,
        mock_upload_dataset_metadata,
        mock_click,
    ):
        """Tests that upload_dataset_metadata_version works as expected"""
        # SETUP
        session = MagicMock()
        dataset_id = MagicMock()
        version_id = MagicMock()
        metadata = MagicMock()
        details = {
            "datasetId": "dataset-id",
            "versionId": "version-id",
            "metadataId": "metadata-id",
        }

        mock_upload_dataset_metadata.return_value = details

        # CALL
        dataset_upload.upload_dataset_metadata_version(
            session, dataset_id, version_id, metadata
        )

        # ASSERT
        mock_upload_dataset_metadata.assert_called_once_with(
            session, dataset_id=dataset_id, version_id=version_id, metadata=metadata
        )

        mock_click.echo.assert_has_calls(
            [
                call("\nUpload successful"),
                call(f"Dataset ID: {details['datasetId']}"),
                call(f"Version ID: {details['versionId']}"),
                call(f"Metadata ID: {details['metadataId']}"),
            ]
        )

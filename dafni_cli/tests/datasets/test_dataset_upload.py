import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import MagicMock, call, mock_open, patch

from requests import HTTPError

from dafni_cli.api.exceptions import DAFNIError, ValidationError
from dafni_cli.consts import DATASET_UPLOAD_FILE_RETRY_ATTEMPTS
from dafni_cli.datasets import dataset_upload
from dafni_cli.datasets.dataset_metadata import (
    DATASET_METADATA_LANGUAGES,
    DATASET_METADATA_SUBJECTS,
    DATASET_METADATA_THEMES,
    DATASET_METADATA_UPDATE_FREQUENCIES,
)
from dafni_cli.tests.fixtures.dataset_metadata import TEST_DATASET_METADATA


class TestParseFilenamesFromPaths(TestCase):
    """Test class to test parse_file_names_from_paths works as
    expected"""

    def test_parse_file_names_from_paths(self):
        """Tests that parse_file_names_from_paths functions correctly"""

        # SETUP
        with TemporaryDirectory("test") as temp_dir:
            temp_dir_path = Path(temp_dir)
            (temp_dir_path / "folder").mkdir()
            (temp_dir_path / "folder/folder").mkdir()

            paths_to_upload = [
                temp_dir_path / "file1.txt",
                temp_dir_path / "file2.txt",
                temp_dir_path / "folder",
            ]
            expected_dict = {
                "file1.txt": temp_dir_path / Path("file1.txt"),
                "file2.txt": temp_dir_path / Path("file2.txt"),
                # Files in a sub folder
                "folder/file3.txt": temp_dir_path / Path("folder/file3.txt"),
                # Recursive
                "folder/folder/file4.txt": temp_dir_path
                / Path("folder/folder/file4.txt"),
            }

            # Create temporary files to test on
            for path in expected_dict.values():
                with open(temp_dir_path / path, "w", encoding="utf-8") as file:
                    file.write("Temp file contents")

            # CALL
            result = dataset_upload.parse_file_names_from_paths(paths=paths_to_upload)

            # ASSERT
            self.assertDictEqual(result, expected_dict)


class TestRemoveDatasetMetadataInvalidForUpload(TestCase):
    """Test class to test remove_dataset_metadata_invalid_for_upload works as
    expected"""

    def test_remove_dataset_metadata_invalid_for_upload(self):
        """Tests that remove_dataset_metadata_invalid_for_upload works as expected"""

        # SETUP
        original_metadata = deepcopy(TEST_DATASET_METADATA["metadata"])
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
        mock_remove_invalid.assert_called_once_with(metadata["metadata"])
        self.assertEqual(result, TEST_DATASET_METADATA["metadata"])

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
        language = "en"
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
        self.assertEqual(
            result["dct:creator"][0],
            {
                "@type": "foaf:Organization",
                "foaf:name": organisation[0],
                "@id": organisation[1],
                "internalID": None,
            },
        )
        for i, person in enumerate(people):
            self.assertEqual(
                result["dct:creator"][i + 1],
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
        self.assertNotEqual(metadata["metadata"]["dafni_version_note"], version_message)
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

    def test_with_invalid_language_raises_error(self, mock_open, mock_remove_invalid):
        """Tests that calling the function when an invalid language raises
        an appropriate ValueError"""

        # SETUP
        metadata = TEST_DATASET_METADATA

        # CALL & ASSERT
        with self.assertRaises(ValueError) as err:
            dataset_upload.modify_dataset_metadata_for_upload(
                metadata, language="Invalid language"
            )
        self.assertEqual(
            str(err.exception),
            f"Language 'Invalid language' is invalid, choose one from {''.join(DATASET_METADATA_LANGUAGES)}",
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


class TestDatasetUpload(TestCase):
    """Test class to test the functions in dataset_upload.py"""

    def setUp(self) -> None:
        super().setUp()

        self.mock_upload_dataset_metadata = patch(
            "dafni_cli.api.datasets_api.upload_dataset_metadata"
        ).start()
        self.mock_upload_file_to_minio = patch(
            "dafni_cli.datasets.dataset_upload.upload_file_to_minio"
        ).start()
        self.mock_get_data_upload_urls = patch(
            "dafni_cli.datasets.dataset_upload.get_data_upload_urls"
        ).start()
        self.mock_create_temp_bucket = patch(
            "dafni_cli.datasets.dataset_upload.create_temp_bucket"
        ).start()
        self.mock_delete_temp_bucket = patch(
            "dafni_cli.datasets.dataset_upload.delete_temp_bucket"
        ).start()
        self.mock_upload_dataset_metadata_version = patch(
            "dafni_cli.datasets.dataset_upload.datasets_api.upload_dataset_metadata_version"
        ).start()
        self.mock_print_json = patch(
            "dafni_cli.datasets.dataset_upload.print_json"
        ).start()
        self.mock_optional_echo = patch(
            "dafni_cli.datasets.dataset_upload.optional_echo"
        ).start()
        self.mock_OverallFileProgressBar = patch(
            "dafni_cli.datasets.dataset_upload.OverallFileProgressBar"
        ).start()
        self.mock_click = patch("dafni_cli.datasets.dataset_upload.click").start()

        self.addCleanup(patch.stopall)

    def _test_upload_files(self, json: bool):
        """Tests that upload_files works as expected with a given value of
        json"""
        # SETUP
        session = MagicMock()
        temp_bucket_id = "some-temp-bucket"
        file_size = 1000
        file_paths = [
            MagicMock(
                name="file_1.txt",
                stat=lambda: MagicMock(st_size=file_size),
                is_dir=MagicMock(return_value=False),
            ),
            MagicMock(
                name="file_2.txt",
                stat=lambda: MagicMock(st_size=file_size),
                is_dir=MagicMock(return_value=False),
            ),
        ]
        urls = [f"upload/url/{file_path.name}" for file_path in file_paths]
        upload_urls = [
            {"urls": {file_path.name: url}} for file_path, url in zip(file_paths, urls)
        ]

        self.mock_get_data_upload_urls.side_effect = upload_urls
        mock_overall_progress_bar = MagicMock()
        self.mock_OverallFileProgressBar.return_value.__enter__.return_value = (
            mock_overall_progress_bar
        )

        # CALL
        dataset_upload.upload_files(session, temp_bucket_id, file_paths, json=json)

        # ASSERT
        self.assertEqual(
            self.mock_get_data_upload_urls.call_args_list,
            [
                call(
                    session,
                    temp_bucket_id,
                    [file_path.name],
                )
                for file_path in file_paths
            ],
        )
        self.mock_OverallFileProgressBar.assert_called_once_with(
            len(file_paths), file_size * len(file_paths)
        )
        self.assertEqual(
            mock_overall_progress_bar.update.call_args_list,
            [call(file_size) for file_path in file_paths],
        )
        self.mock_upload_file_to_minio.assert_has_calls(
            [
                call(
                    session,
                    url,
                    file_paths[idx],
                    file_name=file_paths[idx].name,
                    progress_bar=not json,
                )
                for idx, url in enumerate(urls)
            ]
        )

        self.assertEqual(
            self.mock_optional_echo.call_args_list,
            [
                call("Uploading files", json),
            ],
        )

    def test_upload_files_retries_when_errors_occur(self):
        """Tests that upload_files raises an error less than the maximum number
        of times during a file's upload"""
        # SETUP
        session = MagicMock()
        temp_bucket_id = "some-temp-bucket"
        file_size = 1000
        file_path = MagicMock(
            name="file_1.txt",
            stat=lambda: MagicMock(st_size=file_size),
            is_dir=MagicMock(return_value=False),
        )
        urls = [f"upload/url-{i}" for i in range(0, DATASET_UPLOAD_FILE_RETRY_ATTEMPTS)]
        upload_urls = [{"urls": {file_path.name: url}} for url in urls]

        self.mock_get_data_upload_urls.side_effect = upload_urls
        mock_overall_progress_bar = MagicMock()
        self.mock_OverallFileProgressBar.return_value.__enter__.return_value = (
            mock_overall_progress_bar
        )
        self.mock_upload_file_to_minio.side_effect = [
            RuntimeError for i in range(DATASET_UPLOAD_FILE_RETRY_ATTEMPTS - 1)
        ] + [None]

        # CALL
        dataset_upload.upload_files(session, temp_bucket_id, [file_path])

        # ASSERT
        self.assertEqual(
            self.mock_get_data_upload_urls.call_args_list,
            [
                call(
                    session,
                    temp_bucket_id,
                    [file_path.name],
                )
                for url in urls
            ],
        )
        self.mock_OverallFileProgressBar.assert_called_once_with(1, file_size)
        self.assertEqual(
            mock_overall_progress_bar.update.call_args_list,
            [call(file_size)],
        )
        self.mock_upload_file_to_minio.assert_has_calls(
            [
                call(
                    session, url, file_path, file_name=file_path.name, progress_bar=True
                )
                for url in urls
            ]
        )

        self.assertEqual(
            self.mock_optional_echo.call_args_list,
            [
                call("Uploading files", False),
            ],
        )

    def test_upload_files_raises_runtime_error_when_fails_repeatedly(self):
        """Tests that upload_files raises an error equal to the maximum number
        of times during a file's upload, a RuntimeError is raised"""
        # SETUP
        session = MagicMock()
        temp_bucket_id = "some-temp-bucket"
        file_size = 1000
        file_path = MagicMock(
            name="file_1.txt",
            stat=lambda: MagicMock(st_size=file_size),
            is_dir=MagicMock(return_value=False),
        )
        urls = [f"upload/url-{i}" for i in range(0, DATASET_UPLOAD_FILE_RETRY_ATTEMPTS)]
        upload_urls = [{"urls": {file_path.name: url}} for url in urls]

        self.mock_get_data_upload_urls.side_effect = upload_urls
        mock_overall_progress_bar = MagicMock()
        self.mock_OverallFileProgressBar.return_value.__enter__.return_value = (
            mock_overall_progress_bar
        )
        self.mock_upload_file_to_minio.side_effect = [
            RuntimeError for i in range(DATASET_UPLOAD_FILE_RETRY_ATTEMPTS)
        ]

        # CALL
        with self.assertRaises(RuntimeError) as err:
            dataset_upload.upload_files(session, temp_bucket_id, [file_path])

        # ASSERT
        self.assertEqual(
            self.mock_get_data_upload_urls.call_args_list,
            [
                call(
                    session,
                    temp_bucket_id,
                    [file_path.name],
                )
                for url in urls
            ],
        )
        self.mock_OverallFileProgressBar.assert_called_once_with(1, file_size)
        self.mock_upload_file_to_minio.assert_has_calls(
            [
                call(
                    session, url, file_path, file_name=file_path.name, progress_bar=True
                )
                for url in urls
            ]
        )
        mock_overall_progress_bar.assert_not_called()

        self.assertEqual(
            self.mock_optional_echo.call_args_list,
            [
                call("Uploading files", False),
            ],
        )

        self.assertEqual(
            str(err.exception),
            f"Attempted to upload file {DATASET_UPLOAD_FILE_RETRY_ATTEMPTS} times but failed repeatedly",
        )

    def test_upload_files(self):
        """Tests that upload_files works as expected with json = False"""
        self._test_upload_files(False)

    def test_upload_files_json(self):
        """Tests that upload_files works as expected with json = True"""
        self._test_upload_files(True)

    def _test_commit_metadata(self, json: bool):
        """Tests that _commit_metadata works as expected without a dataset_id
        and a given value of json"""
        # SETUP
        session = MagicMock()
        metadata = MOCK_DEFINITION_DATA
        temp_bucket_id = "some-temp-bucket"

        # CALL
        result = dataset_upload._commit_metadata(
            session, metadata, temp_bucket_id, json=json
        )

        # ASSERT
        self.mock_upload_dataset_metadata.assert_called_with(
            session, temp_bucket_id, metadata, dataset_id=None
        )

        self.mock_optional_echo.assert_called_once_with("Uploading metadata file", json)
        self.assertEqual(result, self.mock_upload_dataset_metadata.return_value)

    def test_commit_metadata(self):
        """Tests that _commit_metadata works as expected without a dataset_id
        and json = False"""
        self._test_commit_metadata(False)

    def test_commit_metadata_json(self):
        """Tests that _commit_metadata works as expected without a dataset_id
        and json = True"""
        self._test_commit_metadata(True)

    def _test_commit_metadata_with_dataset_id(self, json: bool):
        """Tests that _commit_metadata works as expected with a dataset_id and
        a given value of json"""
        # SETUP
        session = MagicMock()
        metadata = MOCK_DEFINITION_DATA
        temp_bucket_id = "some-temp-bucket"
        dataset_id = "some-dataset-id"

        # CALL
        result = dataset_upload._commit_metadata(
            session, metadata, temp_bucket_id, dataset_id=dataset_id, json=json
        )

        # ASSERT
        self.mock_upload_dataset_metadata.assert_called_with(
            session,
            temp_bucket_id,
            metadata,
            dataset_id=dataset_id,
        )

        self.mock_optional_echo.assert_called_once_with("Uploading metadata file", json)
        self.assertEqual(result, self.mock_upload_dataset_metadata.return_value)

    def test_commit_metadata_with_dataset_id(self):
        """Tests that _commit_metadata works as expected with a dataset_id with
        json = False"""
        self._test_commit_metadata_with_dataset_id(False)

    def test_commit_metadata_with_dataset_id_json(self):
        """Tests that _commit_metadata works as expected with a dataset_id with
        json = True"""
        self._test_commit_metadata_with_dataset_id(True)

    def _test_commit_metadata_exits_on_error(self, json: bool):
        """Tests that _commit_metadata calls SystemExit(1) when an error occurs
        and using a given value of json"""
        # SETUP
        session = MagicMock()
        metadata = MOCK_DEFINITION_DATA
        temp_bucket_id = "some-temp-bucket"

        error = DAFNIError("Some error message")
        self.mock_upload_dataset_metadata.side_effect = error

        # CALL
        with self.assertRaises(SystemExit):
            dataset_upload._commit_metadata(
                session, metadata, temp_bucket_id, json=json
            )

        # ASSERT
        self.mock_optional_echo.assert_called_once_with("Uploading metadata file", json)
        self.mock_click.echo.assert_called_once_with(
            f"\nMetadata upload failed: {error}"
        )

    def test_commit_metadata_exits_on_error(self):
        """Tests that _commit_metadata calls SystemExit(1) when an error occurs
        and json = False"""
        self._test_commit_metadata_exits_on_error(False)

    def test_commit_metadata_exits_on_error_json(self):
        """Tests that _commit_metadata calls SystemExit(1) when an error occurs
        and json = True"""
        self._test_commit_metadata_exits_on_error(True)

    def _test_upload_dataset(self, json: bool):
        """Tests that upload_dataset works as expected with the given value
        of json"""

        # Additionally patch these functions in the same file
        with patch(
            "dafni_cli.datasets.dataset_upload._commit_metadata"
        ) as mock_commit_metadata, patch(
            "dafni_cli.datasets.dataset_upload.upload_files"
        ) as mock_upload_files:
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

            self.mock_create_temp_bucket.return_value = temp_bucket_id
            mock_commit_metadata.return_value = details

            # CALL
            dataset_upload.upload_dataset(
                session, metadata, file_paths, dataset_id, json=json
            )

            # ASSERT
            self.mock_create_temp_bucket.assert_called_once_with(session)
            mock_upload_files.assert_called_once_with(
                session, temp_bucket_id, file_paths, json=json
            )
            mock_commit_metadata.assert_called_once_with(
                session, metadata, temp_bucket_id, dataset_id=dataset_id, json=json
            )

            self.mock_optional_echo.assert_has_calls(
                [
                    call("Validating metadata", json),
                    call("Metadata validation successful", json),
                    call("\nRetrieving temporary bucket ID", json),
                ]
            )

            if json:
                self.mock_print_json.assert_called_once_with(details)
                self.mock_click.echo.assert_not_called()
            else:
                self.mock_print_json.assert_not_called()
                self.mock_click.echo.assert_has_calls(
                    [
                        call("\nUpload successful"),
                        call(f"Dataset ID: {details['datasetId']}"),
                        call(f"Version ID: {details['versionId']}"),
                        call(f"Metadata ID: {details['metadataId']}"),
                    ]
                )

    def test_upload_dataset_validation_error(self):
        """Tests that the validation error is handled correctly when raised due to metadata validation failing"""
        with patch(
            "dafni_cli.api.datasets_api.validate_metadata"
        ) as mock_validate_metadata:
            # SETUP
            session = MagicMock()
            metadata = MagicMock()
            paths = MagicMock()
            mock_validate_metadata.side_effect = ValidationError

            # CALL
            with self.assertRaises(SystemExit):
                dataset_upload.upload_dataset(session, metadata, paths)

    def test_upload_dataset(self):
        """Tests that upload_dataset works as expected with json = False"""
        self._test_upload_dataset(False)

    def test_upload_dataset_json(self):
        """Tests that upload_dataset works as expected with json = True"""
        self._test_upload_dataset(True)

    def _test_upload_dataset_deletes_bucket_on_error(self, json: bool):
        """Tests that upload_dataset deletes the temporary bucket when an
        error occurs while using a specific value of json"""

        # Additionally patch these functions in the same file
        with patch(
            "dafni_cli.datasets.dataset_upload._commit_metadata"
        ) as mock_commit_metadata, patch(
            "dafni_cli.datasets.dataset_upload.upload_files"
        ) as mock_upload_files:
            # SETUP
            session = MagicMock()
            metadata = MagicMock()
            file_paths = ["file_1.txt", "file_2.txt"]
            temp_bucket_id = "some-temp-bucket"

            self.mock_create_temp_bucket.return_value = temp_bucket_id
            mock_commit_metadata.side_effect = HTTPError(400)

            # CALL
            with self.assertRaises(HTTPError):
                dataset_upload.upload_dataset(session, metadata, file_paths, json=json)

            # ASSERT
            self.mock_create_temp_bucket.assert_called_once_with(session)
            mock_upload_files.assert_called_once_with(
                session, temp_bucket_id, file_paths, json=json
            )
            mock_commit_metadata.assert_called_once_with(
                session, metadata, temp_bucket_id, dataset_id=None, json=json
            )
            self.mock_delete_temp_bucket.assert_called_once_with(
                session, temp_bucket_id
            )

            self.assertEqual(
                self.mock_optional_echo.call_args_list,
                [
                    call("Validating metadata", json),
                    call("Metadata validation successful", json),
                    call("\nRetrieving temporary bucket ID", json),
                    call("Deleting temporary bucket", json),
                ],
            )

    def test_upload_dataset_deletes_bucket_on_error(self):
        """Tests that upload_dataset deletes the temporary bucket when an
        error occurs and json = False"""
        self._test_upload_dataset_deletes_bucket_on_error(False)

    def test_upload_dataset_deletes_bucket_on_error_json(self):
        """Tests that upload_dataset deletes the temporary bucket when an
        error occurs and json = True"""
        self._test_upload_dataset_deletes_bucket_on_error(True)

    def test_upload_dataset_deletes_bucket_on_system_exit(
        self,
    ):
        """Tests that upload_dataset deletes the temporary bucket when a
        SystemExit is triggered (json is ignored as uses same code as above
        to do the check anyway)"""

        # Additionally patch these functions in the same file
        with patch(
            "dafni_cli.datasets.dataset_upload._commit_metadata"
        ) as mock_commit_metadata, patch(
            "dafni_cli.datasets.dataset_upload.upload_files"
        ) as mock_upload_files:
            # SETUP
            session = MagicMock()
            metadata = MagicMock()
            file_paths = ["file_1.txt", "file_2.txt"]
            temp_bucket_id = "some-temp-bucket"

            self.mock_create_temp_bucket.return_value = temp_bucket_id
            mock_commit_metadata.side_effect = SystemExit(1)

            # CALL
            with self.assertRaises(SystemExit):
                dataset_upload.upload_dataset(session, metadata, file_paths)

            # ASSERT
            self.mock_create_temp_bucket.assert_called_once_with(session)
            mock_upload_files.assert_called_once_with(
                session, temp_bucket_id, file_paths, json=False
            )
            mock_commit_metadata.assert_called_once_with(
                session, metadata, temp_bucket_id, dataset_id=None, json=False
            )
            self.mock_delete_temp_bucket.assert_called_once_with(
                session, temp_bucket_id
            )

            self.assertEqual(
                self.mock_optional_echo.call_args_list,
                [
                    call("Validating metadata", False),
                    call("Metadata validation successful", False),
                    call("\nRetrieving temporary bucket ID", False),
                    call("Deleting temporary bucket", False),
                ],
            )

    def _test_upload_dataset_metadata_version(self, json: bool):
        """Tests that upload_dataset_metadata_version works as expected with
        the given value of json"""

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

        self.mock_upload_dataset_metadata_version.return_value = details

        # CALL
        dataset_upload.upload_dataset_metadata_version(
            session, dataset_id, version_id, metadata, json=json
        )

        # ASSERT
        self.mock_upload_dataset_metadata_version.assert_called_once_with(
            session, dataset_id=dataset_id, version_id=version_id, metadata=metadata
        )

        if json:
            self.mock_print_json.assert_called_once_with(details)
            self.mock_click.echo.assert_not_called()
        else:
            self.mock_print_json.assert_not_called()
            self.mock_click.echo.assert_has_calls(
                [
                    call("\nUpload successful"),
                    call(f"Dataset ID: {details['datasetId']}"),
                    call(f"Version ID: {details['versionId']}"),
                    call(f"Metadata ID: {details['metadataId']}"),
                ]
            )

    def test_upload_dataset_metadata_version(self):
        """Tests that upload_dataset_metadata_version works as expected when
        json = False"""
        self._test_upload_dataset_metadata_version(False)

    def test_upload_dataset_metadata_version_json(self):
        """Tests that upload_dataset_metadata_version works as expected when
        json = True"""
        self._test_upload_dataset_metadata_version(True)

from datetime import datetime
from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from dateutil.tz import tzutc

from dafni_cli.api.parser import ParserBaseObject
from dafni_cli.consts import CONSOLE_WIDTH, DATA_FORMATS, TAB_SPACE
from dafni_cli.datasets.dataset_metadata import (
    Contact,
    Creator,
    DataFile,
    DatasetMetadata,
    DatasetVersionHistory,
    Location,
    Publisher,
    Standard,
    parse_dataset_metadata,
)
from dafni_cli.utils import process_file_size

# Below follows example response data from the API for getting a dataset's
# metadata
# Values labelled with _DEFAULT implies they do not define optional variables
# and are used to test the values still parse correctly
TEST_DATASET_METADATA_DATAFILE: dict = {
    "spdx:fileName": "workflow_def.csv",
    "dcat:mediaType": "text/csv",
    "dcat:byteSize": 6720,
    "dcat:downloadURL": "url/to/file",
}

TEST_DATASET_METADATA_CREATOR: dict = {
    "@type": "foaf:Organization",
    "@id": "http://www.stfc.ac.uk",
    "foaf:name": "STFC",
    "internalID": None,
}

TEST_DATASET_METADATA_CREATOR_DEFAULT: dict = {
    "@type": "foaf:Organization",
    "foaf:name": "Some Name",
}

TEST_DATASET_METADATA_CONTACT: dict = {
    "@type": "vcard:Organization",
    "vcard:fn": "Joe",
    "vcard:hasEmail": "example@domain.com",
}

TEST_DATASET_METADATA_LOCATION: dict = {
    "@id": "2648147",
    "@type": "dct:Location",
    "rdfs:label": "England",
}

TEST_DATASET_METADATA_PUBLISHER: dict = {
    "@id": None,
    "@type": "foaf:Organization",
    "foaf:name": "Publisher",
    "internalID": None,
}

TEST_DATASET_METADATA_PUBLISHER_DEFAULT: dict = {
    "@type": "foaf:Organization",
}

TEST_DATASET_METADATA_STANDARD: dict = {
    "@id": "https://www.iso.org/standard/39229.html",
    "@type": "dct:Standard",
    "label": "ISO 19115-2:2009",
}

TEST_DATASET_METADATA_STANDARD_DEFAULT: dict = {
    "@type": "dct:Standard",
}

TEST_DATASET_METADATA_VERSION_HISTORY: dict = {
    "dataset_uuid": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
    "versions": [
        {
            "version_uuid": "0a0a0a0a-0a00-0a00-a000-0a0a0000000b",
            "metadata_versions": [
                {
                    "metadata_uuid": "0a0a0a0a-0a00-0a00-a000-0a0a0000000c",
                    "dafni_version_note": "Initial Dataset version",
                    "modified_date": "2021-03-16T09:27:21+00:00",
                },
                {
                    "metadata_uuid": "0a0a0a0a-0a00-0a00-a000-0a0a0000000d",
                    "dafni_version_note": "Second Dataset version",
                    "modified_date": "2021-03-17T09:27:21+00:00",
                },
            ],
        },
        {
            "version_uuid": "0a0a0a0a-0a00-0a00-a000-0a0a0000000c",
            "metadata_versions": [
                {
                    "metadata_uuid": "0a0a0a0a-0a00-0a00-a000-0a0a0000000d",
                    "dafni_version_note": "Initial Dataset version",
                    "modified_date": "2021-03-16T09:27:21+00:00",
                },
            ],
        },
    ],
}

TEST_DATASET_METADATA: dict = {
    "@context": ["metadata-v1"],
    "@type": "dcat:Dataset",
    "dct:title": "An example workflow definition",
    "dct:description": "Dataset description",
    "dct:identifier": [
        "0a0a0a0a-0a00-0a00-a000-0a0a0000000a:0a0a0a0a-0a00-0a00-a000-0a0a0000000b:0a0a0a0a-0a00-0a00-a000-0a0a0000000c"
    ],
    "dct:subject": "Subject",
    "dcat:theme": [],
    "dct:language": "en",
    "dcat:keyword": ["test"],
    "dct:conformsTo": TEST_DATASET_METADATA_STANDARD,
    "dct:spatial": TEST_DATASET_METADATA_LOCATION,
    "geojson": {},
    "dct:PeriodOfTime": {
        "type": "dct:PeriodOfTime",
        "time:hasBeginning": "2019-03-27T00:00:00Z",
        "time:hasEnd": "2021-03-27T00:00:00Z",
    },
    "dct:accrualPeriodicity": "Semiannual",
    "dct:creator": [
        TEST_DATASET_METADATA_CREATOR,
        TEST_DATASET_METADATA_CREATOR_DEFAULT,
    ],
    "dct:created": "2021-03-16",
    "dct:publisher": TEST_DATASET_METADATA_PUBLISHER,
    "dcat:contactPoint": TEST_DATASET_METADATA_CONTACT,
    "dct:license": {
        "@type": "LicenseDocument",
        "@id": "https://creativecommons.org/licences/by/4.0/",
        "rdfs:label": None,
    },
    "dct:rights": "Open Government Licence.",
    "dafni_version_note": "Initial Dataset version",
    "@id": {
        "asset_id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a:0a0a0a0a-0a00-0a00-a000-0a0a0000000b:0a0a0a0a-0a00-0a00-a000-0a0a0000000c",
        "dataset_uuid": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
        "version_uuid": "0a0a0a0a-0a00-0a00-a000-0a0a0000000b",
        "metadata_uuid": "0a0a0a0a-0a00-0a00-a000-0a0a0000000c",
    },
    "dct:modified": "2021-03-16T09:27:21+00:00",
    "dct:issued": "2021-03-16T09:27:21+00:00",
    "dcat:distribution": [TEST_DATASET_METADATA_DATAFILE],
    "mediatypes": [None],
    "version_history": TEST_DATASET_METADATA_VERSION_HISTORY,
    "auth": {
        "asset_id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
        "reason": "Accessed as part of the Public group",
        "view": True,
        "read": True,
        "update": False,
        "destroy": False,
    },
}

TEST_DATASET_METADATA_DEFAULT: dict = {
    "@context": ["metadata-v1"],
    "@type": "dcat:Dataset",
    "dct:title": "An example workflow definition",
    "dct:description": "Dataset description",
    "dct:identifier": [
        "0a0a0a0a-0a00-0a00-a000-0a0a0000000a:0a0a0a0a-0a00-0a00-a000-0a0a0000000b:0a0a0a0a-0a00-0a00-a000-0a0a0000000c"
    ],
    "dct:subject": "Subject",
    "dcat:theme": [],
    "dct:language": "en",
    "dcat:keyword": ["test"],
    "dct:conformsTo": TEST_DATASET_METADATA_STANDARD,
    "dct:spatial": TEST_DATASET_METADATA_LOCATION,
    "geojson": {},
    "dct:creator": [
        TEST_DATASET_METADATA_CREATOR,
        TEST_DATASET_METADATA_CREATOR_DEFAULT,
    ],
    "dct:created": "2021-03-16",
    "dct:publisher": TEST_DATASET_METADATA_PUBLISHER,
    "dcat:contactPoint": TEST_DATASET_METADATA_CONTACT,
    "dct:license": {
        "@type": "LicenseDocument",
        "@id": "https://creativecommons.org/licences/by/4.0/",
        "rdfs:label": None,
    },
    "dafni_version_note": "Initial Dataset version",
    "@id": {
        "asset_id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a:0a0a0a0a-0a00-0a00-a000-0a0a0000000b:0a0a0a0a-0a00-0a00-a000-0a0a0000000c",
        "dataset_uuid": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
        "version_uuid": "0a0a0a0a-0a00-0a00-a000-0a0a0000000b",
        "metadata_uuid": "0a0a0a0a-0a00-0a00-a000-0a0a0000000c",
    },
    "dct:modified": "2021-03-16T09:27:21+00:00",
    "dct:issued": "2021-03-16T09:27:21+00:00",
    "dcat:distribution": [TEST_DATASET_METADATA_DATAFILE],
    "mediatypes": [None],
    "version_history": TEST_DATASET_METADATA_VERSION_HISTORY,
    "auth": {
        "asset_id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
        "reason": "Accessed as part of the Public group",
        "view": True,
        "read": True,
        "update": False,
        "destroy": False,
    },
}


class TestDataFile(TestCase):
    """Tests the DataFile dataclass"""

    def test_parse(self):
        """Tests parsing of data files"""

        datafile: DataFile = ParserBaseObject.parse_from_dict(
            DataFile, TEST_DATASET_METADATA_DATAFILE
        )

        self.assertEqual(datafile.name, TEST_DATASET_METADATA_DATAFILE["spdx:fileName"])
        self.assertEqual(
            datafile.size,
            process_file_size(TEST_DATASET_METADATA_DATAFILE["dcat:byteSize"]),
        )
        self.assertEqual(
            datafile.format,
            DATA_FORMATS.get(
                TEST_DATASET_METADATA_DATAFILE["dcat:mediaType"], "Unknown"
            ),
        )
        self.assertEqual(
            datafile.download_url, TEST_DATASET_METADATA_DATAFILE["dcat:downloadURL"]
        )

    @patch("dafni_cli.datasets.dataset_metadata.minio_get_request")
    def test_contents_set_to_returned_file_contents(self, mock_minio_get_request):
        """Tests downloading of a data file"""
        # SETUP
        contents = b"Test data"
        mock_minio_get_request.return_value = contents
        session = MagicMock()

        datafile: DataFile = ParserBaseObject.parse_from_dict(
            DataFile, TEST_DATASET_METADATA_DATAFILE
        )

        # CALL
        datafile.download_contents(session)

        # ASSERT
        mock_minio_get_request.assert_called_once_with(
            TEST_DATASET_METADATA_DATAFILE["dcat:downloadURL"], session, content=True
        )

        self.assertEqual(contents, datafile.contents.getvalue())


class TestCreator(TestCase):
    """Tests the Creator dataclass"""

    def test_parse(self):
        """Tests parsing of creators with all values filled"""

        creator: Creator = ParserBaseObject.parse_from_dict(
            Creator, TEST_DATASET_METADATA_CREATOR
        )
        self.assertEqual(creator.type, TEST_DATASET_METADATA_CREATOR["@type"])
        self.assertEqual(creator.name, TEST_DATASET_METADATA_CREATOR["foaf:name"])
        self.assertEqual(creator.id, TEST_DATASET_METADATA_CREATOR["@id"])
        self.assertEqual(
            creator.internal_id, TEST_DATASET_METADATA_CREATOR["internalID"]
        )

    def test_parse_when_no_optional_values(self):
        """Tests parsing of creators with all values filled"""

        creator: Creator = ParserBaseObject.parse_from_dict(
            Creator, TEST_DATASET_METADATA_CREATOR_DEFAULT
        )
        self.assertEqual(creator.type, TEST_DATASET_METADATA_CREATOR_DEFAULT["@type"])
        self.assertEqual(
            creator.name, TEST_DATASET_METADATA_CREATOR_DEFAULT["foaf:name"]
        )
        self.assertEqual(creator.id, None)
        self.assertEqual(creator.internal_id, None)


class TestContact(TestCase):
    """Tests the Contact dataclass"""

    def test_parse(self):
        """Tests parsing of contact with all values filled"""

        contact: Contact = ParserBaseObject.parse_from_dict(
            Contact, TEST_DATASET_METADATA_CONTACT
        )
        self.assertEqual(contact.type, TEST_DATASET_METADATA_CONTACT["@type"])
        self.assertEqual(contact.name, TEST_DATASET_METADATA_CONTACT["vcard:fn"])
        self.assertEqual(contact.email, TEST_DATASET_METADATA_CONTACT["vcard:hasEmail"])


class TestLocation(TestCase):
    """Tests the Location dataclass"""

    def test_parse(self):
        """Tests parsing of Location with all values filled"""

        location: Location = ParserBaseObject.parse_from_dict(
            Location, TEST_DATASET_METADATA_LOCATION
        )
        self.assertEqual(location.id, TEST_DATASET_METADATA_LOCATION["@id"])
        self.assertEqual(location.type, TEST_DATASET_METADATA_LOCATION["@type"])
        self.assertEqual(location.label, TEST_DATASET_METADATA_LOCATION["rdfs:label"])


class TestPublisher(TestCase):
    """Tests the Publisher dataclass"""

    def test_parse(self):
        """Tests parsing of a publisher with all values filled"""

        publisher: Publisher = ParserBaseObject.parse_from_dict(
            Publisher, TEST_DATASET_METADATA_PUBLISHER
        )
        self.assertEqual(publisher.type, TEST_DATASET_METADATA_PUBLISHER["@type"])
        self.assertEqual(publisher.id, TEST_DATASET_METADATA_PUBLISHER["@id"])
        self.assertEqual(publisher.name, TEST_DATASET_METADATA_PUBLISHER["foaf:name"])
        self.assertEqual(
            publisher.internal_id, TEST_DATASET_METADATA_PUBLISHER["internalID"]
        )

    def test_parse_when_no_optional_values(self):
        """Tests parsing of a publisher with optional values ignored"""

        publisher: Publisher = ParserBaseObject.parse_from_dict(
            Publisher, TEST_DATASET_METADATA_PUBLISHER_DEFAULT
        )
        self.assertEqual(
            publisher.type, TEST_DATASET_METADATA_PUBLISHER_DEFAULT["@type"]
        )
        self.assertEqual(publisher.id, None)
        self.assertEqual(publisher.name, None)
        self.assertEqual(publisher.internal_id, None)


class TestStandard(TestCase):
    """Tests the Standard dataclass"""

    def test_parse(self):
        """Tests parsing of a standard with all values filled"""

        standard: Standard = ParserBaseObject.parse_from_dict(
            Standard, TEST_DATASET_METADATA_STANDARD
        )
        self.assertEqual(standard.type, TEST_DATASET_METADATA_STANDARD["@type"])
        self.assertEqual(standard.id, TEST_DATASET_METADATA_STANDARD["@id"])
        self.assertEqual(standard.label, TEST_DATASET_METADATA_STANDARD["label"])

    def test_parse_when_no_optional_values(self):
        """Tests parsing of a standard with optional values ignored"""

        standard: Standard = ParserBaseObject.parse_from_dict(
            Standard, TEST_DATASET_METADATA_STANDARD_DEFAULT
        )
        self.assertEqual(standard.type, TEST_DATASET_METADATA_STANDARD_DEFAULT["@type"])
        self.assertEqual(standard.id, None)
        self.assertEqual(standard.label, None)


class TestDatasetVersionHistory(TestCase):
    """Tests the DatasetVersionHistory dataclass"""

    def test_parse(self):
        """Tests parsing of a dataset's version history"""

        version_history: DatasetVersionHistory = ParserBaseObject.parse_from_dict(
            DatasetVersionHistory, TEST_DATASET_METADATA_VERSION_HISTORY
        )

        self.assertEqual(
            version_history.dataset_id,
            TEST_DATASET_METADATA_VERSION_HISTORY["dataset_uuid"],
        )
        self.assertEqual(len(version_history.versions), 2)

        # Version 1
        self.assertEqual(
            version_history.versions[0].version_id,
            TEST_DATASET_METADATA_VERSION_HISTORY["versions"][0]["version_uuid"],
        )
        self.assertEqual(len(version_history.versions[0].metadata_versions), 2)

        # Version 1, Metadata Version 1
        self.assertEqual(
            version_history.versions[0].metadata_versions[0].metadata_id,
            TEST_DATASET_METADATA_VERSION_HISTORY["versions"][0]["metadata_versions"][
                0
            ]["metadata_uuid"],
        )
        self.assertEqual(
            version_history.versions[0].metadata_versions[0].label,
            TEST_DATASET_METADATA_VERSION_HISTORY["versions"][0]["metadata_versions"][
                0
            ]["dafni_version_note"],
        )
        self.assertEqual(
            version_history.versions[0].metadata_versions[0].modified_date,
            datetime(2021, 3, 16, 9, 27, 21, tzinfo=tzutc()),
        )

        # Version 1, Metadata Version 2
        self.assertEqual(
            version_history.versions[0].metadata_versions[1].metadata_id,
            TEST_DATASET_METADATA_VERSION_HISTORY["versions"][0]["metadata_versions"][
                1
            ]["metadata_uuid"],
        )
        self.assertEqual(
            version_history.versions[0].metadata_versions[1].label,
            TEST_DATASET_METADATA_VERSION_HISTORY["versions"][0]["metadata_versions"][
                1
            ]["dafni_version_note"],
        )
        self.assertEqual(
            version_history.versions[0].metadata_versions[1].modified_date,
            datetime(2021, 3, 17, 9, 27, 21, tzinfo=tzutc()),
        )

        # Version 2
        self.assertEqual(
            version_history.versions[1].version_id,
            TEST_DATASET_METADATA_VERSION_HISTORY["versions"][1]["version_uuid"],
        )
        self.assertEqual(len(version_history.versions[1].metadata_versions), 1)

        # Version 1, Metadata Version 1
        self.assertEqual(
            version_history.versions[1].metadata_versions[0].metadata_id,
            TEST_DATASET_METADATA_VERSION_HISTORY["versions"][1]["metadata_versions"][
                0
            ]["metadata_uuid"],
        )
        self.assertEqual(
            version_history.versions[1].metadata_versions[0].label,
            TEST_DATASET_METADATA_VERSION_HISTORY["versions"][1]["metadata_versions"][
                0
            ]["dafni_version_note"],
        )
        self.assertEqual(
            version_history.versions[1].metadata_versions[0].modified_date,
            datetime(2021, 3, 16, 9, 27, 21, tzinfo=tzutc()),
        )

    @patch("dafni_cli.datasets.dataset_metadata.print_json")
    @patch.object(DatasetMetadata, "output_version_details")
    @patch("dafni_cli.datasets.dataset_metadata.get_latest_dataset_metadata")
    def test_process_and_output_version_history_with_false_json_flag(
        self,
        mock_get_latest_dataset_metadata,
        mock_output_version_details,
        mock_print_json,
    ):
        """Tests process_and_output_version_history with a 'json_flag' value
        of False"""

        # SETUP
        mock_get_latest_dataset_metadata.return_value = TEST_DATASET_METADATA
        session = MagicMock()

        version_history: DatasetVersionHistory = ParserBaseObject.parse_from_dict(
            DatasetVersionHistory, TEST_DATASET_METADATA_VERSION_HISTORY
        )

        # CALL
        version_history.process_and_output_version_history(session)

        # ASSERT
        mock_get_latest_dataset_metadata.assert_has_calls(
            [
                call(session, version_history.dataset_id, version.version_id)
                for version in version_history.versions
            ]
        )
        self.assertEqual(
            mock_output_version_details.call_count, len(version_history.versions)
        )
        mock_print_json.assert_not_called()

    @patch("dafni_cli.datasets.dataset_metadata.print_json")
    @patch.object(DatasetMetadata, "output_version_details")
    @patch("dafni_cli.datasets.dataset_metadata.get_latest_dataset_metadata")
    def test_process_and_output_version_history_with_true_json_flag(
        self,
        mock_get_latest_dataset_metadata,
        mock_output_version_details,
        mock_print_json,
    ):
        """Tests process_and_output_version_history with a 'json_flag' value
        of True"""

        # SETUP
        mock_get_latest_dataset_metadata.return_value = TEST_DATASET_METADATA

        session = MagicMock()

        version_history: DatasetVersionHistory = ParserBaseObject.parse_from_dict(
            DatasetVersionHistory, TEST_DATASET_METADATA_VERSION_HISTORY
        )

        # CALL
        version_history.process_and_output_version_history(session, json_flag=True)

        # ASSERT
        mock_get_latest_dataset_metadata.assert_has_calls(
            [
                call(session, version_history.dataset_id, version.version_id)
                for version in version_history.versions
            ]
        )
        self.assertEqual(mock_output_version_details.call_count, 0)

        # Above we have mocked mock_get_latest_dataset_metadata's return
        # value to be TEST_DATASET_METADATA, as we have 2 versions in the
        # metadata we expect the same metadata to have been printed twice,
        # once per version
        mock_print_json.assert_called_with(
            [TEST_DATASET_METADATA, TEST_DATASET_METADATA]
        )


class TestDatasetMetadataTestCase(TestCase):
    """Tests the DatasetMetadata dataclass"""

    def test_parse_dataset_metadata(self):
        """Tests parsing of a dataset's metadata"""
        metadata = parse_dataset_metadata(TEST_DATASET_METADATA)

        self.assertEqual(metadata.title, TEST_DATASET_METADATA["dct:title"])
        self.assertEqual(metadata.description, TEST_DATASET_METADATA["dct:description"])
        self.assertEqual(metadata.subject, TEST_DATASET_METADATA["dct:subject"])
        self.assertEqual(metadata.created, datetime(2021, 3, 16, 0, 0))

        # Creators (Contents tested in TestCreator)
        self.assertEqual(len(metadata.creators), 2)
        self.assertEqual(type(metadata.creators[0]), Creator)

        # Contact (Contents tested in TestContact)
        self.assertEqual(type(metadata.contact), Contact)

        self.assertEqual(metadata.identifiers, TEST_DATASET_METADATA["dct:identifier"])

        # Location (Contents tested in TestLocation)
        self.assertEqual(type(metadata.location), Location)

        self.assertEqual(metadata.keywords, TEST_DATASET_METADATA["dcat:keyword"])
        self.assertEqual(metadata.themes, TEST_DATASET_METADATA["dcat:theme"])

        # Publisher (Contents tested in TestPublisher)
        self.assertEqual(type(metadata.publisher), Publisher)

        self.assertEqual(
            metadata.issued, datetime(2021, 3, 16, 9, 27, 21, tzinfo=tzutc())
        )
        self.assertEqual(metadata.language, TEST_DATASET_METADATA["dct:language"])

        # Standard (Contents tested in TestStandard)
        self.assertEqual(type(metadata.standard), Standard)

        self.assertEqual(metadata.asset_id, TEST_DATASET_METADATA["@id"]["asset_id"])
        self.assertEqual(
            metadata.dataset_id, TEST_DATASET_METADATA["@id"]["dataset_uuid"]
        )
        self.assertEqual(
            metadata.version_id, TEST_DATASET_METADATA["@id"]["version_uuid"]
        )
        self.assertEqual(
            metadata.metadata_id, TEST_DATASET_METADATA["@id"]["metadata_uuid"]
        )

        # Files (Contents tested in TestDataFile)
        self.assertEqual(len(metadata.files), 1)
        self.assertEqual(type(metadata.files[0]), DataFile)

        # Version history (Contents tested in TestVersionHistory)
        self.assertEqual(type(metadata.version_history), DatasetVersionHistory)

        self.assertEqual(metadata.rights, TEST_DATASET_METADATA["dct:rights"])
        self.assertEqual(
            metadata.update_frequency, TEST_DATASET_METADATA["dct:accrualPeriodicity"]
        )
        self.assertEqual(
            metadata.start_date, datetime(2019, 3, 27, 0, 0, tzinfo=tzutc())
        )
        self.assertEqual(metadata.end_date, datetime(2021, 3, 27, 0, 0, tzinfo=tzutc()))

    def test_parse_dataset_metadata_no_optional_values(self):
        """Tests parsing of a dataset's metadata while all values that can
        be missing are"""

        # Here will only test those that should be missing (rest are tested
        # above anyway)
        metadata = parse_dataset_metadata(TEST_DATASET_METADATA_DEFAULT)

        self.assertEqual(metadata.rights, None)
        self.assertEqual(metadata.update_frequency, None)
        self.assertEqual(metadata.start_date, None)
        self.assertEqual(metadata.end_date, None)

    @patch.object(DatasetMetadata, "output_metadata_extra_details")
    @patch.object(DatasetMetadata, "output_datafiles_table")
    @patch("dafni_cli.datasets.dataset_metadata.prose_print")
    @patch("dafni_cli.datasets.dataset_metadata.click")
    def test_output_metadata_details(
        self,
        mock_click,
        mock_prose,
        mock_table,
        mock_extra_details,
    ):
        """Tests output_metadata_details functions as expected"""

        # SETUP
        dataset_metadata: DatasetMetadata = parse_dataset_metadata(
            TEST_DATASET_METADATA
        )

        # CALL
        dataset_metadata.output_metadata_details()

        # ASSERT
        mock_click.echo.assert_has_calls(
            [
                call(f"\nCreated: {dataset_metadata.created}"),
                call(f"Creator: {dataset_metadata.creators[0].name}"),
                call(f"Contact: {dataset_metadata.contact}"),
                call("Description:"),
                call("Identifiers:"),
                call(f"Location: {dataset_metadata.location.label}"),
                call(f"Start date: {dataset_metadata.start_date.strftime('%B %d %Y')}"),
                call(f"End date: {dataset_metadata.end_date.strftime('%B %d %Y')}"),
                call(f"Key words:\n {dataset_metadata.keywords}"),
            ]
        )
        mock_prose.assert_has_calls(
            [
                call(dataset_metadata.description, CONSOLE_WIDTH),
                call(" ".join(dataset_metadata.identifiers), CONSOLE_WIDTH),
            ]
        )

        mock_table.assert_has_calls([call()])
        mock_extra_details.assert_not_called()

    @patch.object(DatasetMetadata, "output_metadata_extra_details")
    @patch.object(DatasetMetadata, "output_datafiles_table")
    @patch("dafni_cli.datasets.dataset_metadata.prose_print")
    @patch("dafni_cli.datasets.dataset_metadata.click")
    def test_output_metadata_details_when_start_and_end_date_are_None(
        self,
        mock_click,
        mock_prose,
        mock_table,
        mock_extra_details,
    ):
        """Tests output_metadata_details functions as expected"""

        # SETUP
        dataset_metadata: DatasetMetadata = parse_dataset_metadata(
            TEST_DATASET_METADATA
        )
        dataset_metadata.start_date = None
        dataset_metadata.end_date = None

        # CALL
        dataset_metadata.output_metadata_details()

        # ASSERT
        mock_click.echo.assert_has_calls(
            [
                call(f"\nCreated: {dataset_metadata.created}"),
                call(f"Creator: {dataset_metadata.creators[0].name}"),
                call(f"Contact: {dataset_metadata.contact}"),
                call("Description:"),
                call("Identifiers:"),
                call(f"Location: {dataset_metadata.location.label}"),
                call(f"Start date: None"),
                call(f"End date: None"),
                call(f"Key words:\n {dataset_metadata.keywords}"),
            ]
        )
        mock_prose.assert_has_calls(
            [
                call(dataset_metadata.description, CONSOLE_WIDTH),
                call(" ".join(dataset_metadata.identifiers), CONSOLE_WIDTH),
            ]
        )

        mock_table.assert_has_calls([call()])
        mock_extra_details.assert_not_called()

    @patch.object(DatasetMetadata, "output_metadata_extra_details")
    @patch.object(DatasetMetadata, "output_datafiles_table")
    @patch("dafni_cli.datasets.dataset_metadata.prose_print")
    @patch("dafni_cli.datasets.dataset_metadata.click")
    def test_output_metadata_details_when_long_set_to_true(
        self,
        mock_click,
        mock_prose,
        mock_table,
        mock_extra_details,
    ):
        """Tests output_metadata_details functions as expected when 'long'
        is True"""
        # SETUP
        dataset_metadata: DatasetMetadata = parse_dataset_metadata(
            TEST_DATASET_METADATA
        )

        # CALL
        dataset_metadata.output_metadata_details(long=True)

        # ASSERT
        mock_extra_details.assert_called_once()

    @patch("dafni_cli.datasets.dataset_metadata.output_table")
    @patch("dafni_cli.datasets.dataset_metadata.click")
    def test_output_datafiles_table(self, mock_click, mock_output_table):
        """Tests output_datafiles_table functions as expected"""
        # SETUP
        dataset_metadata: DatasetMetadata = parse_dataset_metadata(
            TEST_DATASET_METADATA
        )

        # CALL
        dataset_metadata.output_datafiles_table()

        # ASSERT
        columns = ["Name", "Size", "Format"]
        name_width = max([len(datafile.name) for datafile in dataset_metadata.files])
        widths = [name_width, 10, 6]
        rows = [
            [datafile.name, datafile.size, datafile.format]
            for datafile in dataset_metadata.files
        ]
        mock_output_table.assert_called_once_with(columns, widths, rows)
        mock_click.echo.assert_has_calls(
            [call("\nData Files"), call(mock_output_table.return_value)]
        )

    @patch("dafni_cli.datasets.dataset_metadata.prose_print")
    @patch("dafni_cli.datasets.dataset_metadata.click")
    def test_output_metadata_extra_details(self, mock_click, mock_prose_print):
        """Tests test_output_metadata_extra_details functions as expected"""
        # SETUP
        dataset_metadata: DatasetMetadata = parse_dataset_metadata(
            TEST_DATASET_METADATA
        )

        # CALL
        dataset_metadata.output_metadata_extra_details()

        # ASSERT
        mock_click.echo.assert_has_calls(
            [
                call(f"Themes:\n{dataset_metadata.themes}"),
                call(f"Publisher: {dataset_metadata.publisher}"),
                call(f"Issued: {dataset_metadata.issued}"),
                call("Rights:"),
                call(f"Language: {dataset_metadata.language}"),
                call(f"Standard: {dataset_metadata.standard}"),
                call(f"Update Frequency: {dataset_metadata.update_frequency}"),
            ]
        )

        mock_prose_print.assert_called_once_with(dataset_metadata.rights, CONSOLE_WIDTH)

    @patch("dafni_cli.datasets.dataset_metadata.prose_print")
    @patch("dafni_cli.datasets.dataset_metadata.click")
    def test_output_version_details(self, mock_click, mock_prose_print):
        """Tests test_output_version_details functions as expected"""
        # SETUP
        dataset_metadata: DatasetMetadata = parse_dataset_metadata(
            TEST_DATASET_METADATA
        )

        # CALL
        dataset_metadata.output_version_details()

        # ASSERT
        mock_click.echo.assert_has_calls(
            [
                call(f"\nTitle: {dataset_metadata.title}"),
                call(f"ID: {dataset_metadata.dataset_id}"),
                call(f"Version ID: {dataset_metadata.version_id}"),
                call(f"Publisher: {dataset_metadata.publisher}"),
                call(
                    f"From: {dataset_metadata.start_date}{TAB_SPACE}To: {dataset_metadata.end_date}"
                ),
                call("Description: "),
            ]
        )

        mock_prose_print.assert_called_once_with(
            dataset_metadata.description, CONSOLE_WIDTH
        )

    @patch.object(DataFile, "download_contents")
    def test_download_dataset_files_returns_empty_arrays_when_no_files(
        self, mock_download
    ):
        """Tests download_dataset_files functions as expected when there are
        no files to download"""
        # SETUP
        dataset_metadata: DatasetMetadata = parse_dataset_metadata(
            TEST_DATASET_METADATA
        )
        dataset_metadata.files = []
        session = MagicMock()

        # CALL
        file_names, file_contents = dataset_metadata.download_dataset_files(session)

        # ASSERT
        mock_download.assert_not_called()

        self.assertEqual(file_names, [])
        self.assertEqual(file_contents, [])

    @patch.object(DataFile, "download_contents")
    def test_download_dataset_files(self, mock_download):
        """Tests download_dataset_files functions as expected"""
        # SETUP
        dataset_metadata: DatasetMetadata = parse_dataset_metadata(
            TEST_DATASET_METADATA
        )
        session = MagicMock()

        # CALL
        file_names, file_contents = dataset_metadata.download_dataset_files(session)

        # ASSERT
        mock_download.assert_has_calls([call(session)])

        self.assertEqual(file_names, [dataset_metadata.files[0].name])
        self.assertEqual(file_contents, [dataset_metadata.files[0].contents])

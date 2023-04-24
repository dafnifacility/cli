from datetime import datetime
from typing import List
from unittest import TestCase

from dateutil.tz import tzutc

from dafni_cli.api.parser import ParserBaseObject
from dafni_cli.consts import DATA_FORMATS
from dafni_cli.datasets.dataset_metadata import (
    Contact,
    Creator,
    DataFile,
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
TEST_DATASET_METADATA_DATAFILES: List[dict] = [
    {
        "spdx:fileName": "workflow_def.csv",
        "dcat:mediaType": "text/csv",
        "dcat:byteSize": 6720,
        "dcat:downloadURL": "url/to/file",
    }
]

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
        }
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
    "dcat:distribution": TEST_DATASET_METADATA_DATAFILES,
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
    "dcat:distribution": TEST_DATASET_METADATA_DATAFILES,
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

        datafiles: List[DataFile] = ParserBaseObject.parse_from_dict_list(
            DataFile, TEST_DATASET_METADATA_DATAFILES
        )

        for datafile, dictionary in zip(datafiles, TEST_DATASET_METADATA_DATAFILES):
            self.assertEqual(datafile.name, dictionary["spdx:fileName"])
            self.assertEqual(
                datafile.size,
                process_file_size(dictionary["dcat:byteSize"]),
            )
            self.assertEqual(
                datafile.format,
                DATA_FORMATS.get(dictionary["dcat:mediaType"], "Unknown"),
            )
            self.assertEqual(datafile.download_url, dictionary["dcat:downloadURL"])


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
        self.assertEqual(len(version_history.versions), 1)
        self.assertEqual(
            version_history.versions[0].version_id,
            TEST_DATASET_METADATA_VERSION_HISTORY["versions"][0]["version_uuid"],
        )
        self.assertEqual(len(version_history.versions[0].metadata_versions), 2)
        # Version 1
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

        # Version 2
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

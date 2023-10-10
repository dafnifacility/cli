from datetime import datetime
from unittest import TestCase
from unittest.mock import call, patch

from dateutil.tz import tzutc

from dafni_cli.api.auth import Auth
from dafni_cli.api.parser import ParserBaseObject
from dafni_cli.consts import (
    CONSOLE_WIDTH,
    TABLE_MODIFIED_HEADER,
    TABLE_VERSION_ID_HEADER,
    TABLE_VERSION_MESSAGE_HEADER,
)
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
from dafni_cli.tests.fixtures.dataset_metadata import (
    TEST_DATASET_METADATA,
    TEST_DATASET_METADATA_CONTACT,
    TEST_DATASET_METADATA_CONTACT_DEFAULT,
    TEST_DATASET_METADATA_CREATOR,
    TEST_DATASET_METADATA_CREATOR_DEFAULT,
    TEST_DATASET_METADATA_DATAFILE,
    TEST_DATASET_METADATA_DATAFILE_DEFAULT,
    TEST_DATASET_METADATA_DEFAULT,
    TEST_DATASET_METADATA_LOCATION,
    TEST_DATASET_METADATA_LOCATION_DEFAULT,
    TEST_DATASET_METADATA_PUBLISHER,
    TEST_DATASET_METADATA_PUBLISHER_DEFAULT,
    TEST_DATASET_METADATA_STANDARD,
    TEST_DATASET_METADATA_STANDARD_DEFAULT,
    TEST_DATASET_METADATA_VERSION_HISTORY,
)
from dafni_cli.utils import format_data_format, format_datetime, format_file_size


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
            TEST_DATASET_METADATA_DATAFILE["dcat:byteSize"],
        )
        self.assertEqual(
            datafile.format, TEST_DATASET_METADATA_DATAFILE["dcat:mediaType"]
        )
        self.assertEqual(
            datafile.download_url, TEST_DATASET_METADATA_DATAFILE["dcat:downloadURL"]
        )

    def test_parse_default(self):
        """Tests parsing of data files"""

        datafile: DataFile = ParserBaseObject.parse_from_dict(
            DataFile, TEST_DATASET_METADATA_DATAFILE_DEFAULT
        )

        self.assertEqual(
            datafile.name, TEST_DATASET_METADATA_DATAFILE_DEFAULT["spdx:fileName"]
        )
        self.assertEqual(
            datafile.size,
            TEST_DATASET_METADATA_DATAFILE_DEFAULT["dcat:byteSize"],
        )
        self.assertEqual(
            datafile.format,
            None,
        )
        self.assertEqual(datafile.download_url, None)


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

    def test_parse_default(self):
        """Tests parsing of contact with optional values ignored"""

        contact: Contact = ParserBaseObject.parse_from_dict(
            Contact, TEST_DATASET_METADATA_CONTACT_DEFAULT
        )
        self.assertEqual(contact.type, TEST_DATASET_METADATA_CONTACT["@type"])
        self.assertEqual(contact.name, None)
        self.assertEqual(contact.email, None)

    def test_string_conversion(self):
        """Tests converting a contact to a string works correctly"""
        contact: Contact = ParserBaseObject.parse_from_dict(
            Contact, TEST_DATASET_METADATA_CONTACT_DEFAULT
        )

        # No contact info
        self.assertEqual(str(contact), "N/A")

        # Just a name
        contact.name = "Some name"
        self.assertEqual(str(contact), "Some name")

        # Just an email
        contact.name = None
        contact.email = "Some email"
        self.assertEqual(str(contact), "Some email")

        # Both a name and an email
        contact.name = "Some name"
        contact.email = "Some email"
        self.assertEqual(str(contact), "Some name, Some email")


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

    def test_parse_when_no_optional_values(self):
        """Tests parsing of Location with optional values ignored"""

        location: Location = ParserBaseObject.parse_from_dict(
            Location, TEST_DATASET_METADATA_LOCATION_DEFAULT
        )
        self.assertEqual(location.id, None)
        self.assertEqual(location.type, TEST_DATASET_METADATA_LOCATION["@type"])
        self.assertEqual(location.label, None)


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

    def test_string_conversion(self):
        """Tests converting a publisher to a string works correctly"""
        publisher: Publisher = ParserBaseObject.parse_from_dict(
            Publisher, TEST_DATASET_METADATA_PUBLISHER_DEFAULT
        )

        # No publisher info
        self.assertEqual(str(publisher), "N/A")

        # With a name
        publisher.name = "Some name"
        self.assertEqual(str(publisher), "Some name")


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
        self.assertEqual(standard.type, None)
        self.assertEqual(standard.id, None)
        self.assertEqual(standard.label, None)

    def test_string_conversion(self):
        """Tests converting a Standard to a string works correctly"""
        standard: Standard = ParserBaseObject.parse_from_dict(
            Standard, TEST_DATASET_METADATA_STANDARD_DEFAULT
        )

        # No standard info
        self.assertEqual(str(standard), "N/A")

        # With a label
        standard.label = "Some label"
        self.assertEqual(str(standard), "Some label")


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
            version_history.versions[0].metadata_versions[0].modified_date,
            datetime(2021, 3, 17, 9, 27, 21, tzinfo=tzutc()),
        )
        self.assertEqual(
            version_history.versions[0].metadata_versions[0].version_message,
            TEST_DATASET_METADATA_VERSION_HISTORY["versions"][0]["metadata_versions"][
                0
            ]["dafni_version_note"],
        )

        # Version 1, Metadata Version 2
        self.assertEqual(
            version_history.versions[0].metadata_versions[1].metadata_id,
            TEST_DATASET_METADATA_VERSION_HISTORY["versions"][0]["metadata_versions"][
                1
            ]["metadata_uuid"],
        )
        self.assertEqual(
            version_history.versions[0].metadata_versions[1].modified_date,
            datetime(2021, 3, 16, 9, 27, 21, tzinfo=tzutc()),
        )
        self.assertEqual(
            version_history.versions[0].metadata_versions[1].version_message,
            TEST_DATASET_METADATA_VERSION_HISTORY["versions"][0]["metadata_versions"][
                1
            ]["dafni_version_note"],
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
            version_history.versions[1].metadata_versions[0].modified_date,
            datetime(2021, 3, 16, 9, 27, 21, tzinfo=tzutc()),
        )
        self.assertEqual(
            version_history.versions[1].metadata_versions[0].version_message,
            TEST_DATASET_METADATA_VERSION_HISTORY["versions"][1]["metadata_versions"][
                0
            ]["dafni_version_note"],
        )

    @patch("dafni_cli.datasets.dataset_metadata.format_table")
    @patch("dafni_cli.datasets.dataset_metadata.click")
    def test_output_version_history(
        self,
        mock_click,
        mock_format_table,
    ):
        """Tests output_version_history works correctly"""

        # SETUP
        version_history: DatasetVersionHistory = ParserBaseObject.parse_from_dict(
            DatasetVersionHistory, TEST_DATASET_METADATA_VERSION_HISTORY
        )

        # CALL
        version_history.output_version_history()

        # ASSERT
        mock_format_table.assert_called_once_with(
            headers=[
                TABLE_VERSION_ID_HEADER,
                TABLE_MODIFIED_HEADER,
                TABLE_VERSION_MESSAGE_HEADER,
            ],
            rows=[
                [
                    "0a0a0a0a-0a00-0a00-a000-0a0a0000000b",
                    format_datetime(
                        datetime(2021, 3, 17, 9, 27, 21), include_time=True
                    ),
                    "Second Dataset version",
                ],
                [
                    "0a0a0a0a-0a00-0a00-a000-0a0a0000000c",
                    format_datetime(
                        datetime(2021, 3, 16, 9, 27, 21), include_time=True
                    ),
                    "Initial Dataset version",
                ],
            ],
        )
        mock_click.echo.assert_called_once_with(mock_format_table.return_value)


class TestDatasetMetadataTestCase(TestCase):
    """Tests the DatasetMetadata dataclass"""

    def test_parse_dataset_metadata(self):
        """Tests parsing of a dataset's metadata"""
        metadata = parse_dataset_metadata(TEST_DATASET_METADATA)

        self.assertEqual(metadata.title, TEST_DATASET_METADATA["metadata"]["dct:title"])
        self.assertEqual(
            metadata.description, TEST_DATASET_METADATA["metadata"]["dct:description"]
        )
        self.assertEqual(
            metadata.subject, TEST_DATASET_METADATA["metadata"]["dct:subject"]
        )
        self.assertEqual(metadata.created, datetime(2021, 3, 16, 0, 0))

        # Creators (Contents tested in TestCreator)
        self.assertEqual(len(metadata.creators), 2)
        self.assertEqual(type(metadata.creators[0]), Creator)

        # Contact (Contents tested in TestContact)
        self.assertEqual(type(metadata.contact), Contact)

        # Location (Contents tested in TestLocation)
        self.assertEqual(type(metadata.location), Location)

        self.assertEqual(
            metadata.keywords, TEST_DATASET_METADATA["metadata"]["dcat:keyword"]
        )

        self.assertEqual(
            metadata.modified, datetime(2021, 3, 16, 9, 27, 21, tzinfo=tzutc())
        )
        self.assertEqual(
            metadata.issued, datetime(2021, 3, 16, 9, 27, 21, tzinfo=tzutc())
        )
        self.assertEqual(
            metadata.language, TEST_DATASET_METADATA["metadata"]["dct:language"]
        )

        self.assertEqual(
            metadata.asset_id, TEST_DATASET_METADATA["metadata"]["@id"]["asset_id"]
        )
        self.assertEqual(
            metadata.dataset_id,
            TEST_DATASET_METADATA["metadata"]["@id"]["dataset_uuid"],
        )
        self.assertEqual(
            metadata.version_id,
            TEST_DATASET_METADATA["metadata"]["@id"]["version_uuid"],
        )
        self.assertEqual(
            metadata.metadata_id,
            TEST_DATASET_METADATA["metadata"]["@id"]["metadata_uuid"],
        )

        # Auth tested in test_auth anyway
        self.assertEqual(type(metadata.auth), Auth)

        # Files (Contents tested in TestDataFile)
        self.assertEqual(len(metadata.files), 1)
        self.assertEqual(type(metadata.files[0]), DataFile)

        self.assertEqual(metadata.status, TEST_DATASET_METADATA["status"])

        self.assertEqual(
            metadata.version_message,
            TEST_DATASET_METADATA["metadata"]["dafni_version_note"],
        )

        # Version history (Contents tested in TestVersionHistory)
        self.assertEqual(type(metadata.version_history), DatasetVersionHistory)

        self.assertEqual(
            metadata.identifiers, TEST_DATASET_METADATA["metadata"]["dct:identifier"]
        )
        self.assertEqual(
            metadata.themes, TEST_DATASET_METADATA["metadata"]["dcat:theme"]
        )

        # Standard (Contents tested in TestStandard)
        self.assertEqual(type(metadata.standard), Standard)

        # Publisher (Contents tested in TestPublisher)
        self.assertEqual(type(metadata.publisher), Publisher)

        self.assertEqual(
            metadata.rights, TEST_DATASET_METADATA["metadata"]["dct:rights"]
        )
        self.assertEqual(
            metadata.update_frequency,
            TEST_DATASET_METADATA["metadata"]["dct:accrualPeriodicity"],
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

        self.assertEqual(metadata.version_message, None)
        self.assertEqual(metadata.identifiers, [])
        self.assertEqual(metadata.themes, [])
        self.assertEqual(metadata.standard, None)
        self.assertEqual(metadata.publisher, None)
        self.assertEqual(metadata.rights, None)
        self.assertEqual(metadata.update_frequency, None)
        self.assertEqual(metadata.start_date, None)
        self.assertEqual(metadata.end_date, None)

    @patch.object(DatasetMetadata, "output_additional_metadata")
    @patch.object(DatasetMetadata, "output_datafiles_table")
    @patch("dafni_cli.datasets.dataset_metadata.prose_print")
    @patch("dafni_cli.datasets.dataset_metadata.click")
    def test_output_details(
        self,
        mock_click,
        mock_prose,
        mock_output_datafiles_table,
        mock_output_additional_metadata,
    ):
        """Tests output_details functions as expected"""

        # SETUP
        dataset_metadata: DatasetMetadata = parse_dataset_metadata(
            TEST_DATASET_METADATA
        )

        # CALL
        dataset_metadata.output_details()

        # ASSERT
        self.assertEqual(
            mock_click.echo.mock_calls,
            [
                call(dataset_metadata.title),
                call(f"Subject: {dataset_metadata.subject}"),
                call(f"Version ID: {dataset_metadata.version_id}"),
                call(""),
                call(
                    f"Created: {format_datetime(dataset_metadata.created, include_time=True)}"
                ),
                call(f"Creator: {dataset_metadata.creators[0].name}"),
                call(f"Contact: {dataset_metadata.contact}"),
                call(""),
                call("Description:"),
                call(""),
                call("Identifier(s):"),
                call(f"Location: {dataset_metadata.location.label}"),
                call(
                    f"Start date: {format_datetime(dataset_metadata.start_date, include_time=False)}"
                ),
                call(
                    f"End date: {format_datetime(dataset_metadata.end_date, include_time=False)}"
                ),
                call(""),
                call("Keywords:"),
                call(", ".join(dataset_metadata.keywords)),
            ],
        )
        mock_prose.assert_has_calls(
            [
                call(dataset_metadata.description, CONSOLE_WIDTH),
                call(" ".join(dataset_metadata.identifiers), CONSOLE_WIDTH),
            ]
        )

        mock_output_datafiles_table.assert_has_calls([call()])
        mock_output_additional_metadata.assert_not_called()

    @patch.object(DatasetMetadata, "output_additional_metadata")
    @patch.object(DatasetMetadata, "output_datafiles_table")
    @patch("dafni_cli.datasets.dataset_metadata.prose_print")
    @patch("dafni_cli.datasets.dataset_metadata.click")
    def test_output_details_when_optional_values_are_None(
        self,
        mock_click,
        mock_prose,
        mock_output_datafiles_table,
        mock_output_additional_metadata,
    ):
        """Tests output_details functions as expected when various optional
        values are None"""

        # SETUP
        dataset_metadata: DatasetMetadata = parse_dataset_metadata(
            TEST_DATASET_METADATA
        )
        dataset_metadata.start_date = None
        dataset_metadata.end_date = None
        dataset_metadata.identifiers = None

        # CALL
        dataset_metadata.output_details()

        # ASSERT
        self.assertEqual(
            mock_click.echo.mock_calls,
            [
                call(dataset_metadata.title),
                call(f"Subject: {dataset_metadata.subject}"),
                call(f"Version ID: {dataset_metadata.version_id}"),
                call(""),
                call(
                    f"Created: {format_datetime(dataset_metadata.created, include_time=True)}"
                ),
                call(f"Creator: {dataset_metadata.creators[0].name}"),
                call(f"Contact: {dataset_metadata.contact}"),
                call(""),
                call("Description:"),
                call(""),
                call("Identifier(s):"),
                call(f"Location: {dataset_metadata.location.label}"),
                call("Start date: N/A"),
                call("End date: N/A"),
                call(""),
                call("Keywords:"),
                call(", ".join(dataset_metadata.keywords)),
            ],
        )
        mock_prose.assert_has_calls(
            [
                call(dataset_metadata.description, CONSOLE_WIDTH),
                call("N/A", CONSOLE_WIDTH),
            ]
        )

        mock_output_datafiles_table.assert_has_calls([call()])
        mock_output_additional_metadata.assert_not_called()

    @patch.object(DatasetMetadata, "output_additional_metadata")
    @patch.object(DatasetMetadata, "output_datafiles_table")
    @patch("dafni_cli.datasets.dataset_metadata.prose_print")
    @patch("dafni_cli.datasets.dataset_metadata.click")
    def test_output_details_when_long_set_to_true(
        self,
        mock_click,
        mock_prose,
        mock_output_datafiles_table,
        mock_output_additional_metadata,
    ):
        """Tests output_details functions as expected when 'long'
        is True"""
        # SETUP
        dataset_metadata: DatasetMetadata = parse_dataset_metadata(
            TEST_DATASET_METADATA
        )
        dataset_metadata.start_date = None
        dataset_metadata.end_date = None
        dataset_metadata.identifiers = None

        # CALL
        dataset_metadata.output_details(long=True)

        # ASSERT
        self.assertEqual(
            mock_click.echo.mock_calls,
            [
                call(dataset_metadata.title),
                call(f"Subject: {dataset_metadata.subject}"),
                call(f"Version ID: {dataset_metadata.version_id}"),
                call(""),
                call(
                    f"Created: {format_datetime(dataset_metadata.created, include_time=True)}"
                ),
                call(f"Creator: {dataset_metadata.creators[0].name}"),
                call(f"Contact: {dataset_metadata.contact}"),
                call(""),
                call("Description:"),
                call(""),
                call("Identifier(s):"),
                call(f"Location: {dataset_metadata.location.label}"),
                call("Start date: N/A"),
                call("End date: N/A"),
                call(""),
                call(""),
                call("Keywords:"),
                call(", ".join(dataset_metadata.keywords)),
            ],
        )
        mock_prose.assert_has_calls(
            [
                call(dataset_metadata.description, CONSOLE_WIDTH),
                call("N/A", CONSOLE_WIDTH),
            ]
        )

        mock_output_datafiles_table.assert_has_calls([call()])
        mock_output_additional_metadata.assert_called_once()

    @patch("dafni_cli.datasets.dataset_metadata.format_table")
    @patch("dafni_cli.datasets.dataset_metadata.click")
    def test_output_datafiles_table(self, mock_click, mock_format_table):
        """Tests output_datafiles_table functions as expected"""
        # SETUP
        dataset_metadata: DatasetMetadata = parse_dataset_metadata(
            TEST_DATASET_METADATA
        )

        # CALL
        dataset_metadata.output_datafiles_table()

        # ASSERT
        headers = ["Name", "Size", "Format"]
        rows = [
            [
                datafile.name,
                format_file_size(datafile.size),
                format_data_format(datafile.format),
            ]
            for datafile in dataset_metadata.files
        ]
        mock_format_table.assert_called_once_with(headers=headers, rows=rows)
        mock_click.echo.assert_has_calls(
            [call("\nData files:"), call(mock_format_table.return_value)]
        )

    @patch("dafni_cli.datasets.dataset_metadata.tabulate")
    @patch("dafni_cli.datasets.dataset_metadata.click")
    def test_output_additional_metadata(self, mock_click, mock_tabulate):
        """Tests test_output_additional_metadata functions as expected"""
        # SETUP
        dataset_metadata: DatasetMetadata = parse_dataset_metadata(
            TEST_DATASET_METADATA
        )

        # CALL
        dataset_metadata.output_additional_metadata()

        # ASSERT
        mock_click.echo.assert_has_calls(
            [call("Additional metadata:"), call(mock_tabulate.return_value)]
        )

        mock_tabulate.assert_called_once_with(
            [
                ["Theme(s):", ", ".join(dataset_metadata.themes)],
                ["Publisher:", dataset_metadata.publisher.name],
                [
                    "Last updated:",
                    format_datetime(dataset_metadata.modified, include_time=False),
                ],
                ["Rights:", dataset_metadata.rights],
                ["Language:", dataset_metadata.language],
                ["Standard:", str(dataset_metadata.standard)],
                ["Update frequency:", dataset_metadata.update_frequency],
            ],
            tablefmt="plain",
        )

    @patch("dafni_cli.datasets.dataset_metadata.tabulate")
    @patch("dafni_cli.datasets.dataset_metadata.click")
    def test_output_additional_metadata_when_optional_values_are_None(
        self, mock_click, mock_tabulate
    ):
        """Tests test_output_additional_metadata functions as expected when
        all optional values are None"""
        # SETUP
        dataset_metadata: DatasetMetadata = parse_dataset_metadata(
            TEST_DATASET_METADATA
        )
        dataset_metadata.publisher.name = None
        dataset_metadata.rights = None
        dataset_metadata.standard = None
        dataset_metadata.update_frequency = None

        # CALL
        dataset_metadata.output_additional_metadata()

        # ASSERT
        mock_click.echo.assert_has_calls(
            [call("Additional metadata:"), call(mock_tabulate.return_value)]
        )

        mock_tabulate.assert_called_once_with(
            [
                ["Theme(s):", ", ".join(dataset_metadata.themes)],
                ["Publisher:", "N/A"],
                [
                    "Last updated:",
                    format_datetime(dataset_metadata.modified, include_time=False),
                ],
                ["Rights:", "N/A"],
                ["Language:", dataset_metadata.language],
                ["Standard:", "N/A"],
                ["Update frequency:", "N/A"],
            ],
            tablefmt="plain",
        )

    def test_get_details(self):
        """Tests get_details functions as expected"""
        # SETUP
        dataset_metadata: DatasetMetadata = parse_dataset_metadata(
            TEST_DATASET_METADATA
        )

        # CALL
        result = dataset_metadata.get_details()

        # ASSERT
        self.assertEqual(
            result,
            f"Title: {dataset_metadata.title}\n"
            f"ID: {dataset_metadata.dataset_id}\n"
            f"Created: {format_datetime(dataset_metadata.created, include_time=True)}\n"
            f"Publisher: {dataset_metadata.publisher.name}\n"
            f"Version IDs:\n"
            f"{dataset_metadata.version_history.versions[0].version_id}\n"
            f"{dataset_metadata.version_history.versions[1].version_id}\n",
        )

    def test_get_version_details(self):
        """Tests get_version_details functions as expected"""
        # SETUP
        dataset_metadata: DatasetMetadata = parse_dataset_metadata(
            TEST_DATASET_METADATA
        )

        # CALL
        result = dataset_metadata.get_version_details()

        # ASSERT
        self.assertEqual(
            result,
            f"Title: {dataset_metadata.title}\n"
            f"Version ID: {dataset_metadata.version_id}\n"
            f"Created: {format_datetime(dataset_metadata.created, include_time=True)}\n"
            f"Publisher: {dataset_metadata.publisher.name}\n",
        )

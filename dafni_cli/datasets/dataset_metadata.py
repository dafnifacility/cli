from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from typing import ClassVar, List, Optional, Tuple

import click

from dafni_cli.api.datasets_api import get_latest_dataset_metadata
from dafni_cli.api.minio_api import minio_get_request
from dafni_cli.api.parser import ParserBaseObject, ParserParam, parse_datetime
from dafni_cli.api.session import DAFNISession
from dafni_cli.consts import (
    CONSOLE_WIDTH,
    DATA_FORMATS,
    OUTPUT_UNKNOWN_FORMAT,
    TAB_SPACE,
)
from dafni_cli.utils import (
    format_datetime,
    format_table,
    print_json,
    process_file_size,
    prose_print,
)


@dataclass
class DataFile(ParserBaseObject):
    """Dataclass representing a DAFNI dataset file

    Methods:
        download_contents(session: DAFNISession): Downloads the files contents

    Attributes:
        name (str): File name
        size (str): File size
        format (str): File format (Defaults to OUTPUT_UNKNOWN_FORMAT if not
                      known)
        download_url (str): File download url
        contents (BytesIO): Downloaded file contents (only assigned after
                            download_contents called)
    """

    name: str
    size: str
    format: str = OUTPUT_UNKNOWN_FORMAT
    download_url: str = None

    # Separate - only used when actually downloading
    contents: Optional[BytesIO] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("name", "spdx:fileName", str),
        ParserParam("size", "dcat:byteSize", process_file_size),
        ParserParam(
            "format",
            "dcat:mediaType",
            lambda value: DATA_FORMATS.get(value, OUTPUT_UNKNOWN_FORMAT),
        ),
        ParserParam("download_url", "dcat:downloadURL", str),
    ]

    def download_contents(self, session: DAFNISession):
        """Downloads the file using the download_url and saves the contents as
        a BytesIO object to self.contents

        Args:
            session (DAFNISession): User session
        """
        self.contents = BytesIO(
            minio_get_request(session, self.download_url, content=True)
        )


@dataclass
class Creator(ParserBaseObject):
    """Dataclass representing a creator listed in a dataset's metadata

    Attributes:
        type (str): Creator type
        name (str): Creator name
        id (Optional[str]): Creator id
    """

    type: str
    name: str
    id: Optional[str] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("type", "@type", str),
        ParserParam("name", "foaf:name", str),
        ParserParam("id", "@id", str),
    ]


@dataclass
class Contact(ParserBaseObject):
    """Dataclass representing the contact listed in a dataset's metadata

    Attributes:
        type (str): Contact type
        name (str): Contact name
        email (str): Contact email
    """

    type: str
    name: str
    email: str

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("type", "@type", str),
        ParserParam("name", "vcard:fn", str),
        ParserParam("email", "vcard:hasEmail", str),
    ]

    def __str__(self) -> str:
        """Nicer string representation for printing"""
        return f"{self.name}, {self.email}"


@dataclass
class Location(ParserBaseObject):
    """Dataclass representing the contact listed in a dataset's metadata

    Attributes:
        type (str): Location type
        id (Optional[str]): Location id
        label (Optional[str]): Location label
    """

    type: str
    id: Optional[str] = None
    label: Optional[str] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("type", "@type", str),
        ParserParam("id", "@id", str),
        ParserParam("label", "rdfs:label", str),
    ]


@dataclass
class Publisher(ParserBaseObject):
    """Dataclass representing the publisher listed in a dataset's metadata

    Attributes:
        type (str or None): Publisher type
        id (str or None): Publisher id
        name (str or None): Publisher name
    """

    type: str
    id: Optional[str] = None
    name: Optional[str] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("type", "@type", str),
        ParserParam("id", "@id", str),
        ParserParam("name", "foaf:name", str),
    ]

    def __str__(self) -> str:
        """Nicer string representation for printing"""
        return f"{self.name}"


@dataclass
class Standard(ParserBaseObject):
    """Dataclass representing the standard listed in a dataset's metadata

    Attributes:
        type (Optional[str]): Standard type
        id (Optional[str]): Standard id
        label (Optional[str]): Standard label
    """

    type: Optional[str] = None
    id: Optional[str] = None
    label: Optional[str] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("type", "@type", str),
        ParserParam("id", "@id", str),
        ParserParam("label", "label", str),
    ]

    def __str__(self) -> str:
        """Nicer string representation for printing"""
        return f"{self.label}"


@dataclass
class DatasetMetadataVersion(ParserBaseObject):
    """Dataclass representing a metadata version listed in a dataset's
    version_history

    Attributes:
        metadata_id (str): ID of this version of the metadata
        modified_date (datetime): Time and date of last modification of this
                                  version
        label (Optional[str]): Label of the metadata version
    """

    metadata_id: str
    modified_date: datetime
    label: Optional[str] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("metadata_id", "metadata_uuid", str),
        ParserParam("modified_date", "modified_date", parse_datetime),
        ParserParam("label", "dafni_version_note", str),
    ]


@dataclass
class DatasetVersion(ParserBaseObject):
    """Dataclass representing a specific dataset version listed under a
       dataset's metadata version_history

    Attributes:
        version_id (str): ID of this version of the dataset
        metadata_versions (List[DatasetMetadataVersion): List of metadata
                              versions under this version of the dataset
    """

    version_id: str
    metadata_versions: List[DatasetMetadataVersion]

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("version_id", "version_uuid", str),
        ParserParam("metadata_versions", "metadata_versions", DatasetMetadataVersion),
    ]


@dataclass
class DatasetVersionHistory(ParserBaseObject):
    """Dataclass for processing the version history of a dataset

    Methods:
        process_and_output_version_history(session: DAFNISession, json_flag: bool): Iterates through all versions and outputs details

    Attributes:
        session (DAFNISession): User session
        dataset_id (str): Dataset ID
        versions (List[dict]): List of associated Version dicts
        version_ids (List[str]): List of Version IDs
    """

    dataset_id: str
    versions: List[DatasetVersion]

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("dataset_id", "dataset_uuid", str),
        ParserParam("versions", "versions", DatasetVersion),
    ]

    def process_and_output_version_history(
        self, session: DAFNISession, json_flag: bool = False
    ):
        """Iterates through all version history ID's, retrieves the associated
        dataset metadata, and outputs the version details or Dataset metadata
        json for each version to the command line.

        Args:
            json_flag (bool): Whether to print the Dataset metadata json for
                              each version, or the version details.
                              Default: False
        """
        json_list = []
        for version in self.versions:
            metadata = get_latest_dataset_metadata(session, version.version_id)
            if json_flag:
                json_list.append(metadata)
            else:
                dataset_meta: DatasetMetadata = ParserBaseObject.parse_from_dict(
                    DatasetMetadata, metadata
                )
                dataset_meta.output_version_details()
        if json_flag:
            print_json(json_list)


@dataclass
class DatasetMetadata(ParserBaseObject):
    """Dataclass representing a DAFNI dataset's metadata

    Methods:
        output_metadata_details(): Prints key information of the dataset metadata to console.
        output_datafiles_table(): Prints a table to the console of all File related information
        output_metadata_extra_details(): Prints extra details relating to the Dataset Metadata

    Attributes:
        title (str): Title of the dataset
        description (str): Description of the dataset
        subject (str): Subject of the dataset
        created (datetime): Date the dataset was created
        creators (List[Creator]): List of named creators of the dataset
        contact (Contact): Contact relating to the dataset
        identifier (str): List of identifiers relating to the dataset
        location (Location): Location the dataset relates to
        keywords (List[str]): Key words relating to the dataset e.g. Transportation
        themes (List[str]): Themes relating to dataset
        publisher (Publisher): Entity responsible for publishing the dataset
        issued (datetime): Date and time the dataset was issued
        language (str): The language used for the dataset
        standard (Standard): Any related standards associated
        asset_id (str): Asset identifier for dataset
        dataset_id (str): Dataset identifier
        version_id (str): Version identifier of the latest version of this
                          dataset
        metadata_id (str): Metadata identifier of the latest metadata for this
                           dataset
        files (List[DataFile]): Files associated with the dataset
        rights (List[str] or None): The user rights linked to the Dataset
        update_frequency (str or None): Update frequency if applicable
        start_date (datetime or None): Dataset start date if applicable
        end_date (datetime or None): Dataset end date if applicable
    """

    title: str
    description: str
    subject: str
    created: datetime
    creators: List[Creator]
    contact: Contact
    identifiers: List[str]
    location: Location
    keywords: List[str]
    themes: List[str]
    publisher: Publisher
    issued: datetime
    language: str
    standard: Standard
    asset_id: str
    dataset_id: str
    version_id: str
    metadata_id: str
    files: List[DataFile]
    version_history: DatasetVersionHistory
    rights: Optional[str] = None
    update_frequency: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("title", "dct:title", str),
        ParserParam("description", "dct:description", str),
        ParserParam("subject", "dct:subject", str),
        ParserParam("created", "dct:created", parse_datetime),
        ParserParam("creators", "dct:creator", Creator),
        ParserParam("contact", "dcat:contactPoint", Contact),
        ParserParam("identifiers", "dct:identifier"),
        ParserParam("location", "dct:spatial", Location),
        ParserParam("keywords", "dcat:keyword"),
        ParserParam("themes", "dcat:theme"),
        ParserParam("publisher", "dct:publisher", Publisher),
        ParserParam("issued", "dct:issued", parse_datetime),
        ParserParam("language", "dct:language", str),
        ParserParam("standard", "dct:conformsTo", Standard),
        ParserParam("asset_id", ["@id", "asset_id"], str),
        ParserParam("dataset_id", ["@id", "dataset_uuid"], str),
        ParserParam("version_id", ["@id", "version_uuid"], str),
        ParserParam("metadata_id", ["@id", "metadata_uuid"], str),
        ParserParam("files", "dcat:distribution", DataFile),
        ParserParam("version_history", "version_history", DatasetVersionHistory),
        ParserParam("rights", "dct:rights", str),
        ParserParam("update_frequency", "dct:accrualPeriodicity", str),
        ParserParam("end_date", ["dct:PeriodOfTime", "time:hasEnd"], parse_datetime),
        ParserParam(
            "start_date", ["dct:PeriodOfTime", "time:hasBeginning"], parse_datetime
        ),
    ]

    def output_metadata_details(self, long: bool = False):
        """Function to output details relating to the Dataset.
        The default behaviour is to print all standard metadata and
        a table relating to the associated files.
        If the long option is given, the additional metadata fields are
        also printed to the console

        Args:
            long (bool, optional): Flag to print additional metadata. Defaults to False.
        """
        click.echo(f"\nCreated: {format_datetime(self.created, include_time=True)}")
        click.echo(f"Creator: {self.creators[0].name}")
        click.echo(f"Contact: {self.contact}")
        click.echo("Description:")
        prose_print(self.description, CONSOLE_WIDTH)
        click.echo("Identifiers:")
        prose_print(
            " ".join(self.identifiers) if self.identifiers else "None", CONSOLE_WIDTH
        )
        click.echo(f"Location: {self.location.label}")
        click.echo(
            f"Start date: {format_datetime(self.start_date, include_time=False)}"
        )
        click.echo(f"End date: {format_datetime(self.end_date, include_time=False)}")
        click.echo(f"Key words:\n {self.keywords}")

        # DataFiles table
        self.output_datafiles_table()

        if long:
            self.output_metadata_extra_details()

    def output_datafiles_table(self):
        """Function to print the datafiles table to the console
        for all associated files
        """
        click.echo("\nData files:")

        # Print table to console
        click.echo(
            format_table(
                headers=["Name", "Size", "Format"],
                rows=[
                    [datafile.name, datafile.size, datafile.format]
                    for datafile in self.files
                ],
            )
        )

    def output_metadata_extra_details(self):
        """Function to print additional metadata to the
        console relating to the dataset
        """
        click.echo(f"Themes:\n{self.themes}")
        click.echo(f"Publisher: {self.publisher}")
        click.echo(f"Issued: {self.issued}")
        click.echo("Rights:")
        prose_print(self.rights or "None", CONSOLE_WIDTH)
        click.echo(f"Language: {self.language}")
        click.echo(f"Standard: {self.standard}")
        click.echo(f"Update Frequency: {self.update_frequency}")

    def output_version_details(self):
        """Prints relevant dataset attributes to command line"""
        click.echo(f"\nTitle: {self.title}")
        click.echo(f"ID: {self.dataset_id}")
        click.echo(f"Version ID: {self.version_id}")
        click.echo(f"Publisher: {self.publisher.name}")
        click.echo(
            f"From: {format_datetime(self.start_date, include_time=True)}{TAB_SPACE}"
            f"To: {format_datetime(self.end_date, include_time=True)}"
        )
        click.echo("Description: ")
        prose_print(self.description, CONSOLE_WIDTH)

    def get_dataset_details(self) -> str:
        """Returns a string with details about the dataset (used prior to
        deletion)"""
        version_ids = "\n".join(
            [version.version_id for version in self.version_history.versions]
        )
        return (
            f"Title: {self.title}\n"
            f"ID: {self.dataset_id}\n"
            f"Latest version: {self.version_id}\n"
            f"Publisher: {self.publisher.name}\n"
            f"Version IDs:\n{version_ids}\n"
        )

    def download_dataset_files(
        self, session: DAFNISession
    ) -> Tuple[List[str], List[BytesIO]]:
        """Function downloads all associated Files, and returns a tuple with
        containing a list of all file names, and a list of all file contents

        Args:
            session (str): User session

        Returns:
            Tuple[List[str], List[BytesIO]]: Tuple of all File names and File contents
        """
        file_names = []
        file_contents = []
        for data_file in self.files:
            data_file.download_contents(session)
            file_names.append(data_file.name)
            file_contents.append(data_file.contents)

        return file_names, file_contents


# The following methods mostly exists to get round current python limitations
# with typing (see https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class)
def parse_dataset_metadata(dataset_dictionary: dict) -> DatasetMetadata:
    """Parses the output of get_latest_dataset_metadata and returns a
    DatasetMetadata instance"""
    return ParserBaseObject.parse_from_dict(DatasetMetadata, dataset_dictionary)

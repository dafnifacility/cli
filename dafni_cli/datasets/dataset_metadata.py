from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar, List, Optional

import click
from tabulate import tabulate

from dafni_cli.api.auth import Auth
from dafni_cli.api.parser import ParserBaseObject, ParserParam, parse_datetime
from dafni_cli.consts import (
    CONSOLE_WIDTH,
    TABLE_MODIFIED_HEADER,
    TABLE_VERSION_ID_HEADER,
    TABLE_VERSION_MESSAGE_HEADER,
)
from dafni_cli.utils import (
    format_data_format,
    format_datetime,
    format_file_size,
    format_table,
    prose_print,
)

# Subjects valid for upload
DATASET_METADATA_SUBJECTS = [
    "Biota",
    "Boundaries",
    "Climate / Meteorology / Atmosphere",
    "Economy",
    "Elevation",
    "Environment",
    "Farming",
    "Geoscientific Information",
    "Health",
    "Imagery / Base Maps / Earth Cover",
    "Inland Waters",
    "Intelligence / Military",
    "Locations",
    "Ocean",
    "Planning / Cadastre",
    "Society",
    "Structure",
    "Transportation",
    "Utilities / Communication",
]

# Themes valid for upload
DATASET_METADATA_THEMES = [
    "Addresses",
    "Administrative units",
    "Agricultural and aquaculture facilities",
    "Area management / restriction / regulation zones & reporting units",
    "Atmospheric conditions",
    "Bio-geographical regions",
    "Buildings",
    "Cadastral parcels",
    "Coordinate reference systems",
    "Elevation",
    "Energy Resources",
    "Environmental monitoring Facilities",
    "Geographical grid systems",
    "Geographical names",
    "Geology",
    "Habitats and biotopes",
    "Human health and safety",
    "Hydrology",
    "Land cover",
    "Land use",
    "Meteorological geographical features",
    "Mineral Resources",
    "Natural risk zones",
    "Oceanographic geographical features",
    "Orthoimagery",
    "Population distribution and demography",
    "Production and industrial facilities",
    "Protected sites",
    "Sea regions",
    "Soil",
    "Species distribution",
    "Statistical units",
    "Transport networks",
    "Utility and governmental services",
]

# Update frequencies valid for upload
DATASET_METADATA_UPDATE_FREQUENCIES = [
    "Triennial",
    "Biennial",
    "Annual",
    "Semiannual",
    "Three times a year",
    "Quarterly",
    "Bimonthly",
    "Monthly",
    "Semimonthly",
    "Biweekly",
    "Three times a month",
    "Weekly",
    "Semiweekly",
    "Three times a week",
    "Daily",
    "Continuous",
    "Irregular",
]

# Languages valid for upload
DATASET_METADATA_LANGUAGES = [
    "en",
    "ga",
    "gd",
    "cy",
    "ab",
    "aa",
    "af",
    "ak",
    "sq",
    "am",
    "ar",
    "an",
    "hy",
    "as",
    "av",
    "ae",
    "ay",
    "az",
    "bm",
    "ba",
    "eu",
    "be",
    "bn",
    "bh",
    "bi",
    "nb",
    "bs",
    "br",
    "bg",
    "my",
    "ca",
    "km",
    "ch",
    "ce",
    "ny",
    "zh",
    "cu",
    "cv",
    "kw",
    "co",
    "cr",
    "hr",
    "cs",
    "da",
    "dv",
    "nl",
    "dz",
    "eo",
    "et",
    "ee",
    "fo",
    "fj",
    "fi",
    "fr",
    "ff",
    "gl",
    "lg",
    "ka",
    "de",
    "el",
    "gn",
    "gu",
    "ht",
    "ha",
    "he",
    "hz",
    "hi",
    "ho",
    "hu",
    "is",
    "io",
    "ig",
    "id",
    "ia",
    "ie",
    "iu",
    "ik",
    "it",
    "ja",
    "jv",
    "kl",
    "kn",
    "kr",
    "ks",
    "kk",
    "ki",
    "rw",
    "ky",
    "kv",
    "kg",
    "ko",
    "kj",
    "ku",
    "lo",
    "la",
    "lv",
    "li",
    "ln",
    "lt",
    "lu",
    "lb",
    "mk",
    "mr",
    "mg",
    "ms",
    "ml",
    "mt",
    "gv",
    "mi",
    "mh",
    "mn",
    "na",
    "nv",
    "nd",
    "nr",
    "ng",
    "ne",
    "se",
    "no",
    "nn",
    "oc",
    "oj",
    "or",
    "om",
    "os",
    "pi",
    "pa",
    "fa",
    "pl",
    "pt",
    "ps",
    "qu",
    "ro",
    "rm",
    "rn",
    "ru",
    "sm",
    "sg",
    "sa",
    "sc",
    "sr",
    "sn",
    "ii",
    "sd",
    "si",
    "sk",
    "sl",
    "so",
    "st",
    "es",
    "su",
    "sw",
    "ss",
    "sv",
    "tl",
    "ty",
    "tg",
    "ta",
    "tt",
    "te",
    "th",
    "bo",
    "ti",
    "to",
    "ts",
    "tn",
    "tr",
    "tk",
    "tw",
    "ug",
    "uk",
    "ur",
    "uz",
    "ve",
    "vi",
    "vo",
    "wa",
    "fy",
    "wo",
    "xh",
    "yi",
    "yo",
    "za",
    "zu",
]


@dataclass
class DataFile(ParserBaseObject):
    """Dataclass representing a DAFNI dataset file

    Methods:
        download_contents(session: DAFNISession): Downloads the files contents

    Attributes:
        name (str): File name
        size (int): File size
        format (str): File format (Defaults to OUTPUT_UNKNOWN_FORMAT if not
                      known)
        download_url (str): File download url
    """

    name: str
    size: int
    format: str = None
    download_url: str = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("name", "spdx:fileName", str),
        ParserParam("size", "dcat:byteSize", int),
        ParserParam(
            "format",
            "dcat:mediaType",
            str,
        ),
        ParserParam("download_url", "dcat:downloadURL", str),
    ]


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
        name (Optional[str]): Contact name
        email (optional[str]): Contact email
    """

    type: str
    name: Optional[str] = None
    email: Optional[str] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("type", "@type", str),
        ParserParam("name", "vcard:fn", str),
        ParserParam("email", "vcard:hasEmail", str),
    ]

    def __str__(self) -> str:
        """Nicer string representation for printing"""
        if self.name is None and self.email is None:
            return "N/A"

        if self.name and self.email:
            return f"{self.name}, {self.email}"
        elif self.name:
            return self.name
        elif self.email:
            return self.email


@dataclass
class Location(ParserBaseObject):
    """Dataclass representing the location listed in a dataset's metadata

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
        if self.name is None:
            return "N/A"
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
        if self.label is None:
            return "N/A"
        else:
            return f"{self.label}"


@dataclass
class DatasetMetadataVersion(ParserBaseObject):
    """Dataclass representing a metadata version listed in a dataset's
    version_history

    Attributes:
        metadata_id (str): ID of this version of the metadata
        modified_date (datetime): Time and date of last modification of this
                                  version
        version_message (Optional[str]): Version message for the metadata
    """

    metadata_id: str
    modified_date: datetime
    version_message: Optional[str] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("metadata_id", "metadata_uuid", str),
        ParserParam("modified_date", "modified_date", parse_datetime),
        ParserParam("version_message", "dafni_version_note", str),
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

    def output_version_history(self):
        """Iterates through all versions and outputs their details in a table
        printed to the command line
        """
        table_rows = []
        for version in self.versions:
            # Latest metadata is always the first
            latest_metadata = version.metadata_versions[0]
            table_rows.append(
                [
                    version.version_id,
                    format_datetime(latest_metadata.modified_date, include_time=True),
                    latest_metadata.version_message,
                ]
            )
        click.echo(
            format_table(
                headers=[
                    TABLE_VERSION_ID_HEADER,
                    TABLE_MODIFIED_HEADER,
                    TABLE_VERSION_MESSAGE_HEADER,
                ],
                rows=table_rows,
            )
        )


@dataclass
class DatasetMetadata(ParserBaseObject):
    """Dataclass representing a DAFNI dataset's metadata

    Methods:
        output_details(): Prints key information of the dataset metadata to console.
        output_datafiles_table(): Prints a table to the console of all File related information
        output_additional_metadata(): Prints additional dataset metadata

    Attributes:
        title (str): Title of the dataset
        description (str): Description of the dataset
        subject (str): Subject of the dataset
        created (datetime): Date the dataset was created
        creators (List[Creator]): List of named creators of the dataset
        contact (Contact): Contact relating to the dataset
        location (Location): Location the dataset relates to
        keywords (List[str]): Key words relating to the dataset e.g. Transportation
        modified (datetime): Date & time the dataset was last modified
        issued (datetime): Date and time the dataset was issued
        language (str): The language used for the dataset
        asset_id (str): Asset identifier for dataset
        dataset_id (str): Dataset identifier
        version_id (str): Version identifier of the latest version of this
                          dataset
        metadata_id (str): Metadata identifier of the latest metadata for this
                           dataset
        auth (Auth): Authentication credentials giving the permissions the
                     current user has on the dataset
        files (List[DataFile]): Files associated with the dataset
        status (str): Status of the dataset e.g. ingested
        version_history (DatasetVersionHistory): Version history of the dataset
        version_message (str): Version message of the dataset
        identifiers (List[str]): List of identifiers relating to the dataset
        themes (List[str]): Themes relating to dataset
        standard (Optional[Standard]): Any related standards associated
        publisher (Optional[Publisher]): Entity responsible for publishing the dataset
        rights (Optional[str]): The user rights linked to the Dataset
        update_frequency (Optional[str]): Update frequency if applicable
        start_date (Optional[datetime]): Dataset start date if applicable
        end_date (Optional[datetime]): Dataset end date if applicable
    """

    title: str
    description: str
    subject: str
    created: datetime
    creators: List[Creator]
    contact: Contact
    location: Location
    keywords: List[str]
    modified: datetime
    issued: datetime
    language: str
    asset_id: str
    dataset_id: str
    version_id: str
    metadata_id: str
    auth: Auth
    files: List[DataFile]
    status: str
    version_history: DatasetVersionHistory
    version_message: Optional[str] = None
    identifiers: List[str] = field(default_factory=list)
    themes: List[str] = field(default_factory=list)
    standard: Standard = None
    publisher: Publisher = None
    rights: Optional[str] = None
    update_frequency: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("title", ["metadata", "dct:title"], str),
        ParserParam("description", ["metadata", "dct:description"], str),
        ParserParam("subject", ["metadata", "dct:subject"], str),
        ParserParam("created", ["metadata", "dct:created"], parse_datetime),
        ParserParam("creators", ["metadata", "dct:creator"], Creator),
        ParserParam("contact", ["metadata", "dcat:contactPoint"], Contact),
        ParserParam("location", ["metadata", "dct:spatial"], Location),
        ParserParam("keywords", ["metadata", "dcat:keyword"]),
        ParserParam("modified", ["metadata", "dct:modified"], parse_datetime),
        ParserParam("issued", ["metadata", "dct:issued"], parse_datetime),
        ParserParam("language", ["metadata", "dct:language"], str),
        ParserParam("asset_id", ["metadata", "@id", "asset_id"], str),
        ParserParam("dataset_id", ["metadata", "@id", "dataset_uuid"], str),
        ParserParam("version_id", ["metadata", "@id", "version_uuid"], str),
        ParserParam("metadata_id", ["metadata", "@id", "metadata_uuid"], str),
        ParserParam("auth", "auth", Auth),
        ParserParam("files", ["metadata", "dcat:distribution"], DataFile),
        ParserParam("status", "status", str),
        ParserParam("version_history", "version_history", DatasetVersionHistory),
        ParserParam("version_message", ["metadata", "dafni_version_note"], str),
        ParserParam("identifiers", ["metadata", "dct:identifier"]),
        ParserParam("themes", ["metadata", "dcat:theme"]),
        ParserParam("standard", ["metadata", "dct:conformsTo"], Standard),
        ParserParam("publisher", ["metadata", "dct:publisher"], Publisher),
        ParserParam("rights", ["metadata", "dct:rights"], str),
        ParserParam("update_frequency", ["metadata", "dct:accrualPeriodicity"], str),
        ParserParam(
            "end_date", ["metadata", "dct:PeriodOfTime", "time:hasEnd"], parse_datetime
        ),
        ParserParam(
            "start_date",
            ["metadata", "dct:PeriodOfTime", "time:hasBeginning"],
            parse_datetime,
        ),
    ]

    def output_details(self, long: bool = False):
        """Outputs details relating to the Dataset

        By default will output standard metadata and a table relating to the
        associated files. If the long option is given, the additional metadata
        fields are also output.

        Args:
            long (bool, optional): Flag to print additional metadata. Defaults to False.
        """
        click.echo(self.title)
        click.echo(f"Subject: {self.subject}")
        click.echo(f"Version ID: {self.version_id}")
        click.echo("")
        click.echo(f"Created: {format_datetime(self.created, include_time=True)}")
        click.echo(f"Creator: {self.creators[0].name}")
        click.echo(f"Contact: {self.contact}")
        click.echo("")
        click.echo("Description:")
        prose_print(self.description, CONSOLE_WIDTH)
        click.echo("")
        click.echo("Identifier(s):")
        prose_print(
            " ".join(self.identifiers) if self.identifiers else "N/A", CONSOLE_WIDTH
        )
        click.echo(f"Location: {self.location.label}")
        click.echo(
            f"Start date: {format_datetime(self.start_date, include_time=False)}"
        )
        click.echo(f"End date: {format_datetime(self.end_date, include_time=False)}")

        # DataFiles table
        self.output_datafiles_table()

        if long:
            click.echo("")
            self.output_additional_metadata()

        click.echo("")
        click.echo("Keywords:")
        click.echo(", ".join(self.keywords))

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
                    [
                        datafile.name,
                        format_file_size(datafile.size),
                        format_data_format(datafile.format),
                    ]
                    for datafile in self.files
                ],
            )
        )

    def output_additional_metadata(self):
        """Function to print additional metadata to the
        console relating to the dataset
        """
        click.echo("Additional metadata:")

        click.echo(
            tabulate(
                [
                    ["Theme(s):", ", ".join(self.themes)],
                    ["Publisher:", str(self.publisher)],
                    [
                        "Last updated:",
                        format_datetime(self.modified, include_time=False),
                    ],
                    ["Rights:", self.rights or "N/A"],
                    ["Language:", self.language],
                    ["Standard:", str(self.standard) if self.standard else "N/A"],
                    ["Update frequency:", self.update_frequency or "N/A"],
                ],
                tablefmt="plain",
            )
        )

    def get_details(self) -> str:
        """Returns a string with details about the dataset (used prior to
        deletion)"""
        version_ids = "\n".join(
            [version.version_id for version in self.version_history.versions]
        )
        return (
            f"Title: {self.title}\n"
            f"ID: {self.dataset_id}\n"
            f"Created: {format_datetime(self.created, include_time=True)}\n"
            f"Publisher: {self.publisher.name}\n"
            f"Version IDs:\n{version_ids}\n"
        )

    def get_version_details(self) -> str:
        """Returns a string with details about the dataset version (used prior
        to deletion)"""
        return (
            f"Title: {self.title}\n"
            f"Version ID: {self.version_id}\n"
            f"Created: {format_datetime(self.created, include_time=True)}\n"
            f"Publisher: {self.publisher.name}\n"
        )


# The following methods mostly exists to get round current python limitations
# with typing (see https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class)
def parse_dataset_metadata(dataset_dictionary: dict) -> DatasetMetadata:
    """Parses the output of get_latest_dataset_metadata and returns a
    DatasetMetadata instance"""
    return ParserBaseObject.parse_from_dict(DatasetMetadata, dataset_dictionary)

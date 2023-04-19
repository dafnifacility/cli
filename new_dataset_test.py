from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from typing import ClassVar, List, Optional

from dafni_cli.api.datasets_api import get_latest_dataset_metadata
from dafni_cli.api.parser import (
    ParserBaseObject,
    ParserParam,
    create_object_from_list_parser,
    parse_datetime,
)
from dafni_cli.api.session import DAFNISession
from dafni_cli.utils import process_file_size


@dataclass
class Creator(ParserBaseObject):
    type: str
    name: str
    id: Optional[str] = None
    internal_id: Optional[str] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("type", "@type", str),
        ParserParam("name", "foaf:name", str),
        ParserParam("id", "@id", str),
        ParserParam("internal_id", "internalID", str),
    ]


@dataclass
class Contact(ParserBaseObject):
    type: str
    name: str
    email: str

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("type", "@type", str),
        ParserParam("name", "vcard:fn", str),
        ParserParam("email", "vcard:hasEmail", str),
    ]


@dataclass
class Location(ParserBaseObject):
    id: str
    type: str
    label: str

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("id", "@id", str),
        ParserParam("type", "@type", str),
        ParserParam("label", "rdfs:label", str),
    ]


@dataclass
class Publisher(ParserBaseObject):
    type: str
    id: Optional[str] = None
    name: Optional[str] = None
    internal_id: Optional[str] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("id", "@id", str),
        ParserParam("type", "@type", str),
        ParserParam("name", "foaf:name", str),
        ParserParam("internal_id", "internalID", str),
    ]


@dataclass
class Standard(ParserBaseObject):
    type: str
    id: Optional[str] = None
    label: Optional[str] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("id", "@id", str),
        ParserParam("type", "@type", str),
        ParserParam("label", "label", str),
    ]


@dataclass
class DataFile(ParserBaseObject):
    name: str
    size: str
    format: str
    download_url: str

    # Separate - only used when actually downloading
    contents: Optional[BytesIO] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("name", "spdx:fileName", str),
        ParserParam("size", "dcat:byteSize", process_file_size),
        ParserParam("format", "dcat:mediaType", str),
        ParserParam("download_url", "dcat:downloadURL", str),
    ]


@dataclass
class DatasetMetadata(ParserBaseObject):
    title: str
    description: str
    subject: str
    created: datetime
    creators: List[Creator]
    contact: Contact
    identifier: str
    location: Location
    keywords: List[str]
    themes: List[str]
    publisher: Publisher
    issued: datetime
    language: str
    standard: Standard
    asset_id: str
    dataset_uuid: str
    version_uuid: str
    metadata_uuid: str
    files: List[DataFile]
    rights: Optional[str] = None
    update_frequency: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("title", "dct:title", str),
        ParserParam("description", "dct:description", str),
        ParserParam("subject", "dct:subject", str),
        ParserParam("created", "dct:created", parse_datetime),
        ParserParam("creators", "dct:creator", create_object_from_list_parser(Creator)),
        ParserParam("contact", "dcat:contactPoint", Contact),
        ParserParam("identifier", "dct:identifier", str),
        ParserParam("location", "dct:spatial", Location),
        ParserParam("keywords", "dcat:keyword"),
        ParserParam("themes", "dcat:theme"),
        ParserParam("publisher", "dct:publisher", Publisher),
        ParserParam("issued", "dct:issued", parse_datetime),
        ParserParam("language", "dct:language", str),
        ParserParam("standard", "dct:conformsTo", Standard),
        ParserParam("asset_id", ["@id", "asset_id"], str),
        ParserParam("dataset_uuid", ["@id", "dataset_uuid"], str),
        ParserParam("version_uuid", ["@id", "version_uuid"], str),
        ParserParam("metadata_uuid", ["@id", "metadata_uuid"], str),
        ParserParam(
            "files", "dcat:distribution", create_object_from_list_parser(DataFile)
        ),
        ParserParam("rights", "dct:rights", str),
        ParserParam("update_frequency", "dct:accrualPeriodicity", str),
        ParserParam("end_date", ["dct:PeriodOfTime", "time:hasEnd"], parse_datetime),
        ParserParam(
            "start_date", ["dct:PeriodOfTime", "time:hasBeginning"], parse_datetime
        ),
    ]


session = DAFNISession()
data = get_latest_dataset_metadata(
    session,
    "f7fd0d12-f6c2-401a-ae7e-21fce0b3bec4",
    "0bd05eea-886a-47f3-983d-6fe47b7fd1a0",
)

print(ParserBaseObject.parse_from_dict(DatasetMetadata, data))

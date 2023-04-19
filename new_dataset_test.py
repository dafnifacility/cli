from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, ClassVar, List, Optional, Type, Union
from dafni_cli.api.datasets_api import get_latest_dataset_metadata
from dafni_cli.api.session import DAFNISession

from dateutil.parser import isoparse
from datetime import datetime


@dataclass
class ParserParam:
    name: str
    keys: Union[str, List[str]]
    datatype: Optional[Union[type, callable]] = None


class ParserBaseObject:
    _parser_params: ClassVar[List[ParserParam]] = []

    @staticmethod
    def parse_from_dict(dataclass_type: type, dictionary):
        # Parse the dictionary using the given params
        parsed_params = {}
        for param in dataclass_type._parser_params:
            # When keys is a list, want to obtain the nested values instead if possible
            if isinstance(param.keys, list):
                parsed_param = dictionary
                for key in param.keys:
                    parsed_param = parsed_param.get(key)
                    if parsed_param is None:
                        break
            else:
                parsed_param = dictionary.get(param.keys)

            if parsed_param is not None:
                if param.datatype is not None:
                    if isinstance(param.datatype, type) and issubclass(
                        param.datatype, ParserBaseObject
                    ):
                        parsed_param = ParserBaseObject.parse_from_dict(
                            param.datatype, parsed_param
                        )
                    else:
                        parsed_param = param.datatype(parsed_param)

                parsed_params[param.name] = parsed_param

        # Convert to the dataclass type
        return dataclass_type(**parsed_params)


def parse_datetime(value: str):
    return isoparse(value).strftime("%B %d %Y")


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
class DatasetMetadata(ParserBaseObject):
    title: str
    description: str
    subject: str
    created: datetime
    contact: Contact
    identifier: str
    location: Location
    keywords: List[str]
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("title", "dct:title", str),
        ParserParam("description", "dct:description", str),
        ParserParam("subject", "dct:subject", str),
        ParserParam("created", "dct:created", parse_datetime),
        ParserParam("contact", "dcat:contactPoint", Contact),
        ParserParam("identifier", "dct:identifier", str),
        ParserParam("location", "dct:spatial", Location),
        ParserParam(
            "start_date", ["dct:PeriodOfTime", "time:hasBeginning"], parse_datetime
        ),
        ParserParam("end_date", ["dct:PeriodOfTime", "time:hasEnd"], parse_datetime),
        ParserParam("keywords", "dcat:keyword"),
    ]


session = DAFNISession()
data = get_latest_dataset_metadata(
    session,
    "f7fd0d12-f6c2-401a-ae7e-21fce0b3bec4",
    "0bd05eea-886a-47f3-983d-6fe47b7fd1a0",
)

print(ParserBaseObject.parse_from_dict(DatasetMetadata, data))

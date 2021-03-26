import pytest
from typing import List

from dafni_cli.datasets.dataset_metadata import DataFile, DatasetMetadata


@pytest.fixture
def get_dataset_list_fixture() -> List[dict]:
    """Test fixture for simulating the dataset data return
    from calling the get datasets API

    Returns:
        List[dict]: example get Dataset response
    """
    datasets = {
        "metadata": [
            {
                "id": {
                    "dataset_uuid": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
                    "version_uuid": "0a0a0a0a-0a00-0a00-a000-0a0a0000000b",
                    "metadata_uuid": "0a0a0a0a-0a00-0a00-a000-0a0a0000000c",
                    "asset_id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a:0a0a0a0a-0a00-0a00-a000-0a0a0000000b:0a0a0a0a-0a00-0a00-a000-0a0a0000000c",
                },
                "title": "Title 1",
                "description": "Description 1",
                "subject": "Planning / Cadastre",
                "source": "DAFNI",
                "date_range": {"begin": None, "end": None},
                "modified_date": "2021-03-04T15:59:26+00:00",
                "formats": [None],
                "auth": {
                    "name": "Executor",
                    "view": True,
                    "read": True,
                    "update": False,
                    "destroy": False,
                    "reason": "Accessed as part of the Public group",
                },
            },
            {
                "id": {
                    "dataset_uuid": "1a0a0a0a-0a00-0a00-a000-0a0a0000000a",
                    "version_uuid": "1a0a0a0a-0a00-0a00-a000-0a0a0000000b",
                    "metadata_uuid": "1a0a0a0a-0a00-0a00-a000-0a0a0000000c",
                    "asset_id": "1a0a0a0a-0a00-0a00-a000-0a0a0000000a:1a0a0a0a-0a00-0a00-a000-0a0a0000000b:1a0a0a0a-0a00-0a00-a000-0a0a0000000c",
                },
                "title": "Title 2",
                "description": "Description 2",
                "subject": "Environment",
                "source": "DAFNI Workflows",
                "date_range": {
                    "begin": "2019-01-01T12:00:00.000Z",
                    "end": "2021-01-01T12:00:00.000Z",
                },
                "modified_date": "2020-08-26T13:21:18.522Z",
                "formats": ["application/zip", None, "text/csv", "text/plain"],
                "auth": {
                    "name": "Executor",
                    "view": True,
                    "read": True,
                    "update": False,
                    "destroy": False,
                    "reason": "Accessed as part of the Public group",
                },
            },
        ],
        "filters": {
            "sources": {
                "Companies House": 1,
                "DAFNI": 1,
                "DAFNI Workflows": 1,
                "Newcastle University": 28,
                "Office for National Statistics": 455,
                "Office of Rail and Road": 2,
            },
            "subjects": {
                "Climatology / Meteorology / Atmosphere": 16,
                "Economy": 1,
                "Environment": 1,
                "Oceans": 2,
                "Planning / Cadastre": 1,
                "Society": 455,
                "Transportation": 10,
                "Utilities / Communication": 2,
            },
            "formats": {
                "text/plain": 1,
                "text/csv": 483,
                "application/zip": 2,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": 3,
                "application/vnd.ms-excel": 1,
                "application/pdf": 1,
                "application/octet-stream": 3,
            },
        },
    }

    return datasets


@pytest.fixture
def dataset_metadata_fixture() -> dict:
    """Test fixture returning an example dataset metadata response dict

    Returns:
        dict: Example Dataset metadata response dict
    """
    data = {
        "@context": ["metadata-v1"],
        "@type": "dcat:Dataset",
        "dct:title": "An example workflow definition",
        "dct:description": "Dataset description",
        "dct:identifier": [
            "0a0a0a0a-0a00-0a00-a000-0a0a0000000a:0a0a0a0a-0a00-0a00-a000-0a0a0000000b:0a0a0a0a-0a00-0a00-a000-0a0a0000000c"
        ],
        "dct:subject": "Biota",
        "dcat:theme": ["Utility and governmental services"],
        "dct:language": "en",
        "dcat:keyword": ["test"],
        "dct:conformsTo": {
            "@id": "https://www.iso.org/standard/39229.html",
            "@type": "dct:Standard",
            "label": "ISO 19115-2:2009",
        },
        "dct:spatial": {"@id": None, "@type": "dct:Location", "rdfs:label": "England"},
        "geojson": {},
        "dct:PeriodOfTime": {
            "type": "dct:PeriodOfTime",
            "time:hasBeginning": "2019-03-27T00:00:00Z",
            "time:hasEnd": "2021-03-27T00:00:00Z",
        },
        "dct:accrualPeriodicity": "Semiannual",
        "dct:creator": [
            {
                "@type": "foaf:Organization",
                "@id": "http://www.stfc.ac.uk",
                "foaf:name": "STFC",
                "internalID": None,
            }
        ],
        "dct:created": "2021-03-16",
        "dct:publisher": {
            "@id": None,
            "@type": "foaf:Organization",
            "foaf:name": "Publisher",
            "internalID": None,
        },
        "dcat:contactPoint": {
            "@type": "vcard:Organization",
            "vcard:fn": "Joe",
            "vcard:hasEmail": "joe.bloggsd@stfc.ac.uk",
        },
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
        "dcat:distribution": [
            {
                "spdx:fileName": "workflow_def.csv",
                "dcat:mediaType": "text/csv",
                "dcat:byteSize": 6720,
                "dcat:downloadURL": "url/to/file",
            }
        ],
        "mediatypes": [None],
        "version_history": {
            "dataset_uuid": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
            "versions": [
                {
                    "version_uuid": "0a0a0a0a-0a00-0a00-a000-0a0a0000000b",
                    "metadata_versions": [
                        {
                            "metadata_uuid": "0a0a0a0a-0a00-0a00-a000-0a0a0000000c",
                            "dafni_version_note": "Initial Dataset version",
                            "modified_date": "2021-03-16T09:27:21+00:00",
                        }
                    ],
                }
            ],
        },
        "auth": {
            "asset_id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
            "reason": "Accessed as part of the Tessella CLI group",
            "view": True,
            "read": True,
            "update": False,
            "destroy": False,
        },
    }

    return data


def datafile_mock(
    name: str = "File 1", size: str = "120 B", file_format: str = "CSV"
) -> DataFile:
    """Test fixture to generate a DataFile object with given attributes

    Args:
        name (str, optional): File name. Defaults to "File 1".
        size (str, optional): Formatted file size string. Defaults to "120 B".
        file_format (str, optional): File Format. Defaults to "CSV".

    Returns:
        DataFile: Generated DataFile for testing
    """
    datafile = DataFile()
    datafile.name = name
    datafile.size = size
    datafile.format = file_format

    return datafile


def dataset_meta_mock(
    created: str = "March 20 2021",
    creator: str = "DAFNI",
    contact: str = "contact@email.com",
    description: str = "description here",
    identifier: List[str] = ["id 1", "id 2"],
    location: str = "UK",
    start_date: str = "May 1 2000",
    end_date: str = "June 1 2020",
    files: List[DataFile] = [datafile_mock()],
    keywords: List[str] = ["Key word 1"],
    themes: List[str] = ["Theme 1", "Theme 2"],
    publisher: str = "Pubisher",
    issued: str = "June 12 2021",
    rights: str = "Some Rights",
    language: str = "en",
    standard: str = "ISO 9001",
    update: str = "Annual",
    title: str = "Title",
    dataset_id: str = "Dataset ID",
    version_id: str = "Version ID",
) -> DatasetMetadata:
    """Function to generate a DatasetMetadata object with mock data for testing

    Args:
        created (str, optional): Created date. Defaults to "March 20 2021".
        creator (str, optional): Created by. Defaults to "DAFNI".
        contact (str, optional): Point of contact. Defaults to "contact@email.com".
        description (str, optional): Description. Defaults to "description here".
        identifier (List[str], optional): List of identifiers. Defaults to ["id 1", "id 2"].
        location (str, optional): Location relating to data. Defaults to "UK".
        start_date (str, optional): Start of date range. Defaults to "May 1 2000".
        end_date (str, optional): End of date range. Defaults to "June 1 2020".
        files (List[DataFile], optional): Associated DataFile objects. Defaults to [mock_datafile()].
        keywords (List[str], optional): Keywords. Defaults to ["Key word 1"].
        themes (List[str], optional): Themes. Defaults to ["Theme 1", "Theme 2"].
        publisher (str, optional): Published by. Defaults to "Pubisher".
        issued (str, optional): Issued date. Defaults to "June 12 2021".
        rights (str, optional): Associated rights. Defaults to "Some Rights".
        language (str, optional): Associated Language. Defaults to "en".
        standard (str, optional): Associated standards. Defaults to "ISO 9001".
        update (str, optional): Frequency updated. Defaults to "Annual".
        title (str, optional): Associated Title. Defaults to "en".
        dataset_id (str, optional): Dataset ID. Defaults to "Dataset ID".
        version_id (str, optional): Dataset Version ID. Defaults to "Version ID".

    Returns:
        DatasetMetadata: DatasetMetadata object with mock data
    """
    instance = DatasetMetadata()
    instance.created = created
    instance.creator = creator
    instance.contact = contact
    instance.description = description
    instance.identifier = identifier
    instance.location = location
    instance.start_date = start_date
    instance.end_date = end_date
    instance.files = files
    instance.keywords = keywords
    instance.themes = themes
    instance.publisher = publisher
    instance.issued = issued
    instance.rights = rights
    instance.language = language
    instance.standard = standard
    instance.update = update
    instance.title = title
    instance.dataset_id = dataset_id
    instance.version_id = version_id

    return instance

# Below follows example response data from the API for getting a dataset's
# metadata
# Values labelled with _DEFAULT implies they do not define optional variables
# and are used to test the values still parse correctly
TEST_DATASET_METADATA_DATAFILE: dict = {
    "spdx:fileName": "workflow_def.csv",
    "dcat:byteSize": 6720,
    "dcat:mediaType": "text/csv",
    "dcat:downloadURL": "url/to/file",
}

TEST_DATASET_METADATA_DATAFILE_DEFAULT: dict = {
    "spdx:fileName": "workflow_def.csv",
    "dcat:byteSize": 6720,
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

TEST_DATASET_METADATA_CONTACT_DEFAULT: dict = {
    "@type": "vcard:Organization",
    "vcard:fn": None,
    "vcard:hasEmail": None,
}

TEST_DATASET_METADATA_LOCATION: dict = {
    "@id": "2648147",
    "@type": "dct:Location",
    "rdfs:label": "England",
}

TEST_DATASET_METADATA_LOCATION_DEFAULT: dict = {
    "@id": None,
    "@type": "dct:Location",
    "rdfs:label": None,
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

TEST_DATASET_METADATA_STANDARD_DEFAULT: dict = {}

TEST_DATASET_METADATA_VERSION_HISTORY: dict = {
    "dataset_uuid": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
    "versions": [
        {
            "version_uuid": "0a0a0a0a-0a00-0a00-a000-0a0a0000000b",
            "metadata_versions": [
                {
                    "metadata_uuid": "0a0a0a0a-0a00-0a00-a000-0a0a0000000d",
                    "dafni_version_note": "Second Dataset version",
                    "modified_date": "2021-03-17T09:27:21+00:00",
                },
                {
                    "metadata_uuid": "0a0a0a0a-0a00-0a00-a000-0a0a0000000c",
                    "dafni_version_note": "Initial Dataset version",
                    "modified_date": "2021-03-16T09:27:21+00:00",
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
    "metadata": {
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
            "@id": "https://creativecommons.org/licenses/by/4.0/",
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
        "dataset_type": "internal",
    },
    "status": "ingested",
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
    "metadata": {
        "@context": ["metadata-v1"],
        "@type": "dcat:Dataset",
        "dct:title": "An example workflow definition",
        "dct:description": "Dataset description",
        "dct:subject": "Subject",
        "dct:language": "en",
        "dcat:keyword": ["test"],
        "dct:spatial": TEST_DATASET_METADATA_LOCATION,
        "geojson": {},
        "dct:creator": [
            TEST_DATASET_METADATA_CREATOR,
            TEST_DATASET_METADATA_CREATOR_DEFAULT,
        ],
        "dct:created": "2021-03-16",
        "dcat:contactPoint": TEST_DATASET_METADATA_CONTACT,
        "dct:license": {
            "@type": "LicenseDocument",
            "@id": "https://creativecommons.org/licenses/by/4.0/",
            "rdfs:label": None,
        },
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
    },
    "status": "ingested",
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

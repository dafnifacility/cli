value = {
    "@context": ["metadata-v1"],
    "@type": "dcat:Dataset",
    "dct:title": "Sunshine levels between 1960 and 2016 - by Joel",
    "dct:description": "Monthly sunshine levels between 1960 and 2016 in the UK. Collected as part of UKCP9.",
    "dct:identifier": [],
    "dct:subject": "Environment",
    "dcat:theme": [],
    "dct:language": "en",
    "dcat:keyword": ["sunshine"],
    "dct:conformsTo": {"@id": None, "@type": "dct:Standard", "label": None},
    "dct:spatial": {
        "@id": "2648147",
        "@type": "dct:Location",
        "rdfs:label": "Great Britain, United Kingdom",
    },
    "geojson": {
        "type": "Feature",
        "properties": {},
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [1.7689121033873, 58.6726008965827],
                    [-6.22821033596556, 58.6726008965827],
                    [-6.22821033596556, 49.9554136614383],
                    [1.7689121033873, 49.9554136614383],
                    [1.7689121033873, 58.6726008965827],
                ]
            ],
        },
    },
    "dct:PeriodOfTime": {
        "type": "dct:PeriodOfTime",
        "time:hasBeginning": "1960-01-01",
        "time:hasEnd": None,
    },
    "dct:accrualPeriodicity": None,
    "dct:creator": [
        {
            "@type": "foaf:Organization",
            "@id": "https://www.metoffice.gov.uk/",
            "foaf:name": "Met Office",
            "internalID": None,
        }
    ],
    "dct:created": "2023-04-04",
    "dct:publisher": {
        "@id": None,
        "@type": "foaf:Organization",
        "foaf:name": None,
        "internalID": None,
    },
    "dcat:contactPoint": {
        "@type": "vcard:Organization",
        "vcard:fn": "Joel Davies",
        "vcard:hasEmail": "joel.davies@stfc.ac.uk",
    },
    "dct:license": {
        "@type": "LicenseDocument",
        "@id": "https://creativecommons.org/licences/by/4.0/",
        "rdfs:label": None,
    },
    "dct:rights": None,
    "dafni_version_note": "Initial Dataset version",
    "dcat:distribution": [
        {
            "dcat:byteSize": 16433208,
            "spdx:fileName": "sunshine.zip",
            "dcat:mediaType": "application/zip",
            "dcat:downloadURL": "https://minio.secure.dafni.rl.ac.uk/63337ec6-f976-403e-8cc0-129e87f1040b/sunshine.zip?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ZAGGGNVQMEUKNAUJXHHX%2F20230418%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20230418T144202Z&X-Amz-Expires=86400&X-Amz-SignedHeaders=host&X-Amz-Signature=060c7b86c4214d6b8e843488e8715065c40725d143e662f3a9f12fc4dfe52222",
        }
    ],
    "@id": {
        "asset_id": "f7fd0d12-f6c2-401a-ae7e-21fce0b3bec4:0bd05eea-886a-47f3-983d-6fe47b7fd1a0:8c1161b8-688a-4271-a108-930d15c049d0",
        "dataset_uuid": "f7fd0d12-f6c2-401a-ae7e-21fce0b3bec4",
        "version_uuid": "0bd05eea-886a-47f3-983d-6fe47b7fd1a0",
        "metadata_uuid": "8c1161b8-688a-4271-a108-930d15c049d0",
    },
    "dct:modified": "2023-04-04T07:55:03+00:00",
    "dct:issued": "2023-04-04T07:55:03+00:00",
    "mediatypes": ["application/zip"],
    "version_history": {
        "dataset_uuid": "f7fd0d12-f6c2-401a-ae7e-21fce0b3bec4",
        "versions": [
            {
                "version_uuid": "0bd05eea-886a-47f3-983d-6fe47b7fd1a0",
                "metadata_versions": [
                    {
                        "metadata_uuid": "8c1161b8-688a-4271-a108-930d15c049d0",
                        "dafni_version_note": "Initial Dataset version",
                        "modified_date": "2023-04-04T07:55:03+00:00",
                    },
                    {
                        "metadata_uuid": "668c5b07-5779-4ec4-9a94-6451b82e15dd",
                        "dafni_version_note": "Initial Dataset version",
                        "modified_date": "2023-04-04T07:52:59+00:00",
                    },
                ],
            }
        ],
    },
    "auth": {
        "asset_id": "0bd05eea-886a-47f3-983d-6fe47b7fd1a0",
        "reason": "Accessed as the owner of the asset",
        "view": True,
        "read": True,
        "update": True,
        "destroy": True,
    },
}

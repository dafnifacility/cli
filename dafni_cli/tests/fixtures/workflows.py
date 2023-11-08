from typing import List

from dafni_cli.tests.fixtures.auth import TEST_AUTH_DATA_OBJECT, TEST_AUTH_DATA_OBJECTS
from dafni_cli.tests.fixtures.workflow_metadata import TEST_WORKFLOW_METADATA
from dafni_cli.tests.workflows.test_instance import TEST_WORKFLOW_INSTANCE_LIST
from dafni_cli.tests.workflows.test_parameter_set import TEST_WORKFLOW_PARAMETER_SET

TEST_WORKFLOW_VERSION: dict = {
    "id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000b",
    "version_tags": ["latest"],
    "publication_date": "2023-04-04T08:34:36.531809Z",
    "version_message": "Initial Workflow version",
}

TEST_WORKFLOW_DATA_WORKFLOWS_ENDPOINT: dict = {
    "auth": TEST_AUTH_DATA_OBJECTS,
    "id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
    "kind": "W",
    "display_name": "A Workflow",
    "name": "test-workflow-name",
    "summary": "Test workflow created to learn about DAFNI",
    "creation_date": "2023-04-04T08:34:36.531809Z",
    "publication_date": "2023-04-04T08:34:36.531809Z",
    "owner": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
    "version_tags": [],
    "version_message": "",
    "parent": "0a0a0a0a-0a00-0a00-a000-0a0a0000000b",
    "version_history": [TEST_WORKFLOW_VERSION],
    "contact_point_name": "Lorem Ipsum",
    "contact_point_email": "lorem.ipsum@example.com",
    "licence": "https://creativecommons.org/licenses/by/4.0/",
    "rights": "Open",
}

TEST_WORKFLOWS: List[dict] = [TEST_WORKFLOW_DATA_WORKFLOWS_ENDPOINT]

TEST_WORKFLOW: dict = {
    "id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
    "metadata": TEST_WORKFLOW_METADATA,
    "version_history": [
        {
            "id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
            "version_tags": ["latest"],
            "publication_date": "2023-04-04T08:34:36.531809Z",
            "version_message": "Initial Workflow version",
        }
    ],
    "auth": TEST_AUTH_DATA_OBJECT,
    "instances": [
        TEST_WORKFLOW_INSTANCE_LIST,
    ],
    "parameter_sets": [TEST_WORKFLOW_PARAMETER_SET],
    "api_version": "v1.0.2",
    "kind": "W",
    "creation_date": "2023-04-04T08:34:36.531809Z",
    "publication_date": "2023-04-04T08:34:36.531809Z",
    "owner": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
    "version_tags": ["latest"],
    "version_message": "Initial Workflow version",
    "spec": {
        "steps": {
            "0a0a0a0a-0a00-0a00-a000-0a0a0000000a": {
                "kind": "visualisation",
                "name": "pub-and-vis-1",
                "files": [
                    {
                        "step": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
                        "paths": ["outputs/*"],
                    }
                ],
                "metadata": {
                    "in_step": {
                        "@type": "dcat:Dataset",
                        "geojson": {
                            "type": "Feature",
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
                            "properties": {},
                        },
                        "@context": ["metadata-v1"],
                        "dct:title": "Sunshine levels between 1960 and 2016 - by Joel",
                        "dcat:theme": [],
                        "dct:rights": None,
                        "dct:created": "2023-04-04T08:34:36Z",
                        "dct:creator": [
                            {
                                "@id": "https://dafni.ac.uk/",
                                "@type": "foaf:Organization",
                                "foaf:name": "test",
                                "internalID": None,
                            }
                        ],
                        "dct:license": {
                            "@id": "https://creativecommons.org/licenses/by/4.0/",
                            "@type": "LicenseDocument",
                            "rdfs:label": None,
                        },
                        "dct:spatial": {
                            "@id": "2648147",
                            "@type": "dct:Location",
                            "rdfs:label": "Great Britain, United Kingdom",
                        },
                        "dct:subject": "Environment",
                        "dcat:keyword": ["sunshine"],
                        "dct:language": "en",
                        "dct:publisher": {
                            "@id": None,
                            "@type": "foaf:Organization",
                            "foaf:name": None,
                            "internalID": None,
                        },
                        "dct:conformsTo": {
                            "@id": None,
                            "@type": "dct:Standard",
                            "label": None,
                        },
                        "dct:identifier": [],
                        "dct:description": "Monthly sunshine levels between 1960 and 2016 in the UK. Collected as part of UKCP9.",
                        "dct:PeriodOfTime": {
                            "type": "dct:PeriodOfTime",
                            "time:hasEnd": "Invalid date",
                            "time:hasBeginning": "1960-01-01",
                        },
                        "dcat:contactPoint": {
                            "@type": "vcard:Organization",
                            "vcard:fn": "Joel Davies",
                            "vcard:hasEmail": "joel.davies@stfc.ac.uk",
                        },
                        "dafni_version_note": "Initial Dataset version",
                        "dct:accrualPeriodicity": None,
                    }
                },
                "position": {"x": 466, "y": 50},
                "dependencies": ["0a0a0a0a-0a00-0a00-a000-0a0a0000000a"],
                "visualisation_title": "uk-climate-vis",
                "visualisation_builder": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
                "visualisation_description": "Test visualisation",
            },
            "0a0a0a0a-0a00-0a00-a000-0a0a0000000b": {
                "kind": "model",
                "name": "uk-climate",
                "inputs": [],
                "position": {"x": 212, "y": 58},
                "dependencies": [],
                "model_version": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
            },
        }
    },
    "parent": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
}

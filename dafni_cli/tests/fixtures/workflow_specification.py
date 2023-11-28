TEST_WORKFLOW_SPECIFICATION_STEP = {
    "dependencies": ["0a0a0a0a-0a00-0a00-a000-0a0a0000000b"],
    "inputs": ["0a0a0a0a-0a00-0a00-a000-0a0a0000000e"],
    "kind": "publisher",
    "name": "some-name",
    "position": {"x": 700, "y": 50},
    "metadata": {"some": "dict"},
    "model_version": "0a0a0a0a-0a00-0a00-a000-0a0a0000000c",
    "iteration_mode": "parallel",
    "workflow_version": "0a0a0a0a-0a00-0a00-a000-0a0a0000000d",
}

TEST_WORKFLOW_SPECIFICATION_DEFAULT = {
    "dependencies": ["0a0a0a0a-0a00-0a00-a000-0a0a0000000b"],
    "kind": "publisher",
    "name": "some-name",
    "position": {"x": 700, "y": 50},
}

TEST_WORKFLOW_SPECIFICATION = {
    "steps": {
        "0a0a0a0a-0a00-0a00-a000-0a0a0000000a": {
            "dependencies": ["0a0a0a0a-0a00-0a00-a000-0a0a0000000b"],
            "files": [
                {
                    "paths": ["outputs/**/*"],
                    "step": "0a0a0a0a-0a00-0a00-a000-0a0a0000000b",
                }
            ],
            "kind": "publisher",
            "metadata": {
                "in_step": {
                    "@context": ["metadata-v1"],
                    "@type": "dcat:Dataset",
                    "dafni_version_note": "Initial dataset version",
                    "dcat:contactPoint": {
                        "@type": "vcard:Organization",
                        "vcard:fn": "Joel Davies",
                        "vcard:hasEmail": "joel.davies@stfc.ac.uk",
                    },
                    "dcat:keyword": ["test"],
                    "dcat:theme": [],
                    "dct:PeriodOfTime": {
                        "time:hasBeginning": None,
                        "time:hasEnd": None,
                        "type": "dct:PeriodOfTime",
                    },
                    "dct:accrualPeriodicity": None,
                    "dct:conformsTo": {
                        "@id": None,
                        "@type": "dct:Standard",
                        "label": None,
                    },
                    "dct:created": "2023-06-12T15:37:23Z",
                    "dct:creator": [
                        {
                            "@id": "https://dafni.ac.uk/",
                            "@type": "foaf:Organization",
                            "foaf:name": "test",
                            "internalID": None,
                        }
                    ],
                    "dct:description": "Test description",
                    "dct:identifier": [],
                    "dct:language": "en",
                    "dct:license": {
                        "@id": "https://creativecommons.org/licenses/by/4.0/",
                        "@type": "LicenseDocument",
                        "rdfs:label": None,
                    },
                    "dct:publisher": {
                        "@id": None,
                        "@type": "foaf:Organization",
                        "foaf:name": None,
                        "internalID": None,
                    },
                    "dct:rights": None,
                    "dct:spatial": {
                        "@id": "2654669",
                        "@type": "dct:Location",
                        "rdfs:label": "British Isles, United Kingdom",
                    },
                    "dct:subject": "Health",
                    "dct:title": "Dataset output",
                    "geojson": {
                        "geometry": {"coordinates": [54, -4], "type": "Point"},
                        "properties": {},
                        "type": "Feature",
                    },
                }
            },
            "name": "some-name",
            "position": {"x": 700, "y": 50},
        },
        "0a0a0a0a-0a00-0a00-a000-0a0a0000000c": {
            "dependencies": [],
            "inputs": [],
            "kind": "model",
            "model_version": "0a0a0a0a-0a00-0a00-a000-0a0a0000000e",
            "name": "test",
            "position": {"x": 200, "y": 50},
        },
        "0a0a0a0a-0a00-0a00-a000-0a0a0000000b": {
            "dependencies": ["0a0a0a0a-0a00-0a00-a000-0a0a0000000c"],
            "inputs": ["0a0a0a0a-0a00-0a00-a000-0a0a0000000c"],
            "kind": "model",
            "model_version": "0a0a0a0a-0a00-0a00-a000-0a0a0000000f",
            "name": "test",
            "position": {"x": 450, "y": 50},
        },
        "0a0a0a0a-0a00-0a00-a000-0a0a0000000d": {
            "dependencies": [],
            "iteration_mode": "parallel",
            "kind": "loop",
            "name": "test_loop",
            "position": {"x": 192, "y": 58},
            "workflow_version": "0a0a0a0a-0a00-0a00-a000-0a0a0000000e",
        },
        "0a0a0a0a-0a00-0a00-a000-0a0a0000000e": {
            "dependencies": [],
            "iteration_mode": "parallel",
            "kind": "loop",
            "name": "test_loop",
            "position": {"x": 192, "y": 58},
            "workflow_version": "0a0a0a0a-0a00-0a00-a000-0a0a0000000e",
        },
        "0a0a0a0a-0a00-0a00-a000-0a0a0000001a": {
            "dependencies": ["0a0a0a0a-0a00-0a00-a000-0a0a0000000c"],
            "files": [
                {"paths": ["outputs/*"], "step": "0a0a0a0a-0a00-0a00-a000-0a0a0000000c"}
            ],
            "kind": "visualisation",
            "metadata": {"some": "dict"},
            "name": "pub-and-vis-1",
            "position": {"x": 466, "y": 50},
            "visualisation_builder": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
            "visualisation_description": "Test visualisation",
            "visualisation_title": "test-vis",
        },
        "0a0a0a0a-0a00-0a00-a000-0a0a0000001b": {
            "dependencies": ["0a0a0a0a-0a00-0a00-a000-0a0a0000000c"],
            "files": [
                {"paths": ["outputs/*"], "step": "0a0a0a0a-0a00-0a00-a000-0a0a0000000c"}
            ],
            "kind": "visualisation",
            "metadata": {"some": "dict"},
            "name": "vis-1",
            "position": {"x": 466, "y": 50},
            "visualisation_builder": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
            "visualisation_description": "Test visualisation",
            "visualisation_title": "test-vis",
        },
    },
}

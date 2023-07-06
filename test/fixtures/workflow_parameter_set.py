TEST_WORKFLOW_PARAMETER_SET_METADATA = {
    "description": "First parameter set",
    "display_name": "First parameter set",
    "name": "first-param-set",
    "publisher": "Joel Davies",
    "workflow_version": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
}

TEST_WORKFLOW_PARAMETER_SET_SPEC_DATASLOT = {
    "name": "Rainfall data",
    "path": "inputs/rainfall/",
    "datasets": ["0a0a0a0a-0a00-0a00-a000-0a0a0000000a"],
}

TEST_WORKFLOW_PARAMETER_SET_SPEC_PARAMETER = {
    "name": "PREDICTION_CYCLE",
    "value": "daily",
}

TEST_WORKFLOW_PARAMETER_SET = {
    "id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
    "owner": "0a0a0a0a-0a00-0a00-a000-0a0a0000000b",
    "creation_date": "2023-04-04T08:34:36.823227Z",
    "publication_date": "2023-04-04T08:34:36.823227Z",
    "kind": "P",
    "api_version": "v1.0.0",
    "spec": {
        "0a0a0a0a-0a00-0a00-a000-0a0a0000000c": {
            "kind": "model",
            "dataslots": [
                {
                    "name": "Rainfall data",
                    "path": "inputs/rainfall/",
                    "datasets": ["0a0a0a0a-0a00-0a00-a000-0a0a0000000d"],
                },
                {
                    "name": "Maximum Temperature data",
                    "path": "inputs/maximum-temperature/",
                    "datasets": ["0a0a0a0a-0a00-0a00-a000-0a0a0000000e"],
                },
            ],
            "parameters": [
                {"name": "PROCESS_RAINFALL", "value": True},
                {"name": "PREDICTION_CYCLE", "value": "daily"},
            ],
        }
    },
    "metadata": TEST_WORKFLOW_PARAMETER_SET_METADATA,
}

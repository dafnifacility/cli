TEST_WORKFLOW_PARAMETER_SET_METADATA = {
    "description": "First parameter set",
    "display_name": "First parameter set",
    "name": "first-param-set",
    "publisher": "Joel Davies",
    "workflow_version": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
}

TEST_WORKFLOW_PARAMETER_SET_SPEC_DATASLOT_MODEL = {
    "name": "Rainfall data",
    "path": "inputs/rainfall/",
    "datasets": ["0a0a0a0a-0a00-0a00-a000-0a0a0000000a"],
}

TEST_WORKFLOW_PARAMETER_SET_SPEC_DATASLOT_LOOP = {
    "steps": ["0a0a0a0a-0a00-0a00-a000-0a0a0000000a"],
    "datasets": [["0a0a0a0a-0a00-0a00-a000-0a0a0000000b"]],
    "dataslot": "Batch file",
}

TEST_WORKFLOW_PARAMETER_SET_SPEC_PARAMETER_MODEL = {
    "name": "PREDICTION_CYCLE",
    "value": "daily",
}

TEST_WORKFLOW_PARAMETER_SET_SPEC_PARAMETER_LOOP = {
    "steps": ["0a0a0a0a-0a00-0a00-a000-0a0a0000000a"],
    "values": ["some_file.csv"],
    "parameter": "BATCH_FILENAME",
    "calculate_values": False,
}

TEST_WORKFLOW_PARAMETER_SET_SPEC_STEP = {
    "base_parameter_set": "0a0a0a0a-0a00-0a00-a000-0a0a0000001a",
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

TEST_WORKFLOW_PARAMETER_SET_SPEC_STEP_DEFAULT = {
    "kind": "model",
    "dataslots": [
        {
            "name": "Rainfall data",
            "path": "inputs/rainfall/",
            "datasets": ["0a0a0a0a-0a00-0a00-a000-0a0a0000000d"],
        },
    ],
    "parameters": [
        {"name": "PROCESS_RAINFALL", "value": True},
    ],
}

TEST_WORKFLOW_PARAMETER_SET = {
    "id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
    "owner": "0a0a0a0a-0a00-0a00-a000-0a0a0000000b",
    "creation_date": "2023-04-04T08:34:36.823227Z",
    "publication_date": "2023-04-04T08:34:36.823227Z",
    "kind": "P",
    "api_version": "v1.0.0",
    "spec": {
        "0a0a0a0a-0a00-0a00-a000-0a0a0000000c": TEST_WORKFLOW_PARAMETER_SET_SPEC_STEP
    },
    "metadata": TEST_WORKFLOW_PARAMETER_SET_METADATA,
}

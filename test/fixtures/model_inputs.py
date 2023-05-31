TEST_MODEL_INPUT_DATASLOT: dict = {
    "name": "Inputs",
    "path": "inputs/",
    "required": True,
    "default": ["0a0a0a0a-0a00-0a00-a000-0a0a0000000f"],
    "description": "Dataslot description",
}

TEST_MODEL_INPUT_DATASLOT_DEFAULT: dict = {
    "name": "Inputs",
    "path": "inputs/",
    "required": True,
}

TEST_MODEL_INPUT_PARAMETER: dict = {
    "max": 2025,
    "min": 2016,
    "name": "YEAR",
    "type": "integer",
    "title": "Year input",
    "default": 2018,
    "required": True,
    "description": "Year input description",
}

TEST_MODEL_INPUTS: dict = {
    "dataslots": [TEST_MODEL_INPUT_DATASLOT],
    "parameters": [
        TEST_MODEL_INPUT_PARAMETER,
    ],
}

TEST_MODEL_INPUTS_DEFAULT: dict = {
    "parameters": [
        {
            "max": 2025,
            "min": 2016,
            "name": "YEAR",
            "type": "integer",
            "title": "Year input",
            "default": 2018,
            "required": True,
            "description": "Year input description",
        },
    ],
}

TEST_MODEL_OUTPUTS: dict = {
    "datasets": [
        {
            "name": "example_dataset.csv",
            "type": "CSV",
            "description": "",
        },
    ]
}

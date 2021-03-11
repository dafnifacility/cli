import pytest
from typing import List


@pytest.fixture
def get_models_list_fixture() -> List[dict]:
    """Test fixture for simulating the models data return
    from calling the get models API

    Returns:
        List[dict]: example get Models response
    """
    models = [
        {
            "name": "test model name",
            "summary": "this model is for use in tests for the Model class",
            "description": "This is a terribly long description of the test dictionary",
            "creation_date": "2021-01-01T00:00:00.000000Z",
            "publication_date": "2021-01-02T00:00:00.000000Z",
            "id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
            "version_tags": ["latest"],
            "container": "reg.dafni.rl.ac.uk/pilots/models/mobile-model/nims",
        },
        {
            "name": "test model name 2",
            "summary": "another testing model",
            "description": "Model 2 description",
            "creation_date": "2021-03-01T00:00:00.000000Z",
            "publication_date": "2021-05-02T00:00:00.000000Z",
            "id": "1a0a0a0a-0a00-0a00-a000-0a0a0000000a",
            "version_tags": ["latest"],
            "container": "reg.dafni.rl.ac.uk/pilots/models/mobile-model/nims",
        },
    ]

    return models


@pytest.fixture
def get_model_metadata_fixture() -> dict:
    """Test fixture for model metadata

    Returns:
        dict: Example metadata response structure
    """
    metadata = {
        "kind": "Model",
        "apiVersion": "v1alpha4",
        "metadata": {
            "displayName": "model display name",
            "name": "test-model",
            "summary": "Model summary",
            "description": "Model description",
            "type": "Simulation",
            "owner": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
        },
        "spec": {
            "inputs": {
                "env": [
                    {
                        "name": "R_NUMBER",
                        "title": "R Number",
                        "desc": "The reproduction number",
                        "type": "number",
                        "default": 1.5,
                        "min": 0.1,
                        "max": 2.0,
                    },
                    {
                        "name": "setting",
                        "title": "Setting",
                        "desc": "Mode to run the model in",
                        "type": "string",
                        "default": "long_default_name",
                    },
                ],
                "dataslots": [
                    {
                        "default": [
                            {
                                "uid": "11111a1a-a111-11aa-a111-11aa11111aaa",
                                "versionUid": "21111a1a-a111-11aa-a111-11aa11111aaa",
                            }
                        ],
                        "path": "inputs/",
                        "required": True,
                        "name": "Inputs",
                    }
                ],
            },
            "outputs": {
                "datasets": [
                    {
                        "name": "dataset_1.xls",
                        "type": "xls",
                        "desc": "Datset 1 description",
                    },
                    {
                        "name": "dataset_2.xls",
                        "type": "xls",
                        "desc": "Datset 2 description",
                    },
                ]
            },
            "image": "dreg.platform.dafni.rl.ac.uk/nims-prod/test-model:0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
        },
    }

    return metadata

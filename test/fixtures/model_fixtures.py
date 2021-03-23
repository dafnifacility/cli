import pytest
from typing import List, Tuple


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
            "version_history": [
                {
                    "id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
                    "version_tags": ["latest", "new_param"],
                    "published": "2021-02-01T00:00:00.000000Z",
                    "version_message": "version 1 message",
                },
                {
                    "id": "1a0a0a0a-0a00-0a00-a000-0a0a0000000a",
                    "version_tags": [],
                    "published": "2021-05-02T00:00:00.000000Z",
                    "version_message": "version 2 message",
                },
            ],
            "container": "reg.dafni.rl.ac.uk/pilots/models/mobile-model/nims",
        },
        {
            "name": "test model name 2",
            "summary": "another testing model",
            "description": "Model 2 description",
            "creation_date": "2021-03-01T00:00:00.000000Z",
            "publication_date": "2021-05-02T00:00:00.000000Z",
            "id": "1a0a0a0a-0a00-0a00-a000-0a0a0000000a",
            "version_tags": [],
            "version_history": [
                {
                    "id": "1a0a0a0a-0a00-0a00-a000-0a0a0000000a",
                    "version_tags": ["latest"],
                    "published": "2021-05-02T00:00:00.000000Z",
                    "version_message": "Latest message",
                }
            ],
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


@pytest.fixture
def get_model_upload_urls_fixture() -> Tuple[str, dict]:
    """Test fixture for model upload urls

    Returns:
        str: Example upload id
        dict: Example dict containing definition and image urls
    """
    upload_id = "00a0a000-00a0-0000-0000-00a0000a0000"
    upload_urls = {"definition": "https://nims-io.secure.dafni.rl.ac.uk/" +
                                 "78f9dfe8-dabe-404d-abfb-c4cd16b9ccab/" +
                                 "definition?X-Amz-Algorithm=AWS4-HMAC-SHA256" +
                                 "&X-Amz-Credential=3DCC953FC59AC3FB3AF5%2F20210319%2Fus-east-1%2Fs3%2Faws4_request" +
                                 "&X-Amz-Date=20210319T114018Z&X-Amz-Expires=14400&X-Amz-SignedHeaders=host" +
                                 "&X-Amz-Signature=5853a7e47b4e173c5e17ecfd799b2121f24809dae741ee95d93d040ddc14d1db",
                   "image": "https://nims-io.secure.dafni.rl.ac.uk/" +
                            "78f9dfe8-dabe-404d-abfb-c4cd16b9ccab/" +
                            "image?X-Amz-Algorithm=AWS4-HMAC-SHA256" +
                            "&X-Amz-Credential=3DCC953FC59AC3FB3AF5%2F20210319%2Fus-east-1%2Fs3%2Faws4_request" +
                            "&X-Amz-Date=20210319T114018Z&X-Amz-Expires=14400" +
                            "&X-Amz-SignedHeaders=host" +
                            "&X-Amz-Signature=be49a3a8fbcee39d2c07197d3bd1b48ef28c637b36a1a00557fdee6f9be90ff1"
                   }
    return upload_id, upload_urls

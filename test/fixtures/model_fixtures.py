import datetime as dt
from typing import List, Tuple

import pytest

from dafni_cli.auth import Auth
from dafni_cli.model.model import Model


@pytest.fixture
def get_models_list_fixture() -> List[dict]:
    """Test fixture for simulating the models data return
    from calling the get models API

    Returns:
        List[dict]: example get Models response
    """
    models = [
        {
            "creation_date": "2021-01-01T00:00:00.000000Z",
            "publication_date": "2021-01-02T00:00:00.000000Z",
            "id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
            "version_tags": ["latest"],
            "container": "reg.dafni.rl.ac.uk/pilots/models/mobile-model/nims",
            "metadata": {
                "description": "This is a terribly long description of the test dictionary",
                "name": "test model name",
                "summary": "this model is for use in tests for the Model class",
            },
            "auth": {
                "asset_id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
                "reason": "reason for accessing",
                "view": True,
                "read": True,
                "update": False,
                "destroy": False,
            },
        },
        {
            "creation_date": "2021-03-01T00:00:00.000000Z",
            "publication_date": "2021-05-02T00:00:00.000000Z",
            "id": "1a0a0a0a-0a00-0a00-a000-0a0a0000000a",
            "version_tags": [],
            "container": "reg.dafni.rl.ac.uk/pilots/models/mobile-model/nims",
            "metadata": {
                "description": "Model 2 description",
                "name": "test model name 2",
                "summary": "another testing model",
            },
            "auth": {
                "asset_id": "1a0a0a0a-0a00-0a00-a000-0a0a0000000a",
                "reason": "reason for accessing",
                "view": True,
                "read": True,
                "update": False,
                "destroy": False,
            },
        },
    ]

    return models


@pytest.fixture
def get_single_model_fixture() -> dict:
    """Test fixture for simulating the models data return
    from calling the get model <version-id> API

    Returns:
        List[dict]: example get Model <version-id> response
    """
    model = {
        "name": "test model name",
        "summary": "this model is for use in tests for the Model class",
        "description": "This is a terribly long description of the test dictionary",
        "creation_date": "2021-01-01T00:00:00.000000Z",
        "publication_date": "2021-01-02T00:00:00.000000Z",
        "id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
        "version_message": "test version message",
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
    }
    return model


@pytest.fixture
def get_model_metadata_fixture() -> dict:
    """
    Test fixture for model metadata

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
    metadata = {
        "displayName": "model display name",
        "name": "test-model",
        "summary": "Model summary",
        "description": "Model description",
        "type": "Simulation",
        "owner": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
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
    upload_urls = {
        "definition": "https://nims-io.secure.dafni.rl.ac.uk/"
        + "78f9dfe8-dabe-404d-abfb-c4cd16b9ccab/"
        + "definition?X-Amz-Algorithm=AWS4-HMAC-SHA256"
        + "&X-Amz-Credential=3DCC953FC59AC3FB3AF5%2F20210319%2Fus-east-1%2Fs3%2Faws4_request"
        + "&X-Amz-Date=20210319T114018Z&X-Amz-Expires=14400&X-Amz-SignedHeaders=host"
        + "&X-Amz-Signature=5853a7e47b4e173c5e17ecfd799b2121f24809dae741ee95d93d040ddc14d1db",
        "image": "https://nims-io.secure.dafni.rl.ac.uk/"
        + "78f9dfe8-dabe-404d-abfb-c4cd16b9ccab/"
        + "image?X-Amz-Algorithm=AWS4-HMAC-SHA256"
        + "&X-Amz-Credential=3DCC953FC59AC3FB3AF5%2F20210319%2Fus-east-1%2Fs3%2Faws4_request"
        + "&X-Amz-Date=20210319T114018Z&X-Amz-Expires=14400"
        + "&X-Amz-SignedHeaders=host"
        + "&X-Amz-Signature=be49a3a8fbcee39d2c07197d3bd1b48ef28c637b36a1a00557fdee6f9be90ff1",
    }
    return upload_id, upload_urls


def auth_mock(
    asset_id: str = "asset id",
    destroy: bool = True,
    name: str = "Auth name",
    read: bool = True,
    reason: str = "Auth reason",
    update: bool = True,
    view: bool = True,
) -> Auth:
    """Test fixture to generate an Auth object with given attributes

    Args:
        asset_id (str, optional): ID for the asset trying to be accessed. Defaults to "asset id".
        destroy (bool, optional): Whether the user has access to delete the entity. Defaults to True.
        name (str, optional): Name. Defaults to "Auth name".
        read (bool, optional): Whether the user has access to read the entity. Defaults to True.
        reason (str, optional): Reason for access. Defaults to "Auth reason".
        update (bool, optional): Whether the user has access to update the entity. Defaults to True.
        view (bool, option): Whether the user has access to view the entity. Defaults to True.

    Returns:
        Auth: Generated Auth object for testing
    """
    instance = Auth()
    instance.asset_id = asset_id
    instance.destroy = destroy
    instance.name = name
    instance.read = read
    instance.reason = reason
    instance.update = update
    instance.view = view

    return instance


def model_mock(
    container: str = "Container name",
    creation_time: dt.datetime = dt.datetime(2020, 1, 1, 00, 00, 00),
    description: str = "Model description",
    dictionary: dict = {"key": "value"},
    display_name: str = "Model name",
    privileges: Auth = auth_mock(),
    publication_time: dt.datetime = dt.datetime(2020, 1, 1, 00, 00, 00),
    summary: str = "Model summary",
    version_id: str = "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
    version_message: str = "Version message",
    version_tags: List[str] = ["tag1", "tag2"],
) -> Model:
    """Test fixture to generate a Model object with given attributes

    Args:
        container (str, optional): Container name. Defaults to "Container name".
        creation_time (dt.datetime, optional): Formatted creation time. Defaults to midnight on 01/01/2020.
        description (str, optional): Model description. Defaults to "Model description".
        dictionary (dict, optional): Model dictionary. Defaults to {"key": "value"}.
        display_name (str, optional): Model display name. Defaults to "Model name".
        privileges (Auth, optional): Authorisation for model. Defaults to mock_auth.
        publication_time (dt.datetime, optional): Formatted publication time. Defaults to midnight on 01/01/2020.
        summary (str, optional): Summary of model. Defaults to "Model summary".
        version_id (str, optional): Version ID of model. Defaults to "0a0a0a0a-0a00-0a00-a000-0a0a0000000a".
        version_message (str, optional): Version message associated with model version. Defaults to "Version message".
        version_tags (List[str], optional): Version tags associated with model version. Defaults to ["tag1", "tag2"].

    Returns:
        Model: Generated Model object for testing
    """

    instance = Model()
    instance.container = container
    instance.creation_time = creation_time
    instance.description = description
    instance.dictionary = dictionary
    instance.display_name = display_name
    instance.privileges = privileges
    instance.publication_time = publication_time
    instance.summary = summary
    instance.version_id = version_id
    instance.version_message = version_message
    instance.version_tags = version_tags

    return instance

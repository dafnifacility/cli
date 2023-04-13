import pytest


@pytest.fixture
def model_auth_fixture() -> dict:
    """Function to generate an auth dictionary with identical keys to those
    returned from a get model request.

    Returns:
        dict: Mock auth dictionary
    """
    auth = {
        "asset_id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
        "reason": "reason for access",
        "view": True,
        "read": True,
        "update": False,
        "destroy": False,
    }
    return auth


@pytest.fixture
def dataset_auth_fixture() -> dict:
    """Function to generate an auth dictionary with identical keys to those
        returned from a get dataset request.

    Returns:
        dict: Mock auth dictionary
    """
    auth = {
        "name": "Executor",
        "reason": "reason for access",
        "view": True,
        "read": True,
        "update": False,
        "destroy": False,
    }
    return auth

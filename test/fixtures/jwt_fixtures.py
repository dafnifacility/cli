import pytest
from mock import MagicMock, PropertyMock

JWT = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJsb2dpbi1hcHAtand0IiwiZXhwIjoxNjE0Nzg2MTk0LCJzdWIiOiJlMTA5MmMzZS1iZTA0LTRjMTktOTU3Zi1jZDg4NGU1MzQ0N2UifQ.EZ7dIoMR9e-M1Zm2YavswHrfOMKpq1EJmw_B_m78FkA"


@pytest.fixture
def request_response_fixture() -> MagicMock:
    """Helper fixture to setup a mock response
    containing the required cookies

    Returns:
        MagicMock: Mocked response object
    """
    # setup response mock object
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"key": "value"}
    # setup cookies
    cookies_mock = PropertyMock(return_value={"access_token": JWT})
    type(mock_response).cookies = cookies_mock

    return mock_response


@pytest.fixture
def processed_jwt_fixture() -> dict:
    """Helper fixture to return a mock processed
    DAFNI JWT

    Returns:
        dict: processed DAFNI JWT
    """
    user_jwt = {
        "expiry": "03/03/2021 12:26:25",
        "user_id": "e1092c3e-be04-4c19-957f-cd884e53447e",
        "user_name": "john-doe",
        "jwt": "Bearer " + JWT,
    }

    return user_jwt

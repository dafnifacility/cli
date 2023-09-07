import json
from typing import Optional
from unittest.mock import MagicMock

from requests import HTTPError

from dafni_cli.api.session import SessionData

TEST_ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJsb2dpbi1hcHAtand0IiwiZXhwIjoxNjE0Nzg2MTk0LCJzdWIiOiJlMTA5MmMzZS1iZTA0LTRjMTktOTU3Zi1jZDg4NGU1MzQ0N2UifQ.EZ7dIoMR9e-M1Zm2YavswHrfOMKpq1EJmw_B_m78FkA"
TEST_SESSION_DATA = SessionData(
    username="test_username",
    access_token=TEST_ACCESS_TOKEN,
    refresh_token="some_refresh_token",
    timestamp_to_refresh=float("inf"),
)
TEST_SESSION_FILE = f"{json.dumps(TEST_SESSION_DATA.__dict__)}"


def create_mock_response(status_code: int, json: Optional[dict] = None):
    """Creates and returns a MagicMock for replacing requests.Response in
    session requests

    Automatically assigns the 'ok' and 'raise_for_status' parameters
    according to whether the status_code is below 400 or not. In the case
    it is >= 400, raise_for_status will return a HTTPError as it would
    normally and 'ok' will return True.

    Args:
        status_code (int): Status code of the response
        json (dict): Any json data to return from the response
    """
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.ok = status_code < 400
    mock_response.json.return_value = json
    if status_code >= 400:
        mock_response.raise_for_status.side_effect = HTTPError(
            f"Test error {status_code}"
        )
    return mock_response


def create_mock_access_token_response():
    """Creates and returns a MagicMock for replacing requests post response
    for obtaining an access_token"""

    return create_mock_response(
        200,
        {
            "access_token": TEST_ACCESS_TOKEN,
            "refresh_token": "some_refresh_token",
            "expires_in": 300,
        },
    )


def create_mock_token_expiry_response():
    """Returns a mock response indicating an access token as become invalid"""
    return create_mock_response(
        403,
        {
            "error": "invalid_grant",
            "error_message": "Some error message",
        },
    )


def create_mock_invalid_login_response():
    """Returns a mock response indicating a username/password was rejected"""
    return create_mock_response(
        401,
        {
            "error": "invalid_grant",
            "error_message": "Some error message",
        },
    )


def create_mock_token_expiry_redirect_response():
    """Returns a mock redirect response indicating an access token as become
    invalid"""
    return create_mock_response(302)


def create_mock_refresh_token_expiry_response():
    """Returns a mock response indicating a refresh token has become invalid"""
    return create_mock_response(
        400,
        {
            "error": "invalid_grant",
            "error_message": "Some error message",
        },
    )


def create_mock_invalid_password_response():
    """Returns a mock response when logging in with an invalid username or
    password"""
    return create_mock_response(
        401,
        {
            "error": "invalid_grant",
            "error_message": "Some error message",
        },
    )


def create_mock_success_response():
    """Returns a mock successful response"""
    return create_mock_response(200)


def create_mock_error_response():
    """Returns a mock response with a single error"""
    return create_mock_response(
        400,
        {"error": "Error"},
    )


def create_mock_error_message_response():
    """Returns a mock response with a single error with a message"""
    return create_mock_response(
        400,
        {
            "error": "Error",
            "error_message": "Error message",
        },
    )


def create_mock_errors_response():
    """Returns a mock response with a multiple error messages"""
    return create_mock_response(
        400,
        {
            "errors": ["Sample error 1", "Sample error 2"],
        },
    )


def create_mock_metadata_errors_response():
    """Returns a mock response with a multiple error messages"""
    return create_mock_response(
        400,
        {
            "metadata": ["Error: Sample error 1", "Error: Sample error 2"],
        },
    )

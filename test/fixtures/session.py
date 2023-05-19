from typing import Optional
from unittest.mock import MagicMock

from requests import HTTPError


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

import json
from pathlib import Path
import unittest
from unittest.mock import MagicMock, mock_open, patch

from dafni_cli.api.session import DAFNISession, SessionData
from dafni_cli.consts import LOGIN_API_ENDPOINT, LOGOUT_API_ENDPOINT, REQUESTS_TIMEOUT

TEST_ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJsb2dpbi1hcHAtand0IiwiZXhwIjoxNjE0Nzg2MTk0LCJzdWIiOiJlMTA5MmMzZS1iZTA0LTRjMTktOTU3Zi1jZDg4NGU1MzQ0N2UifQ.EZ7dIoMR9e-M1Zm2YavswHrfOMKpq1EJmw_B_m78FkA"
TEST_SESSION_DATA = SessionData(
    username="test_username",
    user_id="e1092c3e-be04-4c19-957f-cd884e53447e",
    access_token=TEST_ACCESS_TOKEN,
    refresh_token="some_refresh_token",
)
TEST_SESSION_FILE = f"{json.dumps(TEST_SESSION_DATA.__dict__)}"


@patch("dafni_cli.api.session.requests")
class TestDAFNISession(unittest.TestCase):
    """Tests the DAFNISession class"""

    def create_mock_session(self, use_file: bool):
        """Loads a mock session while mocking whether a session file exists or not"""
        with patch.object(Path, "is_file") as mock_is_file:
            with patch(
                "builtins.open", new_callable=mock_open, read_data=TEST_SESSION_FILE
            ):
                mock_is_file.return_value = use_file

                return DAFNISession()

    def create_mock_session_post(self):
        """Creates and returns a MagicMock for replacing requests post response
        for obtaining an access_token"""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": TEST_ACCESS_TOKEN,
            "refresh_token": "some_refresh_token",
        }
        return mock_response

    def test_session_load(
        self,
        mock_requests,
    ):
        """Tests loading of session with a given username and password"""

        mock_requests.post.return_value = self.create_mock_session_post()

        session = DAFNISession.login(username="test_username", password="test_password")

        mock_requests.post.assert_called_once_with(
            LOGIN_API_ENDPOINT,
            data={
                "username": "test_username",
                "password": "test_password",
                "client_id": "dafni-main",
                "grant_type": "password",
                "scope": "openid",
            },
            timeout=REQUESTS_TIMEOUT,
        )

        self.assertEqual(session._session_data.__dict__, TEST_SESSION_DATA.__dict__)

    def test_session_load_from_file(self, mock_requests):
        """Tests can load existing session from a file"""

        session = self.create_mock_session(True)

        self.assertEqual(session._session_data.__dict__, TEST_SESSION_DATA.__dict__)

    @patch("click.prompt")
    def test_session_load_from_user(
        self,
        mock_click_prompt,
        mock_requests,
    ):
        """Tests loading of a new session requiring input from the user"""

        # Username and password prompt
        mock_click_prompt.side_effect = ["test_username", "test_password"]

        mock_requests.post.return_value = self.create_mock_session_post()

        session = self.create_mock_session(False)
        self.assertEqual(session._session_data.__dict__, TEST_SESSION_DATA.__dict__)

        mock_requests.post.assert_called_once_with(
            LOGIN_API_ENDPOINT,
            data={
                "username": "test_username",
                "password": "test_password",
                "client_id": "dafni-main",
                "grant_type": "password",
                "scope": "openid",
            },
            timeout=REQUESTS_TIMEOUT,
        )

    def test_session_logout(self, mock_requests):
        """Tests can load existing session from a file"""

        session = self.create_mock_session(True)

        with patch.object(Path, "unlink") as mock_unlink:
            session.logout()
            mock_unlink.assert_called_once_with()

        mock_requests.post.assert_called_once_with(
            LOGOUT_API_ENDPOINT,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Bearer {TEST_ACCESS_TOKEN}",
            },
            data={
                "client_id": "dafni-main",
                "refresh_token": "some_refresh_token",
                "scope": "openid",
            },
            timeout=REQUESTS_TIMEOUT,
        )

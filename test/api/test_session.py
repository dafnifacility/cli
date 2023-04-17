import json
import unittest
from pathlib import Path
from unittest.mock import MagicMock, call, mock_open, patch

from dafni_cli.api.session import DAFNISession, LoginError, SessionData
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

    def create_mock_session(self, use_file: bool, return_mock_file=False):
        """Loads a mock session while mocking whether a session file exists or not

        Args:
            return_mock_file (bool): When true also returns the mock file object for asserting
                                     any specific file operations are handled correctly
        """

        with patch.object(Path, "is_file") as mock_is_file:
            with patch(
                "builtins.open", new_callable=mock_open, read_data=TEST_SESSION_FILE
            ) as mock_file:
                mock_is_file.return_value = use_file

                if not return_mock_file:
                    return DAFNISession()
                else:
                    return DAFNISession(), mock_file()

    def create_mock_access_token_response(self):
        """Creates and returns a MagicMock for replacing requests post response
        for obtaining an access_token"""

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": TEST_ACCESS_TOKEN,
            "refresh_token": "some_refresh_token",
        }
        return mock_response

    def create_mock_token_expiry_response(self):
        """Returns a mock response indicating an access token as become invalid"""
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.json.return_value = {
            "error": "invalid_grant",
            "error_message": "Some error message",
        }
        return mock_response

    def create_mock_refresh_token_expiry_response(self):
        """Returns a mock response indicating a refresh token has become invalid"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": "invalid_grant",
            "error_message": "Some error message",
        }
        return mock_response

    def create_mock_success_response(self):
        """Returns a mock response indicating an access token as become invalid"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        return mock_response

    def test_load(
        self,
        mock_requests,
    ):
        """Tests loading of session with a given username and password"""

        # Setup
        mock_requests.post.return_value = self.create_mock_access_token_response()

        # Attempt login
        session = DAFNISession.login(username="test_username", password="test_password")

        # Expect post to be called, and appropriate session data to have
        # been loaded from the obtained JWT
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

    def test_load_error(
        self,
        mock_requests,
    ):
        """Tests loading of session with an invalid username and/or password"""

        # Setup
        mock_requests.post.return_value = self.create_mock_token_expiry_response()

        # Attempt login
        with self.assertRaises(LoginError):
            DAFNISession.login(
                username="test_username", password="test_password"
            )

    def test_load_from_file(self, mock_requests):
        """Tests can load existing session from a file"""

        session = self.create_mock_session(True)

        self.assertEqual(session._session_data.__dict__, TEST_SESSION_DATA.__dict__)

    @patch("click.prompt")
    def test_load_from_user(
        self,
        mock_click_prompt,
        mock_requests,
    ):
        """Tests loading of a new session requiring input from the user"""

        # Setup
        mock_click_prompt.side_effect = ["test_username", "test_password"]
        mock_requests.post.return_value = self.create_mock_access_token_response()

        # Create session using input from user
        session, mock_file = self.create_mock_session(False, return_mock_file=True)

        # Expect post to be called, and appropriate session data to have
        # been loaded from the obtained JWT
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

        # Ensure session file is written
        mock_file.write.assert_called_once_with(
            json.dumps(session._session_data.__dict__)
        )

    def test_logout(self, mock_requests):
        """Tests can load existing session from a file"""

        # Load session from file data
        session = self.create_mock_session(True)

        # Mock unlink of file (as non existent anyway)
        with patch.object(Path, "unlink") as mock_unlink:
            session.logout()
            mock_unlink.assert_called_once_with()

        # Ensure appropriate logout endpoint is called
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

    def test_get_request(self, mock_requests):
        """Tests sending a get request via the DAFNISession"""

        session = self.create_mock_session(True)

        session.get_request(url="some_test_url", content_type="content_type")

        mock_requests.request.assert_called_once_with(
            "get",
            url="some_test_url",
            headers={
                "Authorization": f"Bearer {TEST_ACCESS_TOKEN}",
                "Content-Type": "content_type",
            },
            data=None,
            json=None,
            allow_redirects=False,
            timeout=REQUESTS_TIMEOUT,
        )

    def test_post_request(self, mock_requests):
        """Tests sending a post request via the DAFNISession"""

        session = self.create_mock_session(True)

        session.post_request(url="some_test_url", content_type="content_type")

        mock_requests.request.assert_called_once_with(
            "post",
            url="some_test_url",
            headers={
                "Authorization": f"Bearer {TEST_ACCESS_TOKEN}",
                "Content-Type": "content_type",
            },
            data=None,
            json=None,
            allow_redirects=False,
            timeout=REQUESTS_TIMEOUT,
        )

    def test_put_request(self, mock_requests):
        """Tests sending a put request via the DAFNISession"""

        session = self.create_mock_session(True)

        session.put_request(url="some_test_url", content_type="content_type")

        mock_requests.request.assert_called_once_with(
            "put",
            url="some_test_url",
            headers={
                "Authorization": f"Bearer {TEST_ACCESS_TOKEN}",
                "Content-Type": "content_type",
            },
            data=None,
            json=None,
            allow_redirects=False,
            timeout=REQUESTS_TIMEOUT,
        )

    def test_patch_request(self, mock_requests):
        """Tests sending a patch request via the DAFNISession"""

        session = self.create_mock_session(True)

        session.patch_request(url="some_test_url", content_type="content_type")

        mock_requests.request.assert_called_once_with(
            "patch",
            url="some_test_url",
            headers={
                "Authorization": f"Bearer {TEST_ACCESS_TOKEN}",
                "Content-Type": "content_type",
            },
            data=None,
            json=None,
            allow_redirects=False,
            timeout=REQUESTS_TIMEOUT,
        )

    def test_delete_request(self, mock_requests):
        """Tests sending a delete request via the DAFNISession"""

        session = self.create_mock_session(True)

        session.delete_request(url="some_test_url")

        mock_requests.request.assert_called_once_with(
            "delete",
            url="some_test_url",
            headers={
                "Authorization": f"Bearer {TEST_ACCESS_TOKEN}",
            },
            data=None,
            json=None,
            allow_redirects=False,
            timeout=REQUESTS_TIMEOUT,
        )

    def test_refresh(self, mock_requests):
        """Tests token refreshing on an authentication failure"""

        session = self.create_mock_session(True)

        # Here will test only on the get request as the logic is handled by
        # the base function called by all requests anyway

        # To trigger a refresh need a response with a 403 status code, then
        # should be successful when retried
        mock_requests.request.side_effect = [
            self.create_mock_token_expiry_response(),
            self.create_mock_success_response(),
        ]

        # New token
        mock_requests.post.return_value = self.create_mock_access_token_response()

        with patch(
            "builtins.open", new_callable=mock_open, read_data=TEST_SESSION_FILE
        ) as mock_file:
            session.get_request(url="some_test_url")

            # Should save new token
            mock_file = mock_file()
            mock_file.write.assert_called_once_with(
                json.dumps(session._session_data.__dict__)
            )

        # Expect a request to obtain a new token
        mock_requests.post.assert_called_once_with(
            LOGIN_API_ENDPOINT,
            data={
                "client_id": "dafni-main",
                "grant_type": "refresh_token",
                "refresh_token": "some_refresh_token",
            },
            timeout=REQUESTS_TIMEOUT,
        )

        # Ensure get request is attempted again (should be successful the
        # second time here)
        self.assertEqual(mock_requests.request.call_count, 2)

    def test_refresh_error(self, mock_requests):
        """Tests appropriate error is thrown if refreshing a token fails."""

        session = self.create_mock_session(True)

        # Here will test only on the get request as the logic is handled by
        # the base function called by all requests anyway

        # To trigger a refresh need a response with a 403 status code, then
        # should be successful when retried - here we keep it failing
        mock_requests.request.return_value = self.create_mock_token_expiry_response()

        # New token
        mock_requests.post.return_value = self.create_mock_access_token_response()

        with self.assertRaises(RuntimeError) as error:
            session.get_request(url="some_test_url")

        self.assertEqual(str(error.exception), "Could not authenticate request")

    @patch("click.prompt")
    def test_refresh_expiry(self, mock_click_prompt, mock_requests):
        """Tests refresh token expiry is handled correctly."""

        session = self.create_mock_session(True)

        # Here will test only on the get request as the logic is handled by
        # the base function called by all requests anyway

        # To trigger a refresh need a response with a 403 status code, then
        # should be successful when retried
        mock_requests.request.side_effect = [
            self.create_mock_token_expiry_response(),
            self.create_mock_success_response(),
        ]

        mock_requests.post.side_effect = [
            # Token authentication expiry when trying to obtain a new one
            self.create_mock_refresh_token_expiry_response(),
            # Successful login using user provided credentials
            self.create_mock_access_token_response(),
        ]

        # Will want a new username and password
        mock_click_prompt.side_effect = ["test_username", "test_password"]

        with patch(
            "builtins.open", new_callable=mock_open, read_data=TEST_SESSION_FILE
        ) as mock_file:
            session.get_request(url="some_test_url")

            # Should save new token
            mock_file = mock_file()
            mock_file.write.assert_called_once_with(
                json.dumps(session._session_data.__dict__)
            )

        # Expect a request to obtain a new token
        mock_requests.post.assert_has_calls(
            [
                # Attempt to get new token using refresh token
                call(
                    LOGIN_API_ENDPOINT,
                    data={
                        "client_id": "dafni-main",
                        "grant_type": "refresh_token",
                        "refresh_token": "some_refresh_token",
                    },
                    timeout=REQUESTS_TIMEOUT,
                ),
                # New token request
                call(
                    LOGIN_API_ENDPOINT,
                    data={
                        "username": "test_username",
                        "password": "test_password",
                        "client_id": "dafni-main",
                        "grant_type": "password",
                        "scope": "openid",
                    },
                    timeout=REQUESTS_TIMEOUT,
                ),
            ]
        )

        # Ensure get request is attempted again (should be successful the
        # second time here)
        self.assertEqual(mock_requests.request.call_count, 2)

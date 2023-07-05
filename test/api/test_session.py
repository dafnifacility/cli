import json
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, call, mock_open, patch

from requests import HTTPError
import requests

from dafni_cli.api.exceptions import DAFNIError, EndpointNotFoundError
from dafni_cli.api.session import DAFNISession, LoginError, SessionData
from dafni_cli.consts import (
    LOGIN_API_ENDPOINT,
    LOGOUT_API_ENDPOINT,
    REQUESTS_TIMEOUT,
    SESSION_COOKIE,
    URLS_REQUIRING_COOKIE_AUTHENTICATION,
)

from test.fixtures.session import create_mock_response

TEST_ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJsb2dpbi1hcHAtand0IiwiZXhwIjoxNjE0Nzg2MTk0LCJzdWIiOiJlMTA5MmMzZS1iZTA0LTRjMTktOTU3Zi1jZDg4NGU1MzQ0N2UifQ.EZ7dIoMR9e-M1Zm2YavswHrfOMKpq1EJmw_B_m78FkA"
TEST_SESSION_DATA = SessionData(
    username="test_username",
    access_token=TEST_ACCESS_TOKEN,
    refresh_token="some_refresh_token",
)
TEST_SESSION_FILE = f"{json.dumps(TEST_SESSION_DATA.__dict__)}"


@patch("dafni_cli.api.session.requests")
class TestDAFNISession(TestCase):
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

        return create_mock_response(
            200,
            {
                "access_token": TEST_ACCESS_TOKEN,
                "refresh_token": "some_refresh_token",
            },
        )

    def create_mock_token_expiry_response(self):
        """Returns a mock response indicating an access token as become invalid"""
        return create_mock_response(
            403,
            {
                "error": "invalid_grant",
                "error_message": "Some error message",
            },
        )

    def create_mock_token_expiry_response_dataset_metadata(self):
        """Returns a mock response indicating an access token as become invalid
        while accessing a datasets metadata via the S&D"""
        return create_mock_response(
            400,
            {
                "errors": [
                    "Invalid request: Access to Dataset with dataset_id 'None' "
                    "and version ID '5507336e-a4c8-428a-a92b-4928be29233a' denied."
                ]
            },
        )

    def create_mock_invalid_login_response(self):
        """Returns a mock response indicating a username/password was rejected"""
        return create_mock_response(
            401,
            {
                "error": "invalid_grant",
                "error_message": "Some error message",
            },
        )

    def create_mock_token_expiry_redirect_response(self):
        """Returns a mock redirect response indicating an access token as become
        invalid"""
        return create_mock_response(302)

    def create_mock_refresh_token_expiry_response(self):
        """Returns a mock response indicating a refresh token has become invalid"""
        return create_mock_response(
            400,
            {
                "error": "invalid_grant",
                "error_message": "Some error message",
            },
        )

    def create_mock_invalid_password_response(self):
        """Returns a mock response when logging in with an invalid username or
        password"""
        return create_mock_response(
            401,
            {
                "error": "invalid_grant",
                "error_message": "Some error message",
            },
        )

    def create_mock_success_response(self):
        """Returns a mock successful response"""
        return create_mock_response(200)

    def create_mock_error_response(self):
        """Returns a mock response with a single error"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "Error"}
        return create_mock_response(
            400,
            {"error": "Error"},
        )

    def create_mock_error_message_response(self):
        """Returns a mock response with a single error with a message"""
        return create_mock_response(
            400,
            {
                "error": "Error",
                "error_message": "Error message",
            },
        )

    def create_mock_errors_response(self):
        """Returns a mock response with a multiple error messages"""
        return create_mock_response(
            400,
            {
                "errors": ["Sample error 1", "Sample error 2"],
            },
        )

    def create_mock_metadata_errors_response(self):
        """Returns a mock response with a multiple error messages"""
        return create_mock_response(
            400,
            {
                "metadata": ["Error: Sample error 1", "Error: Sample error 2"],
            },
        )

    def test_has_session_file(self, mock_requests):
        """Tests has_session_file works correctly"""

        session = self.create_mock_session(True)

        with patch.object(Path, "is_file") as mock_is_file:
            mock_is_file.return_value = False
            self.assertEqual(session.has_session_file(), False)

            mock_is_file.return_value = True
            self.assertEqual(session.has_session_file(), True)

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

    def test_load_invalid_login(
        self,
        mock_requests,
    ):
        """Tests loading of session with an invalid username and/or password"""

        # Setup
        mock_requests.post.return_value = self.create_mock_invalid_login_response()

        # Attempt login
        with self.assertRaises(LoginError) as err:
            DAFNISession.login(username="test_username", password="test_password")
        self.assertEqual(
            str(err.exception),
            "Failed to login. Please check your username and password and try again.",
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

    @patch("click.prompt")
    def test_load_from_user_repeated(
        self,
        mock_click_prompt,
        mock_requests,
    ):
        """Tests loading of a new session requiring input from the user, while
        they get the username or password wrong initially."""

        # Setup
        mock_click_prompt.side_effect = [
            "test_username_wrong",
            "test_password_wrong",
            "test_username",
            "test_password",
        ]
        mock_requests.post.side_effect = [
            self.create_mock_invalid_password_response(),
            self.create_mock_access_token_response(),
        ]

        # Create session using input from user
        session, mock_file = self.create_mock_session(False, return_mock_file=True)

        # Expect post to be called, and appropriate session data to have
        # been loaded from the obtained JWT
        mock_requests.post.assert_has_calls(
            [
                call(
                    LOGIN_API_ENDPOINT,
                    data={
                        "username": "test_username_wrong",
                        "password": "test_password_wrong",
                        "client_id": "dafni-main",
                        "grant_type": "password",
                        "scope": "openid",
                    },
                    timeout=REQUESTS_TIMEOUT,
                ),
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

    def test_get_error_message_with_no_error(self, mock_requests):
        """Tests get_error_message when there is no error message"""
        session = self.create_mock_session(True)

        error_message = session.get_error_message(create_mock_response(200, {}))
        self.assertEqual(error_message, None)

    def test_get_error_message_simple(self, mock_requests):
        """Tests get_error_message when there is a simple error message"""
        session = self.create_mock_session(True)

        mock_response = self.create_mock_error_response()
        error_message = session.get_error_message(mock_response)
        self.assertEqual(error_message, f"Error: {mock_response.json()['error']}")

    def test_get_error_message(self, mock_requests):
        """Tests get_error_message when there is a specific error message"""
        session = self.create_mock_session(True)

        mock_response = self.create_mock_error_message_response()
        error_message = session.get_error_message(mock_response)
        self.assertEqual(
            error_message,
            f"Error: {mock_response.json()['error']}, {mock_response.json()['error_message']}",
        )

    def test_get_error_message_with_multiple_errors(self, mock_requests):
        """Tests get_error_message when there are multiple errors"""
        session = self.create_mock_session(True)

        mock_response = self.create_mock_errors_response()
        error_message = session.get_error_message(mock_response)
        expected_errors = mock_response.json()["errors"]
        self.assertEqual(
            error_message,
            "The following errors were returned:\n"
            f"Error: {expected_errors[0]}\nError: {expected_errors[1]}",
        )

    def test_get_error_message_with_multiple_metadata_errors(self, mock_requests):
        """Tests get_error_message when there are multiple errors listed under
        'metadata'"""
        session = self.create_mock_session(True)

        mock_response = self.create_mock_metadata_errors_response()
        error_message = session.get_error_message(mock_response)
        expected_errors = mock_response.json()["metadata"]
        self.assertEqual(
            error_message,
            "Found errors in metadata:\n" f"{expected_errors[0]}\n{expected_errors[1]}",
        )

    def test_get_error_message_handles_decode_error(self, mock_requests):
        """Tests get_error_message when JSON decoding fails"""
        session = self.create_mock_session(True)

        mock_response = self.create_mock_error_response()
        # Unpatch this to avoid TypeError in except block
        mock_requests.JSONDecodeError = requests.JSONDecodeError
        mock_response.json.side_effect = requests.JSONDecodeError("", "", 0)
        error_message = session.get_error_message(mock_response)
        self.assertEqual(error_message, None)

    def test_check_response_raises_endpoint_not_found(self, mock_requests):
        """Tests _check_response raises an EndpointNotFoundError when necessary"""
        session = self.create_mock_session(True)

        with self.assertRaises(EndpointNotFoundError) as err:
            session._check_response("test_url", create_mock_response(404))
        self.assertEqual(str(err.exception), "Could not find test_url")

    def test_check_response_raises_dafni_error(self, mock_requests):
        """Tests _check_response raises a DAFNIError when a specific error is
        given in a failed response"""
        session = self.create_mock_session(True)
        session.get_error_message = MagicMock()
        session.get_error_message.return_value = "Some error message"

        with self.assertRaises(DAFNIError) as err:
            session._check_response("test_url", create_mock_response(400))
        self.assertEqual(str(err.exception), "Some error message")

    def test_check_response_raises_http_error(self, mock_requests):
        """Tests _check_response raises a HTTPError when no specific error
        message is found"""
        session = self.create_mock_session(True)
        session.get_error_message = MagicMock()
        session.get_error_message.return_value = None

        with self.assertRaises(HTTPError) as err:
            session._check_response("test_url", create_mock_response(400))
        self.assertEqual(str(err.exception), "Test error 400")

    def test_authenticated_request_header_auth(self, mock_requests):
        """Tests sending a request via the DAFNISession uses header based
        authentication"""

        session = self.create_mock_session(True)

        session._authenticated_request(
            "get",
            url="test_url",
            headers={},
            data=None,
            json=None,
            allow_redirect=False,
        )

        mock_requests.request.assert_called_once_with(
            "get",
            url="test_url",
            headers={"Authorization": f"Bearer {TEST_ACCESS_TOKEN}"},
            data=None,
            json=None,
            allow_redirects=False,
            timeout=REQUESTS_TIMEOUT,
        )

    def _test_authenticated_request_cookie_auth(self, mock_requests, url: str):
        """Helper function that tests sending a request via the DAFNISession
        uses cookie authentication for a specific URL"""

        session = self.create_mock_session(True)

        session._authenticated_request(
            "get",
            url=url,
            headers={},
            data=None,
            json=None,
            allow_redirect=False,
        )

        mock_requests.request.assert_called_once_with(
            "get",
            url=url,
            headers={},
            data=None,
            json=None,
            allow_redirects=False,
            timeout=REQUESTS_TIMEOUT,
            cookies={SESSION_COOKIE: TEST_ACCESS_TOKEN},
        )

    def test_authenticated_request_cookie_auth(self, mock_requests):
        """Tests sending a request via the DAFNISession uses cookie
        authentication for any URL that should require it"""
        for url in URLS_REQUIRING_COOKIE_AUTHENTICATION:
            mock_requests.reset_mock()
            self._test_authenticated_request_cookie_auth(
                mock_requests, f"{url}/testendpoint"
            )

    def test_get_request(self, mock_requests):
        """Tests sending a get request via the DAFNISession"""

        session = self.create_mock_session(True)
        session._check_response = MagicMock()

        result = session.get_request(url="some_test_url", content_type="content_type")

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
        session._check_response.assert_called_once_with(
            "some_test_url", mock_requests.request.return_value
        )
        self.assertEqual(result, mock_requests.request.return_value.json.return_value)

    def test_get_request_when_content_true(self, mock_requests):
        """Tests sending a get request via the DAFNISession when content=True"""

        session = self.create_mock_session(True)
        session._check_response = MagicMock()

        result = session.get_request(
            url="some_test_url", content_type="content_type", content=True
        )

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
        session._check_response.assert_called_once_with(
            "some_test_url", mock_requests.request.return_value
        )
        self.assertEqual(result, mock_requests.request.return_value.content)

    def test_post_request(self, mock_requests):
        """Tests sending a post request via the DAFNISession"""

        session = self.create_mock_session(True)
        session._check_response = MagicMock()

        result = session.post_request(url="some_test_url", content_type="content_type")

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
        session._check_response.assert_called_once_with(
            "some_test_url", mock_requests.request.return_value
        )
        self.assertEqual(result, mock_requests.request.return_value.json.return_value)

    def test_post_request_when_content_true(self, mock_requests):
        """Tests sending a post request via the DAFNISession when content=True"""

        session = self.create_mock_session(True)
        session._check_response = MagicMock()

        result = session.post_request(
            url="some_test_url", content_type="content_type", content=True
        )

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
        session._check_response.assert_called_once_with(
            "some_test_url", mock_requests.request.return_value
        )
        self.assertEqual(result, mock_requests.request.return_value.content)

    def test_put_request(self, mock_requests):
        """Tests sending a put request via the DAFNISession"""

        session = self.create_mock_session(True)
        session._check_response = MagicMock()

        result = session.put_request(url="some_test_url", content_type="content_type")

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
        session._check_response.assert_called_once_with(
            "some_test_url", mock_requests.request.return_value
        )
        self.assertEqual(result, mock_requests.request.return_value)

    def test_put_request_when_content_true(self, mock_requests):
        """Tests sending a put request via the DAFNISession when content=True"""

        session = self.create_mock_session(True)
        session._check_response = MagicMock()

        result = session.put_request(
            url="some_test_url", content_type="content_type", content=True
        )

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
        session._check_response.assert_called_once_with(
            "some_test_url", mock_requests.request.return_value
        )
        self.assertEqual(result, mock_requests.request.return_value.content)

    def test_patch_request(self, mock_requests):
        """Tests sending a patch request via the DAFNISession"""

        session = self.create_mock_session(True)
        session._check_response = MagicMock()

        result = session.patch_request(url="some_test_url", content_type="content_type")

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
        session._check_response.assert_called_once_with(
            "some_test_url", mock_requests.request.return_value
        )
        self.assertEqual(result, mock_requests.request.return_value.json.return_value)

    def test_patch_request_when_content_true(self, mock_requests):
        """Tests sending a patch request via the DAFNISession when content=True"""

        session = self.create_mock_session(True)
        session._check_response = MagicMock()

        result = session.patch_request(
            url="some_test_url", content_type="content_type", content=True
        )

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
        session._check_response.assert_called_once_with(
            "some_test_url", mock_requests.request.return_value
        )
        self.assertEqual(result, mock_requests.request.return_value.content)

    def test_delete_request(self, mock_requests):
        """Tests sending a delete request via the DAFNISession"""

        session = self.create_mock_session(True)
        session._check_response = MagicMock()

        result = session.delete_request(url="some_test_url")

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
        session._check_response.assert_called_once_with(
            "some_test_url", mock_requests.request.return_value
        )
        self.assertEqual(result, mock_requests.request.return_value)

    def test_delete_request_when_content_true(self, mock_requests):
        """Tests sending a delete request via the DAFNISession when content=True"""

        session = self.create_mock_session(True)
        session._check_response = MagicMock()

        result = session.delete_request(url="some_test_url", content=True)

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
        session._check_response.assert_called_once_with(
            "some_test_url", mock_requests.request.return_value
        )
        self.assertEqual(result, mock_requests.request.return_value.content)

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

    def test_refresh_from_redirect(self, mock_requests):
        """Tests token refreshing on an authentication failure where we
        receive an unexpected redirect rather than a direct authentication
        error"""

        session = self.create_mock_session(True)

        # Here will test only on the get request as the logic is handled by
        # the base function called by all requests anyway

        # To trigger a refresh need a response with a 403 status code, then
        # should be successful when retried
        mock_requests.request.side_effect = [
            self.create_mock_token_expiry_redirect_response(),
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

    def test_refresh_dataset_metadata(self, mock_requests):
        """Tests token refreshing on an authentication failure for the S&D
        /metadata endpoint"""

        session = self.create_mock_session(True)

        # Here will test only on the get request as the logic is handled by
        # the base function called by all requests anyway

        # To trigger a refresh need a response with a 403 status code, then
        # should be successful when retried
        mock_requests.request.side_effect = [
            self.create_mock_token_expiry_response_dataset_metadata(),
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

    def test_refresh_login_error(self, mock_requests):
        """Tests a LoginError is raised when refreshing a token fails to
        return the expected response"""

        session = self.create_mock_session(True)

        # Here will test only on the get request as the logic is handled by
        # the base function called by all requests anyway

        # To trigger a refresh need a response with a 403 status code, then
        # should be successful when retried - here we keep it failing
        mock_requests.request.return_value = self.create_mock_token_expiry_response()

        # No new token
        mock_requests.post.return_value = self.create_mock_invalid_login_response()()

        with self.assertRaises(LoginError) as error:
            # Avoid creating any local files
            with patch(
                "builtins.open", new_callable=mock_open, read_data=TEST_SESSION_FILE
            ):
                session.get_request(url="some_test_url")

        self.assertEqual(str(error.exception), "Unable to refresh login.")

    def test_refresh_runtime_error(self, mock_requests):
        """Tests a RuntimeError is raised when refreshing a token fails"""

        session = self.create_mock_session(True)

        # Here will test only on the get request as the logic is handled by
        # the base function called by all requests anyway

        # To trigger a refresh need a response with a 403 status code, then
        # should be successful when retried - here we keep it failing
        mock_requests.request.return_value = self.create_mock_token_expiry_response()

        # New token
        mock_requests.post.return_value = self.create_mock_access_token_response()

        with self.assertRaises(RuntimeError) as error:
            # Avoid creating any local files
            with patch(
                "builtins.open", new_callable=mock_open, read_data=TEST_SESSION_FILE
            ):
                session.get_request(url="some_test_url")

        self.assertEqual(
            str(error.exception),
            "Could not authenticate request: "
            f"{mock_requests.request.return_value.content.decode.return_value}",
        )

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

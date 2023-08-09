import json
import os
from io import BufferedReader
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, call, mock_open, patch

import requests
from requests import HTTPError

from dafni_cli.api.exceptions import DAFNIError, EndpointNotFoundError
from dafni_cli.api.session import DAFNISession, LoginError
from dafni_cli.consts import (
    LOGIN_API_ENDPOINT,
    LOGOUT_API_ENDPOINT,
    REQUESTS_TIMEOUT,
    SESSION_COOKIE,
    URLS_REQUIRING_COOKIE_AUTHENTICATION,
)
from dafni_cli.tests.fixtures.session import (
    TEST_ACCESS_TOKEN,
    TEST_SESSION_DATA,
    TEST_SESSION_FILE,
    create_mock_access_token_response,
    create_mock_error_message_response,
    create_mock_error_response,
    create_mock_errors_response,
    create_mock_invalid_login_response,
    create_mock_invalid_password_response,
    create_mock_refresh_token_expiry_response,
    create_mock_response,
    create_mock_success_response,
    create_mock_token_expiry_redirect_response,
    create_mock_token_expiry_response,
)


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
        mock_requests.post.return_value = create_mock_access_token_response()

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
        mock_requests.post.return_value = create_mock_invalid_login_response()

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
        mock_requests.post.return_value = create_mock_access_token_response()

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

    @patch.dict(
        os.environ,
        {"DAFNI_USERNAME": "test_username", "DAFNI_PASSWORD": "test_password"},
    )
    def test_load_from_environment(
        self,
        mock_requests,
    ):
        """Tests loading of a new session from environment variables"""

        # Setup
        mock_requests.post.return_value = create_mock_access_token_response()

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

    @patch.dict(
        os.environ,
        {"DAFNI_USERNAME": "test_username", "DAFNI_PASSWORD": "test_password"},
    )
    def test_load_from_environment_when_login_fails(
        self,
        mock_requests,
    ):
        """Tests loading of a new session from environment variables exits
        when unsuccessful"""

        # Setup
        mock_requests.post.return_value = create_mock_invalid_password_response()

        with self.assertRaises(SystemExit) as err:
            self.create_mock_session(False, return_mock_file=True)

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

        self.assertEqual(err.exception.code, 1)

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
            create_mock_invalid_password_response(),
            create_mock_access_token_response(),
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

        # SETUP
        session = self.create_mock_session(True)

        # CALL
        error_message = session.get_error_message(create_mock_response(200, {}))

        # ASSERT
        self.assertEqual(error_message, None)

    def test_get_error_message_simple(self, mock_requests):
        """Tests get_error_message when there is a simple error message"""

        # SETUP
        session = self.create_mock_session(True)
        mock_response = create_mock_error_response()

        # CALL
        error_message = session.get_error_message(mock_response)

        # ASSERT
        self.assertEqual(error_message, f"Error: {mock_response.json()['error']}")

    def test_get_error_message(self, mock_requests):
        """Tests get_error_message when there is a specific error message"""

        # SETUP
        session = self.create_mock_session(True)
        mock_response = create_mock_error_message_response()

        # CALL
        error_message = session.get_error_message(mock_response)

        # ASSERT
        self.assertEqual(
            error_message,
            f"Error: {mock_response.json()['error']}, {mock_response.json()['error_message']}",
        )

    def test_get_error_message_with_multiple_errors(self, mock_requests):
        """Tests get_error_message when there are multiple errors"""

        # SETUP
        session = self.create_mock_session(True)
        mock_response = create_mock_errors_response()
        expected_errors = mock_response.json()["errors"]

        # CALL
        error_message = session.get_error_message(mock_response)

        # ASSERT
        self.assertEqual(
            error_message,
            "The following errors were returned:\n"
            f"Error: {expected_errors[0]}\nError: {expected_errors[1]}",
        )

    def test_get_error_message_handles_decode_error(self, mock_requests):
        """Tests get_error_message when JSON decoding fails"""

        # SETUP
        session = self.create_mock_session(True)
        mock_response = create_mock_error_response()
        # Unpatch this to avoid TypeError in except block
        mock_requests.JSONDecodeError = requests.JSONDecodeError
        mock_response.json.side_effect = requests.JSONDecodeError("", "", 0)

        # CALL
        error_message = session.get_error_message(mock_response)

        # ASSERT
        self.assertEqual(error_message, None)

    def test_check_response_raises_endpoint_not_found(self, mock_requests):
        """Tests _check_response raises an EndpointNotFoundError when necessary"""

        # SETUP
        session = self.create_mock_session(True)

        # CALL & ASSERT
        with self.assertRaises(EndpointNotFoundError) as err:
            session._check_response("test_url", create_mock_response(404))
        self.assertEqual(str(err.exception), "Could not find test_url")

    def test_check_response_raises_dafni_error(self, mock_requests):
        """Tests _check_response raises a DAFNIError when a specific error is
        given in a failed response"""

        # SETUP
        session = self.create_mock_session(True)
        session.get_error_message = MagicMock()
        session.get_error_message.return_value = "Some error message"

        # CALL & ASSERT
        with self.assertRaises(DAFNIError) as err:
            session._check_response("test_url", create_mock_response(400))
        self.assertEqual(str(err.exception), "Some error message")

    def test_check_response_raises_http_error(self, mock_requests):
        """Tests _check_response raises a HTTPError when no specific error
        message is found"""

        # SETUP
        session = self.create_mock_session(True)
        session.get_error_message = MagicMock()
        session.get_error_message.return_value = None

        # CALL & ASSERT
        with self.assertRaises(HTTPError) as err:
            session._check_response("test_url", create_mock_response(400))
        self.assertEqual(str(err.exception), "Test error 400")

    def test_check_response_calls_error_message_func(self, mock_requests):
        """Tests _check_response calls the given error message function and uses
        its returned value for the error message when given"""

        # SETUP
        session = self.create_mock_session(True)
        mock_response = create_mock_response(400)
        error_message_func = MagicMock()

        # CALL & ASSERT
        with self.assertRaises(DAFNIError) as err:
            session._check_response(
                "test_url", mock_response, error_message_func=error_message_func
            )
        error_message_func.assert_called_once_with(mock_response)
        self.assertEqual(str(err.exception), f"{error_message_func.return_value}")

    def test_authenticated_request_header_auth(self, mock_requests):
        """Tests sending a request via the DAFNISession uses header based
        authentication"""

        # SETUP
        session = self.create_mock_session(True)

        # CALL
        session._authenticated_request(
            "get",
            url="test_url",
            headers={},
            data=None,
            json=None,
            allow_redirect=False,
            stream=None,
        )

        # ASSERT
        mock_requests.request.assert_called_once_with(
            "get",
            url="test_url",
            headers={"Authorization": f"Bearer {TEST_ACCESS_TOKEN}"},
            data=None,
            json=None,
            allow_redirects=False,
            stream=None,
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
            stream=None,
        )

        mock_requests.request.assert_called_once_with(
            "get",
            url=url,
            headers={},
            data=None,
            json=None,
            allow_redirects=False,
            stream=None,
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

        # SETUP
        session = self.create_mock_session(True)
        session._check_response = MagicMock()

        # CALL
        result = session.get_request(url="some_test_url", content_type="content_type")

        # ASSERT
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
            stream=False,
            timeout=REQUESTS_TIMEOUT,
        )
        session._check_response.assert_called_once_with(
            "some_test_url", mock_requests.request.return_value, error_message_func=None
        )
        self.assertEqual(result, mock_requests.request.return_value.json.return_value)

    def test_get_request_when_stream_true_and_given_error_message_func(
        self, mock_requests
    ):
        """Tests sending a get request via the DAFNISession when stream=True
        and given an error message function"""

        # SETUP
        session = self.create_mock_session(True)
        session._check_response = MagicMock()
        error_message_func = MagicMock()

        # CALL
        result = session.get_request(
            url="some_test_url",
            content_type="content_type",
            stream=True,
            error_message_func=error_message_func,
        )

        # ASSERT
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
            stream=True,
            timeout=REQUESTS_TIMEOUT,
        )
        session._check_response.assert_called_once_with(
            "some_test_url",
            mock_requests.request.return_value,
            error_message_func=error_message_func,
        )
        self.assertEqual(result, mock_requests.request.return_value)

    def test_post_request(self, mock_requests):
        """Tests sending a post request via the DAFNISession"""

        # SETUP
        session = self.create_mock_session(True)
        session._check_response = MagicMock()

        # CALL
        result = session.post_request(url="some_test_url", content_type="content_type")

        # ASSERT
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
            stream=None,
            timeout=REQUESTS_TIMEOUT,
        )
        session._check_response.assert_called_once_with(
            "some_test_url", mock_requests.request.return_value, error_message_func=None
        )
        self.assertEqual(result, mock_requests.request.return_value.json.return_value)

    def test_post_request_when_given_error_message_func(self, mock_requests):
        """Tests sending a post request via the DAFNISession when given an
        error message function"""

        # SETUP
        session = self.create_mock_session(True)
        session._check_response = MagicMock()
        error_message_func = MagicMock()

        # CALL
        result = session.post_request(
            url="some_test_url",
            content_type="content_type",
            error_message_func=error_message_func,
        )

        # ASSERT
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
            stream=None,
            timeout=REQUESTS_TIMEOUT,
        )
        session._check_response.assert_called_once_with(
            "some_test_url",
            mock_requests.request.return_value,
            error_message_func=error_message_func,
        )
        self.assertEqual(result, mock_requests.request.return_value.json())

    def test_put_request(self, mock_requests):
        """Tests sending a put request via the DAFNISession"""

        # SETUP
        session = self.create_mock_session(True)
        session._check_response = MagicMock()

        # CALL
        result = session.put_request(url="some_test_url", content_type="content_type")

        # ASSERT
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
            stream=None,
            timeout=REQUESTS_TIMEOUT,
        )
        session._check_response.assert_called_once_with(
            "some_test_url", mock_requests.request.return_value, error_message_func=None
        )
        self.assertEqual(result, mock_requests.request.return_value)

    def test_put_request_when_given_error_message_func(self, mock_requests):
        """Tests sending a put request via the DAFNISession when given an error
        message function"""

        # SETUP
        session = self.create_mock_session(True)
        session._check_response = MagicMock()
        error_message_func = MagicMock()

        # CALL
        result = session.put_request(
            url="some_test_url",
            content_type="content_type",
            error_message_func=error_message_func,
        )

        # ASSERT
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
            stream=None,
            timeout=REQUESTS_TIMEOUT,
        )
        session._check_response.assert_called_once_with(
            "some_test_url",
            mock_requests.request.return_value,
            error_message_func=error_message_func,
        )
        self.assertEqual(result, mock_requests.request.return_value)

    def test_patch_request(self, mock_requests):
        """Tests sending a patch request via the DAFNISession"""

        # SETUP
        session = self.create_mock_session(True)
        session._check_response = MagicMock()

        # CALL
        result = session.patch_request(url="some_test_url", content_type="content_type")

        # ASSERT
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
            stream=None,
            timeout=REQUESTS_TIMEOUT,
        )
        session._check_response.assert_called_once_with(
            "some_test_url", mock_requests.request.return_value, error_message_func=None
        )
        self.assertEqual(result, mock_requests.request.return_value.json.return_value)

    def test_patch_request_when_given_error_message_func(self, mock_requests):
        """Tests sending a patch request via the DAFNISession when given an
        error message function"""

        # SETUP
        session = self.create_mock_session(True)
        session._check_response = MagicMock()
        error_message_func = MagicMock()

        # CALL
        result = session.patch_request(
            url="some_test_url",
            content_type="content_type",
            error_message_func=error_message_func,
        )

        # ASSERT
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
            stream=None,
            timeout=REQUESTS_TIMEOUT,
        )
        session._check_response.assert_called_once_with(
            "some_test_url",
            mock_requests.request.return_value,
            error_message_func=error_message_func,
        )
        self.assertEqual(result, mock_requests.request.return_value.json())

    def test_delete_request(self, mock_requests):
        """Tests sending a delete request via the DAFNISession"""

        # SETUP
        session = self.create_mock_session(True)
        session._check_response = MagicMock()

        # CALL
        result = session.delete_request(url="some_test_url")

        # ASSERT
        mock_requests.request.assert_called_once_with(
            "delete",
            url="some_test_url",
            headers={
                "Authorization": f"Bearer {TEST_ACCESS_TOKEN}",
            },
            data=None,
            json=None,
            allow_redirects=False,
            stream=None,
            timeout=REQUESTS_TIMEOUT,
        )
        session._check_response.assert_called_once_with(
            "some_test_url", mock_requests.request.return_value, error_message_func=None
        )
        self.assertEqual(result, mock_requests.request.return_value)

    def test_delete_request_when_given_error_message_func(self, mock_requests):
        """Tests sending a delete request via the DAFNISession when given an
        error message function"""

        # SETUP
        session = self.create_mock_session(True)
        session._check_response = MagicMock()
        error_message_func = MagicMock()

        # CALL
        result = session.delete_request(
            url="some_test_url", error_message_func=error_message_func
        )

        # ASSERT
        mock_requests.request.assert_called_once_with(
            "delete",
            url="some_test_url",
            headers={
                "Authorization": f"Bearer {TEST_ACCESS_TOKEN}",
            },
            data=None,
            json=None,
            allow_redirects=False,
            stream=None,
            timeout=REQUESTS_TIMEOUT,
        )
        session._check_response.assert_called_once_with(
            "some_test_url",
            mock_requests.request.return_value,
            error_message_func=error_message_func,
        )
        self.assertEqual(result, mock_requests.request.return_value)

    def test_refresh(self, mock_requests):
        """Tests token refreshing on an authentication failure"""

        session = self.create_mock_session(True)

        # Here will test only on the get request as the logic is handled by
        # the base function called by all requests anyway

        # To trigger a refresh need a response with a 403 status code, then
        # should be successful when retried
        mock_requests.request.side_effect = [
            create_mock_token_expiry_response(),
            create_mock_success_response(),
        ]

        # New token
        mock_requests.post.return_value = create_mock_access_token_response()

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

    def test_refresh_when_uploading_file(self, mock_requests):
        """Tests token refreshing on an authentication failure while trying
        to upload a file (ensures the file read is reset on failure)"""

        session = self.create_mock_session(True)

        refresh_callback = MagicMock()

        # Here will test only on the get request as the logic is handled by
        # the base function called by all requests anyway

        # To trigger a refresh need a response with a 403 status code, then
        # should be successful when retried
        mock_requests.request.side_effect = [
            create_mock_token_expiry_response(),
            create_mock_success_response(),
        ]

        # New token
        mock_requests.post.return_value = create_mock_access_token_response()

        mock_file_to_upload = MagicMock(spec=BufferedReader)

        with patch(
            "builtins.open", new_callable=mock_open, read_data=TEST_SESSION_FILE
        ) as mock_file:
            session.post_request(
                url="some_test_url",
                data=mock_file_to_upload,
                refresh_callback=refresh_callback,
            )

            # Should save new token
            mock_file = mock_file()
            mock_file.write.assert_called_once_with(
                json.dumps(session._session_data.__dict__)
            )

        # Should have reset the file
        mock_file_to_upload.seek.assert_called_with(0)

        # Should have called the refresh callback
        refresh_callback.assert_called_once()

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
            create_mock_token_expiry_redirect_response(),
            create_mock_success_response(),
        ]

        # New token
        mock_requests.post.return_value = create_mock_access_token_response()

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
        mock_requests.request.return_value = create_mock_token_expiry_response()

        # No new token
        mock_requests.post.return_value = create_mock_invalid_login_response()()

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
        mock_requests.request.return_value = create_mock_token_expiry_response()

        # New token
        mock_requests.post.return_value = create_mock_access_token_response()

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
            create_mock_token_expiry_response(),
            create_mock_success_response(),
        ]

        mock_requests.post.side_effect = [
            # Token authentication expiry when trying to obtain a new one
            create_mock_refresh_token_expiry_response(),
            # Successful login using user provided credentials
            create_mock_access_token_response(),
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

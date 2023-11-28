import datetime
import json
import os
import time
from dataclasses import dataclass
from io import BufferedReader
from pathlib import Path
from typing import BinaryIO, Callable, Dict, List, Literal, Optional, Union

import click
import requests
from requests import HTTPError

from dafni_cli.api.exceptions import DAFNIError, EndpointNotFoundError, LoginError
from dafni_cli.api.notifications_api import get_notifications
from dafni_cli.consts import (
    LOGIN_API_ENDPOINT,
    LOGOUT_API_ENDPOINT,
    REQUEST_ERROR_RETRY_ATTEMPTS,
    REQUEST_ERROR_RETRY_WAIT,
    REQUESTS_TIMEOUT,
    SENDER_TYPE,
    SESSION_COOKIE,
    SESSION_SAVE_FILE,
    TOKEN_EXPIRE_OFFSET,
    URLS_REQUIRING_COOKIE_AUTHENTICATION,
)
from dafni_cli.utils import dataclass_from_dict, get_current_messages


@dataclass
class LoginResponse:
    """Dataclass for storing the response from logging in"""

    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None

    def was_successful(self):
        """
        Returns whether this login response represents a successful login
        """

        return (
            self.access_token is not None
            and self.refresh_token is not None
            and self.expires_in is not None
        )


@dataclass
class SessionData:
    """Dataclass for storing information about a logged in session (This will
    be stored for session persistence)"""

    username: str
    access_token: str
    refresh_token: str
    timestamp_to_refresh: float

    @staticmethod
    def from_login_response(username: str, login_response: LoginResponse):
        """
        Constructs a session data object and returns it

        The timestamp_to_refresh parameter will be set to the current time
        + the token's time to expiry - the TOKEN_EXPIRE_OFFSET.

        Args:
            username (str): Username to identify the session with
            login_response (LoginResponse): Structure containing the response
                                            from logging in
        """

        datetime_to_refresh = datetime.datetime.now() + datetime.timedelta(
            seconds=login_response.expires_in - TOKEN_EXPIRE_OFFSET
        )

        return SessionData(
            username=username,
            access_token=login_response.access_token,
            refresh_token=login_response.refresh_token,
            timestamp_to_refresh=datetime_to_refresh.timestamp(),
        )


class DAFNISession:
    """Handles user login and authentication"""

    # Notifications
    notifications = get_notifications()

    # Session data
    _session_data: SessionData

    # Whether the session data was loaded/saved from/to a file
    # (avoids creating/deleting the file if using as a library
    # instead of through the CLI)
    _use_session_data_file: bool = False

    def __init__(self, session_data: Optional[SessionData] = None):
        """DAFNISession constructor

        Args:
            session_data (SessionData or None) - Session data from built using
                            information obtained after login. When None will
                            attempt to load the last session from a file or
                            otherwise will request the user to login.
        """
        if session_data is None:
            self._use_session_data_file = True
            self._obtain_session_data()
        else:
            self._session_data = session_data

    @staticmethod
    def _get_login_save_path():
        """Returns the filepath to save login responses to"""
        return Path().home() / SESSION_SAVE_FILE

    @staticmethod
    def has_session_file():
        """Returns whether the session file exists and hence whether the user's
        still logged in
        """
        return DAFNISession._get_login_save_path().is_file()

    @property
    def username(self):
        """Username associated with the current session"""
        return self._session_data.username

    def _save_session_data(self):
        """Saves the SessionData instance to a storage file to persist the session"""
        with open(DAFNISession._get_login_save_path(), "w", encoding="utf-8") as file:
            file.write(json.dumps(self._session_data.__dict__))

    def _assign_session_data(self, username: str, login_response: LoginResponse):
        """Assigns and if _use_session_data_file is True, saves session data
        obtained from a successful login response"""
        self._session_data = SessionData.from_login_response(username, login_response)
        if self._use_session_data_file:
            self._save_session_data()

    def _load_session_data(self) -> bool:
        """Attempts to load a SessionData instance from the storage file

        Returns:
            bool: Whether the session data was loaded or not
        """
        path = DAFNISession._get_login_save_path()

        if not path.is_file():
            return False

        with open(path, "r", encoding="utf-8") as file:
            dictionary = json.loads(file.read())
            self._session_data = dataclass_from_dict(SessionData, dictionary)
            return True

    def _obtain_session_data(self):
        """Tries to load a previously stored LoginResponse, or obtains a new
        one and saves it by asking the user to login if the storage file was
        not found"""

        # Attempt to get from a file first
        if not self._load_session_data():
            # Couldn't so request a login
            self.attempt_login()

    def _refresh_tokens(self):
        """Obtains a new access token and stores it

        Will attempt to request one using the currently stored refresh token,
        but in the case it has expired will ask the user to login again.

        Raises:
            LoginError: If unable to login or gain a new refresh token
        """

        # Request a new refresh token
        response = requests.post(
            LOGIN_API_ENDPOINT,
            data={
                "client_id": "dafni-main",
                "grant_type": "refresh_token",
                "refresh_token": self._session_data.refresh_token,
            },
            timeout=REQUESTS_TIMEOUT,
        )

        if response.status_code == 400 and response.json()["error"] == "invalid_grant":
            # This means the refresh token has expired, so login again
            self.attempt_login()
        else:
            response.raise_for_status()

            login_response = dataclass_from_dict(LoginResponse, response.json())

            if not login_response.was_successful():
                raise LoginError("Unable to refresh login.")

            self._session_data = SessionData.from_login_response(
                self._session_data.username, login_response
            )

            if self._use_session_data_file:
                self._save_session_data()

    def _check_and_refresh_tokens(self):
        """Checks whether the current stored token will expire soon, and if
        so will attempt to refresh it

        Raises:
            LoginError: If unable to login or gain a new refresh token
        """
        if (
            datetime.datetime.now().timestamp()
            >= self._session_data.timestamp_to_refresh
        ):
            # Need a refresh
            self._refresh_tokens()

    def logout(self):
        """Logs out of keycloak"""
        response = requests.post(
            LOGOUT_API_ENDPOINT,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Bearer {self._session_data.access_token}",
            },
            data={
                "client_id": "dafni-main",
                "refresh_token": self._session_data.refresh_token,
                "scope": "openid",
            },
            timeout=REQUESTS_TIMEOUT,
        )

        response.raise_for_status()

        if self._use_session_data_file:
            self._get_login_save_path().unlink()

    @staticmethod
    def _login(username: str, password: str) -> LoginResponse:
        """Returns a LoginResponse having logged in with a username and
        password

        Returns:
            LoginResponse - If 'was_successful' is false, it means the username
                            or password given was likely wrong
        """

        response = requests.post(
            LOGIN_API_ENDPOINT,
            data={
                "username": username,
                "password": password,
                "client_id": "dafni-main",
                "grant_type": "password",
                "scope": "openid",
            },
            timeout=REQUESTS_TIMEOUT,
        )

        # When status_code is 401 => The username or password is wrong and
        # there has not been any other error
        if response.status_code != 401:
            response.raise_for_status()

        login_response = dataclass_from_dict(LoginResponse, response.json())

        return login_response

    @staticmethod
    def login(username: str, password: str):
        """Returns a DAFNISession object after logging in with a username and
        password

        Raises:
            LoginError - If login fails and its likely down to something other
                         than a bad password
        """
        login_response = DAFNISession._login(username, password)
        if not login_response.was_successful():
            raise LoginError(
                "Failed to login. Please check your username and password and try again."
            )
        return DAFNISession(SessionData.from_login_response(username, login_response))

    def _attempt_login_from_env(self) -> bool:
        """Attempts to login using environment variables (if found)

        If environment variables are found but login fails will cause
        the program to exit.

        Returns:
            bool: True if a username and password were found in the
                  environment, False otherwise
        """

        username = os.getenv("DAFNI_USERNAME")
        password = os.getenv("DAFNI_PASSWORD")

        if username is not None and password is not None:
            # Attempt login
            login_response = self._login(username, password)

            if not login_response.was_successful():
                click.echo(
                    "Failed to login from environment variables. Please check your username and password and try again."
                )
                raise SystemExit(1)

            self._assign_session_data(username, login_response)

            return True

        return False

    def _request_user_login(self) -> SessionData:
        """Prompts the user for their username and password. If login is
        successful, notifies the user that login has been completed and displays
        their username
        """

        # Continue requesting the username and password for as long as the
        # login fails to recognise them
        login_response = None
        while login_response is None or not login_response.was_successful():
            username = click.prompt("Username")
            password = click.prompt("Password", hide_input=True)

            login_response = self._login(username, password)

            if not login_response.was_successful():
                click.echo(
                    "Failed to login. Please check your username and password and try again."
                )

        self._assign_session_data(username, login_response)

        click.echo(f"Logged in as {self.username}")

    def attempt_login(self):
        """First attempts to find login credentials from environment variables
        and if that fails prompt's the user to enter a username and password
        until login is successful"""

        if not self._attempt_login_from_env():
            self._request_user_login()

        messages = get_current_messages(self.notifications)
        if messages:
            click.echo("***** NOTICE *****")
            for message in messages:
                click.echo(message)
            click.echo("***** NOTICE *****")

    # Listed below this point are various methods for performing specific HTTP
    # requests using the session data

    def _authenticated_request(
        self,
        method: Literal["get", "post", "put", "patch", "delete"],
        url: str,
        headers: dict,
        data: Union[dict, BinaryIO],
        json,
        allow_redirect: bool,
        stream: Optional[bool] = None,
        retry_callback: Optional[Callable] = None,
        auth_recursion_level: int = 0,
        retry_recursion_level: int = 0,
    ) -> requests.Response:
        """Performs an authenticated request from the DAFNI API

        Args:
            url (str): The url endpoint that is being queried
            headers (dict): Headers to include in the request (authorisation
                            will already be added)
            data (dict or BinaryIO): Data to be include in the request
            json: Any JSON serialisable object to include in the request
            allow_redirect (bool): Flag to allow redirects during API call.
            stream (Optional[bool]): Whether to stream the request
            retry_callback (Optional[Callable]): Function called when the
                             request is retried e.g. after a token refresh after an
                             initial request is sent or if there is an SSLError.
                             Particularly useful for file uploads that may need to
                             be reset.
            auth_recursion_level (int): Number of times this method has
                             been recursively called due to an authentication
                             issue (Used to avoid infinite loops)
            retry_recursion_level (int): Number of times this method has
                             been recursively called due to an error
                             (Used to avoid infinite loops)

        Returns:
            requests.Response: Response from the requests library

        Raises:
            LoginError: If unable to login or refresh tokens to authenticate
            RuntimeError: If some other error repeatedly occurs e.g. an SSLError
                          (See https://github.com/dafnifacility/cli/issues/113)
        """

        # Before doing anything check whether the current token will expire
        # soon and refresh if so
        self._check_and_refresh_tokens()

        # Should we retry the request for any reason
        retry = False

        # Add Sender-Type to all headers sent
        headers["Sender-Type"] = SENDER_TYPE

        try:
            # Switch to cookie based authentication only for those that require it
            if any(
                url_requiring_cookie in url
                for url_requiring_cookie in URLS_REQUIRING_COOKIE_AUTHENTICATION
            ):
                response = requests.request(
                    method,
                    url=url,
                    headers=headers,
                    data=data,
                    json=json,
                    allow_redirects=allow_redirect,
                    stream=stream,
                    timeout=REQUESTS_TIMEOUT,
                    cookies={SESSION_COOKIE: self._session_data.access_token},
                )
            else:
                response = requests.request(
                    method,
                    url=url,
                    headers={
                        "Authorization": f"Bearer {self._session_data.access_token}",
                        **headers,
                    },
                    data=data,
                    json=json,
                    allow_redirects=allow_redirect,
                    stream=stream,
                    timeout=REQUESTS_TIMEOUT,
                )

            # Check for any kind of authentication error, or an attempted redirect
            # (this covers a case during file upload where a 302 is returned rather
            # than an actual authentication error)
            if response.status_code == 403 or (
                response.status_code == 302 and not allow_redirect
            ):
                # Try again, but only once
                if auth_recursion_level > 1:
                    # Provide further details from the response (if there is
                    # anything) - one place this occurs is running out of
                    # temporary buckets during upload
                    message = response.content.decode()
                    raise LoginError(f"Could not authenticate request: {message}")
                else:
                    self._refresh_tokens()

                    retry = True
                    auth_recursion_level += 1
        # Pass through in case of auth error
        except LoginError:
            raise
        except Exception as err:
            # Retry a if below the maximum number of retires
            if retry_recursion_level >= REQUEST_ERROR_RETRY_ATTEMPTS:
                raise RuntimeError(
                    f"Could not connect due to an error after retrying {REQUEST_ERROR_RETRY_ATTEMPTS} times"
                ) from err
            else:
                # Workaround for https://github.com/dafnifacility/cli/issues/113
                # Retry up to ERROR_RETRY_ATTEMPTS times, waiting for
                # ERROR_RETRY_WAIT seconds between each attempt
                retry = True
                retry_recursion_level += 1
                time.sleep(REQUEST_ERROR_RETRY_WAIT)

        if retry:
            # It seems in the event we need to retry the request, requests
            # still reads at least a small part of any file being uploaded -
            # this for example can result in  the validation of some metadata
            # files to fail citing that they are missing all parameters when
            # in fact they are defined. Resetting any file reader here
            # solves the issue.
            if isinstance(data, BufferedReader):
                data.seek(0)

            # When tqdm is also involved we cannot quite apply the same
            # solution so allow a callback function that can be used to
            # reset the original file and any progress bars
            if retry_callback is not None:
                retry_callback()

            response = self._authenticated_request(
                method,
                url=url,
                headers=headers,
                data=data,
                json=json,
                stream=stream,
                allow_redirect=allow_redirect,
                retry_callback=retry_callback,
                auth_recursion_level=auth_recursion_level,
                retry_recursion_level=retry_recursion_level,
            )

        return response

    def get_error_message(self, response: requests.Response) -> Optional[str]:
        """Attempts to find an error message from a failed request response

        Args:
            response (requests.Response): The failed request response

        Returns:
            Optional[str]: String representing an error message or None
                           if none was found
        """

        # Try and get JSON data from the response
        try:
            error_message = None
            decoded_response = response.json()
            # Some requests have an error and error_message, in which case we
            # want to override with the latter
            if "error" in decoded_response:
                error_message = f"Error: {decoded_response['error']}"
            if "error_message" in decoded_response:
                error_message = f"{error_message}, {decoded_response['error_message']}"
            elif "errors" in decoded_response:
                error_message = "The following errors were returned:"
                for error in decoded_response["errors"]:
                    error_message += f"\nError: {error}"

            return error_message
        except requests.JSONDecodeError:
            return None

    def _check_response(
        self,
        url: str,
        response: requests.Response,
        error_message_func: Callable[[requests.Response], Optional[str]] = None,
    ):
        """Checks a requests response for any errors and raises them as
        required

        Args:
            url (str): URL endpoint that was being queried
            response (requests.Response): Response from requests
            error_message_func (Optional[Callable[[requests.Response], Optional[str]]]):
                                Function called on a response after an error to
                                obtain an error message. If it returns None, a
                                HTTPError will be returned, otherwise it will be
                                a DAFNIError. By default this will be
                                get_error_message.

        Raises:
            EndpointNotFoundError: If the response returns a 404 status code
            DAFNIError: If an error occurs with an error message from DAFNI
            HTTPError: If any other error occurs without an error message from
                       DAFNI
        """

        if error_message_func is None:
            error_message_func = self.get_error_message

        error_message = None

        # Check for any error response
        if not response.ok:
            # Specialised error for when we get a 404 - helps to identify
            # missing objects
            if response.status_code == 404:
                raise EndpointNotFoundError(f"Could not find {url}")

            # Attempt to find an error message from the API itself
            error_message = error_message_func(response)

        # If there is an error from DAFNI raise a DAFNI exception as well
        # with more details, otherwise leave as any errors are HTTPError's
        try:
            response.raise_for_status()
        except HTTPError as err:
            if error_message is None:
                raise err
            raise DAFNIError(error_message) from err

    def get_request(
        self,
        url: str,
        content_type: str = "application/json",
        allow_redirect: bool = False,
        stream: bool = False,
        error_message_func: Optional[
            Callable[[requests.Response], Optional[str]]
        ] = None,
        retry_callback: Optional[Callable] = None,
    ) -> Union[Dict, List[Dict], requests.Response]:
        """Performs a GET request from the DAFNI API

        Args:
            url (str): The url endpoint that is being queried
            content_type (str): Content type to put in request header
            allow_redirect (bool): Flag to allow redirects during API call.
                                   Defaults to False.
            stream (bool): Whether to stream the request. In this case will
                           return the response object itself rather than the
                           json.
            error_message_func (Optional[Callable[[requests.Response], Optional[str]]]):
                                Function called on a response after an error to
                                obtain an error message. If it returns None, a
                                HTTPError will be returned, otherwise it will be
                                a DAFNIError. By default this will be
                                get_error_message.
            retry_callback (Optional[Callable]): Function called when the
                             request is retried e.g. after a token refresh
                             or if there is an SSLError. Particularly useful
                             for file uploads that may need to be reset.

        Returns:
            Dict: When 'stream' is False for endpoints returning one object
                  e.g. /models/<version_id>
            List[Dict]: When 'stream' is False for endpoints returning multiple
                        objects e.g. /models/
            requests.Response: When 'stream' is True - The whole response object

        Raises:
            EndpointNotFoundError: If the response returns a 404 status code
            DAFNIError: If an error occurs with an error message from DAFNI
            HTTPError: If any other error occurs without an error message from
                       DAFNI
        """
        response = self._authenticated_request(
            method="get",
            url=url,
            headers={"Content-Type": content_type},
            data=None,
            json=None,
            allow_redirect=allow_redirect,
            stream=stream,
            retry_callback=retry_callback,
        )
        self._check_response(url, response, error_message_func=error_message_func)

        if stream:
            return response
        return response.json()

    def post_request(
        self,
        url: str,
        content_type: str = "application/json",
        data: Optional[Union[dict, BinaryIO]] = None,
        json=None,
        allow_redirect: bool = False,
        error_message_func: Optional[
            Callable[[requests.Response], Optional[str]]
        ] = None,
        retry_callback: Optional[Callable] = None,
    ) -> Dict:
        """Performs a POST request to the DAFNI API

        Args:
            url (str): The url endpoint that is being queried
            content_type (str): Content type to put in request header
            data (dict or BinaryIO): Data to be include in the request
            json: Any JSON serialisable object to include in the request
            allow_redirect (bool): Flag to allow redirects during API call.
                                    Defaults to False.
            error_message_func (Optional[Callable[[requests.Response], Optional[str]]]):
                                Function called on a response after an error to
                                obtain an error message. If it returns None, a
                                HTTPError will be returned, otherwise it will be
                                a DAFNIError. By default this will be
                                get_error_message.
            retry_callback (Optional[Callable]): Function called when the
                             request is retried e.g. after a token refresh
                             or if there is an SSLError. Particularly useful
                             for file uploads that may need to be reset.

        Returns:
            Dict: The decoded json response

        Raises:
            EndpointNotFoundError: If the response returns a 404 status code
            DAFNIError: If an error occurs with an error message from DAFNI
            HTTPError: If any other error occurs without an error message from
                        DAFNI
        """
        response = self._authenticated_request(
            method="post",
            url=url,
            headers={"Content-Type": content_type},
            data=data,
            json=json,
            allow_redirect=allow_redirect,
            retry_callback=retry_callback,
        )

        self._check_response(url, response, error_message_func=error_message_func)

        return response.json()

    def put_request(
        self,
        url: str,
        content_type: str = "application/json",
        data: Optional[Union[dict, BinaryIO]] = None,
        json=None,
        allow_redirect: bool = False,
        error_message_func: Optional[
            Callable[[requests.Response], Optional[str]]
        ] = None,
        retry_callback: Optional[Callable] = None,
    ) -> requests.Response:
        """Performs a PUT request to the DAFNI API

        Args:
            url (str): The url endpoint that is being queried
            content_type (str): Content type to put in request header
            data (dict or BinaryIO): Data to be include in the request
            json: Any JSON serialisable object to include in the request
            allow_redirect (bool): Flag to allow redirects during API call.
                                   Defaults to False.
            error_message_func (Optional[Callable[[requests.Response], Optional[str]]]):
                                Function called on a response after an error to
                                obtain an error message. If it returns None, a
                                HTTPError will be returned, otherwise it will be
                                a DAFNIError. By default this will be
                                get_error_message.
            retry_callback (Optional[Callable]): Function called when the
                             request is retried e.g. after a token refresh
                             or if there is an SSLError. Particularly useful
                             for file uploads that may need to be reset.

        Returns:
            requests.Response: The response object

        Raises:
            EndpointNotFoundError: If the response returns a 404 status code
            DAFNIError: If an error occurs with an error message from DAFNI
            HTTPError: If any other error occurs without an error message from
                       DAFNI
        """
        response = self._authenticated_request(
            method="put",
            url=url,
            headers={"Content-Type": content_type},
            data=data,
            json=json,
            allow_redirect=allow_redirect,
            retry_callback=retry_callback,
        )

        self._check_response(url, response, error_message_func=error_message_func)

        return response

    def patch_request(
        self,
        url: str,
        content_type: str = "application/json",
        data: Optional[Union[dict, BinaryIO]] = None,
        json=None,
        allow_redirect: bool = False,
        error_message_func: Optional[
            Callable[[requests.Response], Optional[str]]
        ] = None,
        retry_callback: Optional[Callable] = None,
    ) -> Dict:
        """Performs a PATCH request to the DAFNI API

        Args:
            url (str): The url endpoint that is being queried
            content_type (str): Content type to put in request header
            data (dict or BinaryIO): Data to be include in the request
            json: Any JSON serialisable object to include in the request
            allow_redirect (bool): Flag to allow redirects during API call.
                                   Defaults to False.
            error_message_func (Optional[Callable[[requests.Response], Optional[str]]]):
                                Function called on a response after an error to
                                obtain an error message. If it returns None, a
                                HTTPError will be returned, otherwise it will be
                                a DAFNIError. By default this will be
                                get_error_message.
            retry_callback (Optional[Callable]): Function called when the
                             request is retried e.g. after a token refresh
                             or if there is an SSLError. Particularly useful
                             for file uploads that may need to be reset.

        Returns:
            Dict: The decoded json response

        Raises:
            EndpointNotFoundError: If the response returns a 404 status code
            DAFNIError: If an error occurs with an error message from DAFNI
            HTTPError: If any other error occurs without an error message from
                       DAFNI
        """
        response = self._authenticated_request(
            method="patch",
            url=url,
            headers={"Content-Type": content_type},
            data=data,
            json=json,
            allow_redirect=allow_redirect,
            retry_callback=retry_callback,
        )

        self._check_response(url, response, error_message_func=error_message_func)

        return response.json()

    def delete_request(
        self,
        url: str,
        allow_redirect: bool = False,
        error_message_func: Optional[
            Callable[[requests.Response], Optional[str]]
        ] = None,
        retry_callback: Optional[Callable] = None,
    ) -> requests.Response:
        """Performs a DELETE request to the DAFNI API

        Args:
            url (str): The url endpoint that is being queried
            allow_redirect (bool): Flag to allow redirects during API call.
                                   Defaults to False.
            content (bool): Flag to define if the response content is
                            returned. default is the response json
            error_message_func (Optional[Callable[[requests.Response], Optional[str]]]):
                                Function called on a response after an error to
                                obtain an error message. If it returns None, a
                                HTTPError will be returned, otherwise it will be
                                a DAFNIError. By default this will be
                                get_error_message.
            retry_callback (Optional[Callable]): Function called when the
                             request is retried e.g. after a token refresh
                             or if there is an SSLError. Particularly useful
                             for file uploads that may need to be reset.

        Returns:
            requests.Response: The response object

        Raises:
            EndpointNotFoundError: If the response returns a 404 status code
            DAFNIError: If an error occurs with an error message from DAFNI
            HTTPError: If any other error occurs without an error message from
                       DAFNI
        """
        response = self._authenticated_request(
            method="delete",
            url=url,
            headers={},
            data=None,
            json=None,
            allow_redirect=allow_redirect,
            retry_callback=retry_callback,
        )

        self._check_response(url, response, error_message_func=error_message_func)

        return response

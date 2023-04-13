import base64
import json
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Literal, Optional, Union

import click
import requests

from dafni_cli.consts import (
    LOGIN_API_ENDPOINT,
    LOGOUT_API_ENDPOINT,
    REQUESTS_TIMEOUT,
    SESSION_SAVE_FILE,
)
from dafni_cli.utils import dataclass_from_dict


class LoginError(Exception):
    """Generic error to distinguish login failures"""


@dataclass
class LoginResponse:
    """Dataclass for storing the response from logging in"""

    access_token: Optional[str] = None
    refresh_token: Optional[str] = None

    def was_successful(self):
        """
        Returns whether this login response represents a successful login
        """

        return self.access_token is not None and self.refresh_token is not None


@dataclass
class SessionData:
    """Dataclass for storing information about a logged in session (This will
    be stored for session persistence)"""

    username: str
    user_id: str
    access_token: str
    refresh_token: str

    @staticmethod
    def from_login_response(username: str, login_response: LoginResponse):
        """
        Extracts information from the access_token and stores it
        """
        # JWT string is Base64 encoded and its components are separated by
        # "." symbols
        jwt = login_response.access_token
        claims = jwt.split(".")[1]
        claims_bytes = claims.encode("utf-8") + b"=="
        message_bytes = base64.b64decode(claims_bytes)
        message = message_bytes.decode("utf-8")
        json_dict = json.loads(message)

        return SessionData(
            username=username,
            user_id=json_dict["sub"],
            access_token=login_response.access_token,
            refresh_token=login_response.refresh_token,
        )


class DAFNISession:
    """Handles user login and authentication"""

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
            self._obtain_session_data()
            self._use_session_data_file = True
        else:
            self._session_data = session_data

    @staticmethod
    def _get_login_save_path():
        """Returns the filepath to save login responses to"""
        return Path().home() / SESSION_SAVE_FILE

    @staticmethod
    def is_logged_in():
        """Returns whether the login file exists and hence whether the user's
        still logged in
        """
        return DAFNISession._get_login_save_path().is_file()

    def _save_session_data(self):
        """Saves the SessionData instance to a storage file to persist the session"""
        with open(DAFNISession._get_login_save_path(), "w", encoding="utf-8") as file:
            file.write(json.dumps(self._session_data.__dict__))

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
            self._request_user_login()

    def _refresh_tokens(self):
        """Obtains a new access token and stores it

        Will attempt to request one using the currently stored refresh token,
        but in the case it has expired will ask the user to login again.
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
            self._request_user_login()
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

        Raises:
            LoginError - If login fails and its likely down to something other
                         than a bad password
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
        password"""
        login_response = DAFNISession._login(username, password)
        if not login_response.was_successful():
            raise LoginError(
                "Failed to login. Please check your username and password and try again."
            )
        return DAFNISession(SessionData.from_login_response(username, login_response))

    def output_user_info(self):
        """Outputs info on the logged in user using click.echo"""
        click.echo(
            f"username: {self._session_data.username}, user id: {self._session_data.user_id}"
        )

    def _request_user_login(self):
        """
        Prompts the user for their username and password. If login is successful,
        notifies the user that login has been completed and displays the username
        and UUID.
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

        self._session_data = SessionData.from_login_response(username, login_response)
        if self._use_session_data_file:
            self._save_session_data()

        click.echo("Login Complete")
        self.output_user_info()

    def _authenticated_request(
        self,
        method: Literal["get", "post", "put", "patch", "delete"],
        url: str,
        headers: dict,
        data: Union[dict, BinaryIO],
        json,
        allow_redirect: bool,
        recursion_level: int = 0,
    ):
        """Performs a an authenticated request from the DAFNI API.

        Args:
            url (str): The url endpoint that is being queried
            headers (dict): Headers to include in the request (authorisation will already be added)
            data (dict or BinaryIO): Data to be include in the request
            json: Any JSON serialisable object to include in the request
            allow_redirect (bool): Flag to allow redirects during API call.
            recursion_level (int): Used by this method to avoid infinite loop while attempting to
                                   refresh the access token

        Returns:
            Response
        """

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
            timeout=REQUESTS_TIMEOUT,
        )

        # Check for any kind of authentication error
        if response.status_code == 403:
            # Try again, but only once
            if recursion_level > 1:
                raise RuntimeError("Could not authenticate request")
            else:
                self._refresh_tokens()
                response = self._authenticated_request(
                    method,
                    url,
                    headers,
                    data,
                    json,
                    allow_redirect,
                    recursion_level=recursion_level + 1,
                )

        return response

    # TODO have same optional flags for each function
    def get_request(
        self,
        url: str,
        content_type: str = "application/json",
        allow_redirect: bool = False,
        content: bool = False,
        raise_status: bool = True,
    ):
        """Performs a GET request from the DAFNI API.

        Args:
            url (str): The url endpoint that is being queried
            content_type (str): Content type to put in request header
            allow_redirect (bool): Flag to allow redirects during API call. Defaults to False.
            content (bool): Flag to define if the response content is returned. default is the response json
            raise_status (bool) Flag to define if failure status' should be raised as HttpErrors. Default is True.

        Returns:
            List[dict]: For an endpoint returning several objects, a list is returned (e.g. /models/).
            dict: For an endpoint returning one object, this will be a dictionary (e.g. /models/<version_id>).
        """
        response = self._authenticated_request(
            method="get",
            url=url,
            headers={"Content-Type": content_type},
            data=None,
            json=None,
            allow_redirect=allow_redirect,
        )

        if raise_status:
            response.raise_for_status()
        if content:
            return response.content
        return response.json()

    def post_request(
        self,
        url: str,
        content_type: str = "application/json",
        data: Optional[Union[dict, BinaryIO]] = None,
        json=None,
        allow_redirect: bool = False,
        content: bool = False,
        raise_status: bool = True,
    ):
        """Performs a POST request to the DAFNI API.

        Args:
            url (str): The url endpoint that is being queried
            content_type (str): Content type to put in request header
            data (dict or BinaryIO): Data to be include in the request
            json: Any JSON serialisable object to include in the request
            allow_redirect (bool): Flag to allow redirects during API call. Defaults to False.
            content (bool): Flag to define if the response content is returned. default is the response json
            raise_status (bool) Flag to define if failure status' should be raised as HttpErrors. Default is True.

        Returns:
            List[dict]: For an endpoint returning several objects, a list is returned (e.g. /models/).
            dict: For an endpoint returning one object, this will be a dictionary (e.g. /models/<version_id>).
        """
        response = self._authenticated_request(
            method="post",
            url=url,
            headers={"Content-Type": content_type},
            data=data,
            json=json,
            allow_redirect=allow_redirect,
        )

        if raise_status:
            response.raise_for_status()
        if content:
            return response.content
        return response.json()

    def put_request(
        self,
        url: str,
        content_type: str = "application/json",
        data: Optional[Union[dict, BinaryIO]] = None,
        json=None,
        allow_redirect: bool = False,
        content: bool = False,
        raise_status: bool = True,
    ):
        """Performs a PUT request to the DAFNI API.

        Args:
            url (str): The url endpoint that is being queried
            content_type (str): Content type to put in request header
            data (dict or BinaryIO): Data to be include in the request
            json: Any JSON serialisable object to include in the request
            allow_redirect (bool): Flag to allow redirects during API call. Defaults to False.
            content (bool): Flag to define if the response content is returned. default is the response json
            raise_status (bool) Flag to define if failure status' should be raised as HttpErrors. Default is True.

        Returns:
            List[dict]: For an endpoint returning several objects, a list is returned (e.g. /models/).
            dict: For an endpoint returning one object, this will be a dictionary (e.g. /models/<version_id>).
        """
        response = self._authenticated_request(
            method="put",
            url=url,
            headers={"Content-Type": content_type},
            data=data,
            json=json,
            allow_redirect=allow_redirect,
        )

        if raise_status:
            response.raise_for_status()
        if content:
            return response.content
        return response

    def patch_request(
        self,
        url: str,
        content_type: str = "application/json",
        data: Optional[Union[dict, BinaryIO]] = None,
        json=None,
        allow_redirect: bool = False,
        content: bool = False,
        raise_status: bool = True,
    ):
        """Performs a PATCH request to the DAFNI API.

        Args:
            url (str): The url endpoint that is being queried
            content_type (str): Content type to put in request header
            data (dict or BinaryIO): Data to be include in the request
            json: Any JSON serialisable object to include in the request
            allow_redirect (bool): Flag to allow redirects during API call. Defaults to False.
            content (bool): Flag to define if the response content is returned. default is the response json
            raise_status (bool) Flag to define if failure status' should be raised as HttpErrors. Default is True.

        Returns:
            List[dict]: For an endpoint returning several objects, a list is returned (e.g. /models/).
            dict: For an endpoint returning one object, this will be a dictionary (e.g. /models/<version_id>).
        """
        response = self._authenticated_request(
            method="patch",
            url=url,
            headers={"Content-Type": content_type},
            data=data,
            json=json,
            allow_redirect=allow_redirect,
        )

        if raise_status:
            response.raise_for_status()
        if content:
            return response.content
        return response.json()

    def delete_request(
        self,
        url: str,
        allow_redirect: bool = False,
        content: bool = False,
        raise_status: bool = True,
    ):
        """Performs a PATCH request to the DAFNI API.

        Args:
            url (str): The url endpoint that is being queried
            allow_redirect (bool): Flag to allow redirects during API call. Defaults to False.
            content (bool): Flag to define if the response content is returned. default is the response json
            raise_status (bool) Flag to define if failure status' should be raised as HttpErrors. Default is True.

        Returns:
            List[dict]: For an endpoint returning several objects, a list is returned (e.g. /models/).
            dict: For an endpoint returning one object, this will be a dictionary (e.g. /models/<version_id>).
        """
        response = self._authenticated_request(
            method="delete",
            url=url,
            headers={},
            data=None,
            json=None,
            allow_redirect=allow_redirect,
        )

        if raise_status:
            response.raise_for_status()
        if content:
            return response.content
        return response.json()

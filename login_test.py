import base64
from dataclasses import dataclass, fields
import json
from pathlib import Path
from typing import Dict, Optional
import click
import requests
from dafni_cli.consts import LOGIN_API_URL

# 100 seconds
REQUESTS_TIMEOUT = 100

LOGIN_API_ENDPOINT = (
    f"{LOGIN_API_URL}/auth/realms/Production/protocol/openid-connect/token/"
)
LOGOUT_API_ENDPOINT = (
    f"{LOGIN_API_URL}/auth/realms/Production/protocol/openid-connect/logout"
)

LOGIN_SAVE_FILE = ".dafni-cli"


class LoginError(Exception):
    """Generic error to distinguish login failures"""


def dataclass_from_dict(class_type: dataclass, dictionary: Dict):
    """
    Converts a dictionary of values into a particular dataclass type
    """

    field_set = {f.name for f in fields(class_type) if f.init}
    filtered_arg_dict = {k: v for k, v in dictionary.items() if k in field_set}
    return class_type(**filtered_arg_dict)


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


class DAFNISession:
    """Handles user login and authentication."""

    # Last response from login (contains tokens)
    _login_response: LoginResponse

    # User ID derived from the access token
    _user_id: str

    def __init__(self, login_response: Optional[LoginResponse] = None):
        """DAFNISession constructor

        Args:
            login_response (LoginResponse or None) - Response from logging in
                            when None will attempt to load the last login from
                            a file or otherwise will request the user to login
        """
        if login_response is None:
            self._obtain_login()
        else:
            self._update_login(login_response)

    def _update_login(self, login_response: LoginResponse):
        """Assigns class parameters from a successful login"""

        self._login_response = login_response

        self._process_jwt()

    def _process_jwt(self):
        """
        Extracts information from the access_token and stores the user_id
        """
        # JWT string is Base64 encoded and its components are separated by
        # "." symbols
        jwt = self._login_response.access_token
        claims = jwt.split(".")[1]
        claims_bytes = claims.encode("utf-8") + b"=="
        message_bytes = base64.b64decode(claims_bytes)
        message = message_bytes.decode("utf-8")
        json_dict = json.loads(message)

        self._user_id = json_dict["sub"]

    @staticmethod
    def _get_login_save_path():
        """Returns the filepath to save login responses to"""
        return Path().home() / LOGIN_SAVE_FILE

    def _save_login_response(self):
        """Saves the last LoginResponse to a storage file to persist the session"""
        with open(DAFNISession._get_login_save_path(), "w", encoding="utf-8") as file:
            file.write(json.dumps(self._login_response.__dict__))

    def _load_login_response(self) -> bool:
        """Attempts to load a LoginResponse from the storage file

        Returns:
            bool: Whether the login response was loaded or not
        """
        path = DAFNISession._get_login_save_path()

        if not path.is_file():
            return False

        with open(path, "r", encoding="utf-8") as file:
            dictionary = json.loads(file.read())
            self._update_login(dataclass_from_dict(LoginResponse, dictionary))
            return True

    def _obtain_login(self):
        """Tries to load a previously stored LoginResponse, or obtains a new
        one by asking the user to login if the storage file was not found"""

        # Attempt to get from a file first
        if not self._load_login_response():
            # Couldn't so request a login and save
            self._request_user_login()
            self._save_login_response()

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
                "refresh_token": self._login_response.refresh_token,
            },
            timeout=REQUESTS_TIMEOUT,
        )

        if response.status_code == 400 and response.json()["error"] == "invalid_grant":
            # This means the refresh token has expired, so login again
            self._request_user_login()

        login_response = dataclass_from_dict(LoginResponse, response.json())

        if not login_response.was_successful():
            raise LoginError("Unable to refresh login.")

        self._update_login(login_response)

    def logout(self):
        """Logs out of keycloak"""
        response = requests.post(
            LOGOUT_API_ENDPOINT,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Bearer {self._login_response.access_token}",
            },
            data={
                "client_id": "dafni-main",
                "refresh_token": self._login_response.refresh_token,
                "scope": "openid",
            },
            timeout=REQUESTS_TIMEOUT,
        )

        response.raise_for_status()

    @staticmethod
    def _login(username: str, password: str) -> LoginResponse:
        """Returns a LoginResponse having logged in with a username and
        password"""
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
        response = dataclass_from_dict(LoginResponse, response.json())

        if not response.was_successful():
            raise LoginError("Unable to login. Please check your username and password")

        return response

    @staticmethod
    def login(username: str, password: str):
        """Returns a DAFNISession object after logging in with a username and
        password"""
        return DAFNISession(DAFNISession._login(username, password))

    def _request_user_login(self):
        """
        Prompts the user for their username and password. If login is successful,
        notifies the user that login has been completed and displays the username
        and UUID.
        """
        username = click.prompt("User name")
        password = click.prompt("Password", hide_input=True)

        self._update_login(self._login(username, password))

        click.echo("Login Complete")
        click.echo(f"username: {username}, user id: {self._user_id}")


session = DAFNISession()
session.logout()

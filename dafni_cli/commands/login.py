import requests
from typing import Optional, Tuple
from datetime import datetime as dt
import base64
import os
import click
import json

from dafni_cli.consts import LOGIN_API_URL, JWT_FILENAME, JWT_KEY, DATE_TIME_FORMAT


def get_new_jwt(user_name: str, password: str) -> dict:
    """
    Get a JWT for the supplied user name for DAFNI access

    Args:
        user_name (str): users username
        password (str): users password

    Returns:
        str: returned JWT
    """
    response = requests.post(
        LOGIN_API_URL + "/auth/realms/Production/protocol/openid-connect/token/",
        # Must be "data=" rather than "json=" or fails to log in
        data={
            "username": user_name,
            "password": password,
            "client_id": "dafni-main",
            "grant_type": "password",
            "scope": "openid"
            },
        # The following options cause a login failure.
        #headers={"Content-Type": "application/json"},
        #allow_redirects=False,
    )
    # Get the JWT from the data returned from the login connection
    jwt = response.json()
    if JWT_KEY not in jwt:
        click.echo("Login Failed: Please check your username and password")
        raise SystemExit(1)

    # Process the new JWT
    jwt = jwt[JWT_KEY]
    jwt_dict = process_jwt(jwt, user_name)

    return jwt_dict


def process_jwt(jwt: str, user_name: str) -> dict:
    """
    Extract expiry date, user ID and expiry date from a JWT

    Args:
        jwt (str): Base64 encoded JWT string
        user_name (str): User's username

    Returns:
        dict: Dictionary containing the user's name & ID, the JWT and the expiry date

    Side effects:
        JWT_FILENAME: Saves the dictionary to a file named JWT_FILENAME in the current
        directory. This file contains the JWT login credentials for use by other parts
        of the API.
    """
    # JWT string components are separated by "." symbols
    claims = jwt.split(".")[1]
    claims_bytes = claims.encode("utf-8") + b"=="
    message_bytes = base64.b64decode(claims_bytes)
    message = message_bytes.decode("utf-8")
    json_dict = json.loads(message)

    user_jwt = {
        "expiry": dt.fromtimestamp(json_dict["exp"]).strftime(DATE_TIME_FORMAT),
        "user_id": json_dict["sub"],
        "user_name": user_name,
        "jwt": "Bearer " + jwt,
    }

    with open(JWT_FILENAME, "w") as jwt_file:
        jwt_file.write(json.dumps(user_jwt))

    return user_jwt


def read_jwt_file() -> Optional[dict]:
    """
    Check for and read a stored DAFNI JWT file

    Returns:
        Optional[dict]: returns the dict from the stored file if available
    """
    path = os.path.join(os.getcwd(), JWT_FILENAME)
    if not os.path.exists(path):
        return None

    with open(JWT_FILENAME, "r") as jwt_file:
        jwt_dict = json.loads(jwt_file.read())

    return jwt_dict


def request_login_details() -> dict:
    """
    Prompt the user for their username and password. If login is successful,
    notifies the user that login has been completed and displays the username
    and UUID.

    :return: jwt_dict (dict): user_jwt returned by PROCESS_JWT
    """
    user_name = click.prompt("User name")
    password = click.prompt("Password", hide_input=True)
    jwt_dict = get_new_jwt(user_name, password)
    click.echo("Login Complete")
    click.echo(
        "user name: {0}, user id: {1}".format(
            jwt_dict["user_name"], jwt_dict["user_id"]
        )
    )
    return jwt_dict


def check_for_jwt_file() -> Tuple[dict, bool]:
    """
    Reads a previously-saved DAFNI JWT file if available. Otherwise, starts a
    fresh login process

    Returns:
        Tuple[dict, bool]: processed JWT, flag to indicate if new
    """
    new_jwt = False
    jwt_dict = read_jwt_file()
    if not jwt_dict:
        jwt_dict = request_login_details()
        new_jwt = True
    else:
        # Ensure the existing JWT has not expired
        expiry_date = dt.strptime(jwt_dict["expiry"], DATE_TIME_FORMAT)
        if expiry_date < dt.now():
            jwt_dict = request_login_details()
            new_jwt = True
    return jwt_dict, new_jwt


@click.command(help="Login to DAFNI")
def login():
    """
    Log into the DAFNI CLI. The function requests a new JWT with the user's
    user_name and password if either:
        - there is no cached JWT file in the current working directory
        - the existing JWT has expired
    Otherwise, the cached JWT file is returned
    """
    jwt_dict, jwt_flag = check_for_jwt_file()
    if not jwt_flag:
        click.echo("Already logged in as: ")
        click.echo(
            "user name: {0}, user id: {1}".format(
                jwt_dict["user_name"], jwt_dict["user_id"]
            )
        )


@click.command(help="Logout of DAFNI")
def logout():
    """
    Log out of the DAFNI CLI. Any cached JWT file in the current directory that
    has previously been generated through the login process will be deleted.
    """
    existing_jwt = read_jwt_file()
    if existing_jwt:
        path = os.path.join(os.getcwd(), JWT_FILENAME)
        os.remove(path)
        click.echo("Logout Complete")
        click.echo(
            "user name: {0}, user id: {1}".format(
                existing_jwt["user_name"], existing_jwt["user_id"]
            )
        )
    else:
        click.echo("Already logged out")

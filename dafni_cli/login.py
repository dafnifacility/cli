import requests
from typing import Optional
from datetime import datetime as dt
import base64
import os
import click
import json

from dafni_cli.urls import LOGIN_API_URL
from dafni_cli.consts import JWT_FILENAME, JWT_COOKIE

DATE_TIME_FORMAT = "%m/%d/%Y %H:%M:%S"

def get_new_jwt(user_name: str, password: str) -> dict:
    """Function to get a JWT for the given user for DAFNI access

    Args:
        user_name (str): users username
        password (str): users password

    Returns:
        str: returned JWT
    """
    response = requests.post(
        LOGIN_API_URL + '/login/',         
        json={"username": user_name, "password": password},
        headers={
            "Content-Type": "application/json",
        },
        allow_redirects=False
    )
    # Raise an exception if not successful
    response.raise_for_status()
    # Get the JWT from the returned cookies
    jwt = response.cookies[JWT_COOKIE]

    # process the new JWT
    jwt_dict = process_jwt(jwt, user_name)

    return jwt_dict

def process_jwt(jwt: str, user_name: str) -> dict:
    """Function to process a given JWT to pull out the
    expiry date and Users ID

    Args:
        jwt (str): Base64 encoded JWT string
        user_name (str): Users username

    Returns:
        dict: dict containing the Users name & ID, along with the JWT and expiry date
    """
    claims = jwt.split('.')[1]
    claims_bytes = claims.encode('utf-8') + b'=='
    message_bytes = base64.b64decode(claims_bytes)
    message = message_bytes.decode('utf-8')
    json_dict = json.loads(message)

    user_jwt = {
        'expiry': dt.fromtimestamp(json_dict['exp']).strftime(DATE_TIME_FORMAT),
        'user_id': json_dict['sub'],
        'user_name': user_name,
        'jwt': 'JWT ' + jwt
    }
    
    with open(JWT_FILENAME, 'w') as jwt_file:
        jwt_file.write(json.dumps(user_jwt))
    
    return user_jwt

def read_jwt_file() -> Optional[dict]:
    """Function to check for and read a stored
    DAFNI JWT file

    Returns:
        Optional[dict]: returns the dict from the stored file if available
    """
    path = os.path.join(os.getcwd(), JWT_FILENAME)
    if not os.path.exists(path):
        return None

    with open(JWT_FILENAME, 'r') as jwt_file:
        jwt_dict = json.loads(jwt_file.read())
        
    return jwt_dict

def request_login_details() -> dict:
    """Function to prompt the user for their username and password
    with the feedback that login has been completed and the username and UUID.

    :return: jwt_dict (dict): user_jwt returned by PROCESS_JWT
    """
    user_name = click.prompt("User name")
    password = click.prompt("Password", hide_input=True)
    jwt_dict = get_new_jwt(user_name, password)
    click.echo('Login Complete')
    click.echo('user name: {0}, user id: {1}'.format(jwt_dict['user_name'], jwt_dict['user_id']))
    return jwt_dict


def check_for_jwt_file() -> (Optional[dict], bool):
    new_jwt = False
    jwt_dict = read_jwt_file()
    if not jwt_dict:
        jwt_dict = request_login_details()
        new_jwt = True
    else:
        # Ensure the existing JWT has not expired
        expiry_date = dt.strptime(jwt_dict['expiry'], DATE_TIME_FORMAT)
        if expiry_date < dt.now():
            jwt_dict = request_login_details()
            new_jwt = True
    return jwt_dict, new_jwt


@click.command()
def login():
    """Function to handle DAFNI authentication
    The function will request a new JWT with the users
    usersname and password if either there is no cached JWT
    in the current working directory or the existing JWT has
    expired.
    Otherwise the cached JWT is returned

    Returns:
        str: Base64 encoded JWT string
    """
    jwt_dict, jwt_flag = check_for_jwt_file()
    if not jwt_flag:
        click.echo('Already logged in as: ')
        click.echo('user name: {0}, user id: {1}'.format(jwt_dict['user_name'], jwt_dict['user_id']))

if __name__ == '__main__':
    login()
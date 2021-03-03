import requests
from datetime import datetime as dt
import base64
import json

MODELS_API_URL = "https://dafni-nims-api.secure.dafni.rl.ac.uk"
LOGIN_API_URL = "https://login.secure.dafni.rl.ac.uk"
DATA_UPLOAD_API_URL = "https://dafni-nid-api.secure.dafni.rl.ac.uk"
DISCOVERY_API_URL = "https://dafni-search-and-discovery-api.secure.dafni.rl.ac.uk"
DSS_API_URL = "https://dafni-dss-dssauth.secure.dafni.rl.ac.uk"


def get_dafni_jwt(user_name, password):
    post_response = requests.post(
        LOGIN_API_URL + '/login/',
        json={"username": user_name, "password": password},
        headers={
            "Content-Type": "application/json",
        },
        allow_redirects=False
    )
    post_response.raise_for_status()
    jwt = post_response.cookies['__Secure-dafnijwt']
    return process_jwt(jwt)


def process_jwt(jwt):
    claims = jwt.split('.')[1]
    jwt_bytes = claims.encode('utf-8') + b'=='
    message_bytes = base64.b64decode(jwt_bytes)
    message = message_bytes.decode('utf-8')
    json_dict = json.loads(message)

    return {
        'expiry': dt.fromtimestamp(json_dict['exp']),
        'user_id': json_dict['sub'],
        'jwt': 'JWT ' + jwt
    }

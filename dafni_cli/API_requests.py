import requests

from dafni_cli.urls import MODELS_API_URL

def get_models_dicts(jwt: str) -> list:
    """Function to call the list models endpoint and return the resulting list of dictionaries.

    Args:
        jwt (str): JWT

    Returns:
        list: list of dictionaries with raw response from API
    """
    models_request = requests.get(
        MODELS_API_URL + '/models/',
        headers={
            "Content-Type": "application/json",
            "authorization": jwt
        },
        allow_redirects=False
    )
    models_request.raise_for_status()
    return models_request.json()

def get_single_model_dict(jwt: str, model_version_id: str) -> dict:
    """Function to call the get model details endpoint and return the resulting dictionary.

        Args:
            jwt (str): JWT
            model_version_id (str): model version ID for selected model

        Returns:
            dict: dictionary for the details of selected model
        """
    model_request = requests.get(
        MODELS_API_URL + '/models/' + model_version_id + "/",
        headers={
            "Content-Type": "application/json",
            "authorization": jwt
        },
        allow_redirects=False
    )
    model_request.raise_for_status()
    return model_request.json()

def get_model_metadata_dicts(jwt: str, model_version_id: str) -> dict:
    """Function to call the get model metadata endpoint and return the resulting dictionary.

        Args:
            jwt (str): JWT
            model_version_id (str): model version ID for selected model

        Returns:
            dict: dictionary for the metadata of selected model
        """
    model_metadata_request = requests.get(
        MODELS_API_URL + '/models/' + model_version_id + "/definition/",
        headers={
            "Content-Type": "application/json",
            "authorization": jwt
        },
        allow_redirects=False
    )
    model_metadata_request.raise_for_status()
    return model_metadata_request.json()


if __name__ == "__main__":
    jwt = "JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJsb2dpbi1hcHAtand0IiwiZXhwIjoxNjE0OTY3ODQ4LCJzdWIiOiI4ZDg1N2FjZi0yNjRmLTQ5Y2QtOWU3Zi0xZTlmZmQzY2U2N2EifQ.UxB_67FpglFaJR2pBlVw_mIJY2zQ5y6cNEG5ZRmW8WA"
    version_id = "0b4b0d0a-5b05-4e14-b382-9a5c9082315b"
    model_dict = get_single_model_dict(jwt, version_id)
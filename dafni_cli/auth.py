from typing import Optional

from dafni_cli.utils import (
    check_key_in_dict
)


class Auth:
    """
    Contains the authorisation details that a user has for a DAFNI entity.

    Methods:

    Attributes:
        asset_id (str): ID of the entity
        reason (str): Reason you have access to view this entity
        view (bool): View access
        read (bool): Read access
        update (bool): Update access
        destroy (bool): Deletion access
    """

    def __init__(self, auth_dict: Optional[dict] = None):
        """Auth Constructor

        Args:
            auth_dict (Optional[dict]): auth dictionary found in model and dataset dictionaries
        """
        self.asset_id = None
        self.reason = None
        self.view = None
        self.read = None
        self.update = None
        self.destroy = None

        if auth_dict:
            self.set_details_from_dict(auth_dict)

    def set_details_from_dict(self, auth_dict: dict):
        """Function to set the Auth attributes based on a given auth dictionary

        Args:
            auth_dict (dict): auth dictionary found in model and dataset dictionaries
        """
        self.asset_id = check_key_in_dict(auth_dict, ["asset_id"], default=None)
        self.reason = check_key_in_dict(auth_dict, ["reason"], default=None)
        self.view = check_key_in_dict(auth_dict, ["view"], default=None)
        self.read = check_key_in_dict(auth_dict, ["read"], default=None)
        self.update = check_key_in_dict(auth_dict, ["update"], default=None)
        self.destroy = check_key_in_dict(auth_dict, ["destroy"], default=None)

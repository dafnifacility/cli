from typing import Optional

from dafni_cli.api.datasets_api import get_latest_dataset_metadata
from dafni_cli.datasets.dataset_metadata import DatasetMetadata
from dafni_cli.utils import check_key_in_dict, print_json


class DatasetVersionHistory:
    """Class for processing Dataset Version History,

    Methods:
        __init__(jwt (str), metadata (dict)): DatasetVersionHistory constructor
        set_attributes_from_dict(metadata (dict)): Function to set the class details from a given dict
        process_version_history(jwt (str), dataset (dict)): Iterates through all versions and outputs details

    Attributes:
        jwt (str): Users DAFNI JWT
        dataset_id (str): Dataset ID
        versions (List[dict]): List of associated Version dicts
        version_ids (List[str]): List of Version IDs
    """

    def __init__(self, jwt: Optional[str] = None, metadata: Optional[dict] = None):
        """DatasetVersionHistory constructor

        Args:
            jwt (Optional[str], optional): Users DAFNI JWT. Defaults to None.
            metadata (Optional[dict], optional): Dataset Metadata response. Defaults to None.
        """
        self.jwt = jwt
        self.dataset_id = None
        self.versions = None
        self.version_ids = None

        if metadata:
            self.set_attributes_from_dict(metadata)

    def set_attributes_from_dict(self, metadata: dict):
        """Helper function to populate the DatasetVersionHistory attributes
        based on a given DAFNI Dataset Metadata response

        Args:
            metadata (dict): DAFNI Dataset Metadata response
        """
        self.dataset_id = check_key_in_dict(metadata, ["@id", "dataset_uuid"])
        self.versions = check_key_in_dict(
            metadata, ["version_history", "versions"], default=[]
        )
        self.version_ids = [
            check_key_in_dict(version, ["version_uuid"], default=None)
            for version in self.versions
        ]

    def process_version_history(self, json_flag: bool = False):
        """Function iterates through all Version History ID's,
        retrieves the associated Dataset Metadata, and outputs the Version details
        or Dataset metadata json for each version to the command line

        Args:
            json_flag (bool): Whether to print the Dataset metadata json for each version, or the version details
        """
        json_list = []
        for version_id in self.version_ids:
            metadata = get_latest_dataset_metadata(
                self.jwt, self.dataset_id, version_id
            )
            if json_flag:
                json_list.append(metadata)
            else:
                dataset_meta = DatasetMetadata(metadata)
                dataset_meta.output_version_details()
        if json_flag:
            print_json(json_list)

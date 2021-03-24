from dafni_cli.datasets.dataset_metadata import DatasetMetadata
from dafni_cli.utils import check_key_in_dict
from dafni_cli.api.datasets_api import get_latest_dataset_metadata


class DatasetVersionHistory:
    def __init__(self, jwt: str, version_history: dict):

        self.jwt = jwt
        self.datasets = []
        self.dataset_id = check_key_in_dict(
            version_history, ["version_history", "dataset_uuid"]
        )
        self.versions = check_key_in_dict(
            version_history, ["version_history", "versions"], default=[]
        )
        self.version_ids = [
            check_key_in_dict(version, ["version_uuid"], default=None)
            for version in self.versions
        ]

    def process_version_history(self):
        for version_id in self.version_ids:
            metadata = get_latest_dataset_metadata(
                self.jwt, self.dataset_id, version_id
            )
            dataset_meta = DatasetMetadata(metadata, version_id=version_id)
            dataset_meta.output_version_details()
from typing import List

from dafni_cli.model.model import Model


class VersionHistory:
    """Contains the version history of a model.

    Methods:

    Attributes:

    """

    def __init__(self, jwt: str, latest_model_version: Model):
        self.latest_id = latest_model_version.version_id
        self.version_history_dict = latest_model_version.version_history_dict
        self.model_history = [latest_model_version]
        if len(self.version_history_dict) > 1:
            for version_dict in self.version_history_dict[1:]:
                model_version = Model()
                model_version.get_details_from_id(jwt, version_dict["id"])


def get_version_history(latest_model: Model) -> List[Model]:
    """Produces a list of model objects containing the past versions of a model in reverse chronological order
     from the latest version.

    Args:
        latest_model (Model): instance of model class

    Returns:

    """

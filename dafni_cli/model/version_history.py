import click
from typing import List
from dateutil import parser

from dafni_cli.model.model import Model
from dafni_cli.consts import TAB_SPACE


class VersionHistory:
    """Contains the version history of a model.

    Methods:
        output_version_history

    Attributes:

    """

    def __init__(self, jwt: str, latest_model_version: Model):
        self.latest_id = latest_model_version.version_id
        self.version_history_dict = latest_model_version.version_history_dict
        self.model_history = [latest_model_version]
        self.version_messages = []
        self.version_tags = []
        self.version_publication_dates = []
        for version_dict in self.version_history_dict:
            self.version_messages.append(version_dict["version_message"])
            self.version_tags.append(version_dict["version_tags"])
            self.version_publication_dates.append(parser.isoparse(version_dict["published"]).date())
        if len(self.version_history_dict) > 1:
            for version_dict in self.version_history_dict[1:]:
                model_version = Model()
                model_version.get_details_from_id(jwt, version_dict["id"])
                self.model_history.append(model_version)

    def output_version_history(self):
        """Prints the version history for the model to the command line."""
        for version in self.model_history:
            pass

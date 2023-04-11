import click
from dateutil import parser

from dafni_cli.consts import TAB_SPACE
from dafni_cli.model.model import Model
from dafni_cli.utils import print_json


class ModelVersionHistory:
    """
    Contains the version history of a model.

    Methods:
        output_version_history: Outputs version history to the command line

    Attributes:
        dictionary: Dictionary returned from version_history key from model dictionary
        history: list of model instances of the different versions of the model in reverse chronological order
    """

    def __init__(self, jwt_string: str, latest_version: Model):
        if latest_version.id is None:
            raise Exception("Model has no 'id' attribute")
        elif (
            latest_version.version_tags is None
            or latest_version.publication_date is None
            or latest_version.metadata["display_name"] is None
            or latest_version.dictionary is None
            or latest_version.version_message is None
            or "version_history" not in latest_version.dictionary
        ):
            latest_version.get_attributes_from_id(jwt_string, latest_version.id)

        self.dictionary = latest_version.dictionary["version_history"]
        self.history = [latest_version]

        if len(self.dictionary) > 1:
            for version_dict in self.dictionary[1:]:
                version = Model()
                version.get_attributes_from_id(jwt_string, version_dict["id"])
                self.history.append(version)

    def output_version_history(self, json_flag: bool = False):
        """
        Prints the version history for the model to the command line.

        Args:
            json_flag (bool): Whether to print raw json or pretty print information. Defaults to False.
        """
        if not json_flag:
            for version in self.history:
                click.echo(
                    "Name: "
                    + version.metadata["display_name"]
                    + TAB_SPACE
                    + "ID: "
                    + version.id
                    + TAB_SPACE
                    + "Date: "
                    + version.publication_date.strftime("%B %d %Y")
                )
                click.echo("Version message: " + version.version_message)
                click.echo("Version tags: " + ", ".join(version.version_tags))
                click.echo("")
        else:
            print_json(self.dictionary)

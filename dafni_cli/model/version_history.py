import click
from dateutil import parser

from dafni_cli.model.model import Model
from dafni_cli.consts import TAB_SPACE


class ModelVersionHistory:
    """Contains the version history of a model.

    Methods:
        output_version_history: Outputs version history to the command line

    Attributes:
        dictionary: Dictionary returned from version_history key from model dictionary
        history: list of model instances of the different versions of the model in reverse chronological order
    """

    def __init__(self, jwt_string: str, latest_version: Model):
        if latest_version.version_id is None:
            raise Exception("Model must have version_id property")
        elif (
            latest_version.version_tags is None
            or latest_version.publication_time is None
            or latest_version.display_name is None
            or latest_version.dictionary is None
        ):
            latest_version.get_details_from_id(jwt_string, latest_version.version_id)

        self.dictionary = latest_version.dictionary["version_history"]
        latest_version.version_message = self.dictionary[0]["version_message"]
        self.history = [latest_version]

        if len(self.dictionary) > 1:
            for version_dict in self.dictionary[1:]:
                version = Model()
                version.get_details_from_id(jwt_string, version_dict["id"])
                version.version_message = version_dict["version_message"]
                self.history.append(version)

    def output_version_history(self):
        """Prints the version history for the model to the command line."""
        for version in self.history:
            click.echo(
                "Name: "
                + version.display_name
                + TAB_SPACE
                + "ID: "
                + version.version_id
                + TAB_SPACE
                + "Date: "
                + version.publication_time.strftime("%B %d %Y")
            )
            click.echo("Version message: " + version.version_message)
            tags_string = ""
            for tag in version.version_tags:
                tags_string += tag + ", "
            click.echo("Version tags: " + tags_string[:-2])
            click.echo("")

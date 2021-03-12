import click
from dateutil import parser

from dafni_cli.model.model import Model
from dafni_cli.consts import TAB_SPACE


class VersionHistory:
    """Contains the version history of a model.

    Methods:
        output_version_history: Outputs version history to the command line

    Attributes:
        dictionary: Dictionary returned from version_history key from model dictionary
        model_history: list of model instances of the different versions of the model in reverse chronological order
        version_messages: List of version_messages in reverse chronological order
        version_publication_dates: List of dates each version was published in reverse chronological order
        version_tags: List of lists containing the version tags of each version in reverse chronological order
    """

    def __init__(self, jwt: str, latest_model_version: Model):
        self.dictionary = latest_model_version.dictionary["version_history"]
        self.model_history = [latest_model_version]
        if len(self.dictionary) > 1:
            for version_dict in self.dictionary[1:]:
                model_version = Model()
                model_version.get_details_from_id(jwt, version_dict["id"])
                self.model_history.append(model_version)
        self.version_messages = []
        self.version_publication_dates = []
        self.version_tags = []
        for version_dict in self.dictionary:
            self.version_messages.append(version_dict["version_message"])
            self.version_publication_dates.append(parser.isoparse(version_dict["published"]).date())
            self.version_tags.append(version_dict["version_tags"])

    def output_version_history(self):
        """Prints the version history for the model to the command line."""
        for i in range(len(self.model_history)):
            click.echo(
                "Name: "
                + self.model_history[i].display_name
                + TAB_SPACE
                + "ID: "
                + self.model_history[i].version_id
                + TAB_SPACE
                + "Date: "
                + self.version_publication_dates[i]
            )
            click.echo("Version message: " + self.version_messages[i])
            tags_string = ""
            for tag in self.version_tags:
                tags_string += tag + ", "
            click.echo("Version tags: " + tags_string)
            click.echo("")


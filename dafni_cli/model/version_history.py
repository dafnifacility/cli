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

    def __init__(self, jwt_string: str, latest_model_version: Model):
        self.dictionary = latest_model_version.dictionary["version_history"]
        self.model_history = [latest_model_version]
        if len(self.dictionary) > 1:
            for version_dict in self.dictionary[1:]:
                model_version = Model()
                model_version.get_details_from_id(jwt_string, version_dict["id"])
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
                + self.version_publication_dates[i].strftime("%B %d %Y")
            )
            click.echo("Version message: " + self.version_messages[i])
            tags_string = ""
            for tag in self.version_tags[i]:
                tags_string += tag + ", "
            click.echo("Version tags: " + tags_string[:-2])
            click.echo("")


if __name__ == "__main__":
    jwt = "JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJsb2dpbi1hcHAtand0IiwiZXhwIjoxNjE1ODEzNTgzLCJzdWIiOiI4ZDg1N2FjZi0yNjRmLTQ5Y2QtOWU3Zi0xZTlmZmQzY2U2N2EifQ.pdC8py7YTu-KhVCn2_A3MCJjnhE13JKkXFUqvzBAPQA"
    version_id = []
    #version_id.append("0b4b0d0a-5b05-4e14-b382-9a5c9082315b")  # COVID
    #version_id.append("a2dc91ea-c243-4232-8d2e-f951fc5f8248")  # Transform
    #version_id.append("d0942631-158c-4cd2-a75f-ec7ec5798381")  # SIMIM
    #version_id.append("399cdaac-aab6-494d-870a-66de8a4217bb")  # Spatial Housing
    #version_id.append("ef4b22c8-63be-4b53-ba7c-c1cf301774b2")  # Non-spatial Housing
    #version_id.append("9de4ad50-fd98-4def-9bfc-39378854e6a1")  # 5G
    version_id.append("d50776e8-db8a-4fa6-93d7-c8fb15634e76")  # Fibonacci

    for id in version_id:
        model = Model()
        model.get_details_from_id(jwt, id)
        version_history = VersionHistory(jwt, model)
        version_history.output_version_history()

        initial_fibonacci = version_history.model_history[1]
        initial_fibonacci.get_metadata(jwt)
        initial_fibonacci.output_metadata()


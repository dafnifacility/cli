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


if __name__ == "__main__":
    jwt = "JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJsb2dpbi1hcHAtand0IiwiZXhwIjoxNjE1OTAyOTY0LCJzdWIiOiI4ZDg1N2FjZi0yNjRmLTQ5Y2QtOWU3Zi0xZTlmZmQzY2U2N2EifQ.uwxpXdZSOlw2aWe0l4NdJUiK8xZJ0ctm79r1jWnz1uI"
    version_id = []
    # version_id.append("0b4b0d0a-5b05-4e14-b382-9a5c9082315b")  # COVID
    # version_id.append("a2dc91ea-c243-4232-8d2e-f951fc5f8248")  # Transform
    # version_id.append("d0942631-158c-4cd2-a75f-ec7ec5798381")  # SIMIM
    # version_id.append("399cdaac-aab6-494d-870a-66de8a4217bb")  # Spatial Housing
    # version_id.append("ef4b22c8-63be-4b53-ba7c-c1cf301774b2")  # Non-spatial Housing
    # version_id.append("9de4ad50-fd98-4def-9bfc-39378854e6a1")  # 5G
    version_id.append("d50776e8-db8a-4fa6-93d7-c8fb15634e76")  # Fibonacci

    for id in version_id:
        model = Model()
        model.get_details_from_id(jwt, id)
        version_history = ModelVersionHistory(jwt, model)
        version_history.output_version_history()

        initial_fibonacci = version_history.history[1]
        initial_fibonacci.get_metadata(jwt)
        initial_fibonacci.output_metadata()

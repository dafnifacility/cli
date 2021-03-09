import click
import datetime as dt
from dateutil import parser
import json
import textwrap

from dafni_cli.API_requests import get_single_model_dict, get_model_metadata_dicts
from dafni_cli.model_metadata import ModelMetadata
from dafni_cli.consts import CONSOLE_WIDTH


class Model:
    def __init__(self, identifier=None):
        self.version_id = identifier
        self.display_name = None
        self.summary = None
        self.description = None
        self.creation_time = None
        self.publication_time = None
        self.version_tags = None
        self.container = None
        self.metadata = None
        pass

    def get_details_from_dict(self, model_dict: dict):
        self.display_name = model_dict["name"]
        self.summary = model_dict["summary"]
        self.description = model_dict["description"]
        self.creation_time = parser.isoparse(model_dict["creation_date"])
        self.publication_time = parser.isoparse(model_dict["publication_date"])
        self.version_id = model_dict["id"]
        self.version_tags = model_dict["version_tags"]
        self.container = model_dict["container"]

    def get_details_from_id(self, jwt_string: str, version_id_string: str):
        model_dict = get_single_model_dict(jwt_string, version_id_string)
        self.get_details_from_dict(model_dict)

    def get_metadata(self, jwt_string: str):
        metadata_dict = get_model_metadata_dicts(jwt_string, self.version_id)
        self.metadata = ModelMetadata(metadata_dict)

    def filter_by_date(self, key: str, date: str) -> bool:
        """Filters models based on the date given as an option.
            Args:
                key (str): Key for MODEL_DICT in which date is contained
                date (str): Date for which models are to be filtered on: format DD/MM/YYYY

            Returns:
                bool: Whether to display the model based on the filter
        """
        day, month, year = date.split("/")
        date = dt.date(int(year), int(month), int(day))
        if key == "creation":
            return self.creation_time.date() >= date
        elif key == "publication":
            return self.publication_time.date() >= date
        else:
            raise Exception("Key should be CREATION or PUBLICATION")

    def output_model_details(self):
        """Prints relevant model attributes to command line"""
        click.echo(
            "Name: "
            + self.display_name
            + "     ID: "
            + self.version_id
            + "     Date: "
            + self.creation_time.date().strftime("%B %d %Y")
        )
        click.echo("Summary: " + self.summary)

    def output_model_metadata(self):
        """Prints the metadata for the model to command line."""
        click.echo("Name: " + self.display_name)
        click.echo("Date: " + self.creation_time.strftime("%B %d %Y"))
        click.echo("Summary: ")
        click.echo(self.summary)
        click.echo("Description: ")
        for paragraph in self.description.split("\n"):
            for line in textwrap.wrap(paragraph, width=CONSOLE_WIDTH):
                click.echo(line)
        click.echo("")
        if self.metadata.inputs:
            click.echo("Input Parameters: ")
            click.echo(self.metadata.format_parameters())
            click.echo("Input Data Slots: ")
            click.echo(self.metadata.format_dataslots())
        if self.metadata.outputs:
            click.echo("Outputs: ")
            click.echo(self.metadata.format_outputs())
        pass


def create_model_list(model_dict_list: list) -> list:
    model_list = []
    for model_dict in model_dict_list:
        single_model = Model()
        single_model.get_details_from_dict(model_dict)
        model_list.append(single_model)
    return model_list

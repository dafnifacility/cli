import click
import requests
import datetime as dt
from dateutil import parser

from dafni_cli.urls import MODELS_API_URL
from dafni_cli.login import login, DATE_TIME_FORMAT


def get_models_dicts(jwt_dict: dict) -> list:
    """Function to call the list models endpoint and return the resulting list of dictionaries.

    Args:
        jwt_dict (dict): JWT dictionary

    Returns:
        list: list of dictionaries with raw response from API
    """
    models_request = requests.get(
        MODELS_API_URL + '/models/',
        headers={
            "Content-Type": "application/json",
            "authorization": jwt_dict
        },
        allow_redirects=False
    )
    models_request.raise_for_status()
    return models_request.json()


def filter_by_date(model_dict: dict, key: str, date: str) -> bool:
    # Change format of date to datetime
    day,month,year = date.split("/")
    date = dt.date(int(year), int(month), int(day))
    iso_date = model_dict[key]
    model_date = parser.isoparse(iso_date).date()
    return model_date >= date


@click.group()
@click.pass_context
def model(ctx):
    """Group of functions to perform functions for models
    Callback checks the jwt file and passes it to the
    commands for authentication of the API calls.
    """
    ctx.ensure_object(dict)
    jwt = ctx.invoke(login)
    ctx.obj['jwt'] = jwt


@model.command(help="List and filter models")
@click.option('--summary/--no-summary', default=False,
              help="Display short summary of model")
@click.option('--descr/--no-descr', default=False,
              help="Display full description of model")
@click.option('--creation-date', default=None,
              help="Filter for models created since given date. Format: DD/MM/YYYY")
@click.option('--publication-date', default=None,
              help="Filter for models published since given date. Format: DD/MM/YYYY")
@click.pass_context
def list(ctx, summary, descr, creation_date, publication_date):
    """Displays list of model names with other options allowing
    more details to be listed as well.

    Args:
        ctx: context containing the JWT
        summary (bool): whether summary should be displayed
        descr (bool): whether description should be displayed
        creation_date (str): for filtering by creation date. Format: DD/MM/YYYY
        publication_date (str): for filtering by publication date. Format: DD/MM/YYYY
    """
    models_dicts = get_models_dicts(ctx.obj['jwt'])
    #print(models_dicts)
    for model_dict in models_dicts:
        date_filter = True
        if creation_date:
            date_filter = filter_by_date(model_dict, "creation_date", creation_date)
        if publication_date:
            date_filter = filter_by_date(model_dict, "publication_date", publication_date)
        if date_filter:
            if summary or descr:
                click.echo("Name: " + model_dict['name'])
            else:
                click.echo(model_dict['name'])
            if summary:
                click.echo("Summary: " + model_dict['summary'] + "\n")
            if descr:
                click.echo("Description: \n" + model_dict['description'] + "\n")


@model.command(help="upload a docker image")
@click.option("--docker-image-tag")
@click.option("--metadata-file",default="model-metadata.yaml")
def upload(docker_image_tag: str, metadata_file: str):
    pass


@model.command()
@click.option("--model-id",)
def delete(model_id: str):
    pass


if __name__ == "__main__":
    model(obj={})

import click
import requests
import datetime as dt
from dateutil import parser

from dafni_cli.urls import MODELS_API_URL


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
    """Filters models based on the date given as an option.
    Args:
        model_dict (dict): Dictionary returned by API for a single model
        key (str): Key for MODEL_DICT in which date is contained
        date (str): Date for which models are to be filtered on

    Returns:
        bool: Whether to display the model based on the filter
    """
    day,month,year = date.split("/")
    date = dt.date(int(year), int(month), int(day))
    iso_date = model_dict[key]
    model_date = parser.isoparse(iso_date).date()
    return model_date >= date


def list_groups(ctx, summary, descr, creation_date, publication_date):
    """Lists requested information about non-filtered models.
    Args:
        ctx (context): contains JWT for authentication
        summary (bool): whether summary should be displayed
        descr (bool): whether description should be displayed
        creation_date (str): for filtering by creation date. Format: DD/MM/YYYY
        publication_date (str): for filtering by publication date. Format: DD/MM/YYYY
    """

    models_dicts = get_models_dicts(ctx.obj['jwt'])
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
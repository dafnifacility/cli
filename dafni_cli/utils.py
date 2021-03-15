import click
import textwrap
from typing import List
from datetime import datetime as dt


def prose_print(prose: str, width: int):
    """
    Prints string as separate paragraphs with appropriate line breaks at specified line lengths
    Args:
        prose (str): string to print as prose
        width (int): width of the lines before a new line
    """
    for paragraph in prose.split("\n"):
        for line in textwrap.wrap(paragraph, width=width):
            click.echo(line)


def process_response_to_class_list(response: List[dict], class_instance: object):
    """
    Produces a list of objects of a specified class from a list of dictionaries obtained from the DAFNI API.
    Args:
        response (list[dict]): List of dictionaries returned from the DAFNI API.
        class_instance (object): Class to create a list of.

    Returns:
        class_list (list[object]): List of objects with the attributes populated from the dictionaries.
    """
    class_list = []
    for class_dict in response:
        instance = class_instance()
        instance.set_details_from_dict(class_dict)
        class_list.append(instance)
    return class_list


def optional_column(
    dictionary: dict, key: str, column_width: int = 0, alignment: str = "<"
):
    """Adds a value to a column, if the key exists in the dictionary
    and adds spaces of the appropriate width if not.
    Args:
         dictionary (dict): Dictionary with data inside
         key (str): Key of the data that is to be checked and added if present
         column_width (int): Number of spaces to be returned instead if the key is not present
         alignment (str): Specified alignment of column
    Returns:
        entry (str): Either the value of the entry to be put into the table, column_width number of spaces
    """
    if key in dictionary:
        entry_string = str(dictionary[key])
        if column_width > 0:
            entry = f"{entry_string:{alignment}{column_width}}"
        elif column_width == 0:
            entry = entry_string
        else:
            raise ValueError("Column width for optional column must be non-negative")
    else:
        entry = f" " * column_width
    return entry


def process_date_filter(date_str: str) -> str:
    """Function to take a date str used for filtering on date
    and process into a format to submit to the DAFNI API's

    Args:
        date_str (str): Date Str in format dd/mm/yyyy

    Returns:
        str: Processed date str tp YYYY-MM-DDT00:00:00
    """
    return dt.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%dT%H-%M-%S")
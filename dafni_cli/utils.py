import click
import textwrap
from typing import List, Optional, Union
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
    return dt.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%dT%H:%M:%S")


def check_key_in_dict(
    input_dict: dict,
    key: str,
    nested_key: Optional[str] = None,
    default: Optional[str] = "N/A",
) -> Optional[Union[str, int]]:
    """Utility function to check a nested dict for a given
    key and nested key if applicable. If the keys exist, the
    associated value is returned, otherwise the default value is returned.

    Args:
        input_dict (dict): dict to check in for keys
        key (str): [description]
        nested_key (Optional[str], optional): [description]. Defaults to None.
        default (Optional[str], optional): [description]. Defaults to "N/A".

    Returns:
        Optional[Union[str, int]]: [description]
    """
    if isinstance(input_dict, dict):
        if key in input_dict:
            if nested_key and isinstance(input_dict[key], dict):
                if nested_key in input_dict[key]:
                    return input_dict[key][nested_key]
            elif not nested_key:
                return input_dict[key]

    return default


def output_table_header(
    keys: List[str], widths: List[int], alignment: str = "^"
) -> str:

    header_items = [f"{key:{alignment}{widths[idx]}}" for idx, key in enumerate(keys)]
    header = " ".join(header_items)
    header += "\n"
    header += "-" * sum(widths, len(keys))
    header += "\n"

    return header


def output_table_row(values: List[str], widths: List[int], alignment: str = "<") -> str:
    row_items = [
        f"{value:{alignment}{widths[idx]}}" for idx, value in enumerate(values)
    ]
    row = " ".join(row_items)
    row += "\n"

    return row
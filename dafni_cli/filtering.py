from datetime import datetime
from typing import Any, Callable, List, Union

from dafni_cli.models.model import Model
from dafni_cli.workflows.workflow import Workflow


def filter_multiple(
    filters: List[Callable[[Any], bool]], instances: List[Any], dictionaries: List[dict]
) -> List[Any]:
    """Filters a list of objects given a list of functions that must all return
    true

    Args:
        filters (List[Callable[[Any], bool]]): List of filters that each
                 receive a value from the list and should return true
                 if that value should be in the filtered list or false
                 otherwise.
        values (List[Any]): List of values to filter

    Returns:
        List[Any]: The filtered list of values
    """

    # Skip filtering if unnecessary
    if len(filters) == 0:
        return instances, dictionaries

    filtered_instances = []
    filtered_dictionaries = []
    for instance, dictionary in zip(instances, dictionaries):
        if all(filter_func(instance) for filter_func in filters):
            filtered_instances.append(instance)
            filtered_dictionaries.append(dictionary)
    return filtered_instances, filtered_dictionaries


# Methods to create filters for use with DAFNI objects
def creation_date_filter(
    oldest_creation_date: datetime,
) -> Callable[[Union[Model, Workflow]], bool]:
    """Returns a filter for filtering models or workflows by their creation
    date

    Args:
        oldest_creation_date (datetime): Creation date to filter by. All
                        objects with a date after this will be returned by the
                        filter. (Only the date part will be used)
    Returns:
        Callable[[Union[Model, Workflow]], bool]: Filter function to use with
                                                filter_multiple
    """

    def filter_creation_date(value: Union[Model, Workflow]) -> bool:
        return value.creation_date.date() >= oldest_creation_date.date()

    return filter_creation_date


def publication_date_filter(
    oldest_publication_date: datetime,
) -> Callable[[Union[Model, Workflow]], bool]:
    """Returns a filter for filtering models or workflows by their creation
    date

    Args:
        oldest_creation_date (datetime): Creation date to filter by. All
                        objects with a date after this will be returned by the
                        filter. (Only the date part will be used)
    Returns:
        Callable[[Union[Model, Workflow]], bool]: Filter function to use with
                                                  filter_multiple
    """

    def filter_publication_date(value: Union[Model, Workflow]) -> bool:
        return value.publication_date.date() >= oldest_publication_date.date()

    return filter_publication_date


def workflow_text_filter(
    text: str,
) -> Callable[[Workflow], bool]:
    """Returns a filter for filtering workflows by some search text

    All workflows whose display name or summary contains the search text will
    be returned by the filter. Case is ignored (as in frontend).

    Args:
        text (str): Search text to filter by. All workflows with the search
                    text in either the display name or summary will be
                    returned by the filter.
    Returns:
        Callable[[Workflow], bool]: Filter function to use with
                                    filter_multiple
    """
    text = text.lower()

    def filter_text(value: Workflow) -> bool:
        return (
            text in value.metadata.display_name.lower()
            or text in value.metadata.summary.lower()
        )

    return filter_text

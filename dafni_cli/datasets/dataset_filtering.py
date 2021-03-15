from typing import Optional
from datetime import datetime as dt

from dafni_cli.utils import process_date_filter


def process_datasets_filters(
    search_terms: Optional[str], start: Optional[str], end: Optional[str]
) -> dict:
    """Function to process the optional filters for the get all datasets
    command into an API ready format

    Args:
        search_terms (Optional[str]): Elastic search query
        start (Optional[str]): start date for date range
        end (Optional[str]): end date for date range

    Returns:
        dict: processed filters in an API ready format
    """
    filters = {}
    if search_terms:
        filters["search_text"] = search_terms

    if start or end:
        if start:
            date_filter["begin"] = process_date_filter(start)
        if end:
            date_filter["end"] = process_date_filter(end)

        filters["date_range"] = date_filter

    return filters

from datetime import datetime
from typing import Optional


def process_datasets_filters(
    search_terms: Optional[str], start: Optional[datetime], end: Optional[datetime]
) -> dict:
    """Function to process the optional filters for the get all datasets
    command into an API ready format

    Args:
        search_terms (Optional[str]): Elastic search query
        start (datetime): Start date for date range
        end (datetime): End date for date range

    Returns:
        dict: processed filters in an API ready format
    """
    filters = {}
    if search_terms:
        filters["search_text"] = search_terms

    if start or end:
        date_filter = {"data_with_no_date": False}
        if start:
            date_filter["begin"] = start.isoformat()
        if end:
            date_filter["end"] = end.isoformat()

        filters["date_range"] = date_filter

    return filters

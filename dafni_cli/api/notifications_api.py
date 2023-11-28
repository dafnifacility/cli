from datetime import datetime
from typing import List


def get_notifications() -> List[str]:
    """Function for getting notification messages on DAFNI. In the future the notifications will be pulled from an API, but for now are hard coded with start and end dates"""
    notifications = [
        {
            "start_date": datetime(2023, 10, 15),
            "end_date": datetime(2023, 11, 4),
            "message": "DAFNI will be shutting down for mandatory electrical safety checks and as a result will be unavailable from 27th to 31st October. DAFNI will not be accepting any new Data, Models or Workflows from 25th October as we cannot guarantee any assets submitted after this date will finish ingesting/running before the shutdown. Please see https://www.dafni.ac.uk/important-notice-to-dafni-users/ for more information.",
        }
    ]

    return notifications

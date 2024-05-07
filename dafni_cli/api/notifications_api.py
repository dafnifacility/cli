from datetime import datetime
from typing import List


def get_notifications() -> List[str]:
    """Function for getting notification messages on DAFNI. In the future the notifications will be pulled from an API, but for now are hard coded with start and end dates"""
    notifications = [
        {
            "start_date": datetime(2024, 5, 7, 1),
            "end_date": datetime(2024, 5, 13, 16),
            "message": "DAFNI will be undergoing scheduled maintenance between 1pm and 4pm on the 13th May 2024. Please do not attempt to submit/execute any new Data, Models or Workflows during the maintenance window.",
        }
    ]

    return notifications

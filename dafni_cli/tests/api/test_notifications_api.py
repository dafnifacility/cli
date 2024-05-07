from datetime import datetime
from unittest import TestCase

from dafni_cli.api import notifications_api


class TestNotificationsAPI(TestCase):
    def test_get_notifications_works_as_expected(self):
        # SETUP
        expected_notifications = [
            {
                "start_date": datetime(2024, 5, 7, 1),
                "end_date": datetime(2024, 5, 13, 16),
                "message": "DAFNI will be undergoing scheduled maintenance between 1pm and 4pm on the 13th May 2024. Please do not attempt to submit/execute any new Data, Models or Workflows during the maintenance window.",
            }
        ]
        # CALL
        result = notifications_api.get_notifications()

        # ASSERT
        self.assertEqual(result, expected_notifications)

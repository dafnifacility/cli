from datetime import datetime
from unittest import TestCase

from dafni_cli.api import notifications_api


class TestNotificationsAPI(TestCase):
    def test_get_notifications_works_as_expected(self):
        # SETUP
        expected_notifications = [
            {
                "start_date": datetime(2023, 10, 15),
                "end_date": datetime(2023, 11, 4),
                "message": "DAFNI will be shutting down for mandatory electrical safety checks and as a result will be unavailable from 27th to 31st October. DAFNI will not be accepting any new Data, Models or Workflows from 25th October as we cannot guarantee any assets submitted after this date will finish ingesting/running before the shutdown. Please see https://www.dafni.ac.uk/important-notice-to-dafni-users/ for more information.",
            }
        ]
        # CALL
        result = notifications_api.get_notifications()

        # ASSERT
        self.assertEqual(result, expected_notifications)

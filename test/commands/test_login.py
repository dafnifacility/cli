from unittest import TestCase
from unittest.mock import patch

from click.testing import CliRunner

from dafni_cli.commands import login


@patch("dafni_cli.commands.login.DAFNISession")
class TestLogin(TestCase):
    """Test class to test the login command"""

    def test_when_logged_in(self, mock_session):
        """Tests login behaves appropriately when already logged in"""

        mock_session.is_logged_in.return_value = True
        runner = CliRunner()

        result = runner.invoke(login.login)

        mock_session.assert_called_once_with()
        mock_session_inst = mock_session.return_value

        self.assertEqual(result.stdout, "Already logged in as: \n")
        mock_session_inst.output_user_info.assert_called_once()

    def test_when_not_logged_in(self, mock_session):
        """Tests login behaves appropriately when not logged in"""

        mock_session.is_logged_in.return_value = False
        runner = CliRunner()

        runner.invoke(login.login)

        mock_session.assert_called_once_with()


@patch("dafni_cli.commands.login.DAFNISession")
class TestLogout(TestCase):
    """Test class to test the logout command"""

    def test_when_logged_in(self, mock_session):
        """Tests login behaves appropriately when already logged in"""

        mock_session.is_logged_in.return_value = True
        runner = CliRunner()

        result = runner.invoke(login.logout)

        mock_session.assert_called_once_with()
        mock_session_inst = mock_session.return_value

        mock_session_inst.logout.assert_called_once()
        self.assertEqual(result.stdout, "Logout complete\n")
        mock_session_inst.output_user_info.assert_called_once()

    def test_when_not_logged_in(self, mock_session):
        """Tests login behaves appropriately when not logged in"""

        mock_session.is_logged_in.return_value = False
        runner = CliRunner()

        result = runner.invoke(login.logout)

        self.assertEqual(result.stdout, "Already logged out\n")

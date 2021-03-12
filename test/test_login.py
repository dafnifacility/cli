import pytest
from requests.exceptions import HTTPError
from mock import patch, MagicMock, PropertyMock, mock_open, call
import json
import os
from datetime import datetime as dt
from click.testing import CliRunner

from dafni_cli import login
from dafni_cli.consts import LOGIN_API_URL, JWT_FILENAME, JWT_COOKIE, DATE_TIME_FORMAT

from test.fixtures.jwt_fixtures import (
    request_response_fixture,
    processed_jwt_fixture,
    JWT,
)


@patch("dafni_cli.login.process_jwt")
@patch("dafni_cli.login.requests")
class TestGetNewJwt:
    """Test class to test the get_new_jwt functionality"""

    def test_requests_called_with_correct_values(
        self,
        mock_request,
        mock_process,
        request_response_fixture,
        processed_jwt_fixture,
    ):
        # SETUP
        # setup return value for requests call
        mock_request.post.return_value = request_response_fixture
        # setup return value for process_jwt
        mock_process.return_value = processed_jwt_fixture

        # setup data for call
        user_name = "john-doe"
        password = "password"

        # CALL
        result = login.get_new_jwt(user_name, password)

        # ASSERT
        assert result == processed_jwt_fixture

        mock_request.post.assert_called_once_with(
            LOGIN_API_URL + "/login/",
            json={"username": user_name, "password": password},
            headers={"Content-Type": "application/json",},
            allow_redirects=False,
        )

    def test_process_jwt_called_with_correct_values(
        self,
        mock_request,
        mock_process,
        request_response_fixture,
        processed_jwt_fixture,
    ):
        # SETUP
        # setup return value for requests call
        mock_request.post.return_value = request_response_fixture
        # setup return value for process_jwt
        mock_process.return_value = processed_jwt_fixture

        # setup data for call
        user_name = "john-doe"
        password = "password"

        # CALL
        login.get_new_jwt(user_name, password)

        # ASSERT
        mock_process.assert_called_once_with(
            request_response_fixture.cookies[JWT_COOKIE], user_name
        )

    def test_exception_raised_for_failed_call(
        self,
        mock_request,
        mock_process,
        request_response_fixture,
        processed_jwt_fixture,
    ):
        # SETUP
        # setup return value for requests call
        request_response_fixture.raise_for_status.side_effect = HTTPError(
            "404 client model"
        )
        mock_request.post.return_value = request_response_fixture

        # setup data for call
        user_name = "john-doe"
        password = "password"

        # CALL
        # ASSERT
        with pytest.raises(HTTPError, match="404 client model"):
            login.get_new_jwt(user_name, password)

        mock_process.assert_not_called()


@patch("builtins.open", new_callable=mock_open)
class TestProcessJwt:
    """Test class to test the ProcessJwt functionality"""

    def test_jwt_processed_correctly(self, open_mock):
        # SETUP
        jwt = JWT
        user_name = "john-doe"

        # CALL
        result = login.process_jwt(jwt, user_name)

        # ASSERT
        assert result == {
            "expiry": "03/03/2021 15:43:14",
            "user_name": "john-doe",
            "user_id": "e1092c3e-be04-4c19-957f-cd884e53447e",
            "jwt": "JWT " + JWT,
        }

    def test_open_called_to_write_jwt_to_file(self, open_mock):
        # SETUP
        jwt = JWT
        user_name = "john-doe"

        # CALL
        login.process_jwt(jwt, user_name)

        # ASSERT
        open_mock.assert_called_once_with(JWT_FILENAME, "w")
        open_mock.return_value.write.assert_called_once_with(
            json.dumps(
                {
                    "expiry": "03/03/2021 15:43:14",
                    "user_id": "e1092c3e-be04-4c19-957f-cd884e53447e",
                    "user_name": "john-doe",
                    "jwt": "JWT " + JWT,
                }
            )
        )


@patch("dafni_cli.login.os.path.exists")
@patch(
    "builtins.open", new_callable=mock_open, read_data=json.dumps({"jwt": "JWT String"})
)
class TestReadJwtFile:
    """Test class to test the read_jwt_file functionality"""

    def test_none_returned_if_file_not_found(self, open_mock, mock_os):
        # SETUP
        mock_os.return_value = False
        # CALL
        result = login.read_jwt_file()

        # ASSERT
        assert result is None

        mock_os.assert_called_once_with(os.path.join(os.getcwd(), JWT_FILENAME))

    def test_jwt_dict_loaded_correctly(self, open_mock, mock_os):
        # SETUP
        mock_os.return_value = True

        # CALL
        result = login.read_jwt_file()

        # ASSERT
        open_mock.assert_called_once_with(JWT_FILENAME, "r")
        assert result == {"jwt": "JWT String"}


@patch("dafni_cli.login.get_new_jwt")
@patch("dafni_cli.login.click")
class TestRequestLoginDetails:
    """Test class to test the request_login_details functionality"""

    def test_the_correct_prompts_and_echos_occur_with_click(
        self, mock_click, mock_jwt, processed_jwt_fixture
    ):
        # SETUP
        # setup click.prompt return
        mock_click.prompt.side_effect = ("user_name", "pwd")
        # setup get_new_jet return
        mock_jwt.return_value = processed_jwt_fixture

        # CALL
        login.request_login_details()

        # ASSERT
        assert mock_click.prompt.call_args_list == [
            call("User name"),
            call("Password", hide_input=True),
        ]

        assert mock_click.echo.call_args_list == [
            call("Login Complete"),
            call(
                "user name: {0}, user id: {1}".format(
                    processed_jwt_fixture["user_name"], processed_jwt_fixture["user_id"]
                )
            ),
        ]

    def test_the_correct_jwt_dict_returned(
        self, mock_click, mock_jwt, processed_jwt_fixture
    ):
        # SETUP
        # setup click.prompt return
        mock_click.prompt.side_effect = ("user_name", "pwd")
        # setup get_new_jet return
        mock_jwt.return_value = processed_jwt_fixture

        # CALL
        result = login.request_login_details()

        # ASSERT
        assert result == processed_jwt_fixture

        mock_jwt.assert_called_once_with("user_name", "pwd")


@patch("dafni_cli.login.request_login_details")
@patch("dafni_cli.login.read_jwt_file")
@patch("dafni_cli.login.dt")
class TestCheckForJwtFile:
    """Test class to test the check_for_jwt_file functionality"""

    def test_new_jwt_returned_if_no_existing_jwt_found(
        self, mock_dt, mock_read, mock_login, processed_jwt_fixture
    ):
        # SETUP
        # simulate no JWT file found
        mock_read.return_value = None
        # setup request_login_details return
        mock_login.return_value = processed_jwt_fixture

        # CALL
        jwt_dict, new_jwt = login.check_for_jwt_file()

        # ASSERT
        assert jwt_dict == processed_jwt_fixture
        assert new_jwt is True

    def test_new_jwt_returned_if_existing_jwt_has_expired(
        self, mock_dt, mock_read, mock_login, processed_jwt_fixture
    ):
        # SETUP
        # setup return for dt so token has expired
        mock_dt.now.return_value = dt(2021, 3, 3, 2)
        expiry_date = dt(2021, 3, 3, 1)
        mock_dt.strptime.return_value = expiry_date

        # simulate JWT file found
        mock_read.return_value = {"expiry": expiry_date.strftime(DATE_TIME_FORMAT)}
        # setup request_login_details return
        mock_login.return_value = processed_jwt_fixture

        # CALL
        jwt_dict, new_jwt = login.check_for_jwt_file()

        # ASSERT
        assert jwt_dict == processed_jwt_fixture
        assert new_jwt is True

        mock_dt.strptime.assert_called_once_with(
            expiry_date.strftime(DATE_TIME_FORMAT), DATE_TIME_FORMAT
        )

    def test_existing_jwt_returned_if_existing_jwt_has_not_expired(
        self, mock_dt, mock_read, mock_login, processed_jwt_fixture
    ):
        # SETUP
        # setup return for dt so token has not expired
        mock_dt.now.return_value = dt(2021, 3, 3, 2)
        expiry_date = dt(2021, 3, 3, 3)
        mock_dt.strptime.return_value = expiry_date

        # simulate JWT file found
        mock_read.return_value = {"expiry": expiry_date.strftime(DATE_TIME_FORMAT)}
        # setup request_login_details return
        mock_login.return_value = processed_jwt_fixture

        # CALL
        jwt_dict, new_jwt = login.check_for_jwt_file()

        # ASSERT
        assert jwt_dict == {"expiry": expiry_date.strftime(DATE_TIME_FORMAT)}
        assert new_jwt is False


@patch("dafni_cli.login.check_for_jwt_file")
class TestLogin:
    """Test class to test the login functionality"""

    def test_echo_not_called_if_new_jwt_created(self, mock_jwt, processed_jwt_fixture):
        # SETUP
        runner = CliRunner()
        mock_jwt.return_value = processed_jwt_fixture, True

        # CALL
        result = runner.invoke(login.login)

        # ASSERT
        assert result.stdout == ""

    def test_echo_called_if_existing_jwt_valid(self, mock_jwt, processed_jwt_fixture):
        # SETUP
        runner = CliRunner()
        mock_jwt.return_value = processed_jwt_fixture, False

        # CALL
        result = runner.invoke(login.login)

        # ASSERT
        assert (
            result.stdout
            == "Already logged in as: \nuser name: {0}, user id: {1}\n".format(
                processed_jwt_fixture["user_name"], processed_jwt_fixture["user_id"]
            )
        )


@patch("dafni_cli.login.os.remove")
@patch("dafni_cli.login.os.getcwd")
@patch("dafni_cli.login.read_jwt_file")
class TestLogout:
    """Test class to test the logout command"""

    def test_user_informed_already_logged_out_if_no_cached_jwt_found(
        self, mock_jwt, mock_getcwd, mock_remove
    ):
        # SETUP
        runner = CliRunner()
        mock_jwt.return_value = None

        # CALL
        result = runner.invoke(login.logout)

        # ASSERT
        assert result.stdout == "Already logged out\n"

    def test_cached_jwt_file_removed_if_jwt_file_found(
        self, mock_jwt, mock_getcwd, mock_remove, processed_jwt_fixture
    ):
        # SETUP
        runner = CliRunner()
        mock_jwt.return_value = processed_jwt_fixture
        mock_getcwd.return_value = "\\path\\to\\file"

        # CALL
        runner.invoke(login.logout)

        # ASSERT
        mock_remove.assert_called_once_with("\\path\\to\\file\\" + JWT_FILENAME)

    def test_cached_jwt_details_printed_after_file_removed(
        self, mock_jwt, mock_getcwd, mock_remove, processed_jwt_fixture
    ):
        # SETUP
        runner = CliRunner()
        mock_jwt.return_value = processed_jwt_fixture
        mock_getcwd.return_value = "\\path\\to\\file"

        # CALL
        result = runner.invoke(login.logout)

        # ASSERT
        assert result.stdout == (
            "Logout Complete\nuser name: john-doe, user id: e1092c3e-be04-4c19-957f-cd884e53447e\n"
        )

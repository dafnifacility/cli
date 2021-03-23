import pytest
from mock import patch
from requests.exceptions import HTTPError
from typing import BinaryIO

from dafni_cli.api import dafni_api
from test.fixtures.jwt_fixtures import request_response_fixture, JWT


@patch("dafni_cli.api.dafni_api.requests")
class TestDafniGetRequest:
    """Test class to test the dafni_get_request functionality"""

    def test_requests_response_processed_correctly(
        self, mock_request, request_response_fixture
    ):

        # SETUP
        # setup return value for requests call
        mock_request.get.return_value = request_response_fixture
        # setup data for call
        url = "dafni/models/url"
        jwt = JWT

        # CALL
        result = dafni_api.dafni_get_request(url, jwt)

        # ASSERT
        assert result == {"key": "value"}
        mock_request.get.assert_called_once_with(
            url,
            headers={"Content-Type": "application/json", "authorization": jwt},
            allow_redirects=False,
        )

    def test_exception_raised_for_failed_call(
        self, mock_request, request_response_fixture
    ):

        # SETUP
        # setup return value for requests call
        request_response_fixture.raise_for_status.side_effect = HTTPError(
            "404 client model"
        )
        mock_request.get.return_value = request_response_fixture

        # setup data for call
        url = "dafni/models/url"
        jwt = JWT

        # CALL
        # ASSERT
        with pytest.raises(HTTPError, match="404 client model"):
            dafni_api.dafni_get_request(url, jwt)


@patch("dafni_cli.api.dafni_api.requests")
class TestDafniPostRequest:
    """Test class to test the dafni_post_request functionality"""

    def test_requests_response_processed_correctly_when_allow_redirect_not_set(
        self, mock_request, request_response_fixture
    ):
        # SETUP
        # setup return value for requests call
        mock_request.post.return_value = request_response_fixture
        # setup data for call
        url = "dafni/discovery/url"
        jwt = JWT
        data = {"key_1": "value_1"}

        # CALL
        result = dafni_api.dafni_post_request(url, jwt, data)

        # ASSERT
        assert result == {"key": "value"}
        mock_request.post.assert_called_once_with(
            url,
            headers={"Content-Type": "application/json", "authorization": jwt},
            allow_redirects=False,
            json=data,
        )

    @pytest.mark.parametrize("allow_redirects", [True, False])
    def test_requests_response_processed_correctly_when_allow_redirect_set(
        self, mock_request, allow_redirects, request_response_fixture
    ):
        # SETUP
        # setup return value for requests call
        mock_request.post.return_value = request_response_fixture
        # setup data for call
        url = "dafni/discovery/url"
        jwt = JWT
        data = {"key_1": "value_1"}

        # CALL
        result = dafni_api.dafni_post_request(
            url, jwt, data, allow_redirect=allow_redirects
        )

        # ASSERT
        assert result == {"key": "value"}
        mock_request.post.assert_called_once_with(
            url,
            headers={"Content-Type": "application/json", "authorization": jwt},
            allow_redirects=allow_redirects,
            json=data,
        )

    def test_exception_raised_for_failed_call(
        self, mock_request, request_response_fixture
    ):
        # SETUP
        # setup return value for requests call
        request_response_fixture.raise_for_status.side_effect = HTTPError(
            "404 client model"
        )
        mock_request.post.return_value = request_response_fixture

        # setup data for call
        url = "dafni/discovery/url"
        jwt = JWT
        data = {"key_1": "value_1"}

        # CALL
        # ASSERT
        with pytest.raises(HTTPError, match="404 client model"):
            dafni_api.dafni_post_request(url, jwt, data)


@patch("dafni_cli.api.dafni_api.requests")
class TestDafniPutRequest:
    """Test class to test the dafni_put_request functionality"""

    def test_requests_response_processed_correctly(
        self, mock_request, request_response_fixture
    ):
        # SETUP
        # setup return value for requests call
        mock_request.put.return_value = request_response_fixture
        # setup data for call
        url = "dafni/models/url"
        jwt = JWT
        data = BinaryIO()
        content_type = "content type"

        # CALL
        result = dafni_api.dafni_put_request(url, jwt, data, content_type)

        # ASSERT
        assert result == request_response_fixture
        mock_request.put.assert_called_once_with(
            url,
            headers={"Content-Type": content_type, "authorization": jwt},
            data=data,
        )

    def test_exception_raised_for_failed_call(
        self, mock_request, request_response_fixture
    ):
        # SETUP
        # setup return value for requests call
        request_response_fixture.raise_for_status.side_effect = HTTPError(
            "404 client model"
        )
        mock_request.put.return_value = request_response_fixture

        # setup data for call
        url = "dafni/models/url"
        jwt = JWT
        data = BinaryIO()
        content_type = "content type"

        # CALL
        # ASSERT
        with pytest.raises(HTTPError, match="404 client model"):
            dafni_api.dafni_put_request(url, jwt, data, content_type)

from unittest import TestCase

from dafni_cli.api.auth import Auth
from dafni_cli.api.parser import ParserBaseObject
from dafni_cli.tests.fixtures.auth import TEST_AUTH_DATA_OBJECT, TEST_AUTH_DATA_OBJECTS


class TestAuth(TestCase):
    """Tests the Auth dataclass parsing"""

    def test_data_object_parse(self):
        """Tests parsing of the auth data from either the model or workflow
        endpoints"""
        auth_obj = ParserBaseObject.parse_from_dict(Auth, TEST_AUTH_DATA_OBJECT)
        self.assertEqual(
            auth_obj,
            Auth(
                view=TEST_AUTH_DATA_OBJECT["view"],
                read=TEST_AUTH_DATA_OBJECT["read"],
                update=TEST_AUTH_DATA_OBJECT["update"],
                destroy=TEST_AUTH_DATA_OBJECT["destroy"],
                reason=TEST_AUTH_DATA_OBJECT["reason"],
                asset_id=TEST_AUTH_DATA_OBJECT["asset_id"],
                role_id=None,
                name=None,
            ),
        )

    def test_data_objects_parse(self):
        """Tests parsing of the auth data from either the models or workflows
        endpoints"""
        auth_obj = ParserBaseObject.parse_from_dict(Auth, TEST_AUTH_DATA_OBJECTS)
        self.assertEqual(
            auth_obj,
            Auth(
                view=TEST_AUTH_DATA_OBJECTS["view"],
                read=TEST_AUTH_DATA_OBJECTS["read"],
                update=TEST_AUTH_DATA_OBJECTS["update"],
                destroy=TEST_AUTH_DATA_OBJECTS["destroy"],
                reason=TEST_AUTH_DATA_OBJECTS["reason"],
                asset_id=None,
                role_id=TEST_AUTH_DATA_OBJECTS["role_id"],
                name=TEST_AUTH_DATA_OBJECTS["name"],
            ),
        )

    def test_get_permission_string_full_access(self):
        """Tests get_permission_string returns 'Full access' when
        appropriate"""
        auth_obj = ParserBaseObject.parse_from_dict(Auth, TEST_AUTH_DATA_OBJECTS)
        auth_obj.read = True
        auth_obj.view = True
        self.assertEqual(auth_obj.get_permission_string(), "Full access")

    def test_get_permission_string_view_only(self):
        """Tests get_permission_string returns 'View only' when
        appropriate"""
        auth_obj = ParserBaseObject.parse_from_dict(Auth, TEST_AUTH_DATA_OBJECTS)
        auth_obj.read = False
        auth_obj.view = True
        self.assertEqual(auth_obj.get_permission_string(), "View only")

    def test_get_permission_string_not_visible(self):
        """Tests get_permission_string returns 'Not visible' when
        appropriate"""
        auth_obj = ParserBaseObject.parse_from_dict(Auth, TEST_AUTH_DATA_OBJECTS)
        auth_obj.read = False
        auth_obj.view = False
        self.assertEqual(auth_obj.get_permission_string(), "Not visible")

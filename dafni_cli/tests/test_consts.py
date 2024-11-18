from unittest import TestCase

from dafni_cli.consts import (
    DSS_API_URL,
    ENVIRONMENT,
    KEYCLOAK_API_URL,
    LOGIN_API_ENDPOINT,
    LOGOUT_API_ENDPOINT,
    NID_API_URL,
    NIMS_API_URL,
    SEARCH_AND_DISCOVERY_API_URL,
)


class TestConsts(TestCase):
    """Tests on the values of constants in consts.py"""

    def test_using_production(self):
        """Test that the URLs in consts.py are using production and not
        staging"""
        # Ensure using production
        self.assertEqual(ENVIRONMENT, "production")

        # Ensure URLs look correct
        self.assertEqual(DSS_API_URL, "https://dss.secure.dafni.rl.ac.uk")
        self.assertEqual(NIMS_API_URL, "https://nims.secure.dafni.rl.ac.uk")
        self.assertEqual(NID_API_URL, "https://nid.secure.dafni.rl.ac.uk")
        self.assertEqual(
            SEARCH_AND_DISCOVERY_API_URL,
            "https://snd.secure.dafni.rl.ac.uk",
        )
        self.assertEqual(KEYCLOAK_API_URL, "https://keycloak.secure.dafni.rl.ac.uk")
        self.assertEqual(
            LOGIN_API_ENDPOINT,
            f"{KEYCLOAK_API_URL}/realms/Production/protocol/openid-connect/token/",
        )
        self.assertEqual(
            LOGOUT_API_ENDPOINT,
            f"{KEYCLOAK_API_URL}/realms/Production/protocol/openid-connect/logout",
        )

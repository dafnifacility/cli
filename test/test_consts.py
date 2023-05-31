from unittest import TestCase

from dafni_cli.consts import (
    DSS_API_URL,
    ENVIRONMENT,
    KEYCLOAK_API_URL,
    LOGIN_API_ENDPOINT,
    LOGOUT_API_ENDPOINT,
    MINIO_API_URL,
    MINIO_DOWNLOAD_REDIRECT_API_URL,
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
        self.assertEqual(DSS_API_URL, "https://dafni-dss-dssauth.secure.dafni.rl.ac.uk")
        self.assertEqual(NIMS_API_URL, "https://dafni-nims-api.secure.dafni.rl.ac.uk")
        self.assertEqual(NID_API_URL, "https://dafni-nid-api.secure.dafni.rl.ac.uk")
        self.assertEqual(
            SEARCH_AND_DISCOVERY_API_URL,
            "https://dafni-search-and-discovery-api.secure.dafni.rl.ac.uk",
        )
        self.assertEqual(MINIO_API_URL, "https://minio.secure.dafni.rl.ac.uk")
        self.assertEqual(
            MINIO_DOWNLOAD_REDIRECT_API_URL,
            "https://fwd.secure.dafni.rl.ac.uk/nidminio",
        )
        self.assertEqual(KEYCLOAK_API_URL, "https://keycloak.secure.dafni.rl.ac.uk")
        self.assertEqual(
            LOGIN_API_ENDPOINT,
            f"{KEYCLOAK_API_URL}/auth/realms/Production/protocol/openid-connect/token/",
        )
        self.assertEqual(
            LOGOUT_API_ENDPOINT,
            f"{KEYCLOAK_API_URL}/auth/realms/Production/protocol/openid-connect/logout",
        )

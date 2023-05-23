# Timeout for requests (in seconds)
REQUESTS_TIMEOUT = 100

# Environment - Either 'production' or 'staging' for development purposes
ENVIRONMENT = "production"
ENVIRONMENT_DOMAIN = "secure" if ENVIRONMENT == "production" else "staging"

# URLs
DSS_API_URL = f"https://dafni-dss-dssauth.{ENVIRONMENT_DOMAIN}.dafni.rl.ac.uk"
NIMS_API_URL = f"https://dafni-nims-api.{ENVIRONMENT_DOMAIN}.dafni.rl.ac.uk"
NID_API_URL = f"https://dafni-nid-api.{ENVIRONMENT_DOMAIN}.dafni.rl.ac.uk"
SEARCH_AND_DISCOVERY_API_URL = (
    f"https://dafni-search-and-discovery-api.{ENVIRONMENT_DOMAIN}.dafni.rl.ac.uk"
)
MINIO_API_URL = f"https://minio.{ENVIRONMENT_DOMAIN}.dafni.rl.ac.uk"
MINIO_DOWNLOAD_REDIRECT_API_URL = (
    f"https://fwd.{ENVIRONMENT_DOMAIN}.dafni.rl.ac.uk/nidminio"
)
KEYCLOAK_API_URL = f"https://keycloak.{ENVIRONMENT_DOMAIN}.dafni.rl.ac.uk"

WORKFLOWS_API_URL = NIMS_API_URL
MODELS_API_URL = NIMS_API_URL
DATA_UPLOAD_API_URL = NID_API_URL
DATA_DOWNLOAD_API_URL = MINIO_API_URL
DATA_DOWNLOAD_REDIRECT_API_URL = MINIO_DOWNLOAD_REDIRECT_API_URL

# Keycloak realm
KEYCLOAK_API_REALM = ENVIRONMENT.capitalize()

# Specific endpoints
LOGIN_API_ENDPOINT = f"{KEYCLOAK_API_URL}/auth/realms/{KEYCLOAK_API_REALM}/protocol/openid-connect/token/"
LOGOUT_API_ENDPOINT = f"{KEYCLOAK_API_URL}/auth/realms/{KEYCLOAK_API_REALM}/protocol/openid-connect/logout"

# Authentication
SESSION_SAVE_FILE = ".dafni-cli"
SESSION_COOKIE = "__Secure-dafni"

# Content types
MINIO_UPLOAD_CT = "multipart/form-data"
VALIDATE_MODEL_CT = "application/yaml"

# Formatting
DATE_TIME_FORMAT = "%m/%d/%Y %H:%M:%S"

# Model Input/Output Table Formatting
INPUT_TITLE_HEADER = "Title"
INPUT_TYPE_HEADER = "Type"
INPUT_MIN_HEADER = "Min"
INPUT_MAX_HEADER = "Max"
INPUT_DEFAULT_HEADER = "Default"
INPUT_DESCRIPTION_HEADER = "Description"

INPUT_TYPE_COLUMN_WIDTH = 10
INPUT_MIN_MAX_COLUMN_WIDTH = 10
INPUT_DESCRIPTION_LINE_WIDTH = 20

OUTPUT_NAME_HEADER = "Name"
OUTPUT_FORMAT_HEADER = "Format"
OUTPUT_SUMMARY_HEADER = "Summary"

OUTPUT_FORMAT_COLUMN_WIDTH = 10
OUTPUT_SUMMARY_COLUMN_WIDTH = 20

CONSOLE_WIDTH = 120

TAB_SPACE = "    "

# Datasets
DATA_FORMATS = {
    "application/octet-stream": "Binary",
    "application/pdf": "PDF",
    "application/vnd.ms-excel": "Excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "Excel",
    "application/zip": "ZIP",
    "text/csv": "CSV",
    "text/plain": "Text",
}

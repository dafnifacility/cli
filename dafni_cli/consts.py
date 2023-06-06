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

# URLs that require cookie based auth instead of header based
URLS_REQUIRING_COOKIE_AUTHENTICATION = [
    MINIO_API_URL,
    f"https://nid-minio.{ENVIRONMENT_DOMAIN}.dafni.rl.ac.uk",
]

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

# Tabulate arguments for table formatting
TABULATE_ARGS = {"tablefmt": "simple", "stralign": "left", "numalign": "left"}

# Model Input/Output Table Formatting
INPUT_TITLE_HEADER = "Title"
INPUT_DESCRIPTION_HEADER = "Description"
INPUT_NAME_HEADER = "Name"
INPUT_TYPE_HEADER = "Type"
INPUT_MIN_HEADER = "Min"
INPUT_MAX_HEADER = "Max"
INPUT_DEFAULT_HEADER = "Default"
INPUT_REQUIRED_HEADER = "Required?"
INPUT_SLOT_NAME_HEADER = "Slot Name"
INPUT_PATH_IN_CONTAINER_HEADER = "Path in container"
INPUT_DEFAULT_DATASETS_HEADER = "Default datasets (Version IDs)"

INPUT_DESCRIPTION_MAX_COLUMN_WIDTH = 80

OUTPUT_NAME_HEADER = "Name"
OUTPUT_FORMAT_HEADER = "Format"
OUTPUT_SUMMARY_HEADER = "Summary"

OUTPUT_SUMMARY_MAX_COLUMN_WIDTH = 80

CONSOLE_WIDTH = 120

# What to display if a data format is unknown
OUTPUT_UNKNOWN_FORMAT = "Unknown"

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

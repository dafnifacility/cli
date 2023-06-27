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

# ISO8601
DATE_TIME_OUTPUT_FORMAT = "%Y-%m-%dT%H:%M:%S"
DATE_OUTPUT_FORMAT = "%Y-%m-%d"
DATE_INPUT_FORMAT = "%Y-%m-%d"
# Same as above but for displaying to the user
DATE_INPUT_FORMAT_VERBOSE = "YYYY-MM-DD"

# Tabulate arguments for table formatting
TABULATE_ARGS = {"tablefmt": "simple", "stralign": "left", "numalign": "left"}

# Table headers
TABLE_TITLE_HEADER = "Title"
TABLE_DESCRIPTION_HEADER = "Description"
TABLE_NAME_HEADER = "Name"
TABLE_TYPE_HEADER = "Type"
TABLE_MIN_HEADER = "Min"
TABLE_MAX_HEADER = "Max"
TABLE_DEFAULT_HEADER = "Default"
TABLE_REQUIRED_HEADER = "Required?"
TABLE_SLOT_NAME_HEADER = "Slot Name"
TABLE_PATH_IN_CONTAINER_HEADER = "Path in container"
TABLE_DEFAULT_DATASETS_HEADER = "Default datasets (Version IDs)"
TABLE_FORMAT_HEADER = "Format"
TABLE_SUMMARY_HEADER = "Summary"
TABLE_ID_HEADER = "ID"
TABLE_PUBLISHED_BY_HEADER = "Published by"
TABLE_PUBLISHED_DATE_HEADER = "Date published"
TABLE_WORKFLOW_VERSION_ID_HEADER = "Workflow version ID"
TABLE_PARAMETER_SET_HEADER = "Parameter set"
TABLE_STARTED_HEADER = "Started"
TABLE_FINISHED_HEADER = "Finished"
TABLE_STATUS_HEADER = "Status"
TABLE_VERSION_ID_HEADER = "Version ID"
TABLE_MODIFIED_HEADER = "Modified"
TABLE_VERSION_MESSAGE_HEADER = "Version message"
TABLE_ACCESS_HEADER = "Access"
TABLE_PUBLICATION_DATE_HEADER = "Publication date"

TABLE_DESCRIPTION_MAX_COLUMN_WIDTH = 80
TABLE_DISPLAY_NAME_MAX_COLUMN_WIDTH = 40
TABLE_SUMMARY_MAX_COLUMN_WIDTH = 60


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

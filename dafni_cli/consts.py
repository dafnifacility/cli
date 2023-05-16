# Timeout for requests (in seconds)
REQUESTS_TIMEOUT = 100

# URLs
WORKFLOWS_API_URL = "https://dafni-nims-api.secure.dafni.rl.ac.uk"
MODELS_API_URL = "https://dafni-nims-api.secure.dafni.rl.ac.uk"
LOGIN_API_URL = "https://keycloak.secure.dafni.rl.ac.uk"
LOGIN_API_ENDPOINT = (
    f"{LOGIN_API_URL}/auth/realms/Production/protocol/openid-connect/token/"
)
LOGOUT_API_ENDPOINT = (
    f"{LOGIN_API_URL}/auth/realms/Production/protocol/openid-connect/logout"
)
DATA_UPLOAD_API_URL = "https://dafni-nid-api.secure.dafni.rl.ac.uk"
DISCOVERY_API_URL = "https://dafni-search-and-discovery-api.secure.dafni.rl.ac.uk"
DSS_API_URL = "https://dafni-dss-dssauth.secure.dafni.rl.ac.uk"
MINIO_API_URL = "https://minio.secure.dafni.rl.ac.uk"
DATA_DOWNLOAD_API_URL = MINIO_API_URL
DATA_DOWNLOAD_REDIRECT_API_URL = "https://fwd.secure.dafni.rl.ac.uk/nidminio"

# Authentication
SESSION_SAVE_FILE = ".dafni-cli"
# JWT_COOKIE = "__Secure-dafnijwt"

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

import os

ROOT_FOLDER = os.path.join(
    os.path.dirname(__file__), "..", "..", ".."
)
LOCAL_DATA_FOLDER = os.path.join(ROOT_FOLDER, "data")

BUCKET_NAME = os.environ["BUCKET_NAME"]
API_SECRETS_PARAM = os.environ["API_SECRETS_PARAM"]
API_REQUEST_SLEEP = int(os.getenv("API_REQUEST_SLEEP", 1))
API_REQUEST_TIMEOUT = int(os.getenv("API_REQUEST_TIMEOUT", 10))
API_REQUEST_RETRIES = int(os.getenv("API_REQUEST_RETRIES", 5))

TOKEN_ENDPOINT = "https://myanimelist.net/v1/oauth2/token"
API_ENDPOINT = "https://api.myanimelist.net/v2"

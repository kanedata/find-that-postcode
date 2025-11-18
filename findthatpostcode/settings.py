import os

from dotenv import load_dotenv

load_dotenv()


def get_es_url(default):
    potential_env_vars = ["ELASTICSEARCH_URL", "ES_URL", "BONSAI_URL"]
    for e_v in potential_env_vars:
        if os.environ.get(e_v):
            return os.environ.get(e_v)
    return default


ENVIRONMENT = "development" if os.environ.get("DEBUG") else "production"
DEBUG = ENVIRONMENT == "development"

SECRET_KEY = os.environ.get("SECRET_KEY", "dev")
ES_URL = get_es_url("http://localhost:9200")
ES_INDEX = os.environ.get("ES_INDEX", "postcodes")
LOGGING_DB = os.environ.get("LOGGING_DB")
SERVER_NAME = os.environ.get("SERVER_NAME")

S3_REGION = os.environ.get("S3_REGION")
S3_ENDPOINT = os.environ.get("S3_ENDPOINT")
S3_ACCESS_ID = os.environ.get("S3_ACCESS_ID")
S3_SECRET_KEY = os.environ.get("S3_SECRET_KEY")
S3_BUCKET = os.environ.get("S3_BUCKET", "geo-boundaries")

ETHICAL_ADS_PUBLISHER = os.environ.get("ETHICAL_ADS_PUBLISHER")
SENTRY_DSN = os.environ.get("SENTRY_DSN")

RATE_LIMIT_EXEMPT_HEADER = "X-RateLimit-Exempt"
RATE_LIMIT_EXEMPT_KEYS = os.environ.get("RATE_LIMIT_EXEMPT_KEYS", "").split(",")

STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")

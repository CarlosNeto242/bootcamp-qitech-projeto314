import os


SERVICE_ROOT = os.path.abspath(os.path.dirname(__file__))

SCHEMA_PATH = os.path.join(SERVICE_ROOT, "schemas")

APP_ENV = os.environ.get("APP_ENV", "local")
SERVICE_NAME = os.environ.get("SERVICE_NAME", "bootcamp-api")

DATABASE_URL = os.environ.get("DATABASE_URL")
INTERNAL_TOKEN = os.environ.get("INTERNAL_TOKEN")

FEE_ACCOUNT_KEY = os.environ.get("FEE_ACCOUNT_KEY", "26ccf53d-7a91-41bf-acc2-09a93743f423")
UNIVERSITY_API_URL = os.environ.get("UNIVERSITY_API_URL", "http://localhost:1080")
UNIVERSITY_API_INTERNAL_TOKEN = os.environ.get("UNIVERSITY_API_INTERNAL_TOKEN", "default_token")

UNIVERSITY_API_TIMEOUT = int(os.environ.get("UNIVERSITY_API_TIMEOUT", "5"))

BYPASS_ENDPOINTS = [
    "/",
    "/health_check",
]

REQUIRED_VARIABLES = ["DATABASE_URL", "INTERNAL_TOKEN"]


def check_variables():
    missing = []
    for name in REQUIRED_VARIABLES:
        if not globals().get(name):
            missing.append(name)

    if missing:
        raise EnvironmentError(
            f"Faltam variáveis de ambiente: {', '.join(missing)}. "
            "Rodando com 'docker compose up' elas já vêm preenchidas. "
            "Fora do Docker, copie o .env.example para .env."
        )

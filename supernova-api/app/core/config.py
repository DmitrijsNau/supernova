import os

from dotenv import find_dotenv, load_dotenv

from app.core.logger import logger

expected_configs = [
    "PYTHON_ENV",
    "ECHO",
    "MAIN_DB_SERVER",
    "MAIN_DB_NAME",
    "MAIN_DB_USER",
    "MAIN_DB_PWD",
    "MAIN_DB_PORT",
    "MAIN_DB_DBO_SERVER",
    "MAIN_DB_DBO_NAME",
    "MAIN_DB_DBO_USER",
    "MAIN_DB_DBO_PWD",
    "MAIN_DB_DBO_PORT",
    "FMNH_JWT_TOKEN_SECRET_KEY",
]

env_path = find_dotenv(
    filename=".env", raise_error_if_not_found=True, usecwd=False
)
load_dotenv(dotenv_path=env_path, override=True)


settings = {a: os.environ.get(a) for a in expected_configs}

for expected_config in expected_configs:
    if expected_config not in settings or not settings[expected_config]:
        logger.warn(f"Configuration missing: {expected_config}")

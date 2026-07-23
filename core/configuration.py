from pathlib import Path
import tomllib

# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# core/app_config.toml
CONFIG_FILE = Path(__file__).resolve().parent / "app_config.toml"

with open(CONFIG_FILE, "rb") as f:
    CONFIG = tomllib.load(f)

ENVIRONMENT = CONFIG["app"]["environment"]

SECRET_KEY = CONFIG["security"]["secret_key"]

DEBUG = CONFIG[ENVIRONMENT]["debug"]

DATABASE = CONFIG["database"]

IMPORT = CONFIG["import"]

ICEBERG = CONFIG["iceberg"]

ELASTICSEARCH = CONFIG["elasticsearch"]

DYNAMODB = CONFIG["dynamodb"]



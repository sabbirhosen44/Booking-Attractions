from pathlib import Path
import tomllib

BASE_DIR = Path(__file__).resolve().parent.parent

CONFIG_FILE = (
    BASE_DIR
    / "config"
    / "app_config.toml"
)

with open(CONFIG_FILE, "rb") as f:
    CONFIG = tomllib.load(f)

ENVIRONMENT = CONFIG["app"]["environment"]

SECRET_KEY = CONFIG["security"]["secret_key"]

DEBUG = CONFIG[ENVIRONMENT]["debug"]

DATABASE = CONFIG["database"]

IMPORT = CONFIG["import"]
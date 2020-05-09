"""App config."""
from os import environ, path

from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))


class Config:
    """Flask configuration variables."""

    # General Config
    SECRET_KEY = environ.get("SECRET_KEY")
    FLASK_APP = environ.get("FLASK_APP")
    FLASK_ENV = environ.get("FLASK_ENV")

    # Database Config
    DB_URL = environ.get("DB_URL")

    # Cache Config
    # CACHE_DEBUG = environ.get('CACHE_DEBUG')
    # CACHE_TYPE = environ.get('CACHE_TYPE')
    # CACHE_URL = environ.get('CACHE_URL')

    # Bucket Config
    AWS_ACCESS_KEY_ID = environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = environ.get("AWS_SECRET_ACCESS_KEY")
    PERMANENT_BUCKET_PATH = environ.get("PERMANENT_BUCKET_PATH")
    TEMP_BUCKET_PATH = environ.get("TEMP_BUCKET_PATH")

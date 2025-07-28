# Add these at the top of your settings.py
import os
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qsl
from .env import config
import dj_database_url

load_dotenv()

# Replace the DATABASES section of your settings.py with this
tmpPostgres = urlparse(os.getenv("DATABASE_URL"))

DATABASE_URL=config('DATABASE_URL', default=None)
if DATABASE_URL is not None:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True
        )
    }
    
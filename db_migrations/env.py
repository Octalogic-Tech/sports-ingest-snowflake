import os
from sqlalchemy import engine_from_config, pool
from alembic import context

from app.models import Base  # <-- add this

config = context.config

# Prefer env var; fallback to alembic.ini if you really want
db_url = os.getenv("DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

target_metadata = Base.metadata

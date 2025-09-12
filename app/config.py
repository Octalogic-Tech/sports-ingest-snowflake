import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


load_dotenv()


@dataclass
class Settings:
    postgres_user: str = os.getenv("POSTGRES_USER", "postgres")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    postgres_host: str = os.getenv("POSTGRES_HOST", os.getenv("DB_HOST", "localhost"))
    postgres_port: str = os.getenv("POSTGRES_PORT", os.getenv("DB_PORT", "5432"))
    postgres_db: str = os.getenv("POSTGRES_DB", os.getenv("DB_NAME", "sports"))

    database_url: Optional[str] = os.getenv("DATABASE_URL")

    def get_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()



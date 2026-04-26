import os
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import psycopg2
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _normalize_database_url(raw_url: str | None) -> str:
    if not raw_url:
        raise ValueError(
            "DATABASE (or DATABASE_URL / DB_URL) environment variable not set!"
        )

    parsed = urlsplit(raw_url)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))

    if parsed.scheme.startswith("postgresql"):
        # Neon requires SSL in most environments.
        query.setdefault("sslmode", "require")
        # Not all psycopg/libpq combinations accept this query arg.
        query.pop("channel_binding", None)

    return urlunsplit(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            urlencode(query),
            parsed.fragment,
        )
    )


URL_DATABASE = _normalize_database_url(
    os.getenv("DATABASE") or os.getenv("DATABASE_URL") or os.getenv("DB_URL")
)
DATABASE_HOST = urlsplit(URL_DATABASE).hostname or "unknown"

engine = create_engine(URL_DATABASE, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_connection():
    return psycopg2.connect(URL_DATABASE)

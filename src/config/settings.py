"""
Loads app configuration from environment variables (via a local .env file
in development). Kept deliberately simple — plain os.environ reads, no
framework — since this is the one module every other module depends on,
and it should have as few ways to fail as possible.

See .env.example for the full list of variables this reads, and
SYSTEM_DESIGN.md Section 7 for how each one is used.
"""
import os

from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            f"Copy .env.example to .env and fill it in."
        )
    return value


DATABASE_URL = _require("DATABASE_URL")

# Pool sizing matches SYSTEM_DESIGN.md Section 7's database config block.
DB_POOL_SIZE = int(os.environ.get("DB_POOL_SIZE", "20"))
DB_MAX_OVERFLOW = int(os.environ.get("DB_MAX_OVERFLOW", "10"))
DB_ECHO = os.environ.get("DB_ECHO", "false").lower() == "true"

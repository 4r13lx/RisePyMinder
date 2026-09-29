"""
Centralized project configuration
"""

import logging
import os
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Environment initialization
try:
    from dotenv import load_dotenv
except ImportError:

    def load_dotenv(*args, **kwargs):
        logger.warning("python-dotenv not installed; skipping .env loading")


# Define base paths for dotenv
_BASE_DIR_ = Path(__file__).resolve().parent.parent
_ENV_FILE_ = _BASE_DIR_ / ".env"

# Load environment variables from .env file if it exists
if _ENV_FILE_.exists():
    try:
        load_dotenv(override=True, dotenv_path=_ENV_FILE_)
    except Exception as e:
        logger.warning(f"Failed to load .env file {_ENV_FILE_}: {e}")
else:
    logger.warning(f"No .env file found at: {_ENV_FILE_}")


# Configuration class
class Config:
    """Application configuration"""

    # Base paths
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"

    # Files
    SCHEDULE_PATH = DATA_DIR / "schedule.json"
    ENV_FILE = BASE_DIR / ".env"

    # Create directories if they don't exist
    DATA_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)

    # Notification configuration
    NOTIFICATION_TITLE: str = "Virtual Assistant Reminder"
    NOTIFICATION_TYPE: str = "INFO"

    # Timezone - Load from environment or default to UTC
    TIMEZONE_STR: str = os.environ.get("TIME_ZONE", "UTC")

    # Time rounding in minutes for schedule matching
    TIME_ROUNDING_MINUTES: int = int(os.environ.get("TIME_ROUNDING_MINUTES", "60"))

    # Interval in seconds for how often the scheduler checks for upcoming events
    INTERVAL_SECONDS: int = int(os.environ.get("INTERVAL_SECONDS", "3600"))


def get_env_var(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get environment variable with error handling"""
    try:
        return os.environ.get(key, default)
    except Exception as e:
        logger.error(f"Error accessing environment variable {key}: {e}")
        return default

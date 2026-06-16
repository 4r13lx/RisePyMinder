#!/usr/bin/env python3
"""
Entry point for the RisePyMinder application

Usage:
    python main.py
"""

import sys
import logging
from pathlib import Path

# Add root directory to path
sys.path.insert(0, str(Path(__file__).parent))

from scheduler import MessageScheduler
from scheduler.config import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Main function"""
    try:
        
        # Log embellecido
        logger.info("┌─────────────────────────────────────────────────────────")
        logger.info("│ 🚀 Starting RisePyMinder...                             ")
        logger.info("├─────────────────────────────────────────────────────────")
        logger.info(f"│ ⚙️  Config file:  {str(Config.ENV_FILE):<36} ")
        logger.info(f"│ 📅 Schedule:     {str(Config.SCHEDULE_PATH):<36} ")
        logger.info(f"│ 🌐 Timezone:     {str(Config.TIMEZONE_STR):<36} ")
        logger.info(f"│ ⏱️  Rounding:     {str(f'{Config.TIME_ROUNDING_MINUTES} min'):<36} ")
        logger.info(f"│ 🕒 Current time: {str(MessageScheduler().get_current_time()):<36} ")
        logger.info(f"│ 🕒 Interval:     {str(f'{Config.INTERVAL_SECONDS} sec'):<36} ")
        logger.info("└─────────────────────────────────────────────────────────")
        
        # Create scheduler instance
        scheduler = MessageScheduler(schedule_path=Config.SCHEDULE_PATH)
        
        # Execute
        if scheduler.run():
            sys.exit(0)
        else:
            logger.error("Scheduler execution failed")
            sys.exit(1)
    
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Unhandled error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

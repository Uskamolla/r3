import os
import logging
from datetime import datetime
import structlog

class CustomLogger:
    def __init__(self, log_dir="logs"):
        # Create the logs/ folder if it doesn't exist yet
        # Every run saves logs in this folder so you can look back later
        self.logs_dir = os.path.join(os.getcwd(), log_dir)
        os.makedirs(self.logs_dir, exist_ok=True)

        # Each run gets its own log file named with the exact date and time
        # Example: 02_18_2026_10_30_45.log — so logs never overwrite each other
        log_file = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
        self.log_file_path = os.path.join(self.logs_dir, log_file)

    def get_logger(self, name=__file__):
        # Use just the filename (not full path) as the logger's identity
        logger_name = os.path.basename(name)

        # This handler writes logs to the .log file on disk
        file_handler = logging.FileHandler(self.log_file_path)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter("%(message)s"))

        # This handler prints logs to your terminal so you see them live
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter("%(message)s"))

        # Hook both handlers into Python's built-in logging system
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",  # structlog formats the actual content, not basicConfig
            handlers=[console_handler, file_handler]
        )

        # structlog turns every log call into a clean JSON line
        # e.g: {"timestamp": "...", "level": "info", "event": "model loaded"}
        # This makes logs easy to read, search, and parse later
        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
                structlog.processors.add_log_level,
                structlog.processors.EventRenamer(to="event"),
                structlog.processors.JSONRenderer()
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

        return structlog.get_logger(logger_name)

# One shared logger for the entire project.
# Every file imports GLOBAL_LOGGER from here instead of creating their own.
# This way all logs go to the same file and look consistent.
from src.logger.custom_logger import CustomLogger

GLOBAL_LOGGER = CustomLogger().get_logger("src")

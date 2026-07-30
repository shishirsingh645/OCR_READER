from logger import get_logger

logger = get_logger(__name__)

logger.info("Logger initialized successfully.")
logger.warning("Warning test.")
logger.error("Error test.")
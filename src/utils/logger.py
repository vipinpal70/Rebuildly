import sys
from loguru import logger
from config.settings import settings

# Remove default handler
logger.remove()

# Add structured loguru handler with formatting
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level:<8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL,
)

# Export logger
__all__ = ["logger"]

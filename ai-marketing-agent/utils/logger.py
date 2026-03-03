import sys
from loguru import logger
from utils.config import get_settings

settings = get_settings()

# Remove default handler
logger.remove()

# Console handler
logger.add(
    sys.stdout,
    level=settings.log_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    colorize=True,
)

# File handler
logger.add(
    "logs/marketing_agent.log",
    rotation="10 MB",
    retention="30 days",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{line} - {message}",
)


def get_logger(name: str):
    return logger.bind(name=name)

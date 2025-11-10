import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from src.paths import LOGS, ensure_dirs


def setup_logging(log_dir: str | None = None) -> logging.Logger:
    """Configure logging with rotation and formatting."""
    # Määritä lokihakemisto ja varmista että se on olemassa
    if log_dir is None:
        log_dir = str(LOGS)
    ensure_dirs()

    Path(log_dir).mkdir(exist_ok=True)

    # Luo logger
    logger = logging.getLogger("homedashboard")
    logger.setLevel(logging.INFO)

    # Console handler
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        Path(log_dir) / "homedashboard.log",
        maxBytes=5_000_000,  # 5 MB
        backupCount=3,
    )

    # Formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Lisää handlerit (jos ei jo lisätty)
    if not logger.hasHandlers():
        logger.addHandler(console)
        logger.addHandler(file_handler)

    return logger

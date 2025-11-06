import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging(log_dir: str = "logs") -> logging.Logger:
    """Configure logging with rotation and formatting"""
    # Ensure log directory exists
    Path(log_dir).mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("homedashboard")
    logger.setLevel(logging.INFO)
    
    # Console handler
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        Path(log_dir) / "homedashboard.log",
        maxBytes=5_000_000,  # 5MB
        backupCount=3
    )
    file_handler.setLevel(logging.INFO)
    
    # Formatting
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(console)
    logger.addHandler(file_handler)
    
    return logger
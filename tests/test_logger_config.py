import logging
from pathlib import Path

from src.logger_config import setup_logging


def _reset_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
    logger.setLevel(logging.NOTSET)
    return logger


def test_setup_logging_adds_handlers_even_with_root(tmp_path):
    root_logger = logging.getLogger()
    root_handler = logging.StreamHandler()
    root_logger.addHandler(root_handler)

    logger = _reset_logger("homedashboard")
    setup_logging(log_dir=str(tmp_path))

    try:
        assert len(logger.handlers) == 2
        assert any(h.__class__.__name__ == "RotatingFileHandler" for h in logger.handlers)
        assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)
    finally:
        root_logger.removeHandler(root_handler)
        _reset_logger("homedashboard")


def test_setup_logging_idempotent(tmp_path):
    logger = _reset_logger("homedashboard")
    setup_logging(log_dir=str(tmp_path))
    setup_logging(log_dir=str(tmp_path / Path("second")))

    assert len(logger.handlers) == 2

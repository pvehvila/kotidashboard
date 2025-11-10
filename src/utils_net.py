# src/utils_net.py
"""Networking-related utilities."""

import socket

from src.utils import report_error


def get_ip() -> str:
    """Get the local IP address of the machine."""
    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception as e:
        report_error("get_ip", e)
        return "localhost"

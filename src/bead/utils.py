"""
Utility functions for the data pipeline.
"""

import os
from datetime import datetime


def ensure_directory(path: str):
    """Create directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)
    return path


def get_timestamp():
    """Get current timestamp string."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def print_header(title: str, char: str = "=", width: int = 60):
    """Print a formatted header."""
    print(char * width)
    print(title.center(width))
    print(char * width)


def print_section(title: str, char: str = "-", width: int = 60):
    """Print a section divider."""
    print(f"\n{char * width}")
    print(title)
    print(char * width)


def format_number(n) -> str:
    """Format number with commas."""
    if n is None:
        return "N/A"
    return f"{n:,.0f}" if isinstance(n, (int, float)) else str(n)

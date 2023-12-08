"""Utility functions for the Spotipy API."""

from configparser import ConfigParser
from pathlib import Path


def load_credentials(database: str) -> dict[str, str]:
    """Load credentials from config.ini file."""
    config_path = Path("./config.ini")
    if not config_path.exists():
        print(f"Config file {config_path} does not exist!")

    credentials = ConfigParser()
    credentials.read(config_path)

    return {
        "SPOTIPY_CLIENT_ID": credentials[database]["SPOTIPY_CLIENT_ID"],
        "SPOTIPY_CLIENT_SECRET": credentials[database]["SPOTIPY_CLIENT_SECRET"],
        "SPOTIPY_REDIRECT_URI": credentials[database]["SPOTIPY_REDIRECT_URI"],
    }

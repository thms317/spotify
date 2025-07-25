"""
Spotify, YouTube, and SoundCloud Link Extractor & Spotify Playlist Updater

This script:
1. Extracts track links from a text file for Spotify, YouTube, and SoundCloud.
2. Saves them into separate CSV files.
3. Authenticates to Spotify API.
4. Fetches and updates Spotify playlists by adding new songs.

Dependencies:
- spotipy
- yt_dlp
- chardet
- youtubesearchpython
- mutagen
- numpy
- pandas
"""

import csv
import os
import re

import chardet
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# ------------------------------- #
#        CONFIGURATION           #
# ------------------------------- #

INPUT_FILE_PATH = "file.txt"
OUTPUT_SPOTIFY_FILE = "spotify_links.csv"
OUTPUT_SOUNDCLOUD_FILE = "soundcloud_links.csv"
OUTPUT_YOUTUBE_FILE = "youtube_links.csv"

DOWNLOAD_FOLDER = "D:/SpotifyDatagrab/"  # Modify as needed

# Set your Spotify credentials here
SPOTIPY_CLIENT_ID = "your_client_id"
SPOTIPY_CLIENT_SECRET = "your_client_secret"
SPOTIFY_USERNAME = "your_username"
SPOTIFY_REDIRECT_URI = "https://example.com/callback"

# Spotify Playlist to Add Tracks To
TARGET_PLAYLIST_ID = "your_target_playlist_id"  # playlist you want to update
EXISTING_PLAYLIST_URI = "your_existing_playlist_uri"  # used to check existing tracks

# ------------------------------- #
#         REGEX PATTERNS         #
# ------------------------------- #

REGEX_PATTERNS = {
    "spotify_open": r"https:\/\/open.spotify.com\/track\/([a-zA-Z0-9]+)\?*",
    "spotify_short": r"https:\/\/spotify.link\/([a-zA-Z0-9]+)",
    "soundcloud": r"https:\/\/soundcloud.com\/([a-zA-Z0-9\-_\/]+)",
    "soundcloud_on": r"https:\/\/on.soundcloud.com\/([a-zA-Z0-9\-_\/]+)",
    "youtube_full": r"https:\/\/www.youtube.com\/watch\?v=([a-zA-Z0-9_-]+)",
    "youtube_short": r"https:\/\/youtu.be\/([a-zA-Z0-9_-]+)",
}

# ------------------------------- #
#        LINK EXTRACTION         #
# ------------------------------- #


def detect_encoding(file_path):
    with open(file_path, "rb") as file:
        return chardet.detect(file.read())["encoding"]


def extract_links(file_path):
    encoding = detect_encoding(file_path)
    with open(file_path, encoding=encoding) as file:
        text = file.read()

    links = {"spotify": [], "spotify_ids": [], "spotify_short": [], "soundcloud": [], "youtube": []}

    for match in re.findall(REGEX_PATTERNS["spotify_open"], text):
        links["spotify"].append(f"spotify:track:{match}")
        links["spotify_ids"].append(match)

    for match in re.findall(REGEX_PATTERNS["spotify_short"], text):
        links["spotify_short"].append(f"https://spotify.link/{match}")

    for match in re.findall(REGEX_PATTERNS["soundcloud"], text):
        links["soundcloud"].append(f"https://soundcloud.com/{match}")
    for match in re.findall(REGEX_PATTERNS["soundcloud_on"], text):
        links["soundcloud"].append(f"https://on.soundcloud.com/{match}")

    for match in re.findall(REGEX_PATTERNS["youtube_full"], text):
        links["youtube"].append(f"https://www.youtube.com/watch?v={match}")
    for match in re.findall(REGEX_PATTERNS["youtube_short"], text):
        links["youtube"].append(f"https://youtu.be/{match}")

    return links


def write_links_to_csv(links, file_path):
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for link in links:
            writer.writerow([link])


# ------------------------------- #
#        SPOTIFY AUTH SETUP      #
# ------------------------------- #


def setup_spotify():
    os.environ["SPOTIPY_CLIENT_ID"] = SPOTIPY_CLIENT_ID
    os.environ["SPOTIPY_CLIENT_SECRET"] = SPOTIPY_CLIENT_SECRET

    scope = ["user-library-read", "playlist-modify-public", "playlist-modify-private"]
    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI,
            scope=scope,
        )
    )


def get_existing_playlist_ids(sp, playlist_uri):
    total_tracks = sp.playlist_items(playlist_uri)["total"]
    offsets = np.arange(0, total_tracks + 100, 100)
    existing_ids = []

    for offset in offsets:
        items = sp.playlist_items(playlist_uri, offset=offset)["items"]
        existing_ids.extend([item["track"]["uri"].split(":")[2] for item in items])

    return existing_ids


def add_tracks_to_playlist(sp, playlist_id, track_ids):
    for i in range(0, len(track_ids), 100):
        sp.playlist_add_items(playlist_id, track_ids[i : i + 100])


# ------------------------------- #
#        MAIN FUNCTION           #
# ------------------------------- #


def main():
    print("Extracting links...")
    links = extract_links(INPUT_FILE_PATH)

    write_links_to_csv(links["spotify"] + links["spotify_short"], OUTPUT_SPOTIFY_FILE)
    write_links_to_csv(links["soundcloud"], OUTPUT_SOUNDCLOUD_FILE)
    write_links_to_csv(links["youtube"], OUTPUT_YOUTUBE_FILE)

    print("Saved links to CSV files.")

    print("Authenticating with Spotify...")
    sp = setup_spotify()

    print("Fetching existing playlist track IDs...")
    existing_ids = set(get_existing_playlist_ids(sp, EXISTING_PLAYLIST_URI))
    new_ids = list(set(links["spotify_ids"]) - existing_ids)

    print(f"New songs to add: {len(new_ids)}")
    if new_ids:
        add_tracks_to_playlist(sp, TARGET_PLAYLIST_ID, new_ids)
        print(f"Added {len(new_ids)} new tracks to playlist.")
    else:
        print("No new tracks to add.")


if __name__ == "__main__":
    main()

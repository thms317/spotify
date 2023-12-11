"""Utility functions for the Spotipy API."""

import json
from configparser import ConfigParser
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from spotipy.client import Spotify


def load_credentials(database: str) -> dict[str, str]:
    """Load credentials from config.ini file."""
    config_path = Path("./config.ini")
    if not config_path.exists():
        msg = f"Config file {config_path} does not exist!"
        raise FileNotFoundError(msg)

    credentials = ConfigParser()
    credentials.read(config_path)

    return {
        "SPOTIPY_CLIENT_ID": credentials[database]["SPOTIPY_CLIENT_ID"],
        "SPOTIPY_CLIENT_SECRET": credentials[database]["SPOTIPY_CLIENT_SECRET"],
        "SPOTIPY_REDIRECT_URI": credentials[database]["SPOTIPY_REDIRECT_URI"],
    }


def get_playlist_track_uris(sp: Spotify, playlist_uri: str) -> list[str]:
    """Retrieve all track IDs from a Spotify playlist, handling pagination."""
    track_uris = []
    response = sp.playlist_tracks(playlist_uri)
    while response:
        track_uris += [item["track"]["uri"] for item in response["items"] if item["track"]]
        if response["next"]:
            response = sp.next(response)
        else:
            break
    return track_uris


def export_to_json(data: dict[Any, Any] | list[dict[Any, Any]], name: str) -> None:
    """Export dictionary or list of dictionaries to a JSON file."""
    with Path(f"./data/{name}.json").open("w") as f:
        json.dump(data, f)


def transform_track_duration(track_duration_ms: int) -> str:
    """Transform track duration from ms to minutes."""
    duration_min = track_duration_ms / 60000
    duration_sec = (duration_min - int(duration_min)) * 60
    return f"{int(duration_min)}:{int(duration_sec)}"


def fetch_playlist_details(sp: Spotify, playlist_uri: str) -> pd.DataFrame:
    """Fetch details of each track in a playlist and return as a pandas DataFrame."""
    # Initialize pandas dataframe
    df_playlist = pd.DataFrame()
    # Use the Spotify API to fetch the playlist details, handling pagination
    response = sp.playlist_tracks(playlist_uri)
    # Iterate tracks in playlist
    while response:
        for track in response["items"]:
            if track:
                track_details = fetch_track_details(sp, track)
                df_playlist = pd.concat([df_playlist, pd.Series(track_details)], axis=1)
        # Check if there's more tracks to load (pagination)
        if response["next"]:
            response = sp.next(response)
        else:
            break
    return df_playlist.T


def fetch_track_details(sp: Spotify, track: dict[Any, Any]) -> dict[str, Any]:
    """Fetch track details."""
    # Fetch track URI
    track_uri = track["track"]["uri"]
    # Fetch artist URIs
    artists_uri_list = [artist["uri"] for artist in track["track"]["artists"]]
    # Build list of nested dictionaries with artist details
    artists_nested = []
    for artist_uri in artists_uri_list:
        artist = {
            "name": sp.artist(artist_uri)["name"],
            "genres": sp.artist(artist_uri)["genres"],
            "popularity": sp.artist(artist_uri)["popularity"],
        }
        # Append artist to list of dictionaries
        artists_nested.append(artist)
    # Build artists columns
    artists_genres = [artist["genres"] for artist in artists_nested]
    artists_popularities = [artist["popularity"] for artist in artists_nested]
    artists_names = [artist["name"] for artist in artists_nested]
    artists = ", ".join(artists_names)
    artists_avg_popularity = np.mean([artist["popularity"] for artist in artists_nested])
    # Fetch audio features
    audio_features = sp.audio_features(track_uri)[0]
    # Fetch user details
    user_details = sp.user(track["added_by"]["id"])
    # Print track details
    print(f"Fetching details for: {track['track']['name']} - {artists}")
    # Build the stats dictionary
    return {
        "name": track["track"]["name"],
        "artist": artists,
        "album": track["track"]["album"]["name"],
        "album_type": track["track"]["album"]["album_type"],
        "release_date": track["track"]["album"]["release_date"],
        "duration": transform_track_duration(track["track"]["duration_ms"]),
        "added_at": track["added_at"],
        "added_by": user_details["display_name"],
        "track_popularity": track["track"]["popularity"],
        "artist_avg_popularity": artists_avg_popularity,
        "danceability": audio_features["danceability"],
        "energy": audio_features["energy"],
        "key": audio_features["key"],
        "loudness": audio_features["loudness"],
        "mode": audio_features["mode"],
        "speechiness": audio_features["speechiness"],
        "acousticness": audio_features["acousticness"],
        "instrumentalness": audio_features["instrumentalness"],
        "liveness": audio_features["liveness"],
        "valence": audio_features["valence"],
        "tempo": audio_features["tempo"],
        "time_signature": audio_features["time_signature"],
        "track_id": track["track"]["id"],
        "artist_names": artists_names,
        "artist_genres": artists_genres,
        "artist_popularities": artists_popularities,
    }


def calculate_total_overlap_percentage(
    sp: Spotify, first_playlist_uri: str, second_playlist_uri: str
) -> float:
    """Calculate the total overlap percentage between two playlists, considering the unique tracks in both."""
    first_playlist_track_ids = get_playlist_track_uris(sp, first_playlist_uri)
    second_playlist_track_ids = get_playlist_track_uris(sp, second_playlist_uri)
    common_tracks = set(first_playlist_track_ids).intersection(second_playlist_track_ids)
    # Calculate the total number of unique tracks in both playlists
    total_unique_tracks = len(set(first_playlist_track_ids + second_playlist_track_ids))
    # Calculate the overlap percentage: common tracks / total unique tracks in both playlists
    return len(common_tracks) / total_unique_tracks * 100


def calculate_first_playlist_track_overlap_percentage(
    sp: Spotify, first_playlist_uri: str, second_playlist_uri: str
) -> float:
    """Calculate the percentage of tracks from the first playlist that are also present in the second playlist."""
    first_playlist_track_ids = get_playlist_track_uris(sp, first_playlist_uri)
    second_playlist_track_ids = get_playlist_track_uris(sp, second_playlist_uri)
    common_tracks = set(first_playlist_track_ids).intersection(second_playlist_track_ids)
    # Calculate the total number of unique tracks in the first playlist also present in the second
    first_playlist_unique_tracks = len(first_playlist_track_ids)
    # Calculate the overlap percentage: common tracks / total unique tracks in first playlist
    return len(common_tracks) / first_playlist_unique_tracks * 100

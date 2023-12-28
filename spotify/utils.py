"""Utility functions for the Spotipy API."""

import json
import logging
import sys
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


def fetch_playlist_tracks(sp: Spotify, playlist_uri: str) -> list[dict[str, Any] | None]:
    """Fetch all tracks in a playlist."""
    tracks = []
    response = sp.playlist_tracks(playlist_uri)
    # Iterate tracks in playlist, handling pagination
    while response:
        tracks.extend([track for track in response["items"] if track])
        response = sp.next(response) if response["next"] else None
    return tracks


def initialize_playlist_stats(tracks: list[dict[str, Any]]) -> pd.DataFrame:
    """Parse all tracks in a playlist as a dataframe."""
    # Initialize pandas dataframe
    df_playlist = pd.DataFrame()
    # Iterate tracks in playlist and add to dataframe
    for track in tracks:
        track_details = parse_track_details(track)
        df_playlist = pd.concat([df_playlist, pd.Series(track_details)], axis=1)
    # Transpose, drop index column, and reset index
    return df_playlist.T.reset_index().drop(["index"], axis=1)


def parse_track_details(track: dict[Any, Any]) -> dict[str, Any]:
    """Parse track details."""
    # Parse artist details
    artists_uris = [artist["uri"] for artist in track["track"]["artists"]]
    artists_names = [artist["name"] for artist in track["track"]["artists"]]
    artists_label = ", ".join(artists_names)
    # Build the stats dictionary
    return {
        "name": track["track"]["name"],
        "artist": artists_label,
        "album": track["track"]["album"]["name"],
        "album_type": track["track"]["album"]["album_type"],
        "release_date": track["track"]["album"]["release_date"],
        "duration": transform_track_duration(track["track"]["duration_ms"]),
        "duration_ms": track["track"]["duration_ms"],
        "added_at": track["added_at"],
        "added_by_id": track["added_by"]["id"],
        "track_popularity": track["track"]["popularity"],
        "track_id": track["track"]["id"],
        "track_uri": track["track"]["uri"],
        "artist_uris": artists_uris,
        "artist_names": artists_names,
        "enriched": False,
    }


def fetch_user_names(sp: Spotify, df_stats: pd.DataFrame) -> pd.DataFrame:
    """Fetch user display names from id."""
    user_ids = df_stats["added_by_id"].unique().tolist()
    # Iterate unique users in dataset
    for user_id in user_ids:
        user_details = sp.user(user_id)
        # Update user display name
        df_stats.loc[df_stats["added_by_id"] == user_id, "added_by"] = user_details["display_name"]
    return df_stats


def fetch_artist_details(sp: Spotify, track: pd.Series) -> dict[str, Any]:
    """Fetch artist details by iterating the dataset. Skip tracks that have been previously fetched."""
    # Build list of nested dictionaries with artist details
    artists_nested = []
    # Transform string representation of artist URIs to list of URIs
    try:
        # first try to JSON requires double quotes
        artist_uris = json.loads(track["artist_uris"].replace("'", '"'))
    except AttributeError:
        artist_uris = track["artist_uris"]
    for artist_uri in artist_uris:
        artist = {
            "genres": sp.artist(artist_uri)["genres"],
            "popularity": sp.artist(artist_uri)["popularity"],
        }
        # Append artist to list of dictionaries
        artists_nested.append(artist)
    return {
        "artists_genres": [artist["genres"] for artist in artists_nested],
        "artists_popularities": [artist["popularity"] for artist in artists_nested],
        "artists_avg_popularity": np.mean([artist["popularity"] for artist in artists_nested]),
    }


def enrich_playlist_stats(sp: Spotify, df_playlist: pd.DataFrame) -> pd.DataFrame:
    """Iterate dataframe to enrich dataset with artist details and audio features."""
    logger = logging.getLogger("spotify")
    # Initialize empty list to store enriched rows
    df_enriched = pd.DataFrame()
    # Iterate dataframe
    for _, track in df_playlist.iterrows():
        # If song is already enriched, add to dataframe and continue
        if track["enriched"] is True:
            df_enriched = pd.concat([df_enriched, pd.Series(track)], axis=1)
            continue
        try:
            logger.debug(f"Fetching details for: {track['name']} - {track['artist']}")
            # Fetch artist details, audio features, and add an `enriched` tag
            artist_details = fetch_artist_details(sp, track)
            audio_features = fetch_audio_features(sp, track)
            enriched_row = {
                # "track_id": track["track_id"],
                **track,
                **audio_features,
                **artist_details,
                "enriched": True,
            }
            # Concatenate the enriched row to the dataframe
            df_enriched = pd.concat([df_enriched, pd.Series(enriched_row)], axis=1)
        except TimeoutError as e:
            msg = f"Error processing track {track['name']} - {track['artist']}: {e}"
            logger.exception(msg)
            continue
    # left join the enriched dataframe with the original dataframe
    return df_enriched.T.reset_index().drop(["index"], axis=1)
    # df_enriched = df_enriched.T.reset_index().drop(["index"], axis=1)
    # # Merge the enriched dataframe with the original dataframe
    # df_playlist = df_playlist.merge(
    #     df_enriched, how="left", on=["track_id"], suffixes=("_outdated", "")
    # )
    # logger.info(f"Enriched dataframe with {len(df_enriched)} tracks.")
    # # Drop original columns, that were updated
    # return df_playlist[[col for col in df_playlist.columns if not col.endswith("_outdated")]]


def fetch_audio_features(sp: Spotify, track: pd.Series) -> dict[str, Any]:
    """Fetch audio features by iterating the dataset."""
    logger = logging.getLogger("spotify")
    audio_features = sp.audio_features(track["track_uri"])[0]
    if not audio_features:
        logger.info(f"Audio features not found for: {track['name']} - {track['artist']}")
    return {
        "danceability": audio_features["danceability"] if audio_features else None,
        "energy": audio_features["energy"] if audio_features else None,
        "key": audio_features["key"] if audio_features else None,
        "loudness": audio_features["loudness"] if audio_features else None,
        "mode": audio_features["mode"] if audio_features else None,
        "speechiness": audio_features["speechiness"] if audio_features else None,
        "acousticness": audio_features["acousticness"] if audio_features else None,
        "instrumentalness": audio_features["instrumentalness"] if audio_features else None,
        "liveness": audio_features["liveness"] if audio_features else None,
        "valence": audio_features["valence"] if audio_features else None,
        "tempo": audio_features["tempo"] if audio_features else None,
        "time_signature": audio_features["time_signature"] if audio_features else None,
    }


def calculate_playlist_overlap(
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


def create_logger(name: str, level: int = logging.DEBUG) -> logging.Logger:
    """Create a logger instance."""
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    # Create console handler and set level
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    # Add formatter to handler
    handler.setFormatter(formatter)
    # Add handler to logger
    logger.addHandler(handler)
    return logger


def update_playlist_stats(df_playlist: pd.DataFrame, file_name: str) -> pd.DataFrame:
    """Update playlist stats with existing data."""
    logger = logging.getLogger("spotify")
    try:
        # Load previously exported (enriched) data
        df_outdated = pd.read_csv(f"./data/{file_name}.csv")
        try:
            # Drop rows that have not yet been enriched
            df_enriched_outdated = df_outdated.dropna(subset=["enriched"])
            logger.info(f"Previously enriched tracks: {len(df_enriched_outdated)}")
            logger.info(f"Unenriched tracks: {len(df_outdated[df_outdated['enriched'].isna()])}")
            # Update playlist stats with the existing enriched data
            df_playlist = df_playlist.merge(
                df_outdated,
                how="left",
                on=["track_id"],
                suffixes=("", "_outdated"),
            )
            # Drop columns with the _outdated suffixes
            return df_playlist[
                [col for col in df_playlist.columns if not col.endswith("_outdated")]
            ]
        except KeyError:
            logger.info("No previously enriched data found.")
            return df_playlist
    except FileNotFoundError:
        logger.info("No previously exported data found.")
        return df_playlist

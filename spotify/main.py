"""Main file for the spotify package."""


from pathlib import Path
from typing import Any

import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from spotify.utils import load_credentials


def export_to_json(data: dict[Any, Any] | list[dict[Any, Any]], name: str) -> None:
    """Export dictionary to JSON file."""
    import json

    with Path(f"./data/{name}.json").open("w") as f:
        json.dump(data, f)


# Load credentials from config.ini file
credentials = load_credentials("spotify")

# Pass credentials to Spotipy API
spotipy_client_id = credentials["SPOTIPY_CLIENT_ID"]
spotipy_client_secret = credentials["SPOTIPY_CLIENT_SECRET"]
spotipy_redirect_uri = credentials["SPOTIPY_REDIRECT_URI"]

# Authentication
client_credentials_manager = SpotifyClientCredentials(
    client_id=spotipy_client_id, client_secret=spotipy_client_secret
)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Get playlist URI
playlist_link = "https://open.spotify.com/playlist/2flYqzsxSNSIHjCNCphCMw?si=6408cf90576944be"
playlist_uri = playlist_link.split("/")[-1].split("?")[0]
track_uris = [x["track"]["uri"] for x in sp.playlist_tracks(playlist_uri)["items"]]

# for track in sp.playlist_tracks(playlist_URI)["items"]:
#     # URI
#     track_uri = track["track"]["uri"]

#     # Track name
#     track_name = track["track"]["name"]
#     print(track_name)

#     # Main Artist
#     artist_uri = track["track"]["artists"][0]["uri"]
#     artist_info = sp.artist(artist_uri)

#     # Name, popularity, genre
#     artist_name = track["track"]["artists"][0]["name"]
#     artist_pop = artist_info["popularity"]
#     artist_genres = artist_info["genres"]

#     # Album
#     album = track["track"]["album"]["name"]

#     # Popularity of the track
#     track_pop = track["track"]["popularity"]

# print(track_name)

# Initialize empty DataFrame for aggregated features (genres, artists)
df_aggregated = pd.DataFrame()

# Iterate over tracks in playlist
for track in sp.playlist_tracks(playlist_uri)["items"]:
    # Export to JSON
    # export_to_json(track, "track")

    # Get track URI
    track_uri = track.get("track").get("uri")

    # Get artists
    artists_dict = track.get("track").get("artists")
    artists_list = [artist.get("name") for artist in artists_dict]
    artists_uri_list = [artist.get("uri") for artist in artists_dict]
    artists = ", ".join(artists_list)
    print(artists_list)

    # Get artist info
    artists_info = [sp.artist(artist_uri) for artist_uri in artists_uri_list]
    genres = [artist.get("genres") for artist in artists_info]
    artists_popularity = [artist.get("popularity") for artist in artists_info]
    # export_to_json(artists_info, "artists")

    # Get categories (???)
    categories = sp.categories()
    print(categories)
    # export_to_json(categories, "categories")

    # Get track duration in minutes
    duration_ms = track.get("track").get("duration_ms")
    duration_min = duration_ms / 60000
    duration_sec = (duration_min - int(duration_min)) * 60
    duration = f"{int(duration_min)}:{int(duration_sec)}"

    # Get audio features
    audio_features = sp.audio_features(track_uri)[0]
    # export_to_json(audio_features, "audio_features")

    # Build dictionary with track stats
    stats_dict = {
        "track_name": track.get("track").get("name"),
        "track_artists": artists_list,
        "track_album": track.get("track").get("album").get("name"),
        "release_date": track.get("track").get("album").get("release_date"),
        "album_type": track.get("track").get("album").get("album_type"),
        "duration_min": duration,
        "added_by_user_id": track.get("added_by").get("id"),
        "added_at": track.get("added_at"),
        "track_popularity": track.get("track").get("popularity"),
        "track_id": track.get("track").get("id"),
        "danceability": audio_features.get("danceability"),
        "energy": audio_features.get("energy"),
        "acousticness": audio_features.get("acousticness"),
        "tempo": audio_features.get("tempo"),
        "genres": genres,
        "artists_popularity": artists_popularity,
    }

    # print(stats_dict)

    break

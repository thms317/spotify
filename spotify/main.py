"""Main file for the spotify package."""

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from utils import (
    calculate_first_playlist_track_overlap_percentage,
    calculate_total_overlap_percentage,
    fetch_playlist_details,
    load_credentials,
)


def main() -> None:
    """Extract song statistics from Spotify playlist."""
    # Load credentials and authenticate with Spotify
    credentials = load_credentials("spotify")
    client_credentials_manager = SpotifyClientCredentials(
        client_id=credentials["SPOTIPY_CLIENT_ID"],
        client_secret=credentials["SPOTIPY_CLIENT_SECRET"],
    )
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # Playlist: Pallen 2023
    playlist_uri = "https://open.spotify.com/playlist/2flYqzsxSNSIHjCNCphCMw?si=6408cf90576944be"

    # Fetch playlist details
    df_playlist = fetch_playlist_details(sp, playlist_uri)
    df_playlist.to_csv("./data/playlist_stats.csv", index=False)

    # Compare playlists
    total_overlap = calculate_total_overlap_percentage(
        sp=sp,
        first_playlist_uri=playlist_uri,
        second_playlist_uri="https://open.spotify.com/playlist/4gjdA4c6B0YB7S5GmgxLEk?si=070cab20524f4ddc",
    )
    print(f"Overlap: {total_overlap:.2f}%")

    # Compare playlists
    playlist_hype = calculate_first_playlist_track_overlap_percentage(
        sp=sp,
        first_playlist_uri="https://open.spotify.com/playlist/4gjdA4c6B0YB7S5GmgxLEk?si=070cab20524f4ddc",
        second_playlist_uri=playlist_uri,
    )
    print(f"Playlist hype (Pallen 2023 vs. 3voor12 SvhJ 2023): {playlist_hype:.2f}%")


if __name__ == "__main__":
    main()

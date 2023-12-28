"""Main file for the spotify package."""

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from utils import (
    create_logger,
    enrich_playlist_stats,
    fetch_playlist_tracks,
    initialize_playlist_stats,
    load_credentials,
    update_playlist_stats,
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
    playlist_uri = "https://open.spotify.com/playlist/2flYqzsxSNSIHjCNCphCMw?si=6408cf90576944be"  # Pallen 2023
    # playlist_uri = "https://open.spotify.com/playlist/6xbkFqSuhmYeG1TRrvpoTC?si=b57441a2ce844789"  # 2023 (albums)
    # playlist_uri = "https://open.spotify.com/playlist/16aMi5Mu9PMss7NdZTnPcr?si=883603597e7b46e7"  # 2023 (tracks)

    # Set export filename
    file_name = "playlist_stats"
    # file_name = "playlist_stats_2023_albums"
    # file_name = "playlist_stats_2023_tracks"

    # Fetch playlist stats
    logger.info("Fetching playlist tracks...")
    tracks = fetch_playlist_tracks(sp, playlist_uri)
    logger.info(f"Fetched {len(tracks)} tracks.")

    # Initialize dataframe of playlist stats
    logger.info("Initializing dataframe of playlist stats...")
    df_playlist = initialize_playlist_stats(tracks)
    logger.info(f"Initialized dataframe with {len(df_playlist)} tracks.")

    # Update playlist stats with previously exported data
    logger.info("Updating dataframe with previously loaded data...")
    df_playlist = update_playlist_stats(df_playlist, file_name)

    # Enrich playlist stats (e.g. audio features) - iterative -> slow
    df_playlist = enrich_playlist_stats(sp, df_playlist)

    # Export playlist stats
    df_playlist.to_csv(f"./data/{file_name}.csv", index=False)
    logger.info(f"Exported playlist stats to ./data/{file_name}.csv")


if __name__ == "__main__":
    logger = create_logger("spotify")
    main()

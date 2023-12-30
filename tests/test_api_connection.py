import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from utils import load_credentials


def test_api_connection() -> None:
    """Test connection with Spotify API."""
    credentials = load_credentials("spotify-sandra")  # "spotify" / "spotify-2" / "spotify-sandra"
    print(credentials["SPOTIPY_CLIENT_ID"])
    client_credentials_manager = SpotifyClientCredentials(
        client_id=credentials["SPOTIPY_CLIENT_ID"],
        client_secret=credentials["SPOTIPY_CLIENT_SECRET"],
    )
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # ID of a track (example: "7GhIk7Il098yCjg4BQjzvb" for "Thinking Out Loud" by Ed Sheeran)
    track_id = "7GhIk7Il098yCjg4BQjzvb"

    # Fetch track details
    track = sp.track(track_id)
    print(f"Track Name: {track['name']}")
    print(f"Artist: {track['artists'][0]['name']}")


if __name__ == "__main__":
    test_api_connection()

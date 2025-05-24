import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

# Load the credentials from the .env file
load_dotenv()

# Get credentials from environment
client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

# DEBUG: Print to check if credentials loaded correctly
print(f"DEBUG: client_id = {client_id}")
print(f"DEBUG: client_secret = {client_secret}")

# Raise error if credentials missing (to catch problems early)
if not client_id or not client_secret:
    raise ValueError("Spotify client_id or client_secret not found. Please check your .env file.")

# Authenticate with Spotify
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=client_id,
    client_secret=client_secret
))

# Mapping emotion to music genres
emotion_genres = {
    "happy": ["pop", "dance", "party"],
    "sad": ["acoustic", "piano", "sad"],
    "angry": ["rock", "metal", "hardcore"],
    "neutral": ["indie", "chill"],
    "calm": ["ambient", "classical", "lo-fi"]
}

# Function to get playlists for a given emotion
def get_playlist_for_emotion(emotion):
    playlists = []
    genres = emotion_genres.get(emotion, ["pop"])  # default to pop

    for genre in genres:
        results = sp.search(q=genre, type="playlist", limit=1)
        if results:
            playlists_data = results.get("playlists")
            if playlists_data:
                items = playlists_data.get("items", [])
                if items and items[0] and isinstance(items[0], dict):
                    url = items[0].get('external_urls', {}).get('spotify')
                    if url:
                        playlists.append(url)

    return playlists
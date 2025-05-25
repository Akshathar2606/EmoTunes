import os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")  # Add this to your .env file, e.g. "http://localhost:8501/"

if not client_id or not client_secret or not redirect_uri:
    raise ValueError("Spotify client ID, secret or redirect URI not found in .env.")

# Enhanced scope for more features
scope = "playlist-read-private playlist-modify-public playlist-modify-private user-read-playback-state user-modify-playback-state streaming user-library-read user-library-modify"

# Initialize SpotifyOAuth for user authorization
sp_oauth = SpotifyOAuth(client_id=client_id,
                       client_secret=client_secret,
                       redirect_uri=redirect_uri,
                       scope=scope)

# This function gets a Spotify client with a valid user token, given the token info
def get_spotify_client(token_info=None):
    if token_info:
        access_token = token_info["access_token"]
        return Spotify(auth=access_token)
    else:
        # fallback to client credentials flow if no token
        from spotipy.oauth2 import SpotifyClientCredentials
        return Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

# Emotion to genres mapping with more detailed categories
emotion_genres = {
    "happy": ["pop", "dance", "party", "happy", "feel-good"],
    "sad": ["acoustic", "piano", "sad", "melancholic", "ballad"],
    "angry": ["rock", "metal", "hardcore", "punk", "aggressive"],
    "neutral": ["indie", "alternative", "chill", "ambient"],
    "calm": ["ambient", "classical", "lo-fi", "meditation", "peaceful"]
}

def search_tracks(query, token_info=None, limit=10):
    """Search for tracks and artists"""
    sp = get_spotify_client(token_info)
    try:
        results = sp.search(q=query, type='track,artist', limit=limit)
        tracks = results.get('tracks', {}).get('items', [])
        artists = results.get('artists', {}).get('items', [])
        
        return {
            'tracks': [{
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'url': track['external_urls']['spotify'],
                'uri': track['uri'],
                'preview_url': track['preview_url']
            } for track in tracks],
            'artists': [{
                'name': artist['name'],
                'url': artist['external_urls']['spotify'],
                'uri': artist['uri']
            } for artist in artists]
        }
    except Exception as e:
        print(f"Error searching: {e}")
        return {'tracks': [], 'artists': []}

def create_playlist(user_id, name, description, token_info):
    """Create a new playlist for the user"""
    sp = get_spotify_client(token_info)
    try:
        playlist = sp.user_playlist_create(
            user_id,
            name,
            public=True,
            description=description
        )
        return playlist
    except Exception as e:
        print(f"Error creating playlist: {e}")
        return None

def add_tracks_to_playlist(playlist_id, track_uris, token_info):
    """Add tracks to a playlist"""
    sp = get_spotify_client(token_info)
    try:
        sp.playlist_add_items(playlist_id, track_uris)
        return True
    except Exception as e:
        print(f"Error adding tracks: {e}")
        return False

def get_playlist_for_emotion_and_language(emotion, language, genre=None, token_info=None):
    """
    Fetch playlists based on emotion, language, and optional genre filter.
    If token_info is provided, use authenticated Spotify client, else fallback to public client.
    """
    playlists = []
    genres = emotion_genres.get(emotion.lower(), ["pop"])
    
    # Add genre filter if specified
    if genre and genre != "All Genres":
        genres = [genre.lower()]
    
    sp = get_spotify_client(token_info)
    
    for genre in genres:
        query = f"{genre} {language} {emotion}"
        try:
            results = sp.search(q=query, type="playlist", limit=2)
            playlist_data = results.get("playlists", {}).get("items", [])
            
            for playlist in playlist_data:
                playlists.append({
                    "name": playlist["name"],
                    "url": playlist["external_urls"]["spotify"],
                    "uri": playlist["uri"],
                    "description": playlist.get("description", ""),
                    "image": playlist["images"][0]["url"] if playlist["images"] else None
                })
        except Exception as e:
            print(f"Error fetching playlist for '{query}': {e}")
            
    return playlists

def save_track_to_library(track_uri, token_info):
    """Save a track to user's Spotify library"""
    sp = get_spotify_client(token_info)
    try:
        sp.current_user_saved_tracks_add([track_uri])
        return True
    except Exception as e:
        print(f"Error saving track: {e}")
        return False                                    
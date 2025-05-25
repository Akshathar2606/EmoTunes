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
    "energetic": [
        "edm", "rock", "workout", "electronic", "dance", "power", 
        "gym", "motivation", "high-intensity", "cardio", "pump",
        "energy", "adrenaline"
    ],
    "romantic": [
        "r&b", "soft pop", "ballads", "love songs", "romantic",
        "soul", "slow jams", "romance", "passionate", "love",
        "dreamy", "affectionate"
    ],
    "heartbroken": [
        "indie", "sad pop", "acoustic", "melancholic", "emotional",
        "breakup songs", "heartbreak", "longing", "reflective",
        "sad acoustic", "emotional ballads"
    ],
    "chill": [
        "lo-fi", "chillhop", "acoustic", "relaxing", "chill",
        "ambient", "laid back", "easy listening", "breezy",
        "beach", "coffeehouse", "mellow"
    ],
    "uplifting": [
        "gospel", "motivational", "indie pop", "inspirational",
        "positive", "feel good", "confidence", "upbeat",
        "hopeful", "empowering", "sunshine"
    ],
    "dark": [
        "alt rock", "dark pop", "trap soul", "moody", "intense",
        "mysterious", "dark", "introspective", "alternative",
        "underground", "brooding"
    ],
    "party": [
        "dance", "reggaeton", "pop hits", "party", "club",
        "disco", "celebration", "fun", "fiesta", "dance pop",
        "top hits", "party anthems"
    ],
    "nostalgic": [
        "retro", "classics", "synthwave", "oldies", "vintage",
        "throwback", "old school", "memories", "80s", "90s",
        "sentimental", "golden oldies"
    ],
    "angry": [
        "metal", "punk", "hardcore rap", "aggressive", "heavy metal",
        "rage", "rebellion", "defiant", "intense", "hard rock",
        "screamo", "thrash"
    ],
    "lonely": [
        "ambient", "minimalist", "acoustic", "quiet", "solitude",
        "isolation", "minimal", "atmospheric", "contemplative",
        "solo piano", "ethereal"
    ]
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
    Fetch playlists based on emotion and language with optimized search.
    """
    playlists = []
    sp = get_spotify_client(token_info)
    
    # Simplified language mapping
    language_queries = {
        "English": ["english playlist", "english songs"],
        "Hindi": ["hindi songs", "bollywood songs"],
        "Kannada": ["kannada songs", "kannada hits"],
        "Telugu": ["telugu songs", "tollywood hits"],
        "Tamil": ["tamil songs", "kollywood hits"]
    }

    # Get base queries for the selected language
    base_queries = language_queries.get(language, [language.lower()])
    
    try:
        # Make just 2-3 targeted searches instead of many combinations
        for query in base_queries:
            search_query = f"{emotion} {query}"
            try:
                results = sp.search(q=search_query, type="playlist", limit=3)
                if results and 'playlists' in results and 'items' in results['playlists']:
                    playlist_data = results['playlists']['items']
                    
                    for playlist in playlist_data:
                        # Basic validation to ensure we have all required fields
                        if not playlist or 'uri' not in playlist:
                            continue
                            
                        # Check if playlist is not already added
                        if not any(p['uri'] == playlist['uri'] for p in playlists):
                            playlists.append({
                                "name": playlist.get("name", "Untitled Playlist"),
                                "url": playlist.get("external_urls", {}).get("spotify", ""),
                                "uri": playlist["uri"],
                                "description": playlist.get("description", ""),
                                "image": playlist.get("images", [{}])[0].get("url") if playlist.get("images") else None
                            })
                            
                        # If we have enough playlists, stop searching
                        if len(playlists) >= 6:
                            return playlists
                            
            except Exception as e:
                print(f"Warning: Error in search query '{search_query}': {str(e)}")
                continue
                
        return playlists
        
    except Exception as e:
        print(f"Error in playlist search: {str(e)}")
        return []

def save_track_to_library(track_uri, token_info):
    """Save a track to user's Spotify library"""
    sp = get_spotify_client(token_info)
    try:
        sp.current_user_saved_tracks_add([track_uri])
        return True
    except Exception as e:
        print(f"Error saving track: {e}")
        return False 
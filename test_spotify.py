from spotify_module import get_playlist_for_emotion

emotion = "sad"
playlists = get_playlist_for_emotion(emotion)
print("Playlists found:", playlists)
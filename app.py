import streamlit as st
from spotify_module import get_playlist_for_emotion

st.title("EmoTunes - Mood-Based Music Recommender")

emotion = st.selectbox("How are you feeling?", ["happy", "sad", "angry", "calm", "neutral"])

if st.button("Get Music 🎶"):
    st.success(f"Getting songs for your mood: *{emotion}*")
    playlists = get_playlist_for_emotion(emotion)

    for url in playlists:
        st.markdown(f"[🎵 Open Playlist]({url})", unsafe_allow_html=True)
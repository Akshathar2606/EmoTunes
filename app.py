import streamlit as st
import random
from spotify_module import (
    get_playlist_for_emotion_and_language,
    search_tracks,
    create_playlist,
    add_tracks_to_playlist,
    save_track_to_library,
    get_spotify_client,
    sp_oauth
)

# Define mood mappings with emojis and mesmerizing color combinations
MOOD_MAPPING = {
    "⚡ Energetic": {
        "emotion": "energetic",
        "color": "#FF4D4D",  # Vibrant red
        "gradient": ["#FF4D4D", "#FF8C42", "#FFA07A"],
        "secondary_gradient": ["#FFD141", "#FF8C42"],
        "contrast": "#2A2A3C",
        "icon": "⚡"
    },
    "💝 Romantic": {
        "emotion": "romantic",
        "color": "#FF69B4",  # Hot pink
        "gradient": ["#FF69B4", "#FFB6C1", "#FFC0CB"],
        "secondary_gradient": ["#FF1493", "#FF69B4"],
        "contrast": "#2D1F2A",
        "icon": "💝"
    },
    "💔 Heartbroken": {
        "emotion": "heartbroken",
        "color": "#4A4A8F",  # Deep blue
        "gradient": ["#4A4A8F", "#6B6BB8", "#8080C0"],
        "secondary_gradient": ["#483D8B", "#6959CD"],
        "contrast": "#1A1A2E",
        "icon": "💔"
    },
    "🎉 Party": {
        "emotion": "party",
        "color": "#FF1493",  # Deep pink
        "gradient": ["#FF1493", "#FF69B4", "#FFB6C1"],
        "secondary_gradient": ["#FF00FF", "#FF1493"],
        "contrast": "#2A1F2D",
        "icon": "🎉"
    },
    "😠 Angry": {
        "emotion": "angry",
        "color": "#8B0000",  # Dark red
        "gradient": ["#8B0000", "#B22222", "#CD5C5C"],
        "secondary_gradient": ["#DC143C", "#8B0000"],
        "contrast": "#1A0F0F",
        "icon": "😠"
    }
}

# Update mood quotes for the new moods
MOOD_QUOTES = {
    "⚡ Energetic": "Time to get pumped up and moving!",
    "💝 Romantic": "Let love fill the air with sweet melodies.",
    "💔 Heartbroken": "Music heals the heart's deepest wounds.",
    "🎉 Party": "Let's turn up the fun and dance!",
    "😠 Angry": "Channel that energy into powerful beats."
}

# Page config must be the first Streamlit command
st.set_page_config(
    page_title="EmoTunes",
    layout="centered",
    initial_sidebar_state="expanded",
    page_icon="🎵"
)

# Initialize session states
if 'spotify_auth' not in st.session_state:
    st.session_state.spotify_auth = False
if 'token_info' not in st.session_state:
    st.session_state.token_info = None
if 'search_results' not in st.session_state:
    st.session_state.search_results = None
if 'saved_tracks' not in st.session_state:
    st.session_state.saved_tracks = []
if 'selected_mood' not in st.session_state:
    st.session_state.selected_mood = "⚡ Energetic"  # Default mood

# Function to update mood and trigger rerun
def update_mood(new_mood):
    st.session_state.selected_mood = new_mood
    st.rerun()  # Using st.rerun() instead of experimental_rerun

# Custom CSS for modern styling with enhanced blur and softer transitions
st.markdown(f"""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Quicksand:wght@400;500;600;700&display=swap');

    /* Base Font Settings */
    * {{
        font-family: 'Poppins', sans-serif;
    }}

    /* Modern Card Styling with enhanced depth */
    .stApp {{
        background: linear-gradient(135deg, 
            {MOOD_MAPPING[st.session_state.selected_mood]["gradient"][0]}dd 0%,
            {MOOD_MAPPING[st.session_state.selected_mood]["gradient"][1]}ee 50%,
            {MOOD_MAPPING[st.session_state.selected_mood]["gradient"][2]}dd 100%
        ) !important;
        background-size: 400% 400% !important;
        animation: gradientBG 15s ease infinite;
        min-height: 100vh;
    }}

    /* Typography Styles */
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Quicksand', sans-serif;
        font-weight: 700;
        color: white;
    }}

    /* Button Styling */
    .stButton > button {{
        font-family: 'Quicksand', sans-serif !important;
        font-weight: 600 !important;
        padding: 0.4em 1em !important;
        border: none !important;
        background: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        transition: all 0.3s ease !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
    }}

    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        background: rgba(255, 255, 255, 0.2) !important;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2) !important;
    }}

    /* Primary button style for selected mood */
    .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg,
            {MOOD_MAPPING[st.session_state.selected_mood]["gradient"][0]} 0%,
            {MOOD_MAPPING[st.session_state.selected_mood]["gradient"][1]} 100%
        ) !important;
        box-shadow: 0 4px 12px {MOOD_MAPPING[st.session_state.selected_mood]["gradient"][0]}66 !important;
    }}

    /* Input Field Styling */
    .stTextInput input {{
        background-color: rgba(255, 255, 255, 0.9) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: #333 !important;
        border-radius: 8px !important;
    }}

    /* Selectbox Styling */
    .stSelectbox > div > div {{
        background-color: rgba(255, 255, 255, 0.9) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: #333 !important;
        border-radius: 8px !important;
    }}

    /* Label colors */
    .stTextInput label, .stSelectbox label {{
        color: white !important;
    }}

    /* Sidebar styling */
    .css-1d391kg {{
        background: linear-gradient(to bottom,
            {MOOD_MAPPING[st.session_state.selected_mood]["contrast"]},
            rgba(25, 25, 35, 0.98)
        ) !important;
    }}

    /* Gradient animation */
    @keyframes gradientBG {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}
</style>
""", unsafe_allow_html=True)

# Update the title with new styling
st.markdown(r"""
<div class="title-container">
    <h1 class="main-title">
        <span class="title-emotunes">🎧 EmoTunes</span>
    </h1>
    <div class="subtitle">Mood-Based Music Recommender</div>
</div>
""", unsafe_allow_html=True)

# Create columns for better layout
col1, col2 = st.columns([3, 1])

with col1:
    # Create mood selection buttons in a grid
    st.markdown("""
    <div style='text-align: center; margin: 20px 0;'>
        <h2 style='color: white; margin-bottom: 20px;'>How are you feeling today?</h2>
    </div>
    """, unsafe_allow_html=True)

    # Define the mood grid layout
    moods = {
        "⚡ Energetic": "energetic",
        "💝 Romantic": "romantic",
        "💔 Heartbroken": "heartbroken",
        "🎉 Party": "party",
        "😠 Angry": "angry"
    }

    # Create a single row of 5 mood buttons
    mood_cols = st.columns(5)

    # Display all mood buttons in a single row
    for idx, (mood_text, mood_key) in enumerate(moods.items()):
        with mood_cols[idx]:
            if st.button(
                mood_text,
                key=mood_key,
                use_container_width=True,
                type="primary" if st.session_state.selected_mood == mood_text else "secondary"
            ):
                update_mood(mood_text)

    # Language selection with flags
    language = st.selectbox(
        "Preferred language for music:",
        [
            "🇺🇸 English",
            "🇮🇳 Hindi",
            "🇮🇳 Kannada",
            "🇮🇳 Telugu",
            "🇮🇳 Tamil"
        ],
        format_func=lambda x: x,
        key="language_selector"
    )

    # Search bar with improved styling
    search_query = st.text_input(
        "🔍 Search songs or artists", 
        "", 
        help="Search for your favorite songs or artists",
        key="main_search"  # Adding unique key
    )

# Get the current mood color for dynamic styling
def get_mood_style(selected_mood):
    mood_data = MOOD_MAPPING.get(selected_mood, MOOD_MAPPING["⚡ Energetic"])
    return fr"""
    <style>
    .stApp {{
        background: linear-gradient(
            135deg,
            {mood_data['gradient'][0]}dd 0%,
            {mood_data['gradient'][1]}ee 35%,
            {mood_data['gradient'][2]}dd 65%,
            {mood_data['gradient'][0]}dd 100%
        ) !important;
        background-size: 400% 400% !important;
        animation: gradientBG 20s ease infinite;
        min-height: 100vh;
        -webkit-background-size: 400% 400% !important;
        -moz-background-size: 400% 400% !important;
        -o-background-size: 400% 400% !important;
    }}
    
    /* Enhanced gradient animation */
    @keyframes gradientBG {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    /* Mood-specific particle colors and effects */
    .particle {{
        background: linear-gradient(
            135deg,
            {mood_data['secondary_gradient'][0]},
            {mood_data['secondary_gradient'][1]}
        );
        box-shadow: 
            0 0 20px {mood_data['gradient'][0]}88,
            0 0 40px {mood_data['gradient'][1]}44;
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
    }}

    /* Enhanced mood icon animation */
    .mood-icon {{
        font-size: 4rem;
        animation: float 6s ease-in-out infinite;
        display: inline-block;
        margin: 10px;
        background: linear-gradient(
            135deg,
            {mood_data['gradient'][0]},
            {mood_data['gradient'][1]},
            {mood_data['gradient'][2]}
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 
            0 8px 24px {mood_data['gradient'][0]}88,
            0 0 40px {mood_data['gradient'][1]}66;
        filter: drop-shadow(0 0 8px {mood_data['gradient'][1]}66);
    }}

    /* Smooth hover transitions with mood colors */
    .glass-card {{
        background: linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.08),
            rgba(255, 255, 255, 0.12)
        );
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 25px;
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 
            0 8px 32px 0 rgba(0, 0, 0, 0.1),
            inset 0 0 0 1px rgba(255, 255, 255, 0.05);
    }}

    .glass-card:hover {{
        transform: translateY(-5px) scale(1.02);
        background: linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.12),
            rgba(255, 255, 255, 0.18)
        );
        box-shadow: 
            0 15px 35px rgba(0, 0, 0, 0.2),
            inset 0 0 0 1px rgba(255, 255, 255, 0.1),
            0 0 20px {mood_data['gradient'][0]}33,
            0 0 40px {mood_data['gradient'][1]}22;
    }}

    /* Mobile optimization with enhanced colors */
    @media (max-width: 768px) {{
        .stApp {{
            background: linear-gradient(
                135deg,
                {mood_data['gradient'][0]}ee 0%,
                {mood_data['gradient'][1]}ff 50%,
                {mood_data['gradient'][2]}ee 100%
            ) !important;
            background-size: 300% 300% !important;
            animation: gradientBG 15s ease infinite;
        }}

        .particle {{
            opacity: 0.25 !important;
            mix-blend-mode: screen;
        }}
    }}

    /* Enhanced text effects with mood colors */
    .mood-title {{
        font-size: 3rem;
        font-weight: bold;
        margin: 20px 0;
        background: linear-gradient(
            135deg,
            {mood_data['gradient'][0]},
            {mood_data['gradient'][1]},
            {mood_data['gradient'][2]},
            {mood_data['secondary_gradient'][0]},
            {mood_data['secondary_gradient'][1]}
        );
        background-size: 300% auto;
        animation: shimmer 8s linear infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 
            0 8px 24px {mood_data['gradient'][0]}88,
            0 0 40px {mood_data['gradient'][1]}66;
        filter: drop-shadow(0 0 12px {mood_data['gradient'][1]}44);
    }}

    @keyframes shimmer {{
        0% {{ background-position: 0% center; }}
        100% {{ background-position: 300% center; }}
    }}

    /* Add ambient light effect */
    .ambient-light {{
        position: fixed;
        width: 100%;
        height: 100%;
        top: 0;
        left: 0;
        pointer-events: none;
        background: radial-gradient(
            circle at 50% 50%,
            {mood_data['gradient'][1]}22,
            transparent 80%
        );
        mix-blend-mode: overlay;
        z-index: -1;
        animation: pulse 8s ease-in-out infinite;
    }}

    @keyframes pulse {{
        0%, 100% {{ opacity: 0.5; transform: scale(1); }}
        50% {{ opacity: 0.8; transform: scale(1.1); }}
    }}
    </style>
    <div class="ambient-light"></div>
    <div class="mood-icon icon-pulse">{mood_data['icon']}</div>
    """

# Apply mood-based styling
st.markdown(get_mood_style(st.session_state.selected_mood), unsafe_allow_html=True)

# Display mood quote after mood selection
selected_quote = MOOD_QUOTES.get(st.session_state.selected_mood, "Let the music guide you.")
st.markdown(f'<div class="mood-quote">{selected_quote}</div>', unsafe_allow_html=True)

# Enhanced quotes with animations and better content
quotes = [
    {"text": "Music is the shorthand of emotion.", "author": "Leo Tolstoy", "icon": "🎭"},
    {"text": "Let the music lift your mood!", "author": "EmoTunes", "icon": "🚀"},
    {"text": "Feel the vibe, catch the rhythm.", "author": "EmoTunes", "icon": "🌊"},
    {"text": "Where words fail, music speaks.", "author": "Hans Christian Andersen", "icon": "🎵"},
    {"text": "Music is the universal language of mankind.", "author": "Henry Wadsworth Longfellow", "icon": "🌍"},
    {"text": "Life is a song, love is the music.", "author": "EmoTunes", "icon": "💝"},
    {"text": "Music expresses that which cannot be put into words.", "author": "Victor Hugo", "icon": "✨"},
    {"text": "Music is the poetry of the air.", "author": "Jean Paul Richter", "icon": "🍃"},
    {"text": "Music is the art of thinking with sounds.", "author": "Jules Combarieu", "icon": "🎼"},
    {"text": "Music is the literature of the heart.", "author": "Alphonse de Lamartine", "icon": "📚"}
]

quote = random.choice(quotes)
mood_data = MOOD_MAPPING.get(st.session_state.selected_mood, MOOD_MAPPING["⚡ Energetic"])

st.markdown(fr"""
    <style>
    @keyframes quoteGlow {{
        0% {{ box-shadow: 0 0 20px {mood_data['gradient'][0]}66; }}
        50% {{ box-shadow: 0 0 30px {mood_data['gradient'][1]}88; }}
        100% {{ box-shadow: 0 0 20px {mood_data['gradient'][0]}66; }}
    }}

    .quote-box {{
        position: relative;
        padding: 40px;
        background: linear-gradient(
            135deg,
            {mood_data['gradient'][0]}22,
            {mood_data['gradient'][1]}33
        );
        border-radius: 20px;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        margin: 30px 0;
        border: 2px solid rgba(255, 255, 255, 0.1);
        animation: quoteGlow 4s ease-in-out infinite;
        overflow: hidden;
        box-shadow: 
            0 10px 30px {mood_data['gradient'][0]}33,
            0 5px 15px rgba(0, 0, 0, 0.2);
    }}

    .quote-text {{
        font-family: 'Quicksand', sans-serif;
        font-size: 2rem;
        font-weight: 600;
        line-height: 1.6;
        color: white;
        text-shadow: 
            /* Outline for better contrast */
            -1px -1px 0 {mood_data['contrast']},
            1px -1px 0 {mood_data['contrast']},
            -1px 1px 0 {mood_data['contrast']},
            1px 1px 0 {mood_data['contrast']},
            /* Original glow */
            2px 2px 4px {mood_data['gradient'][0]}99;
        margin-bottom: 20px;
        text-align: center;
        letter-spacing: 0.5px;
    }}

    .quote-author {{
        font-family: 'Poppins', sans-serif;
        font-size: 1.2rem;
        color: {mood_data['gradient'][2]};
        font-weight: 500;
        text-align: center;
        letter-spacing: 1px;
        text-shadow: 
            /* Outline for better contrast */
            -1px -1px 0 {mood_data['contrast']},
            1px -1px 0 {mood_data['contrast']},
            -1px 1px 0 {mood_data['contrast']},
            1px 1px 0 {mood_data['contrast']};
    }}

    .quote-icon {{
        font-size: 3rem;
        margin-bottom: 20px;
        text-align: center;
        color: {mood_data['gradient'][1]};
        text-shadow: 
            /* Outline for better contrast */
            -1px -1px 0 {mood_data['contrast']},
            1px -1px 0 {mood_data['contrast']},
            -1px 1px 0 {mood_data['contrast']},
            1px 1px 0 {mood_data['contrast']},
            /* Original glow */
            0 0 10px {mood_data['gradient'][0]}66;
    }}
    </style>

    <div class="quote-box">
        <div class="quote-icon">{quote['icon']}</div>
        <div class="quote-text">"{quote['text']}"</div>
        <div class="quote-author">- {quote['author']}</div>
    </div>
""", unsafe_allow_html=True)

with col1:
    # Remove duplicate search bar
    if search_query:
        if st.button("Search", key="search_button"):
            with st.spinner("Searching..."):
                results = search_tracks(search_query, token_info=st.session_state.token_info if st.session_state.spotify_auth else None)
                st.session_state.search_results = results

# Display search results if any
if st.session_state.search_results:
    st.markdown(r"""
        <div style='background: rgba(255,255,255,0.1); border-radius: 15px; padding: 20px; backdrop-filter: blur(10px);'>
            <h2 style='color: white; margin-bottom: 20px;'>🔍 Search Results</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Display tracks with enhanced styling and white text
    if st.session_state.search_results['tracks']:
        for track in st.session_state.search_results['tracks']:
            with st.container():
                st.markdown(fr"""
                    <div class='glass-card'>
                        <div style='display: flex; align-items: center; justify-content: space-between;'>
                            <div style='display: flex; align-items: center; gap: 15px;'>
                                <span style='font-size: 1.5rem;'>🎵</span>
                                <div>
                                    <p style='margin: 0; font-weight: bold; font-size: 1.1rem; color: white;'>{track['name']}</p>
                                    <p style='margin: 0; font-size: 0.9rem; opacity: 0.8; color: rgba(255, 255, 255, 0.8);'>{track['artist']}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    if track['preview_url']:
                        st.audio(track['preview_url'])
                        st.markdown("""
                            <div style='
                                padding: 8px 15px;
                                border-radius: 10px;
                                background: rgba(255, 255, 255, 0.1);
                                display: inline-block;
                                font-size: 0.9rem;
                                margin: 5px 0;
                            '>
                                ℹ Preview is limited to 30 seconds - Click "Open in Spotify" for full song
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                            <div style='
                                padding: 8px 15px;
                                border-radius: 10px;
                                background: rgba(255, 255, 255, 0.1);
                                display: inline-block;
                                font-size: 0.9rem;
                                margin: 5px 0;
                            '>
                                ℹ Preview not available - Try opening in Spotify
                            </div>
                        """, unsafe_allow_html=True)
                            
                    st.markdown(f"""
                        <a href='{track["url"]}' target='_blank' style='
                            display: inline-block;
                            padding: 8px 15px;
                            background: #1DB954;
                            color: white;
                            text-decoration: none;
                            border-radius: 20px;
                            font-size: 0.9rem;
                            margin: 5px 0;
                            transition: all 0.3s ease;
                        '>
                            🎵 Open in Spotify
                        </a>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.session_state.spotify_auth:
                        if track['uri'] in st.session_state.saved_tracks:
                            st.markdown("""
                                <div style='
                                    padding: 8px 15px;
                                    border-radius: 20px;
                                    background: rgba(29, 185, 84, 0.2);
                                    color: #1DB954;
                                    display: inline-block;
                                    font-size: 0.9rem;
                                '>
                                    ✅ Saved to Library
                                </div>
                            """, unsafe_allow_html=True)

# Get the actual emotion from the emoji selection
selected_emotion = MOOD_MAPPING[st.session_state.selected_mood]["emotion"]
selected_language = language.split(" ")[1]  # Remove flag emoji

# Button to get music playlists
if st.button("🎵 Get Music Recommendations", help="Find playlists matching your mood"):
    with st.spinner("🔍 Finding the perfect playlists for you..."):
        playlists = get_playlist_for_emotion_and_language(
            selected_emotion,
            selected_language,
            token_info=st.session_state.token_info if st.session_state.spotify_auth else None
        )

    if playlists:
        st.markdown(fr"""
            <div style='text-align: center; margin: 30px 0;'>
                <h2>🎵 Your {selected_emotion.title()} Mood Playlists</h2>
                <div class='progress-bar'></div>
            </div>
        """, unsafe_allow_html=True)
        
        # Create columns for playlist display with enhanced styling
        for i in range(0, len(playlists), 2):
            col1, col2 = st.columns(2)
            
            with col1:
                if i < len(playlists):
                    with st.expander(f"🎵 {playlists[i]['name']}", expanded=True):
                        st.markdown(fr"""
                            <div style='text-align: center;'>
                                <a href='{playlists[i]['url']}' target='_blank' style='
                                    display: inline-block;
                                    padding: 8px 15px;
                                    background: rgba(29, 185, 84, 0.8);
                                    color: white;
                                    text-decoration: none;
                                    border-radius: 20px;
                                    margin: 10px 0;
                                    transition: all 0.3s ease;
                                '>
                                    🔗 Open in Spotify
                                </a>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        if playlists[i]['image']:
                            st.image(playlists[i]['image'], use_container_width=True)
                        if playlists[i].get('description'):
                            st.markdown(fr"""
                                <div style='
                                    padding: 10px;
                                    background: rgba(255,255,255,0.05);
                                    border-radius: 8px;
                                    margin: 10px 0;
                                    color: white;
                                '>
                                    {playlists[i]['description']}
                                </div>
                            """, unsafe_allow_html=True)
                        embed_url = f"https://open.spotify.com/embed/playlist/{playlists[i]['uri'].split(':')[-1]}"
                        st.components.v1.iframe(embed_url, height=80, scrolling=False)
            
            with col2:
                if i + 1 < len(playlists):
                    # Similar enhanced styling for the second column
                    with st.expander(f"🎵 {playlists[i+1]['name']}", expanded=True):
                        st.markdown(fr"""
                            <div style='text-align: center;'>
                                <a href='{playlists[i+1]['url']}' target='_blank' style='
                                    display: inline-block;
                                    padding: 8px 15px;
                                    background: rgba(29, 185, 84, 0.8);
                                    color: white;
                                    text-decoration: none;
                                    border-radius: 20px;
                                    margin: 10px 0;
                                    transition: all 0.3s ease;
                                '>
                                    🔗 Open in Spotify
                                </a>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        if playlists[i+1]['image']:
                            st.image(playlists[i+1]['image'], use_container_width=True)
                        if playlists[i+1].get('description'):
                            st.markdown(fr"""
                                <div style='
                                    padding: 10px;
                                    background: rgba(255,255,255,0.05);
                                    border-radius: 8px;
                                    margin: 10px 0;
                                '>
                                    {playlists[i+1]['description']}
                                </div>
                            """, unsafe_allow_html=True)
                        embed_url = f"https://open.spotify.com/embed/playlist/{playlists[i+1]['uri'].split(':')[-1]}"
                        st.components.v1.iframe(embed_url, height=80, scrolling=False)
    else:
        st.warning("No matching playlists found. Try different settings! 🎵")

# Add custom CSS for the sidebar
st.markdown("""
<style>
    /* Style the entire sidebar */
    .css-1d391kg {
        background: linear-gradient(135deg, rgba(45, 45, 60, 0.9), rgba(30, 30, 40, 0.9)) !important;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
    }

    /* Style sidebar elements container */
    .css-163ttbj {
        background: transparent !important;
    }
    
    /* Style the sidebar content */
    .css-1d391kg > div {
        background: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# Spotify Authentication Section in Sidebar
st.sidebar.markdown(r"""
    <div style='
        background: linear-gradient(135deg, rgba(29, 29, 40, 0.95), rgba(35, 35, 45, 0.95));
        padding: 20px;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        margin-bottom: 20px;
    '>
        <h2 style='
            color: #1DB954;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        '>
            <span>🎵</span> EmoTunes Connections
        </h2>
    </div>
""", unsafe_allow_html=True)

if not st.session_state.spotify_auth:
    auth_url = sp_oauth.get_authorize_url()
    st.sidebar.markdown(r'''
        <div style='
            text-align: center;
            margin: 20px 0;
            background: linear-gradient(135deg, rgba(29, 29, 40, 0.95), rgba(35, 35, 45, 0.95));
            padding: 20px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        '>
            <p style='margin-bottom: 15px; color: #1DB954; font-weight: 600;'>
                Connect your Spotify account to unlock all features:
            </p>
            <ul style='
                list-style: none;
                padding: 0;
                margin-bottom: 20px;
                color: #1DB954;
                font-weight: 500;
            '>
                <li style='margin: 10px 0;'>✓ Save tracks to your library</li>
                <li style='margin: 10px 0;'>✓ Create custom playlists</li>
                <li style='margin: 10px 0;'>✓ Get personalized recommendations</li>
            </ul>
        </div>
    ''', unsafe_allow_html=True)
    
    # Check for auth code in URL
    try:
        code = st.query_params.get('code', None)
        if code:
            code = code[0]
            token_info = sp_oauth.get_access_token(code)
            if token_info:
                st.session_state.token_info = token_info
                st.session_state.spotify_auth = True
                st.success("Successfully connected to Spotify! 🎉")
                st.experimental_rerun()
    except Exception as e:
        st.error(f"Authentication failed: {str(e)} 😔")
else:
    st.sidebar.markdown(r"""
        <div style='
            background: rgba(29,185,84,0.1);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            margin: 20px 0;
        '>
            <span style='
                color: #1DB954;
                font-size: 1.2rem;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
            '>
                ✓ Connected to Spotify
            </span>
        </div>
    """, unsafe_allow_html=True)
    
    # Create playlist section
    st.sidebar.markdown(r"""
        <div style='
            background: rgba(255,255,255,0.05);
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
            color: white;
        '>
            <h3 style='margin-bottom: 15px; color: white;'>Create Playlist</h3>
        </div>
    """, unsafe_allow_html=True)
    
    playlist_name = st.sidebar.text_input(
        "Playlist Name", 
        f"My {st.session_state.selected_mood.split()[1]} Mix",
        key="playlist_name"  # Adding unique key
    )
    playlist_description = st.sidebar.text_area(
        "Description", 
        f"A {st.session_state.selected_mood.split()[1].lower()} playlist created with EmoTunes",
        key="playlist_description"  # Adding unique key
    )
    
    if st.sidebar.button("Create Playlist 🎵"):
        if st.session_state.saved_tracks:
            sp = get_spotify_client(st.session_state.token_info)
            try:
                user_profile = sp.current_user()
                user_id = user_profile['id']
                
                with st.sidebar.spinner("Creating your playlist... 🎵"):
                    playlist = create_playlist(user_id, playlist_name, playlist_description, st.session_state.token_info)
                    if playlist:
                        if add_tracks_to_playlist(playlist['id'], st.session_state.saved_tracks, st.session_state.token_info):
                            st.sidebar.success("Playlist created successfully! 🎉")
                            st.session_state.saved_tracks = []
                            
                            st.sidebar.markdown(fr"""
                                <a href='{playlist["external_urls"]["spotify"]}' target='_blank' style='
                                    display: inline-block;
                                    width: 100%;
                                    padding: 10px;
                                    background: #1DB954;
                                    color: white;
                                    text-align: center;
                                    text-decoration: none;
                                    border-radius: 20px;
                                    margin: 10px 0;
                                '>
                                    Open Playlist in Spotify 🎵
                                </a>
                            """, unsafe_allow_html=True)
                        else:
                            st.sidebar.error("Failed to add tracks to playlist 😔")
                    else:
                        st.sidebar.error("Failed to create playlist 😔")
            except Exception as e:
                st.sidebar.error(f"Error: {str(e)} 😔")
        else:
            st.sidebar.warning("Save some tracks first! 🎵")
    
    if st.sidebar.button("Disconnect from Spotify"):
        st.session_state.spotify_auth = False
        st.session_state.token_info = None
        st.session_state.saved_tracks = []
        st.experimental_rerun()

# Fun button for balloons animation with enhanced styling
if st.button("✨ Spark Another Vibe!", help="Click for a surprise!"):
    st.balloons()
    st.markdown(r"""
        <div style='
            background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.2));
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            animation: float 3s ease-in-out infinite;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
            margin: 20px 0;
        '>
            <h3 style='margin: 0; color: white;'>
                ✨ Yay! Keep the good vibes flowing! ✨
            </h3>
        </div>
    """, unsafe_allow_html=True)

# Add custom CSS to ensure emojis stay visible
st.markdown("""
<style>
    /* Ensure emojis are visible in buttons */
    .stButton button {
        font-family: "Segoe UI Emoji", "Noto Color Emoji", "Apple Color Emoji", "Segoe UI Symbol", "Android Emoji", "EmojiSymbols" !important;
        font-size: 1rem !important;
    }
    
    /* Improve button appearance */
    .stButton button {
        min-height: 45px !important;
        white-space: normal !important;
        height: auto !important;
        padding: 8px 16px !important;
    }
    
    /* Make selected button more visible */
    .stButton button[kind="primary"] {
        border: 2px solid white !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)      
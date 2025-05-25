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

# Custom CSS for modern styling with enhanced blur and softer transitions
st.markdown(r"""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Quicksand:wght@400;500;600;700&family=Comfortaa:wght@400;500;600;700&display=swap');

    /* Base Font Settings */
    * {
        font-family: 'Poppins', sans-serif;
    }

    /* Modern Card Styling with enhanced depth */
    .stApp {
        font-family: 'Poppins', sans-serif;
        background: rgba(255, 255, 255, 0.02) !important;
        background-attachment: fixed !important;
        -webkit-background-size: cover !important;
        -moz-background-size: cover !important;
        -o-background-size: cover !important;
        background-size: cover !important;
        position: relative;
        overflow: hidden;
    }

    /* Typography Styles */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Quicksand', sans-serif;
        font-weight: 700;
        letter-spacing: 0.5px;
    }

    .stSelectbox label, .stTextInput label {
        font-family: 'Poppins', sans-serif;
        font-weight: 500 !important;
        letter-spacing: 0.3px;
    }

    p, div {
        font-family: 'Poppins', sans-serif;
        font-weight: 400;
    }

    /* Enhanced floating particles effect with music notes */
    @keyframes float-particles {
        0%, 100% { transform: translateY(0) translateX(0) rotate(0deg); opacity: 0.3; }
        25% { transform: translateY(-20px) translateX(10px) rotate(5deg); opacity: 0.6; }
        50% { transform: translateY(-35px) translateX(-10px) rotate(-5deg); opacity: 0.8; }
        75% { transform: translateY(-20px) translateX(15px) rotate(3deg); opacity: 0.6; }
    }

    .particle {
        position: fixed;
        width: 24px;
        height: 24px;
        pointer-events: none;
        opacity: 0.3;
        z-index: -1;
        filter: blur(1px);
        font-family: 'Arial Unicode MS', sans-serif;
        content: '♪';
        color: rgba(255, 255, 255, 0.6);
        font-size: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .particle::before {
        content: '♪';
        position: absolute;
    }

    /* Accent Colors */
    .accent-teal {
        color: #4ECDC4 !important;
    }

    .accent-lavender {
        color: #9D84B7 !important;
    }

    /* Button Styling */
    .stButton button {
        font-family: 'Quicksand', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        padding: 0.6em 1.2em !important;
        background: linear-gradient(135deg, #4ECDC4, #9D84B7) !important;
        border: none !important;
        color: white !important;
        transition: all 0.3s ease !important;
    }

    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(78, 205, 196, 0.3) !important;
    }

    /* Dropdown Styling */
    .stSelectbox > div > div {
        font-family: 'Poppins', sans-serif !important;
        font-weight: 500 !important;
    }

    /* Input Field Styling */
    .stTextInput input {
        color: #000000 !important;  /* Black text */
        font-weight: 500 !important;
        background-color: rgba(255, 255, 255, 0.9) !important;  /* More opaque white background */
        border: 1px solid rgba(157, 132, 183, 0.3) !important;
    }
    
    .stTextInput input::placeholder {
        color: rgba(0, 0, 0, 0.5) !important;  /* Dark gray for placeholder */
    }
    
    .stTextInput input:focus {
        border-color: #9D84B7 !important;
        box-shadow: 0 0 0 1px #9D84B7 !important;
    }

    /* Container Styling */
    .glass-container {
        font-family: 'Poppins', sans-serif;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    /* Title Container */
    .title-container {
        font-family: 'Quicksand', sans-serif;
        text-align: center;
        margin: 2rem auto;
        padding: 0.5rem;
        position: relative;
        max-width: 800px;
    }

    .main-title {
        font-family: 'Quicksand', sans-serif;
        font-size: 3.2rem;
        font-weight: 700;
        color: #FFFFFF;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin: 0;
        padding: 0.5rem 1rem;
        position: relative;
        display: inline-block;
        text-shadow: 2px 2px 0 rgba(0, 0, 0, 0.2);
    }

    .title-emotunes {
        background: linear-gradient(
            to right,
            #FF6B6B,
            #4ECDC4,
            #9D84B7,
            #FF6B6B
        );
        background-size: 300% auto;
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        animation: shine 8s linear infinite;
        font-size: 3.5rem;
        font-weight: 800;
        letter-spacing: 2px;
        display: inline-block;
        padding: 0.2em;
        position: relative;
    }

    @keyframes shine {
        0% { background-position: 0% center; }
        100% { background-position: 300% center; }
    }

    .subtitle {
        font-family: 'Poppins', sans-serif;
        font-size: 1.4rem;
        font-weight: 500;
        color: rgba(255, 255, 255, 0.9);
        margin-top: 0.5rem;
        letter-spacing: 1px;
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.5rem;
        }
        .subtitle {
            font-size: 1.2rem;
        }
    }

    /* Animated Title Effect */
    .title-emotunes {
        background: linear-gradient(
            to right,
            #FF6B6B,
            #4ECDC4,
            #9D84B7,
            #FF6B6B
        );
        background-size: 300% auto;
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        animation: shine 8s linear infinite;
        font-size: 3.5rem;
        font-weight: 800;
        letter-spacing: 2px;
        display: inline-block;
        padding: 0.2em;
        position: relative;
    }

    @keyframes shine {
        0% { background-position: 0% center; }
        100% { background-position: 300% center; }
    }

    /* Enhanced Hover Effects */
    .stButton > button {
        transform: scale(1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
    }

    .stButton > button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.2) !important;
    }

    .stSelectbox > div {
        transition: all 0.3s ease !important;
    }

    .stSelectbox > div:hover {
        transform: translateY(-2px);
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    }

    /* Spotify Connect Section */
    .spotify-connect-card {
        background: rgba(25, 20, 20, 0.9);
        border-radius: 12px;
        padding: 24px;
        margin: 20px 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        animation: glow 2s ease-in-out infinite;
        position: relative;
        overflow: hidden;
    }

    .spotify-connect-card::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #1DB954, #191414);
        z-index: -1;
        animation: borderGlow 3s ease-in-out infinite;
        border-radius: 13px;
    }

    .spotify-button {
        background: #1DB954 !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        border-radius: 25px !important;
        border: none !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 8px !important;
        transition: all 0.3s ease !important;
    }

    .spotify-button:hover {
        background: #1ed760 !important;
        box-shadow: 0 0 20px rgba(29, 185, 84, 0.4) !important;
    }

    /* Mood Quote Styling */
    .mood-quote {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 15px 25px;
        border-radius: 12px;
        margin: 15px 0;
        font-family: 'Quicksand', sans-serif;
        font-weight: 500;
        font-size: 1.1rem;
        color: white;
        text-align: center;
        position: relative;
        overflow: hidden;
    }

    .mood-quote::before {
        content: '"';
        position: absolute;
        left: 10px;
        top: 5px;
        font-size: 3rem;
        opacity: 0.2;
        font-family: Georgia, serif;
    }

    .mood-quote::after {
        content: '"';
        position: absolute;
        right: 10px;
        bottom: -10px;
        font-size: 3rem;
        opacity: 0.2;
        font-family: Georgia, serif;
    }

    /* Loading Animation */
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .loader {
        width: 50px;
        height: 50px;
        border: 3px solid rgba(255,255,255,0.3);
        border-radius: 50%;
        border-top-color: #fff;
        animation: spin 1s ease-in-out infinite;
        margin: 20px auto;
    }

    .loading-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 15px;
    }

    .music-note {
        font-size: 24px;
        animation: bounce 1s ease infinite;
    }

    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }

    @keyframes borderGlow {
        0%, 100% { opacity: 0.5; }
        50% { opacity: 1; }
    }

    /* Enhanced Glassmorphism */
    .glass-card {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: 20px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    transition: all 0.3s ease;
    color: white;
        color: white;
    }

    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }

    /* Make text inputs and labels visible */
    .stTextInput label, .stSelectbox label, .stTextArea label {
        color: white !important;
    }
    
    .stTextInput input, .stSelectbox select, .stTextArea textarea {
        color: white !important;
        background-color: rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Make dropdown options visible */
    .stSelectbox select option {
        background-color: #2C3338 !important;
        color: white !important;
    }
    
    /* Make all regular text white */
    .stMarkdown, .stText {
        color: white !important;
    }

    /* Override Streamlit's default styles with higher specificity */
    div[data-baseweb="input"] input[type="text"],
    div[data-baseweb="input"] input {
        color: black !important;
        background-color: white !important;
        font-weight: 500 !important;
        border: 2px solid #9D84B7 !important;
    }

    /* Style placeholder text */
    div[data-baseweb="input"] input::placeholder {
        color: #666666 !important;
        opacity: 1 !important;
    }

    /* Style the input when focused */
    div[data-baseweb="input"]:focus-within input {
        border-color: #9D84B7 !important;
        box-shadow: 0 0 0 2px #9D84B7 !important;
    }

    /* Ensure label remains visible */
    div[data-baseweb="input"] + label {
        color: white !important;
    }
</style>

<!-- Add floating music note particles -->
<div class="particle-container">
    <div class="particle">♪</div>
    <div class="particle">♫</div>
    <div class="particle">♩</div>
    <div class="particle">♪</div>
    <div class="particle">♫</div>
    <div class="particle">♬</div>
</div>
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

# Define mood mappings with emojis and mesmerizing color combinations
MOOD_MAPPING = {
    "😊 Happy": {
        "emotion": "happy",
        "color": "#FF7E5F",  # Warm coral
        "gradient": ["#FEB47B", "#FF7E5F", "#FF5E62"],  # Sunset gradient
        "secondary_gradient": ["#FFD141", "#FF8C42"],  # Golden accent
        "contrast": "#2A2A3C",  # Deep slate
        "icon": "🌟"
    },
    "😢 Sad": {
        "emotion": "sad",
        "color": "#5B86E5",  # Royal blue
        "gradient": ["#36D1DC", "#5B86E5", "#3657DC"],  # Ocean depths
        "secondary_gradient": ["#5F72BE", "#9921E8"],  # Twilight accent
        "contrast": "#1A1A2E",  # Night blue
        "icon": "🌧"
    },
    "😠 Angry": {
        "emotion": "angry",
        "color": "#FF5757",  # Passionate red
        "gradient": ["#FF5757", "#8C1F1F", "#D92B2B"],  # Deep crimson
        "secondary_gradient": ["#FF8C42", "#FF5757"],  # Fire accent
        "contrast": "#2D142C",  # Deep purple
        "icon": "⚡"
    },
    "😌 Calm": {
        "emotion": "calm",
        "color": "#43CEA2",  # Serene teal
        "gradient": ["#43CEA2", "#185A9D", "#43CEA2"],  # Ocean breeze
        "secondary_gradient": ["#96FBC4", "#43CEA2"],  # Mint accent
        "contrast": "#1A2C38",  # Deep teal
        "icon": "🍃"
    },
    "😐 Neutral": {
        "emotion": "neutral",
        "color": "#8E9EAB",  # Cool gray
        "gradient": ["#8E9EAB", "#414345", "#8E9EAB"],  # Misty mountain
        "secondary_gradient": ["#D3CCE3", "#8E9EAB"],  # Fog accent
        "contrast": "#2C3338",  # Charcoal
        "icon": "🌈"
    }
}

# Define mood-specific quotes
MOOD_QUOTES = {
    "😊 Happy": "Turn up the volume, it's a good day!",
    "😢 Sad": "Even the rain needs a melody.",
    "😠 Angry": "Let the music calm your storm.",
    "😌 Calm": "Float away on waves of harmony.",
    "😐 Neutral": "Find your rhythm in the everyday."
}

# Create columns for better layout
col1, col2 = st.columns([2, 1])

with col1:
    # Emoji mood selection
    selected_mood = st.selectbox(
        "How are you feeling today?",
        list(MOOD_MAPPING.keys()),
        format_func=lambda x: x  # Show emojis in dropdown
    )

# Get the current mood color for dynamic styling
def get_mood_style(selected_mood):
    mood_data = MOOD_MAPPING.get(selected_mood, MOOD_MAPPING["😐 Neutral"])
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
st.markdown(get_mood_style(selected_mood), unsafe_allow_html=True)

# Display mood quote after mood selection
selected_quote = MOOD_QUOTES.get(selected_mood, "Let the music guide you.")
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
mood_data = MOOD_MAPPING.get(selected_mood, MOOD_MAPPING["😐 Neutral"])

st.markdown(fr"""
    <style>
    @keyframes gradientMove {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    @keyframes borderGlow {{
        0% {{
            border-color: {mood_data['gradient'][0]};
            box-shadow: 0 0 20px {mood_data['gradient'][0]}66;
        }}
        50% {{
            border-color: {mood_data['gradient'][1]};
            box-shadow: 0 0 30px {mood_data['gradient'][1]}88;
        }}
        100% {{
            border-color: {mood_data['gradient'][0]};
            box-shadow: 0 0 20px {mood_data['gradient'][0]}66;
        }}
    }}

    @keyframes textGlow {{
        0% {{
            text-shadow: 0 0 10px {mood_data['gradient'][0]};
            color: {mood_data['gradient'][0]};
        }}
        50% {{
            text-shadow: 0 0 20px {mood_data['gradient'][1]};
            color: {mood_data['gradient'][1]};
        }}
        100% {{
            text-shadow: 0 0 10px {mood_data['gradient'][0]};
            color: {mood_data['gradient'][0]};
        }}
    }}
    </style>

    <div style='
        position: relative;
        padding: 40px;
        background: {mood_data['contrast']};
        border-radius: 20px;
        backdrop-filter: blur(10px);
        margin: 30px 0;
        border: 3px solid {mood_data['gradient'][0]};
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.3);
        overflow: hidden;
        animation: borderGlow 4s ease-in-out infinite;
    '>
        <div style='
            position: absolute;
            top: -20px;
            right: -20px;
            font-size: 100px;
            opacity: 0.05;
            transform: rotate(10deg);
            animation: float 6s ease-in-out infinite;
            color: {mood_data['gradient'][1]};
        '>
            {quote['icon']}
        </div>
        <div style='
            position: relative;
            z-index: 1;
            text-align: center;
        '>
            <div style='
                font-size: 3rem;
                margin-bottom: 25px;
                animation: textGlow 4s ease-in-out infinite;
                background: linear-gradient(45deg, {mood_data['gradient'][0]}, {mood_data['gradient'][1]});
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-shadow: 0 0 20px {mood_data['gradient'][1]}88;
            '>
                {quote['icon']}
            </div>
            <p style='
                font-size: 1.6rem;
                font-style: italic;
                margin-bottom: 20px;
                line-height: 1.6;
                color: {mood_data['gradient'][1]};
                text-shadow: 2px 2px 4px {mood_data['contrast']};
                font-weight: 500;
            '>"{quote['text']}"</p>
            <div style='
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 15px;
                margin-top: 25px;
            '>
                <div style='
                    width: 50px;
                    height: 3px;
                    background: linear-gradient(90deg, {mood_data['contrast']}, {mood_data['gradient'][0]});
                '></div>
                <p style='
                    font-size: 1.1rem;
                    color: {mood_data['gradient'][0]};
                    font-weight: 600;
                    letter-spacing: 1px;
                '>- {quote['author']}</p>
                <div style='
                    width: 50px;
                    height: 3px;
                    background: linear-gradient(90deg, {mood_data['gradient'][1]}, {mood_data['contrast']});
                '></div>
            </div>
        </div>
        <div style='
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(90deg, 
                {mood_data['gradient'][0]}, 
                {mood_data['gradient'][1]}, 
                {mood_data['gradient'][0]}
            );
            animation: gradientMove 6s ease infinite;
            background-size: 200% 200%;
        '></div>
    </div>
""", unsafe_allow_html=True)

with col1:
    # Language selection with flags
    language = st.selectbox(
        "Preferred language for music:",
        ["🇺🇸 English", "🇮🇳 Hindi", "🇮🇳 Kannada"],
        format_func=lambda x: x
    )

with col2:
    # Search bar for songs/artists with custom styling
    search_query = st.text_input("🔍 Search songs or artists", "", 
        help="Search for your favorite songs or artists")

# Handle search functionality
if search_query:
    if st.button("Search"):
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
                        else:
                            if st.button("💚 Save", key=f"save_{track['uri']}", help="Save to your library"):
                                if save_track_to_library(track['uri'], st.session_state.token_info):
                                    st.success("Track saved! 🎉")
                                    st.session_state.saved_tracks.append(track['uri'])
                                else:
                                    st.error("Failed to save track 😔")

# Get the actual emotion from the emoji selection
selected_emotion = MOOD_MAPPING[selected_mood]["emotion"]
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
                            st.image(playlists[i]['image'], use_column_width=True)
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
                            st.image(playlists[i+1]['image'], use_column_width=True)
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

# Spotify Authentication Section in Sidebar
st.sidebar.markdown(r"""
    <div style='
        background: linear-gradient(135deg, rgba(29,185,84,0.1) 0%, rgba(29,185,84,0.2) 100%);
        padding: 20px;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(29,185,84,0.2);
    '>
        <h2 style='
            color: #1DB954;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        '>
            <span>🎵</span> Spotify Connection
        </h2>
    </div>
""", unsafe_allow_html=True)

if not st.session_state.spotify_auth:
    auth_url = sp_oauth.get_authorize_url()
    st.sidebar.markdown(r'''
        <div style='text-align: center; margin: 20px 0;'>
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
            <a href="{auth_url}" target="_self">
                <button style="
                    background-color: #1DB954;
                    color: white;
                    padding: 12px 24px;
                    border: none;
                    border-radius: 24px;
                    cursor: pointer;
                    font-weight: bold;
                    width: 100%;
                    margin: 8px 0;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 10px;
                    transition: all 0.3s ease;
                ">
                    <span>🔗</span> Connect with Spotify
                </button>
            </a>
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
    
    # Create playlist section with enhanced styling
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
    
    playlist_name = st.sidebar.text_input("Playlist Name", f"My {selected_emotion} Mix")
    playlist_description = st.sidebar.text_area("Description", f"A {selected_emotion} playlist created with EmoTunes")
    
    if st.sidebar.button("Create Playlist 🎵", help="Create a new playlist with your saved tracks"):
        if st.session_state.saved_tracks:
            sp = get_spotify_client(st.session_state.token_info)
            try:
                # Get current user's ID
                user_profile = sp.current_user()
                user_id = user_profile['id']
                
                # Create playlist with progress bar
                with st.sidebar.spinner("Creating your playlist... 🎵"):
                    playlist = create_playlist(user_id, playlist_name, playlist_description, st.session_state.token_info)
                    if playlist:
                        # Add tracks to playlist
                        if add_tracks_to_playlist(playlist['id'], st.session_state.saved_tracks, st.session_state.token_info):
                            st.sidebar.success("Playlist created successfully! 🎉")
                            st.session_state.saved_tracks = []  # Clear saved tracks
                            
                            # Display playlist link
                            st.sidebar.markdown(fr"""
                                <a href='{playlist['external_urls']['spotify']}' target='_blank' style='
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
    
    if st.sidebar.button("Disconnect from Spotify", help="Disconnect your Spotify account"):
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
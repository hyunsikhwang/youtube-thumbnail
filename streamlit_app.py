import streamlit as st
import requests
from urllib.parse import urlparse, parse_qs
import re

st.set_page_config(
    page_title="YouTube Thumbnail Extractor",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for minimal light vivid glow design
st.markdown("""
<style>
    /* Light theme colors */
    :root {
        --primary-glow: #0066ff;
        --secondary-glow: #ff0066;
        --accent-glow: #00cc66;
        --bg-light: #fafafa;
        --bg-card: #ffffff;
        --bg-gradient: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        --text-primary: #2c3e50;
        --text-secondary: #6c757d;
        --border-light: #dee2e6;
        --shadow-light: rgba(0, 0, 0, 0.1);
        --shadow-glow: rgba(0, 102, 255, 0.3);
    }
    
    /* Global styles */
    .stApp {
        background: var(--bg-gradient);
        color: var(--text-primary);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Glow effect for title */
    .main-title {
        text-align: center;
        font-size: clamp(2.5rem, 5vw, 4rem);
        font-weight: 800;
        background: linear-gradient(45deg, var(--primary-glow), var(--secondary-glow));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        animation: glow-pulse 3s ease-in-out infinite alternate;
        letter-spacing: -0.02em;
    }
    
    @keyframes glow-pulse {
        from { 
            filter: drop-shadow(0 0 15px rgba(0, 102, 255, 0.4));
            transform: scale(1);
        }
        to { 
            filter: drop-shadow(0 0 25px rgba(255, 0, 102, 0.4));
            transform: scale(1.01);
        }
    }
    
    /* Subtitle */
    .subtitle {
        text-align: center;
        font-size: clamp(1rem, 2vw, 1.25rem);
        color: var(--text-secondary);
        margin-bottom: 3rem;
        font-weight: 400;
    }
    
    /* Main container */
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 2rem;
    }
    
    /* Responsive grid */
    .content-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 2rem;
        align-items: start;
    }
    
    @media (min-width: 768px) {
        .content-grid {
            grid-template-columns: 1fr 1fr;
            gap: 3rem;
        }
    }
    
    @media (min-width: 1024px) {
        .content-grid {
            grid-template-columns: 1fr 400px;
            gap: 4rem;
        }
    }
    
    /* Input section styling */
    .input-section {
        background: var(--bg-card);
        border-radius: 20px;
        padding: 2.5rem;
        box-shadow: 0 10px 30px var(--shadow-light);
        border: 1px solid var(--border-light);
        transition: all 0.3s ease;
    }
    
    .input-section:hover {
        box-shadow: 0 15px 40px var(--shadow-glow);
        transform: translateY(-2px);
    }
    
    /* Input field styling */
    .stTextInput > div > div > input {
        background: var(--bg-light);
        border: 2px solid var(--border-light);
        border-radius: 15px;
        color: var(--text-primary);
        font-size: 1.1rem;
        padding: 18px 24px;
        transition: all 0.3s ease;
        width: 100%;
        box-sizing: border-box;
    }
    
    .stTextInput > div > div > input:focus {
        outline: none;
        border-color: var(--primary-glow);
        box-shadow: 0 0 0 4px rgba(0, 102, 255, 0.1);
        background: var(--bg-card);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, var(--primary-glow), var(--secondary-glow));
        border: none;
        border-radius: 15px;
        color: white;
        font-weight: 700;
        font-size: 1.1rem;
        padding: 18px 40px;
        transition: all 0.3s ease;
        cursor: pointer;
        box-shadow: 0 8px 25px rgba(0, 102, 255, 0.3);
        width: 100%;
        margin-top: 1rem;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(0, 102, 255, 0.4);
        background: linear-gradient(45deg, #0052cc, #cc0052);
    }
    
    /* Results section */
    .results-section {
        background: var(--bg-card);
        border-radius: 20px;
        padding: 2.5rem;
        box-shadow: 0 10px 30px var(--shadow-light);
        border: 1px solid var(--border-light);
        transition: all 0.3s ease;
        min-height: 400px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    
    .results-section:hover {
        box-shadow: 0 15px 40px var(--shadow-glow);
    }
    
    /* Success message styling */
    .stSuccess {
        background: rgba(0, 204, 102, 0.1);
        border: 1px solid rgba(0, 204, 102, 0.3);
        border-radius: 12px;
        color: var(--text-primary);
        font-weight: 500;
    }
    
    /* Error message styling */
    .stError {
        background: rgba(255, 77, 77, 0.1);
        border: 1px solid rgba(255, 77, 77, 0.3);
        border-radius: 12px;
        color: var(--text-primary);
        font-weight: 500;
    }
    
    /* Warning message styling */
    .stWarning {
        background: rgba(255, 193, 7, 0.1);
        border: 1px solid rgba(255, 193, 7, 0.3);
        border-radius: 12px;
        color: var(--text-primary);
        font-weight: 500;
    }
    
    /* Video title styling */
    .video-title {
        font-size: clamp(1.25rem, 2.5vw, 1.75rem);
        font-weight: 700;
        color: var(--text-primary);
        margin: 1.5rem 0;
        text-align: center;
        line-height: 1.4;
    }
    
    /* Image styling */
    .stImage > img {
        border-radius: 15px;
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        max-width: 100%;
        height: auto;
    }
    
    .stImage > img:hover {
        box-shadow: 0 20px 50px rgba(0, 102, 255, 0.2);
        transform: scale(1.02);
    }
    
    /* Download button styling */
    .stDownloadButton > button {
        background: linear-gradient(45deg, var(--accent-glow), #00aa55);
        border: none;
        border-radius: 12px;
        color: white;
        font-weight: 700;
        padding: 15px 30px;
        transition: all 0.3s ease;
        cursor: pointer;
        box-shadow: 0 6px 20px rgba(0, 204, 102, 0.3);
        width: 100%;
        margin: 1rem 0;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 204, 102, 0.4);
        background: linear-gradient(45deg, #00aa55, #008844);
    }
    
    /* Twitter share button styling */
    .twitter-share-btn {
        background: linear-gradient(45deg, #000000, #434343);
        border: 2px solid var(--primary-glow);
        border-radius: 12px;
        color: white;
        font-weight: 700;
        padding: 15px 30px;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        transition: all 0.3s ease;
        cursor: pointer;
        box-shadow: 0 6px 20px rgba(0, 102, 255, 0.2);
        width: 100%;
        margin: 1rem 0;
        font-size: 1rem;
    }
    
    .twitter-share-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 102, 255, 0.3);
        background: linear-gradient(45deg, #434343, #000000);
        border-color: var(--secondary-glow);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.8);
        border: 1px solid var(--border-light);
        border-radius: 10px;
        color: var(--text-primary);
        font-weight: 500;
    }
    
    .streamlit-expanderContent {
        background: rgba(255, 255, 255, 0.6);
        border-radius: 0 0 10px 10px;
        border: 1px solid var(--border-light);
        border-top: none;
    }
    
    /* Code block styling */
    .stCodeBlock {
        background: rgba(248, 249, 250, 0.9);
        border: 1px solid var(--border-light);
        border-radius: 10px;
        color: var(--text-primary);
    }
    
    /* Instructions styling */
    .instructions {
        background: rgba(0, 102, 255, 0.05);
        border: 1px solid rgba(0, 102, 255, 0.1);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 2rem 0;
    }
    
    .instructions h3 {
        color: var(--primary-glow);
        margin-bottom: 1rem;
        font-size: 1.25rem;
    }
    
    .instructions ul {
        margin-left: 1rem;
        color: var(--text-secondary);
        line-height: 1.6;
    }
    
    .instructions li {
        margin-bottom: 0.5rem;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        color: var(--text-secondary);
        margin-top: 4rem;
        padding: 2rem;
        border-top: 1px solid var(--border-light);
        font-size: 0.9rem;
    }
    
    /* Loading state */
    .loading {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 3rem;
        color: var(--text-secondary);
    }
    
    .loading-spinner {
        width: 40px;
        height: 40px;
        border: 4px solid var(--border-light);
        border-top: 4px solid var(--primary-glow);
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-bottom: 1rem;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 3rem 1rem;
        color: var(--text-secondary);
    }
    
    .empty-state-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        opacity: 0.5;
    }
    
    .empty-state-text {
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    
    .empty-state-subtext {
        font-size: 0.9rem;
        opacity: 0.7;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main-container {
            padding: 0 1rem;
        }
        
        .input-section,
        .results-section {
            padding: 1.5rem;
        }
        
        .stButton > button,
        .stDownloadButton > button,
        .twitter-share-btn {
            padding: 15px 20px;
            font-size: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

def extract_video_id(youtube_url):
    """유튜브 URL에서 비디오 ID를 추출하는 함수"""
    patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([^&]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([^?]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/v/([^?]+)',
        r'(?:https?://)?youtu\.be/([^?]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/shorts/([^?]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)
    
    try:
        parsed_url = urlparse(youtube_url)
        if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
            return parse_qs(parsed_url.query).get('v', [None])[0]
        elif parsed_url.hostname == 'youtu.be':
            return parsed_url.path.strip('/')
    except:
        pass
    
    return None

def get_video_title(video_id):
    """유튜브 비디오 제목을 가져오는 함수"""
    try:
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        response = requests.get(oembed_url)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('title', 'Unknown Title')
        else:
            return 'Unknown Title'
    except Exception as e:
        return 'Unknown Title'

def get_thumbnail_url(video_id):
    """비디오 ID로 썸네일 URL을 생성하는 함수"""
    if not video_id:
        return None
    return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

def create_twitter_share_url(video_title, video_url):
    """X.com 공유 URL 생성"""
    encoded_title = video_title.replace(" ", "%20").replace("\"", "%22").replace("'", "%27")
    encoded_url = video_url.replace(":", "%3A").replace("/", "%2F")
    return f"https://x.com/intent/post?text={encoded_title}&url={encoded_url}"

# Main title with glow effect
st.markdown('<h1 class="main-title">🎬 YouTube Thumbnail Extractor</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Extract high-quality thumbnails from any YouTube video</p>', unsafe_allow_html=True)

# Main container
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Content grid
st.markdown('<div class="content-grid">', unsafe_allow_html=True)

# Input section
st.markdown('<div class="input-section">', unsafe_allow_html=True)

st.markdown('<h3 style="margin-bottom: 1.5rem; color: var(--text-primary);">🔗 Enter YouTube URL</h3>', unsafe_allow_html=True)

# URL input with responsive width
youtube_url = st.text_input(
    "YouTube URL",
    placeholder="https://www.youtube.com/watch?v=...",
    label_visibility="collapsed"
)

# Extract button
cols = st.columns([1, 2, 1])
with cols[1]:
    extract_button = st.button("✨ Extract Thumbnail", type="primary", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)  # Close input-section

# Results section
st.markdown('<div class="results-section">', unsafe_allow_html=True)

if extract_button:
    if youtube_url:
        with st.spinner("Extracting thumbnail..."):
            # 비디오 ID 추출
            video_id = extract_video_id(youtube_url)
            
            if video_id:
                # 비디오 제목 가져오기
                video_title = get_video_title(video_id)
                
                # 썸네일 URL 생성
                thumbnail_url = get_thumbnail_url(video_id)
                
                try:
                    # 썸네일 이미지 표시
                    response = requests.get(thumbnail_url)
                    if response.status_code == 200:
                        st.success("✅ Thumbnail extracted successfully!")
                        
                        # 비디오 제목 표시
                        st.markdown(f'<h3 class="video-title">📹 {video_title}</h3>', unsafe_allow_html=True)
                        
                        # 썸네일 표시
                        st.image(thumbnail_url, caption=f"Thumbnail for: {video_title}", use_column_width=True)
                        
                        # Action buttons in columns
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # 다운로드 버튼
                            st.download_button(
                                label="📥 Download",
                                data=response.content,
                                file_name=f"youtube_thumbnail_{video_id}.jpg",
                                mime="image/jpeg",
                                help="Download the thumbnail image",
                                use_container_width=True
                            )
                        
                        with col2:
                            # X.com 공유 버튼
                            twitter_share_url = create_twitter_share_url(video_title, youtube_url)
                            st.markdown(f"""
                                <a href="{twitter_share_url}" target="_blank" class="twitter-share-btn">
                                    <span>🐦</span>
                                    Share on X
                                </a>
                            """, unsafe_allow_html=True)
                        
                        # 썸네일 URL 표시
                        with st.expander("🔗 Show Thumbnail URL"):
                            st.code(thumbnail_url, language=None)
                            
                    else:
                        st.error("❌ Failed to load thumbnail. Please check the URL.")
                        
                except Exception as e:
                    st.error(f"❌ Error loading thumbnail: {str(e)}")
            else:
                st.error("❌ Invalid YouTube URL. Please check the format.")
    else:
        st.warning("⚠️ Please enter a YouTube URL.")
else:
    # Empty state
    st.markdown('''
        <div class="empty-state">
            <div class="empty-state-icon">🎥</div>
            <div class="empty-state-text">Enter a YouTube URL to get started</div>
            <div class="empty-state-subtext">Supports all YouTube video formats</div>
        </div>
    ''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # Close results-section
st.markdown('</div>', unsafe_allow_html=True)  # Close content-grid

# Instructions
div class="instructions">
    st.markdown("<h3>📖 How to Use</h3>", unsafe_allow_html=True)
    st.markdown("""
    <ul>
        <li><strong>Enter YouTube URL:</strong> Copy and paste any YouTube video URL</li>
        <li><strong>Click Extract:</strong> Press the 'Extract Thumbnail' button</li>
        <li><strong>View Results:</strong> See the video title and thumbnail</li>
        <li><strong>Download:</strong> Click 'Download' to save the image</li>
        <li><strong>Share:</strong> Click 'Share on X' to post on X/Twitter</li>
    </ul>
    """)
    
    with st.expander("🔗 Supported URL Formats"):
        st.markdown("""
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://www.youtube.com/shorts/VIDEO_ID
        - https://www.youtube.com/embed/VIDEO_ID
        """)

# 푸터
st.markdown("""
<div class="footer">
    <p><strong>✨ YouTube Thumbnail Extractor ✨</strong></p>
    <p>High-quality thumbnails • Real video titles • Cross-platform sharing</p>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # Close main-container
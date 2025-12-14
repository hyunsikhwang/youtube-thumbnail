import streamlit as st
import requests
from urllib.parse import urlparse, parse_qs
import re
import json

st.set_page_config(
    page_title="YouTube Thumbnail Extractor",
    page_icon="🎥",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for minimal vivid glow design
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-glow: #00ffff;
        --secondary-glow: #ff00ff;
        --accent-glow: #ffff00;
        --bg-dark: #0a0a0a;
        --bg-card: #1a1a1a;
        --text-primary: #ffffff;
        --text-secondary: #cccccc;
    }
    
    /* Global styles */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
        color: var(--text-primary);
    }
    
    /* Glow effect for title */
    .main-title {
        text-align: center;
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(45deg, var(--primary-glow), var(--secondary-glow));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 0 0 30px rgba(0, 255, 255, 0.5);
        margin-bottom: 2rem;
        animation: glow-pulse 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow-pulse {
        from { filter: drop-shadow(0 0 20px rgba(0, 255, 255, 0.8)); }
        to { filter: drop-shadow(0 0 30px rgba(255, 0, 255, 0.8)); }
    }
    
    /* Input field styling */
    .stTextInput > div > div > input {
        background: rgba(26, 26, 26, 0.8);
        border: 2px solid transparent;
        border-radius: 15px;
        color: var(--text-primary);
        font-size: 1.1rem;
        padding: 15px 20px;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .stTextInput > div > div > input:focus {
        outline: none;
        border-color: var(--primary-glow);
        box-shadow: 0 0 25px rgba(0, 255, 255, 0.4);
        background: rgba(26, 26, 26, 1);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, var(--primary-glow), var(--secondary-glow));
        border: none;
        border-radius: 15px;
        color: #000;
        font-weight: bold;
        font-size: 1.1rem;
        padding: 15px 30px;
        transition: all 0.3s ease;
        cursor: pointer;
        box-shadow: 0 5px 15px rgba(0, 255, 255, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 255, 255, 0.5);
        background: linear-gradient(45deg, #00cccc, #cc00cc);
    }
    
    /* Download button styling */
    .stDownloadButton > button {
        background: linear-gradient(45deg, var(--accent-glow), #ff6600);
        border: none;
        border-radius: 12px;
        color: #000;
        font-weight: bold;
        padding: 12px 25px;
        transition: all 0.3s ease;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(255, 255, 0, 0.3);
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(255, 255, 0, 0.4);
    }
    
    /* Success message styling */
    .stSuccess {
        background: rgba(0, 255, 0, 0.1);
        border: 1px solid rgba(0, 255, 0, 0.3);
        border-radius: 10px;
        color: var(--text-primary);
    }
    
    /* Error message styling */
    .stError {
        background: rgba(255, 0, 0, 0.1);
        border: 1px solid rgba(255, 0, 0, 0.3);
        border-radius: 10px;
        color: var(--text-primary);
    }
    
    /* Warning message styling */
    .stWarning {
        background: rgba(255, 165, 0, 0.1);
        border: 1px solid rgba(255, 165, 0, 0.3);
        border-radius: 10px;
        color: var(--text-primary);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(26, 26, 26, 0.6);
        border: 1px solid rgba(0, 255, 255, 0.2);
        border-radius: 10px;
        color: var(--text-primary);
    }
    
    .streamlit-expanderContent {
        background: rgba(26, 26, 26, 0.4);
        border-radius: 0 0 10px 10px;
        border: 1px solid rgba(0, 255, 255, 0.1);
        border-top: none;
    }
    
    /* Image styling */
    .stImage > img {
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 255, 255, 0.3);
        transition: all 0.3s ease;
    }
    
    .stImage > img:hover {
        box-shadow: 0 15px 40px rgba(255, 0, 255, 0.4);
        transform: scale(1.02);
    }
    
    /* Code block styling */
    .stCodeBlock {
        background: rgba(26, 26, 26, 0.8);
        border: 1px solid rgba(0, 255, 255, 0.2);
        border-radius: 10px;
        color: var(--text-primary);
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        color: var(--text-secondary);
        margin-top: 3rem;
        padding: 2rem;
        border-top: 1px solid rgba(0, 255, 255, 0.2);
    }
    
    /* Twitter share button styling */
    .twitter-share-btn {
        background: linear-gradient(45deg, #000000, #434343);
        border: 2px solid #00ffff;
        border-radius: 12px;
        color: white;
        font-weight: bold;
        padding: 12px 25px;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        transition: all 0.3s ease;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0, 255, 255, 0.2);
    }
    
    .twitter-share-btn:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(0, 255, 255, 0.4);
        background: linear-gradient(45deg, #434343, #000000);
    }
</style>
""", unsafe_allow_html=True)

def extract_video_id(youtube_url):
    """유튜브 URL에서 비디오 ID를 추출하는 함수"""
    
    # 정규식 패턴들
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
    
    # URL 파싱 방식으로 시도
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
        # YouTube oEmbed API 사용
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        response = requests.get(oembed_url)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('title', 'Unknown Title')
        else:
            return 'Unknown Title'
    except Exception as e:
        st.error(f"Failed to get video title: {str(e)}")
        return 'Unknown Title'

def get_thumbnail_url(video_id):
    """비디오 ID로 썸네일 URL을 생성하는 함수"""
    if not video_id:
        return None
    
    # 최대 품질의 썸네일 URL (1280x720)
    return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

def create_twitter_share_url(video_title, video_url):
    """X.com 공유 URL 생성"""
    # 따옴표와 특수문자 이스케이프
    encoded_title = video_title.replace(" ", "%20").replace("\"", "%22").replace("'", "%27")
    encoded_url = video_url.replace(":", "%3A").replace("/", "%2F")
    
    return f"https://x.com/intent/post?text={encoded_title}&url={encoded_url}"

# Main title with glow effect
st.markdown('<h1 class="main-title">🎬 YouTube Thumbnail Extractor</h1>', unsafe_allow_html=True)

# 유튜브 URL 입력
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    youtube_url = st.text_input(
        "Enter YouTube URL:",
        placeholder="https://www.youtube.com/watch?v=...",
        label_visibility="collapsed"
    )

# 중앙 정렬을 위한 컬럼
if youtube_url:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✨ Extract Thumbnail", type="primary", use_container_width=True):
            if youtube_url:
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
                            st.markdown(f"### 📹 {video_title}")
                            
                            # 썸네일 표시
                            st.image(thumbnail_url, caption=f"Thumbnail for: {video_title}", use_column_width=True)
                            
                            col1, col2, col3 = st.columns([1, 1, 1])
                            with col2:
                                # 다운로드 버튼
                                st.download_button(
                                    label="📥 Download Thumbnail",
                                    data=response.content,
                                    file_name=f"youtube_thumbnail_{video_id}.jpg",
                                    mime="image/jpeg",
                                    help="Click to download the thumbnail image",
                                    use_container_width=True
                                )
                            
                            # X.com 공유 버튼
                            st.markdown("---")
                            st.markdown("### 🐦 Share on X (Twitter)")
                            
                            twitter_share_url = create_twitter_share_url(video_title, youtube_url)
                            
                            col1, col2, col3 = st.columns([1, 2, 1])
                            with col2:
                                st.markdown(f"""
                                    <a href="{twitter_share_url}" target="_blank" class="twitter-share-btn">
                                        <span>🐦</span>
                                        Share "{video_title}" on X
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

# 사용법 안내
with st.expander("📖 How to Use"):
    st.markdown("""
    1. **Enter YouTube URL**: Copy and paste any YouTube video URL
    2. **Click Extract**: Press the 'Extract Thumbnail' button
    3. **View Thumbnail**: The thumbnail and video title will be displayed
    4. **Download**: Click 'Download Thumbnail' to save the image
    5. **Share**: Click 'Share on X' to post the video title and link on X/Twitter
    
    **Supported URL formats:**
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/shorts/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    """)

# 푸터
st.markdown("""
<div class="footer">
    <p>✨ Made with Streamlit & Glow Effects ✨</p>
    <p>Supports all YouTube video formats • High-quality thumbnails • Direct X/Twitter sharing</p>
</div>
""", unsafe_allow_html=True)
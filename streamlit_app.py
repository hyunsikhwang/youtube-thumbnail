import streamlit as st
import requests
from urllib.parse import urlparse, parse_qs
import re

st.set_page_config(
    page_title="YouTube Thumbnail Extractor",
    page_icon="🎥",
    layout="centered"
)

st.title("🎬 YouTube Thumbnail Extractor")
st.markdown("---")

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

def get_thumbnail_url(video_id):
    """비디오 ID로 썸네일 URL을 생성하는 함수"""
    if not video_id:
        return None
    
    # 최대 품질의 썸네일 URL (1280x720)
    return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

def create_twitter_share_url(thumbnail_url, video_url):
    """X.com 공유 URL 생성"""
    text = f"Check out this YouTube video thumbnail! 🎥"
    encoded_text = text.replace(" ", "%20")
    encoded_url = video_url.replace(":", "%3A").replace("/", "%2F")
    
    return f"https://x.com/intent/post?text={encoded_text}&url={encoded_url}"

# 유튜브 URL 입력
youtube_url = st.text_input(
    "Enter YouTube URL:",
    placeholder="https://www.youtube.com/watch?v=..."
)

if st.button("Extract Thumbnail", type="primary"):
    if youtube_url:
        # 비디오 ID 추출
        video_id = extract_video_id(youtube_url)
        
        if video_id:
            # 썸네일 URL 생성
            thumbnail_url = get_thumbnail_url(video_id)
            
            try:
                # 썸네일 이미지 표시
                response = requests.get(thumbnail_url)
                if response.status_code == 200:
                    st.success("✅ Thumbnail extracted successfully!")
                    
                    # 썸네일 표시
                    st.image(thumbnail_url, caption="YouTube Thumbnail", use_column_width=True)
                    
                    # 다운로드 버튼
                    st.download_button(
                        label="📥 Download Thumbnail",
                        data=response.content,
                        file_name=f"youtube_thumbnail_{video_id}.jpg",
                        mime="image/jpeg",
                        help="Click to download the thumbnail image"
                    )
                    
                    # X.com 공유 버튼
                    twitter_share_url = create_twitter_share_url(thumbnail_url, youtube_url)
                    st.markdown("---")
                    st.markdown("### Share on X (Twitter)")
                    
                    # X.com 공유 버튼 (HTML로 구현)
                    st.markdown(f"""
                        <a href="{twitter_share_url}" target="_blank" style="text-decoration: none;">
                            <button style="
                                background-color: #000000;
                                color: white;
                                border: none;
                                padding: 10px 20px;
                                border-radius: 5px;
                                cursor: pointer;
                                font-size: 16px;
                                font-weight: bold;
                                display: inline-flex;
                                align-items: center;
                                gap: 8px;
                            ">
                                <span>🐦</span>
                                Share on X
                            </button>
                        </a>
                    """, unsafe_allow_html=True)
                    
                    # 썸네일 URL 표시
                    with st.expander("Show Thumbnail URL"):
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
    3. **View Thumbnail**: The thumbnail will be displayed
    4. **Download**: Click 'Download Thumbnail' to save the image
    5. **Share**: Click 'Share on X' to post on X/Twitter
    
    **Supported URL formats:**
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/shorts/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    """)

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888;'>
    <p>Made with ❤️ using Streamlit</p>
    <p>Supports all YouTube video formats including Shorts, regular videos, and embedded videos</p>
</div>
""", unsafe_allow_html=True)
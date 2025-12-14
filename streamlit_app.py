import streamlit as st
import re
import urllib.parse
import requests

# ==========================================
# 1. 초기 설정 (Page Config)
# ==========================================
st.set_page_config(
    page_title="YouTube Thumbnail Share", 
    page_icon=":sparkles:", 
    layout="centered"
)

# ==========================================
# 2. [DESIGN] Minimal + Vivid Glow Styling
#    (업로드된 파일의 CSS를 그대로 적용)
# ==========================================
st.markdown("""
<style>
    /* 1. 기본 배경: 아주 깔끔한 오프 화이트 (눈이 편안함) */
    [data-testid="stAppViewContainer"] {
        background-color: #F8F9FA;
        color: #212529;
    }
    
    /* 2. 폰트 적용 (Pretendard) */
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * { font-family: 'Pretendard', sans-serif !important; }

    /* 3. 헤더: 군더더기 없는 모던 타이포그래피 */
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        color: #111111;
        text-align: center;
        margin-top: 20px;
        letter-spacing: -1px;
    }
    .main-header span {
        color: #4361EE; /* Vivid Blue Accent */
    }
    .sub-header {
        text-align: center;
        color: #868e96;
        font-size: 1rem;
        font-weight: 500;
        margin-bottom: 50px;
    }

    /* 4. 메인 카드 (Clean White Box) */
    [data-testid="stVerticalBlockBorderWrapper"] > div {
        background: #FFFFFF !important;
        border: 1px solid #E9ECEF !important;
        border-radius: 20px !important;
        padding: 40px !important;
        /* 부드럽지만 명확한 그림자 */
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.05) !important; 
    }

    /* 5. 입력창: 미니멀하다가 클릭하면 Vivid Glow 발동 */
    .stTextInput > div > div > input {
        background-color: #F8F9FA !important;
        color: #212529 !important;
        border: 2px solid #E9ECEF !important;
        border-radius: 12px !important;
        padding: 12px 15px !important;
        transition: all 0.3s ease !important;
    }
    .stTextInput > div > div > input:focus {
        background-color: #FFFFFF !important;
        border-color: #4361EE !important; /* Vivid Blue */
        /* 선명한 글로우 효과 */
        box-shadow: 0 0 15px rgba(67, 97, 238, 0.4) !important; 
    }

    /* 6. 메인 액션 버튼: 가장 강렬한 포인트 (Neon Gradient) */
    .stButton > button {
        width: 100%;
        /* Vivid Blue to Purple Gradient */
        background: linear-gradient(90deg, #4361EE 0%, #7209B7 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 20px !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
        /* 버튼 자체가 빛나는 효과 */
        box-shadow: 0 5px 20px rgba(67, 97, 238, 0.4) !important; 
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(114, 9, 183, 0.5) !important;
    }
    
    /* 7. X 공유 버튼 커스텀 (CSS Selector 매칭을 위해 link_button 대신 html 사용 예정) */
    .x-share-btn {
        display: inline-flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        background-color: #000000 !important; 
        color: #ffffff !important;
        text-decoration: none;
        border-radius: 12px;
        padding: 12px 20px;
        font-weight: 700;
        margin-top: 12px;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border: none;
    }
    .x-share-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        color: #ffffff !important;
    }
    .x-share-btn::before {
        content: "𝕏 "; 
        margin-right: 8px;
        font-size: 1.2rem;
    }

    /* UI 정리 */
    header, footer {visibility: hidden;}
    /* 이미지 스타일 */
    img { 
        border-radius: 16px; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.1); 
        margin-bottom: 20px; 
        border: 1px solid #E9ECEF;
    }
    
    /* 결과 텍스트 스타일 */
    .result-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #212529;
        margin-bottom: 5px;
    }
    .result-desc {
        font-size: 0.9rem;
        color: #868e96;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. 로직 함수 (Script A 기능 유지)
# ==========================================
YOUTUBE_OEMBED = "https://www.youtube.com/oembed?format=json&url="

def extract_youtube_video_id(url: str) -> str | None:
    if not url:
        return None
    url = url.strip()
    m = re.search(r"(?:https?://)?(?:www\.)?youtu\.be/([A-Za-z0-9_-]{6,})", url)
    if m: return m.group(1)
    m = re.search(r"(?:https?://)?(?:www\.)?youtube\.com/watch\?([^#]+)", url)
    if m:
        qs = urllib.parse.parse_qs(m.group(1))
        vid = qs.get("v", [None])[0]
        if vid: return vid
    m = re.search(r"(?:https?://)?(?:www\.)?youtube\.com/shorts/([A-Za-z0-9_-]{6,})", url)
    if m: return m.group(1)
    m = re.search(r"(?:https?://)?(?:www\.)?youtube\.com/embed/([A-Za-z0-9_-]{6,})", url)
    if m: return m.group(1)
    return None

def canonical_watch_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"

def get_youtube_title_via_oembed(youtube_url: str, timeout_sec: float = 6.0) -> str | None:
    try:
        resp = requests.get(
            YOUTUBE_OEMBED + urllib.parse.quote(youtube_url, safe=""),
            timeout=timeout_sec,
        )
        if resp.status_code != 200:
            return None
        return resp.json().get("title")
    except Exception:
        return None

def best_thumbnail_url(video_id: str) -> str:
    maxres = f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"
    hq = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
    try:
        r = requests.head(maxres, timeout=4.0)
        if r.status_code == 200:
            return maxres
    except Exception:
        pass
    return hq

def x_share_intent_url(text: str, url: str) -> str:
    # CSS 매칭을 위해 base URL을 x.com으로 변경 권장하나, 리다이렉트 고려하여 twitter.com 유지해도 됨.
    # 하지만 디자인 코드의 CSS 선택자가 a[href*="x.com/intent"] 이므로 x.com으로 설정합니다.
    base = "https://x.com/intent/tweet"
    params = {"text": text or "", "url": url or ""}
    return base + "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)

# ==========================================
# 4. UI 구성 (Minimal + Vivid Design Layout)
# ==========================================

# Header
st.markdown('<div class="main-header">YouTube <span>Thumb & Share</span></div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">썸네일 확인부터 X 공유까지, 가장 아름답게.</div>', unsafe_allow_html=True)

# Main Card Container
with st.container(border=True):
    # Input Area
    target_url = st.text_input("유튜브 링크", placeholder="https://youtu.be/...", label_visibility="collapsed")
    
    # Action Button
    if st.button("🚀 썸네일 가져오기 (Fetch)"):
        if not target_url:
            st.warning("🔗 유튜브 링크를 입력해주세요.")
        else:
            with st.spinner("⚡ 정보를 가져오는 중입니다..."):
                video_id = extract_youtube_video_id(target_url)
                
                if video_id:
                    watch_url = canonical_watch_url(video_id)
                    title = get_youtube_title_via_oembed(watch_url) or "제목을 가져올 수 없음"
                    thumb_url = best_thumbnail_url(video_id)
                    
                    # 구분선
                    st.markdown("---")
                    
                    # 1. 썸네일 이미지 표시
                    st.image(thumb_url, caption="", use_container_width=True)
                    
                    # 2. 텍스트 정보 표시
                    st.markdown(f'<div class="result-title">{title}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="result-desc">이 제목과 링크로 공유됩니다.</div>', unsafe_allow_html=True)
                    
                    # 3. X (Twitter) 공유 버튼
                    # 디자인 파일의 CSS(.x-share-btn 등)를 활용하기 위해 HTML a 태그 직접 삽입
                    share_link = x_share_intent_url(text=title, url=watch_url)
                    
                    st.markdown(
                        f"""
                        <a href="{share_link}" target="_blank" class="x-share-btn">
                            Share on X
                        </a>
                        """, 
                        unsafe_allow_html=True
                    )
                    
                else:
                    st.error("❌ 올바른 유튜브 링크 형식이 아닙니다.")
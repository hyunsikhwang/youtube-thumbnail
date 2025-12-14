import re
import urllib.parse
import requests
import streamlit as st

# -----------------------------
# Utilities
# -----------------------------
YOUTUBE_OEMBED = "https://www.youtube.com/oembed?format=json&url="

def extract_youtube_video_id(url: str) -> str | None:
    if not url:
        return None
    url = url.strip()

    m = re.search(r"(?:https?://)?(?:www\.)?youtu\.be/([A-Za-z0-9_-]{6,})", url)
    if m:
        return m.group(1)

    m = re.search(r"(?:https?://)?(?:www\.)?youtube\.com/watch\?([^#]+)", url)
    if m:
        qs = urllib.parse.parse_qs(m.group(1))
        vid = qs.get("v", [None])[0]
        if vid:
            return vid

    m = re.search(r"(?:https?://)?(?:www\.)?youtube\.com/shorts/([A-Za-z0-9_-]{6,})", url)
    if m:
        return m.group(1)

    m = re.search(r"(?:https?://)?(?:www\.)?youtube\.com/embed/([A-Za-z0-9_-]{6,})", url)
    if m:
        return m.group(1)

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
    base = "https://twitter.com/intent/tweet"
    params = {"text": text or "", "url": url or ""}
    return base + "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)


# -----------------------------
# Page
# -----------------------------
st.set_page_config(page_title="YouTube Thumbnail → Share to X", page_icon="✨", layout="centered")

st.markdown(
    """
    <style>
      :root{
        --bg-light: #f8faff;
        --card-bg: rgba(255, 255, 255, 0.75);
        --border: rgba(0, 0, 0, 0.04);
        --accent-glow: rgba(99, 102, 241, 0.25);
        --text-primary: #0f172a;
        --text-secondary: #64748b;
      }

      /* Global Reset & Light Theme */
      .stApp{
        background-color: var(--bg-light);
        background-image:
            radial-gradient(circle at 10% 10%, rgba(236, 72, 153, 0.10) 0%, transparent 40%),
            radial-gradient(circle at 90% 20%, rgba(99, 102, 241, 0.10) 0%, transparent 40%);
        color: var(--text-primary);
      }

      /* Streamlit overrides */
      [data-testid="stAppViewContainer"] .main{
        padding-top: 40px;
        padding-bottom: 60px;
      }
      h1, h2, h3, p, div, span { color: var(--text-primary); }
      .stCaption { color: var(--text-secondary) !important; }

      /* Layout Wrapper */
      .wrap{
        max-width: 720px;
        margin: 0 auto;
      }

      .title{
        font-size: 42px;
        font-weight: 800;
        background: linear-gradient(120deg, #0f172a 0%, #6366f1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
        letter-spacing: -0.02em;
      }
      .sub{
        color: var(--text-secondary);
        font-size: 16px;
        margin-bottom: 36px;
        font-weight: 400;
      }

      .card{
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 24px;
        padding: 32px;
        backdrop-filter: blur(20px);
        box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.06);
      }

      .section-title{
        color: var(--text-secondary);
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 700;
        margin-bottom: 8px;
        margin-left: 4px;
      }

      /* Input Fields */
      div[data-baseweb="input"] > div{
        background-color: #ffffff !important;
        border: 1px solid rgba(0,0,0,0.08) !important;
        border-radius: 14px !important;
      }
      div[data-baseweb="input"] input{
        color: var(--text-primary) !important;
        font-weight: 500;
      }

      /* Primary Button */
      .stButton > button{
        background: linear-gradient(90deg, #6366f1, #ec4899) !important;
        border: none !important;
        color: white !important;
        font-weight: 700 !important;
        height: 50px !important;
        border-radius: 14px !important;
        box-shadow: 0 10px 25px -5px var(--accent-glow) !important;
        transition: transform 0.2s, box-shadow 0.2s !important;
      }
      .stButton > button:hover{
        transform: translateY(-2px);
        box-shadow: 0 15px 35px -5px var(--accent-glow) !important;
      }

      /* Divider */
      .divider{
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(0,0,0,0.06), transparent);
        margin: 24px 0;
      }

      /* Pill Badge */
      .pill{
        display:inline-flex;
        align-items:center;
        justify-content:center;
        height: 50px;
        padding: 0 20px;
        border-radius: 999px;
        border: 1px solid var(--border);
        background: rgba(255,255,255,0.6);
        color: var(--text-secondary);
        font-size: 13px;
        font-weight: 600;
        backdrop-filter: blur(10px);
        white-space: nowrap;
      }

      /* X Share Button */
      .xbtn{
        display:flex;
        align-items:center;
        justify-content:center;
        gap:10px;
        padding: 16px;
        border-radius: 16px;
        background: #000;
        border: 1px solid #000;
        color: #fff !important;
        text-decoration:none !important;
        font-weight: 700;
        width: 100%;
        box-shadow: 0 10px 25px -10px rgba(0,0,0,0.3);
        transition: all 0.2s ease;
      }
      .xbtn:hover{
        background: #222;
        transform: translateY(-2px);
        box-shadow: 0 20px 40px -10px rgba(0,0,0,0.2);
      }
      .xicon{ width: 16px; height: 16px; }

      .hint{
        color: #94a3b8;
        font-size: 12px;
        margin-top: 12px;
        text-align: center;
      }

      /* 이미지 라운드 */
      img{
        border-radius: 16px !important;
        border: 1px solid rgba(0,0,0,0.05) !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="wrap">', unsafe_allow_html=True)

st.markdown('<div class="title">YouTube Thumbnail → Share to X ✨</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">유튜브 링크를 넣으면 썸네일을 보여주고, 제목 그대로 X.com에 공유합니다.</div>', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown('<div class="section-title">유튜브 공유 링크</div>', unsafe_allow_html=True)
    youtube_link = st.text_input(
        label="유튜브 공유 링크",
        placeholder="https://youtu.be/VIDEO_ID 또는 https://www.youtube.com/watch?v=VIDEO_ID",
        label_visibility="collapsed",
    )

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # 버튼 + pill을 같은 줄에 정렬 (비율 안정적으로)
    c1, c2 = st.columns([3, 1.2], vertical_alignment="center")
    with c1:
        fetch = st.button("썸네일/제목 불러오기", type="primary", use_container_width=True)
    with c2:
        st.markdown('<div class="pill">minimal + vivid glow</div>', unsafe_allow_html=True)

    # 실행 조건: 버튼 클릭 또는 링크 변경
    should_run = False
    if youtube_link:
        if fetch:
            should_run = True
        elif st.session_state.get("last_link") != youtube_link:
            should_run = True

    if should_run and youtube_link:
        st.session_state["last_link"] = youtube_link
        vid = extract_youtube_video_id(youtube_link)

        if not vid:
            st.error("유튜브 링크에서 video id를 추출하지 못했습니다. 공유 링크 형태를 확인해 주세요.")
        else:
            watch_url = canonical_watch_url(vid)
            title = get_youtube_title_via_oembed(watch_url) or "제목을 가져올 수 없음"
            thumb_url = best_thumbnail_url(vid)

            st.markdown("")  # breathing room
            st.subheader("미리보기")

            st.caption("썸네일")
            st.image(thumb_url, use_container_width=True)

            st.caption("제목 (X 공유 텍스트)")
            st.write(title)

            intent = x_share_intent_url(text=title, url=watch_url)
            st.markdown(
                f"""
                <a class="xbtn" href="{intent}" target="_blank" rel="noopener noreferrer">
                  <svg class="xicon" viewBox="0 0 24 24" aria-hidden="true" fill="currentColor">
                    <path d="M18.244 2H21l-6.53 7.47L22.5 22h-6.79l-5.32-6.93L4.3 22H1.5l7.05-8.08L1.5 2h6.96l4.8 6.29L18.244 2Zm-1.19 18h1.88L7.9 3.9H5.88L17.055 20Z"/>
                  </svg>
                  X.com 에 공유하기
                </a>
                <div class="hint">공유 텍스트는 유튜브 제목 그대로이며, 링크는 자동으로 첨부됩니다.</div>
                """,
                unsafe_allow_html=True,
            )
    elif not youtube_link:
        st.info("유튜브 공유 링크를 입력해 주세요.")

    st.markdown("</div>", unsafe_allow_html=True)  # card end

st.markdown(
    '<div class="hint">참고: 제목은 YouTube oEmbed로 가져옵니다(API Key 불필요). 네트워크 환경에 따라 제목 로딩이 실패할 수 있습니다.</div>',
    unsafe_allow_html=True,
)

st.markdown("</div>", unsafe_allow_html=True)  # wrap end

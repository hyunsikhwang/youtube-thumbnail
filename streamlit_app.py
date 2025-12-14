import re
import urllib.parse
import requests
import streamlit as st


# -----------------------------
# Utilities
# -----------------------------
YOUTUBE_OEMBED = "https://www.youtube.com/oembed?format=json&url="

def extract_youtube_video_id(url: str) -> str | None:
    """Extract YouTube video_id from various URL forms, including share links."""
    if not url:
        return None
    url = url.strip()

    # Handle youtu.be/<id>
    m = re.search(r"(?:https?://)?(?:www\.)?youtu\.be/([A-Za-z0-9_-]{6,})", url)
    if m:
        return m.group(1)

    # Handle youtube.com/watch?v=<id>
    m = re.search(r"(?:https?://)?(?:www\.)?youtube\.com/watch\?([^#]+)", url)
    if m:
        qs = urllib.parse.parse_qs(m.group(1))
        vid = qs.get("v", [None])[0]
        if vid:
            return vid

    # Handle youtube.com/shorts/<id>
    m = re.search(r"(?:https?://)?(?:www\.)?youtube\.com/shorts/([A-Za-z0-9_-]{6,})", url)
    if m:
        return m.group(1)

    # Handle youtube.com/embed/<id>
    m = re.search(r"(?:https?://)?(?:www\.)?youtube\.com/embed/([A-Za-z0-9_-]{6,})", url)
    if m:
        return m.group(1)

    return None


def canonical_watch_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"


def get_youtube_title_via_oembed(youtube_url: str, timeout_sec: float = 6.0) -> str | None:
    """Fetch YouTube title using oEmbed (no API key required)."""
    try:
        resp = requests.get(YOUTUBE_OEMBED + urllib.parse.quote(youtube_url, safe=""), timeout=timeout_sec)
        if resp.status_code != 200:
            return None
        data = resp.json()
        return data.get("title")
    except Exception:
        return None


def best_thumbnail_url(video_id: str) -> str:
    """
    YouTube thumbnail patterns:
    - maxresdefault.jpg (may not exist)
    - hqdefault.jpg (almost always exists)
    We'll try maxres first; if it 404s, fall back to hqdefault.
    """
    maxres = f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"
    hq = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"

    # Lightweight existence check
    try:
        r = requests.head(maxres, timeout=4.0)
        if r.status_code == 200:
            return maxres
    except Exception:
        pass
    return hq


def x_share_intent_url(text: str, url: str) -> str:
    """
    X share intent.
    Requirement: share text must be exactly YouTube title.
    We'll set `text=title` and also include the YouTube URL as `url=...`.
    """
    base = "https://twitter.com/intent/tweet"
    params = {
        "text": text or "",
        "url": url or "",
    }
    return base + "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)


# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(
    page_title="YouTube Thumbnail → Share to X",
    page_icon="✨",
    layout="centered",
)

# Minimal + vivid glow styling (bright background)
st.markdown(
    """
    <style>
      :root{
        --bg:#fbfbff;
        --card:#ffffff;
        --text:#111827;
        --muted:#6b7280;
        --glow1: rgba(99,102,241,.35);
        --glow2: rgba(236,72,153,.25);
        --stroke: rgba(17,24,39,.08);
      }
      .stApp { background: radial-gradient(1200px 600px at 15% 0%, var(--glow1), transparent 60%),
                          radial-gradient(900px 520px at 85% 10%, var(--glow2), transparent 55%),
                          var(--bg); }
      .app-title{
        font-size: 34px;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: var(--text);
        margin-bottom: 8px;
      }
      .app-sub{
        color: var(--muted);
        margin-top: 0px;
        margin-bottom: 18px;
        font-size: 14.5px;
      }
      .card{
        background: var(--card);
        border: 1px solid var(--stroke);
        border-radius: 18px;
        padding: 18px 18px 14px 18px;
        box-shadow: 0 10px 28px rgba(17,24,39,.08);
      }
      .glow-line{
        height: 1px;
        background: linear-gradient(90deg, rgba(99,102,241,.7), rgba(236,72,153,.7));
        border-radius: 999px;
        margin: 12px 0 18px 0;
      }
      .pill{
        display:inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        border: 1px solid var(--stroke);
        background: rgba(255,255,255,.75);
        color: var(--muted);
        font-size: 12px;
      }
      .xbtn{
        display:inline-flex;
        align-items:center;
        justify-content:center;
        gap:10px;
        padding: 12px 14px;
        border-radius: 14px;
        border: 1px solid rgba(17,24,39,.12);
        background: #0b0f19;
        color: #ffffff !important;
        text-decoration: none !important;
        font-weight: 700;
        width: 100%;
        box-shadow: 0 10px 25px rgba(11,15,25,.18);
        transition: transform .08s ease, box-shadow .2s ease;
      }
      .xbtn:hover{
        transform: translateY(-1px);
        box-shadow: 0 14px 30px rgba(11,15,25,.25);
      }
      .xicon{
        width: 16px; height: 16px;
        display:inline-block;
      }
      .hint{
        color: var(--muted);
        font-size: 12.5px;
        margin-top: 8px;
      }
      /* Make Streamlit inputs look cleaner */
      div[data-baseweb="input"] > div{
        border-radius: 14px !important;
      }
      button[kind="primary"]{
        border-radius: 14px !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="app-title">YouTube Thumbnail → Share to X ✨</div>', unsafe_allow_html=True)
st.markdown('<p class="app-sub">유튜브 공유 링크를 넣으면 썸네일을 보여주고, 제목 그대로 X.com에 공유할 수 있어요.</p>', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)

    youtube_link = st.text_input(
        "유튜브 공유 링크",
        placeholder="예: https://youtu.be/VIDEO_ID 또는 https://www.youtube.com/watch?v=VIDEO_ID",
        label_visibility="visible",
    )

    st.markdown('<div class="glow-line"></div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        fetch = st.button("썸네일/제목 불러오기", type="primary", use_container_width=True)
    with col2:
        st.markdown('<span class="pill">minimal + vivid glow</span>', unsafe_allow_html=True)

    # Auto-run when URL changes or button pressed
    should_run = fetch or (youtube_link and "last_link" not in st.session_state) or (
        youtube_link and st.session_state.get("last_link") != youtube_link
    )

    if should_run and youtube_link:
        st.session_state["last_link"] = youtube_link
        vid = extract_youtube_video_id(youtube_link)

        if not vid:
            st.error("유튜브 링크에서 video id를 추출하지 못했습니다. 공유 링크 형태를 확인해 주세요.")
        else:
            watch_url = canonical_watch_url(vid)
            title = get_youtube_title_via_oembed(watch_url) or "제목을 가져올 수 없음"
            thumb_url = best_thumbnail_url(vid)

            st.subheader("미리보기")
            st.caption("썸네일")
            st.image(thumb_url, use_container_width=True)

            st.caption("제목 (X 공유 텍스트)")
            st.write(title)

            # X Share button
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
        st.info("먼저 유튜브 공유 링크를 입력해 주세요.")

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="hint">
      참고: 제목은 YouTube oEmbed로 가져옵니다(API Key 불필요). 네트워크 환경에 따라 제목 로딩이 실패할 수 있습니다.
    </div>
    """,
    unsafe_allow_html=True,
)

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
        --bg:#fbfbff;
        --card:#ffffff;
        --text:#0f172a;
        --muted:#64748b;
        --stroke: rgba(15,23,42,.10);
        --shadow: 0 18px 50px rgba(2,6,23,.10);
        --shadow2: 0 10px 30px rgba(2,6,23,.08);
        --glow1: rgba(99,102,241,.28);
        --glow2: rgba(236,72,153,.20);
      }

      /* 전체 배경 + 가운데 폭 고정 */
      .stApp{
        background:
          radial-gradient(1200px 600px at 12% 0%, var(--glow1), transparent 60%),
          radial-gradient(900px 520px at 90% 8%, var(--glow2), transparent 55%),
          var(--bg);
      }

      /* Streamlit 기본 padding 정리 */
      [data-testid="stAppViewContainer"] .main{
        padding-top: 36px;
        padding-bottom: 48px;
      }

      /* 중앙 폭(카드가 너무 넓게 퍼지는 문제 해결) */
      .wrap{
        max-width: 920px;
        margin: 0 auto;
      }

      .title{
        font-size: 40px;
        font-weight: 850;
        letter-spacing: -0.03em;
        color: var(--text);
        line-height: 1.08;
        margin: 0 0 10px 0;
      }
      .sub{
        color: var(--muted);
        font-size: 15px;
        margin: 0 0 22px 0;
      }

      .card{
        background: rgba(255,255,255,.78);
        border: 1px solid var(--stroke);
        border-radius: 22px;
        padding: 20px;
        box-shadow: var(--shadow);
        backdrop-filter: blur(10px);
      }

      .section-title{
        font-size: 13px;
        font-weight: 700;
        color: var(--muted);
        margin: 2px 0 8px 2px;
      }

      /* 입력창 높이/라운드 통일 */
      div[data-baseweb="input"] > div{
        border-radius: 16px !important;
        border: 1px solid rgba(15,23,42,.12) !important;
        background: rgba(255,255,255,.90) !important;
        box-shadow: var(--shadow2);
      }
      div[data-baseweb="input"] input{
        padding: 14px 14px !important;
        font-size: 16px !important;
      }

      /* 버튼 높이 통일 */
      .stButton > button{
        height: 48px !important;
        border-radius: 16px !important;
        font-weight: 800 !important;
      }

      /* 구분선 */
      .divider{
        height: 1px;
        background: linear-gradient(90deg, rgba(99,102,241,.65), rgba(236,72,153,.65));
        border-radius: 999px;
        margin: 16px 0 18px 0;
      }

      /* pill */
      .pill{
        display:inline-flex;
        align-items:center;
        justify-content:center;
        height: 48px;
        padding: 0 14px;
        border-radius: 999px;
        border: 1px solid rgba(15,23,42,.10);
        background: rgba(255,255,255,.70);
        color: var(--muted);
        font-size: 13px;
        font-weight: 700;
        box-shadow: var(--shadow2);
        white-space: nowrap;
      }

      /* X 공유 버튼 */
      .xbtn{
        display:flex;
        align-items:center;
        justify-content:center;
        gap:10px;
        padding: 14px 14px;
        border-radius: 18px;
        border: 1px solid rgba(15,23,42,.12);
        background: #0b0f19;
        color: #fff !important;
        text-decoration:none !important;
        font-weight: 900;
        width: 100%;
        box-shadow: 0 16px 35px rgba(11,15,25,.22);
        transition: transform .08s ease, box-shadow .2s ease;
      }
      .xbtn:hover{ transform: translateY(-1px); box-shadow: 0 22px 45px rgba(11,15,25,.28); }
      .xicon{ width: 16px; height: 16px; }

      .hint{
        color: var(--muted);
        font-size: 12.5px;
        margin-top: 10px;
      }

      /* 이미지 라운드 */
      img{
        border-radius: 18px !important;
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
        vid = extract_youtube_video_id(_

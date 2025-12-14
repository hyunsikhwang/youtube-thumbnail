import streamlit as st
import re
import urllib.parse
import requests  # HTTP 요청을 위해 추가된 라이브러리

def extract_video_id(url):
    """
    유튜브 URL에서 비디오 ID를 추출합니다.
    """
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

def get_video_title(url):
    """
    YouTube oEmbed API를 사용하여 영상 제목을 가져옵니다.
    공식적인 방법으로 메타데이터를 조회하므로 안정적입니다.
    """
    oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
    try:
        response = requests.get(oembed_url)
        if response.status_code == 200:
            data = response.json()
            return data.get('title', 'YouTube Video') # 제목이 없으면 기본값 반환
        else:
            return "YouTube Video"
    except Exception as e:
        return "YouTube Video"

# --- Streamlit 앱 설정 ---
st.set_page_config(page_title="YouTube 썸네일 추출기", page_icon="📺")

st.title("📺 YouTube 썸네일 추출기")
st.markdown("링크를 입력하면 썸네일을 확인하고, **영상 제목 그대로** X(트위터)에 공유할 수 있습니다.")

# 1. 사용자 입력 받기
video_url = st.text_input("유튜브 동영상 링크를 입력하세요:", placeholder="https://www.youtube.com/watch?v=...")

if video_url:
    video_id = extract_video_id(video_url)

    if video_id:
        # 2. 썸네일 URL 생성
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        
        # 3. 영상 제목 가져오기 (추가된 기능)
        with st.spinner("영상 정보를 가져오는 중입니다..."):
            video_title = get_video_title(video_url)

        st.success("정보 추출 성공!")
        
        # 썸네일과 제목 출력
        st.image(thumbnail_url, caption=f"제목: {video_title}", use_container_width=True)
        st.subheader(f"🎬 {video_title}")

        # 4. X.com 공유 버튼 생성 (제목 적용)
        st.divider()
        st.write("📢 친구들에게 공유하기")

        # 공유할 텍스트에 '영상 제목'을 적용
        share_text = video_title 
        
        # URL 인코딩 (특수문자, 공백 처리)
        encoded_text = urllib.parse.quote(share_text)
        encoded_url = urllib.parse.quote(video_url)
        
        # X 공유 링크 생성
        x_share_link = f"https://twitter.com/intent/tweet?text={encoded_text}&url={encoded_url}"

        st.link_button(
            label=f"X(트위터)에 '{video_title}' 공유하기", 
            url=x_share_link, 
            type="primary"
        )

    else:
        st.error("올바르지 않은 유튜브 링크입니다.")
        st.info("지원 형식: https://youtu.be/..., https://youtube.com/watch?v=...")

else:
    st.info("위 입력창에 링크를 입력해주세요.")
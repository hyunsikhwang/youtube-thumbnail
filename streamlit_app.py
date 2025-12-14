import streamlit as st
import re
import urllib.parse

def extract_video_id(url):
    """
    유튜브 URL에서 비디오 ID를 추출하는 함수입니다.
    다양한 URL 형식(youtu.be, watch?v=, shorts/)을 지원합니다.
    """
    # 유튜브 비디오 ID 추출을 위한 정규표현식 패턴
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    
    if match:
        return match.group(1)
    return None

# --- Streamlit 앱 설정 ---
st.set_page_config(page_title="YouTube 썸네일 추출기", page_icon="📺")

st.title("📺 YouTube 썸네일 추출기")
st.markdown("유튜브 링크를 입력하면 **고해상도 썸네일**을 보여주고, X(트위터)에 공유할 수 있어요.")

# 1. 사용자 입력 받기
video_url = st.text_input("유튜브 동영상 링크를 여기에 붙여넣으세요:", placeholder="https://www.youtube.com/watch?v=...")

if video_url:
    # 2. 비디오 ID 추출 및 썸네일 생성
    video_id = extract_video_id(video_url)

    if video_id:
        # 유튜브 썸네일의 표준 URL 구조 (최대 해상도)
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        
        st.success("썸네일 추출 성공!")
        
        # 썸네일 이미지 출력
        st.image(thumbnail_url, caption="추출된 썸네일", use_container_width=True)

        # 3. X.com (트위터) 공유 버튼 생성
        st.divider() # 구분선
        st.subheader("📢 친구들에게 공유하기")

        # 공유할 텍스트와 URL 인코딩
        share_text = "이 유튜브 영상 썸네일 좀 보세요! 👀"
        # X의 트윗 Intent URL 생성
        # 포맷: https://twitter.com/intent/tweet?text={텍스트}&url={링크}
        encoded_text = urllib.parse.quote(share_text)
        encoded_url = urllib.parse.quote(video_url)
        
        x_share_link = f"https://twitter.com/intent/tweet?text={encoded_text}&url={encoded_url}"

        # Streamlit의 link_button을 사용하여 외부 링크로 이동 (가장 깔끔한 방법)
        st.link_button("X(트위터)에 공유하기", x_share_link, type="primary")

    else:
        st.error("올바르지 않은 유튜브 링크입니다. 다시 확인해주세요.")
        st.info("지원 형식: https://youtu.be/..., https://youtube.com/watch?v=..., https://youtube.com/shorts/...")

else:
    st.info("위 입력창에 링크를 입력하면 결과가 나타납니다.")
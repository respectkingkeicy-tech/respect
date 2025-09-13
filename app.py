import streamlit as st
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import base64

# --- 커스텀 CSS를 이용한 미니멀 테마 적용 ---
st.markdown("""
<style>
    /* 전체 페이지 배경 및 폰트 */
    .stApp {{
        background-color: #0d1117;
        color: #c9d1d9;
    }}
    /* 헤더 텍스트 색상 */
    h1, h2, h3, h4, h5, h6 {{
        color: #ffffff;
    }}
    /* 파일 업로더 디자인 */
    .stFileUploader label {{
        color: #ffffff;
    }}
    /* 기본 버튼 디자인 */
    .stButton>button {{
        background-color: #161b22;
        color: #c9d1d9;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 8px 16px;
    }}
    /* 버튼 호버 (마우스 올렸을 때) 효과 */
    .stButton>button:hover {{
        background-color: #21262d;
        border-color: #8b949e;
        color: #c9d1d9;
    }}
</style>
""", unsafe_allow_html=True)

# Streamlit 페이지 설정
st.set_page_config(
    page_title="AI 모델 사진 생성기",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.title("🛍️ 가상 피팅 AI 모델 생성기")
st.markdown("얼굴, 옷, 배경 사진을 조합하여 쇼핑몰 모델 사진을 만들어보세요.")

# --- Google Cloud 및 Vertex AI 설정 ---
PROJECT_ID = "central-web-429206-f2"
LOCATION = "asia-northeast3"

try:
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    model = GenerativeModel("gemini-2.5-flash-image")
except Exception as e:
    st.error(f"Vertex AI 초기화 오류: {e}")
    st.info("터미널에서 'gcloud auth application-default login' 명령어를 실행했는지 확인해주세요.")


# --- 입력 프레임 ---
st.header("1. 이미지 업로드")
col1, col2, col3, col4 = st.columns(4)

with col1:
    face_image = st.file_uploader("👤 모델 얼굴", type=["jpg", "jpeg", "png"])

with col2:
    top_image = st.file_uploader("👕 상의", type=["jpg", "jpeg", "png"])

with col3:
    bottom_image = st.file_uploader("👖 하의", type=["jpg", "jpeg", "png"])

with col4:
    bg_image = st.file_uploader("🖼️ 배경", type=["jpg", "jpeg", "png"])


# --- 옵션 선택 ---
st.header("2. 옵션 선택")
col5, col6 = st.columns(2)

with col5:
    st.subheader("하의 옵션")
    selected_length = st.selectbox(
        "기장", ["크롭", "일반", "오버"], index=1
    )
    selected_fit = st.selectbox(
        "핏", ["레귤러", "테이퍼드", "세미와이드", "와이드"], index=0
    )

with col6:
    st.subheader("포즈 선택 (중복 가능)")
    pose_front_attention = st.checkbox("정면 차렷")
    pose_front_posing = st.checkbox("정면 포징")
    pose_side_posing = st.checkbox("측면 포징")
    pose_rear_attention = st.checkbox("후면 차렷")

st.header("3. 세부 디테일")
detail_text = st.text_area("옷의 재질, 색상, 디테일 등을 자세히 설명해주세요.", height=150)


# --- AI 로직 및 버튼 ---
if st.button("✨ 사진 생성하기", type="primary"):
    if face_image and top_image and bottom_image and bg_image:
        with st.spinner("AI가 사진을 생성 중입니다..."):
            try:
                # 프롬프트 생성 함수
                def create_prompt(selected_length, selected_fit, selected_poses, detail_text):
                    base_prompt = """A professional fashion photoshoot. A model is wearing the uploaded clothes and in the uploaded background. The model's face is exactly the same as the uploaded image. The lighting is soft and natural."""
                    
                    length_prompt = {
                        "크롭": "The length of the bottom is cropped, ending above the ankle.",
                        "일반": "The length of the bottom is normal, ending at the ankle.",
                        "오버": "The length of the bottom is over, covering the ankle and creating a slight drape."
                    }.get(selected_length, "")
                    
                    fit_prompt = {
                        "레귤러": "The fit of the bottom is regular, straight from the hip to the ankle.",
                        "테이퍼드": "The fit of the bottom is tapered, narrowing towards the ankle.",
                        "세미와이드": "The fit of the bottom is semi-wide, with a slightly loose fit throughout.",
                        "와이드": "The fit of the bottom is wide, with a loose and flowing fit throughout."
                    }.get(selected_fit, "")
                    
                    pose_prompts = []
                    if "정면 차렷" in selected_poses:
                        pose_prompts.append("The model is standing naturally, looking straight ahead with hands at their side.")
                    if "정면 포징" in selected_poses:
                        pose_prompts.append("The model is
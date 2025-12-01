import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# ===== 1) 환경설정 =====
load_dotenv()  # .env 불러오기
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("❌ OPENAI_API_KEY 가 .env 에 설정되어 있지 않습니다.")
    st.stop()

client = OpenAI(api_key=api_key)

# ===== 2) CSV 불러오기 =====
DATA_PATH = "./data/final_urgent_prompts.csv"

@st.cache_data
def load_data(path):
    return pd.read_csv(path, encoding="utf-8")

try:
    df = load_data(DATA_PATH)
except FileNotFoundError:
    st.error(f"❌ CSV 파일을 찾을 수 없습니다: {DATA_PATH}")
    st.stop()

if "prompt" not in df.columns:
    st.error("❌ CSV 안에 'prompt' 라는 컬럼이 없습니다.")
    st.write("현재 컬럼들:", list(df.columns))
    st.stop()

# ===== 3) Streamlit UI =====
st.title("🐶 유기동물 긴급 입양 추천 AI 데모")
st.caption("KNIME → CSV → GPT → Streamlit 까지 전체 파이프라인 시연")

st.sidebar.header("데이터 선택")

# 행 번호 선택
max_idx = len(df) - 1
row_idx = st.sidebar.number_input(
    "분석할 행 번호 (0 ~ {0})".format(max_idx),
    min_value=0,
    max_value=max_idx,
    value=0,
    step=1,
)

row = df.loc[row_idx]
prompt_text = str(row["prompt"])

st.subheader("📌 선택된 프롬프트")
st.code(prompt_text, language="markdown")

st.write("---")

# ===== 4) GPT 호출 버튼 =====
if st.button("🤖 AI 분석 실행"):
    with st.spinner("AI가 분석 중입니다..."):
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",   # 필요하면 다른 모델 이름으로 변경
                messages=[
                    {
                        "role": "system",
                        "content": "너는 유기동물 입양 적합도를 분석해 주는 전문가야. "
                                   "사용자 라이프스타일과 공고 정보를 기반으로 입양 적합도를 설명해 줘."
                    },
                    {"role": "user", "content": prompt_text},
                ],
            )

            answer = response.choices[0].message["content"]

            st.subheader("✅ AI 분석 결과")
            st.write(answer)

        except Exception as e:
            st.error(f"❌ API 호출 중 오류가 발생했습니다: {e}")

st.write("---")
st.caption("※ 실제 서비스에서는 여러 마리 동물을 한 번에 평가하거나, 사용자 라이프스타일 입력 폼을 추가할 수 있습니다.")

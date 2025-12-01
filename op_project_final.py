import streamlit as st
import pandas as pd
import os
from openai import OpenAI
from dotenv import load_dotenv

# =====================================
# 1) .env 로드
# =====================================
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    st.error("❌ ERROR: OPENAI_API_KEY가 .env 파일에 설정되지 않았습니다.")
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)


# =====================================
# 2) CSV 로드 (인코딩 자동 처리)
# =====================================
DATA_PATH = "./data/final_urgent_prompts.csv"

def load_csv_safely(path):
    try:
        return pd.read_csv(path, encoding="cp949")
    except:
        try:
            return pd.read_csv(path, encoding="euc-kr")
        except:
            return pd.read_csv(path, encoding="latin1")

df = load_csv_safely(DATA_PATH)


# =====================================
# 3) Streamlit UI
# =====================================
st.title("🐶 AI 유기동물 입양 상담 챗봇")
st.write("CSV에서 데이터를 불러오고, 선택된 동물의 프롬프트를 기반으로 AI 분석을 생성합니다.")

st.write("### 📌 CSV Columns")
st.write(df.columns.tolist())   # 디버깅용(원하면 삭제 가능)


# =====================================
# 4) 동물 선택 UI
# =====================================
st.write("### 🔍 상담할 동물을 선택하세요")

index = st.number_input(
    "행 번호 선택 (0 ~ 총 {}개)".format(len(df)-1),
    min_value=0,
    max_value=len(df)-1,
    value=0
)

selected_row = df.loc[index]
st.write("선택된 데이터:", selected_row)


# =====================================
# 5) 프롬프트 추출
# =====================================
if "AI_Consulting_Prompt" not in df.columns:
    st.error("❌ ERROR: CSV에 'AI_Consulting_Prompt' 컬럼이 없습니다.")
    st.stop()

prompt_text = selected_row["AI_Consulting_Prompt"]

st.write("### 📝 사용될 프롬프트")
st.code(prompt_text)


# =====================================
# 6) 버튼 클릭 → OpenAI 호출
# =====================================
if st.button("🚀 AI 분석 생성하기"):
    with st.spinner("AI가 분석 중입니다..."):

        try:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "너는 유기동물 입양 전문가 상담 챗봇입니다."},
                    {"role": "user", "content": prompt_text}
                ],
                temperature=0.7
            )

            result = completion.choices[0].message.content

            st.success("분석 완료!")
            st.write("### 💡 AI 상담 결과")
            st.write(result)

        except Exception as e:
            st.error(f"❌ API 호출 중 오류 발생: {str(e)}")


import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# ===== 1) 환경설정 =====
load_dotenv()  # .env 파일 불러오기

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("❌ OPENAI_API_KEY 가 .env 에 설정되어 있지 않습니다.")
    st.stop()

client = OpenAI(api_key=api_key)

# ===== 2) CSV 불러오기 =====
DATA_PATH = "./data/final_urgent_prompts.csv"

st.title("🐶 반려동물 입양 적합도 분석 데모")

if not os.path.exists(DATA_PATH):
    st.error("❌ final_urgent_prompts.csv 파일을 찾을 수 없습니다. data 폴더를 확인하세요.")
    st.stop()

df = pd.read_csv(DATA_PATH, encoding="utf-8")

# 사용자 선택
index = st.number_input("분석할 행 번호 선택", min_value=0, max_value=len(df)-1, value=0)
prompt_text = df.loc[index, "prompt"]

st.subheader("📌 선택된 프롬프트")
st.write(prompt_text)

# ===== 3) GPT 호출 버튼 =====
if st.button("AI 분석 실행"):
    with st.spinner("AI가 분석 중입니다..."):
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "너는 유기동물 데이터를 분석하는 전문가 AI야."},
                {"role": "user", "content": prompt_text}
            ]
        )

    ai_output = response.choices[0].message["content"]
    st.subheader("🐾 AI 분석 결과")
    st.write(ai_output)

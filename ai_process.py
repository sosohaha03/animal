import os
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

# 1) .env 파일 불러오기
load_dotenv()

# 2) 환경변수에서 API 키 가져오기
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# 3) CSV 파일 불러오기
df = pd.read_csv('./data/final_urgent_prompts.csv', encoding='utf-8')

# 4) 예: 첫 번째 행의 prompt만 사용
prompt_text = df.loc[0, 'prompt']

# 5) GPT 호출
response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {"role": "system", "content": "너는 유기동물 분석을 도와주는 AI야."},
        {"role": "user", "content": prompt_text}
    ]
)

# 6) 결과 출력
print("\n=== AI Response ===\n")
print(response.choices[0].message["content"])

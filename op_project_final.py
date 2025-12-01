import os
import pandas as pd
from google import genai 
import json 
import sys # 인코딩 오류 처리를 위해 sys 라이브러리를 추가합니다.

# --- 1. 환경 설정: API 키 직접 입력 (발표 시연용) ---
# 🚨🚨🚨 여기에 본인의 'AIza...' 키를 문자열로 직접 입력합니다! 🚨🚨🚨
# 이 방법으로 .env 파일 경로 문제와 API 키 미전달 문제를 모두 우회합니다.
api_key = "AI로 시작하는 api " 
client = genai.Client(api_key=api_key) 

# --- 2. 데이터 준비: 경로 및 인코딩 문제 해결 ---
# 🚨🚨🚨 CSV 파일 경로를 OneDrive 경로로 정확히 지정 (사용자 이름 변경 필수) 🚨🚨🚨
csv_path = ''

# 🚨 인코딩 오류(UnicodeDecodeError) 처리를 위한 try-except 구조 🚨
try:
    # 1. 한국어 환경에서 가장 흔한 'cp949'로 먼저 시도
    df = pd.read_csv(csv_path, encoding='cp949')
except UnicodeDecodeError:
    try:
        # 2. 실패 시 다른 한국어 인코딩인 'euc-kr'로 시도
        df = pd.read_csv(csv_path, encoding='euc-kr')
    except Exception as e:
        # 3. 두 인코딩 모두 실패 시 오류 메시지 출력 후 종료
        print(f"\n[치명적인 인코딩 오류]: 파일({csv_path})을 읽을 수 없습니다.")
        print("인코딩 문제이거나 파일 내용 자체가 손상되었을 수 있습니다.")
        sys.exit(1) # 프로그램 종료

# 4) 첫 번째 행의 AI_Consulting_Prompt 추출
animal_prompt = df.loc[0, 'AI_Consulting_Prompt'] 

# 5) 사용자 환경 정보 (발표 시 시연을 위해 가정하는 데이터)
user_env = """
입양 희망자는 30대 싱글 직장인이며, 반려 동물을 기른 경험이 전혀 없습니다.
주거 형태는 아파트이고, 하루 6시간 이상 집을 비웁니다.
"""

# 6) Gemini 호출을 위한 최종 프롬프트 조합
final_query = f"""
{animal_prompt}

#사용자 환경: {user_env}

#요청: 이 동물과 사용자의 환경을 비교하여 입양 적합도 점수(10점 만점)와 상세 컨설팅 의견을 'JSON 형식'으로 출력해 주세요.
"""

# --- 3. Gemini 호출 및 결과 출력 ---
try:
    print("--- Gemini API 호출 중... ---")
    response = client.models.generate_content(
        model='gemini-2.5-flash', 
        contents=[final_query]
    )
    
    # 7) 결과 출력
    print("\n=== AI Response (입양 적합도 컨설팅) ===\n")
    print(response.text)
    
except Exception as e:
    print(f"\n[오류 발생]: Gemini API 호출에 실패했습니다. 키 또는 네트워크 연결을 확인하세요. \n에러: {e}")


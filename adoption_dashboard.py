# -*- coding: utf-8 -*-
import os
import pandas as pd
import streamlit as st
from google import genai 
from dotenv import load_dotenv
import json
import sys
import requests # requests 라이브러리 추가

# --- 1. 환경설정 및 API 클라이언트 초기화 ---
# 🚨🚨🚨 여기에 본인의 'AIza...' 키를 문자열로 직접 입력합니다! 🚨🚨🚨
api_key = "" 

# [수정 1] API 키 공백 제거 및 유효성 검사 강화
api_key = api_key.strip() # 앞뒤 공백 제거
if not api_key:
    st.error("❌ API 키가 설정되지 않았습니다. 코드 내 api_key 변수를 확인하세요.")
    sys.exit(1)

# [수정 1] API 키 플레이스홀더 사용 시 오류 처리 강화
if api_key == "AIza로시작하는본인의_Google_API_키":
    st.error("❌ **경고:** API 키가 플레이스홀더 문자열 그대로 설정되어 있습니다. 올바른 Gemini API 키를 입력해 주세요.")
    sys.exit(1)

# API 클라이언트 초기화 (requests 사용을 위해 주석 처리)
# client = genai.Client(api_key=api_key)

# --- 2. CSV 파일 불러오기 및 오류 처리 ---
# 🚨🚨🚨 CSV 파일 경로를 이미지에서 확인된 절대 경로로 수정  🚨🚨🚨
csv_path = '' 
DATA_PATH = os.path.abspath(csv_path) 
PROMPT_COLUMN = "AI_Consulting_Prompt" 

st.title("🐶 반려동물 입양 적합도 분석 데모 (Powered by Gemini)")

if not os.path.exists(DATA_PATH):
    st.error(f"❌ 파일을 찾을 수 없습니다: {DATA_PATH}. 경로를 확인하세요.")
    st.stop()

try:
    df = pd.read_csv(DATA_PATH, encoding='cp949')
except UnicodeDecodeError:
    try:
        df = pd.read_csv(DATA_PATH, encoding='euc-kr')
    except Exception:
        st.error("❌ CSV 파일 인코딩 오류! cp949/euc-kr로도 읽을 수 없습니다.")
        st.stop()
        
# --- 3. 사용자 입력 섹션 ---

st.sidebar.header("📝 분석 대상 동물 선택")
display_options = [f"#{i}: {p[:20]}..." for i, p in enumerate(df[PROMPT_COLUMN])]
selected_option_index = st.sidebar.selectbox(
    "긴급 입양 동물 프롬프트 선택",
    options=list(range(len(df))),
    format_func=lambda i: display_options[i]
)
animal_prompt = df.loc[selected_option_index, PROMPT_COLUMN]

st.sidebar.header("🏡 입양 희망자 환경 입력")
user_env = st.sidebar.text_area(
    "사용자 환경 정보",
    value="30대 싱글 직장인이며, 반려동물을 기른 경험이 없습니다. 주거 형태는 아파트이고, 하루 6시간 이상 집을 비웁니다.",
    height=150
)

st.subheader(f"📌 선택된 동물 정보 (Row #{selected_option_index})")
st.code(animal_prompt, language='text')

# --- 4. Gemini 호출 버튼 및 로직 ---
final_query = "" # 초기화

if st.button("AI 기반 적합도 분석 실행 (Gemini)"):
    if not user_env.strip():
        st.warning("사용자 환경 정보를 입력해 주세요.")
    else:
        user_query = f"""
        #동물 정보: {animal_prompt}

        #사용자 환경: {user_env}

        #요청: 이 동물과 사용자의 환경을 비교하여 입양 적합도 점수(10점 만점)와 상세 컨설팅 의견을 'JSON 형식'으로 출력해 주세요. 점수(adoptionSuitabilityScore)는 숫자형태(0~10)로, 다른 내용은 문자열로 반환해야 합니다.
        """
        
        # --- [수정된 부분]: Structured JSON Output을 위한 API 호출 설정 ---
        apiUrl = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={api_key}"

        # AI에게 반드시 지켜야 할 JSON Schema를 제공합니다.
        json_schema = {
            "type": "OBJECT",
            "properties": {
                "adoptionSuitabilityScore": {
                    "type": "NUMBER",
                    "description": "입양 적합도 점수 (0에서 10 사이의 숫자)"
                },
                "consultationDetails": {
                    "type": "OBJECT",
                    "properties": {
                        "overallAssessment": {
                            "type": "STRING",
                            "description": "적합도에 대한 포괄적인 한 문장 평가"
                        },
                        "strengths": {
                            "type": "ARRAY",
                            "items": {
                                "type": "OBJECT",
                                "properties": {
                                    "category": {"type": "STRING"},
                                    "description": {"type": "STRING"}
                                }
                            },
                            "description": "입양에 긍정적인 요인 목록"
                        },
                        "challenges": {
                            "type": "ARRAY",
                            "items": {
                                "type": "OBJECT",
                                "properties": {
                                    "category": {"type": "STRING"},
                                    "description": {"type": "STRING"}
                                }
                            },
                            "description": "입양에 신중해야 할 도전 과제 목록"
                        }
                    }
                }
            },
            "required": ["adoptionSuitabilityScore", "consultationDetails"]
        }
        
        payload = {
            "contents": [{"parts": [{"text": user_query}]}],
            "generationConfig": { # <--- 'config'를 'generationConfig'로 수정했습니다.
                "responseMimeType": "application/json",
                "responseSchema": json_schema
            }
        }
        # -------------------------------------------------------------------

        with st.spinner("Gemini AI가 적합도를 분석 중입니다... (JSON 형식 강제 적용 중)"):
            try:
                # 4-2. Gemini API 호출 (requests 사용)
                response = requests.post(
                    apiUrl, 
                    json=payload
                )
                
                # HTTP 오류 발생 시, 오류 응답 본문을 포함하여 예외를 발생시킵니다.
                response.raise_for_status() 

                result = response.json()
                
                # API 응답에서 JSON 텍스트 추출
                json_string = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '{}')
                
                # 유효한 JSON 객체로 변환 시도
                try:
                    # AI가 반환한 JSON 문자열을 파이썬 객체로 로드합니다.
                    result_json = json.loads(json_string) 
                    
                    # --- 결과 유효성 검사 ---
                    if not result_json or result_json.get("adoptionSuitabilityScore") is None:
                        st.error("⚠️ AI 분석 결과에 **핵심 정보(적합도 점수)**가 포함되어 있지 않습니다. AI 모델이 예상치 못한 형식을 반환했습니다. 원본 텍스트를 확인하세요.")
                        st.caption("디버깅 정보: AI가 반환한 원본 텍스트")
                        st.code(json_string, language='json')
                        st.stop()
                    # -------------------------

                    st.subheader("🐾 AI 컨설팅 분석 결과")
                    st.success("✅ 분석 완료!")
                    
                    # --- JSON 대신 문장으로 변환하여 출력하는 로직 시작 ---
                    
                    score = result_json.get("adoptionSuitabilityScore", "N/A")
                    details = result_json.get("consultationDetails", {})
                    overall = details.get("overallAssessment", "상세 평가 정보 없음")
                    strengths = result_json.get("consultationDetails", {}).get("strengths", [])
                    challenges = result_json.get("consultationDetails", {}).get("challenges", [])
                    
                    st.markdown(f"### 입양 적합도 점수: <span style='color: #0077b6;'>{score}점 / 10점</span>", unsafe_allow_html=True)
                    st.markdown("---")
                    
                    st.markdown("#### 💬 종합 평가")
                    st.write(f"**{overall}**")
                    st.write("") # 빈 줄 추가

                    st.markdown("#### ✅ 강점 및 적합 요인")
                    if strengths:
                        for i, item in enumerate(strengths):
                            if isinstance(item, dict):
                                st.write(f"**{i+1}. {item.get('category', '분류 없음')}**: {item.get('description', '설명 없음')}")
                            else: # JSON 구조가 약간 다를 경우를 대비한 처리
                                st.write(f"- {item}")
                    else:
                        st.write("강점 요인이 발견되지 않았습니다.")
                        
                    st.markdown("#### ⚠️ 고려 사항 및 도전 과제")
                    if challenges:
                        for i, item in enumerate(challenges):
                            if isinstance(item, dict):
                                st.write(f"**{i+1}. {item.get('category', '분류 없음')}**: {item.get('description', '설명 없음')}")
                            else: # JSON 구조가 약간 다를 경우를 대비한 처리
                                st.write(f"- {item}")
                    else:
                        st.write("주요 도전 과제가 발견되지 않았습니다.")

                    st.markdown("---")
                    st.caption("AI가 반환한 원본 JSON 데이터 (디버깅용)")
                    st.json(result_json) # 원본 JSON은 디버깅용으로 하단에 작게 유지
                    
                    # --- JSON 대신 문장으로 변환하여 출력하는 로직 끝 ---
                    
                except json.JSONDecodeError as e:
                    st.error("⚠️ JSON 파싱 오류: AI 모델이 유효하지 않은 JSON 형식을 반환했습니다. 원본 텍스트를 확인하세요.")
                    st.code(json_string, language='json')
                    st.error(f"오류 내용: {e}")
                    
            except requests.exceptions.HTTPError as http_err:
                # HTTPError 발생 시 (400, 403, 404 등)
                st.error(f"⚠️ Gemini API 호출 중 HTTP 오류 발생: {http_err}")
                st.caption(f"**요청 URL:** {apiUrl}")
                
                # [수정 2] 오류 응답 본문을 출력하여 정확한 원인 진단
                try:
                    error_json = http_err.response.json()
                    st.caption("**API 서버의 오류 메시지 (JSON):**")
                    st.json(error_json)
                except:
                    st.caption("**API 서버의 오류 메시지 (Raw Text):**")
                    st.code(http_err.response.text, language='text')

            except requests.exceptions.RequestException as e:
                # requests 라이브러리의 네트워크 오류 처리 (연결, 타임아웃 등)
                st.error(f"⚠️ Gemini API 호출 중 네트워크 오류 발생: {e}")
                st.caption(f"**요청 URL:** {apiUrl}")
            except Exception as e:
                # 기타 오류 처리
                st.error(f"⚠️ 기타 오류 발생: {e}")


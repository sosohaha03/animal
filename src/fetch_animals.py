import requests
import json
import datetime
import os
import time
from urllib.parse import quote
import xmltodict  # 설치 필요: pip install xmltodict
import random


# -------------------------------------------------------------------
# ★ 1) 원본 서비스키 → URL 인코딩
# -------------------------------------------------------------------
RAW_SERVICE_KEY = "c2a34e82596d30a92592a4955af22d5c8dc01a07f9bb2377b7ce9a56c56bfa8f"
SERVICE_KEY = quote(RAW_SERVICE_KEY, safe='')


# -------------------------------------------------------------------
# API 기본 URL
# -------------------------------------------------------------------
BASE_URL = "https://apis.data.go.kr/1543061/abandonmentPublicSrvc/abandonmentPublic"


# -------------------------------------------------------------------
# 2) 서버 상태 확인 함수 (서버 장애 감지)
# -------------------------------------------------------------------
def check_server_status():
    test_url = BASE_URL + "?serviceKey=" + SERVICE_KEY
    try:
        r = requests.get(test_url, timeout=5)
        if r.status_code >= 500:
            return False
        return True
    except:
        return False


# -------------------------------------------------------------------
# 3) 페이지 단위 데이터 요청 (JSON → JSON 실패 시 XML로 재요청)
# -------------------------------------------------------------------
def fetch_page(page_no):
    params = {
        "serviceKey": SERVICE_KEY,
        "numOfRows": 100,    # 서버 부담 줄이기 위해 100개로 나눔
        "pageNo": page_no,
        "_type": "json",
        "rnd": random.randint(1, 999999)  # 서버 캐싱 버그 방지
    }

    # 서버가 불안정하면 자동 재시도
    for attempt in range(5):
        try:
            res = requests.get(BASE_URL, params=params, timeout=10)

            # 성공 코드면 break
            if res.status_code == 200:
                try:
                    data = res.json()  # JSON 파싱 시도
                    return data
                except:
                    print(f"⚠️ JSON 파싱 실패 → XML로 재시도")
                    return fetch_page_xml(page_no)

            # 500, 502, 503, 504 → 재시도
            if res.status_code in [500, 502, 503, 504]:
                print("⚠️ 서버 오류 → 2초 후 재시도")
                time.sleep(2)
                continue

            print("❌ 비정상 응답:", res.status_code)
            return None

        except Exception as e:
            print("⚠️ 요청 오류:", e)
            time.sleep(2)

    print("❌ 재시도 실패")
    return None


# -------------------------------------------------------------------
# 4) JSON 실패 시 XML로 요청 (사실 XML이 더 안정적)
# -------------------------------------------------------------------
def fetch_page_xml(page_no):
    params = {
        "serviceKey": SERVICE_KEY,
        "numOfRows": 100,
        "pageNo": page_no,
        "_type": "xml",
        "rnd": random.randint(1, 999999)
    }

    try:
        res = requests.get(BASE_URL, params=params, timeout=10)

        if res.status_code == 200:
            xml_data = xmltodict.parse(res.text)
            return xml_data
        else:
            print("❌ XML 호출 실패:", res.status_code)
            return None

    except Exception as e:
        print("❌ XML 요청 오류:", e)
        return None


# -------------------------------------------------------------------
# 5) 전체 페이지 자동 반복 수집
# -------------------------------------------------------------------
def fetch_all():
    print("📡 서버 상태 확인 중...")

    if not check_server_status():
        print("🚨 현재 API 서버가 불안정하거나 장애 상태입니다.")
        print("⏳ 그래도 요청을 계속 시도합니다...\n")

    all_items = []
    page = 1

    while True:
        print(f"\n📄 페이지 {page} 요청 중...")

        data = fetch_page(page)

        if data is None:
            print("⚠️ 데이터 없음 → 종료")
            break

        # JSON 응답 형태 체크
        try:
            items = data["response"]["body"]["items"]["item"]
        except:
            print("⚠️ 페이지 데이터 없음 → 종료")
            break

        if isinstance(items, list):
            all_items += items
        else:
            all_items.append(items)

        print(f"   → 현재까지 {len(all_items)}건 수집됨")

        # 마지막 페이지 확인
        total_count = int(data["response"]["body"]["totalCount"])
        if page * 100 >= total_count:
            break

        page += 1
        time.sleep(0.3)  # 서버 보호

    return all_items


# -------------------------------------------------------------------
# 6) 전체 데이터 저장
# -------------------------------------------------------------------
def save_data(data):
    os.makedirs("./data", exist_ok=True)
    filename = f"./data/animals_{datetime.datetime.now().date()}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"\n✅ 전체 데이터 저장 완료 → {filename}")


# -------------------------------------------------------------------
# 실행부
# -------------------------------------------------------------------
if __name__ == "__main__":
    all_data = fetch_all()
    save_data(all_data)

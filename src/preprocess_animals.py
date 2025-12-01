# src/preprocess_animals.py
import datetime
import re

# -------------------------------------
# 날짜 변환
# -------------------------------------
def parse_date(date_str):
    """
    '20250131' → datetime.date 객체
    """
    try:
        return datetime.datetime.strptime(date_str, "%Y%m%d").date()
    except:
        return None


# -------------------------------------
# 품종 정리
# -------------------------------------
def clean_kind(kindCd):
    """
    '[개] 포메라니안' → '포메라니안'
    '[고양이] 코리안숏헤어' → '코리안숏헤어'
    """
    if not kindCd:
        return ""

    # 대괄호 [xxx] 제거
    cleaned = re.sub(r"\[.*?\]\s*", "", kindCd).strip()
    return cleaned


# -------------------------------------
# 장소(happenPlace) 정리
# -------------------------------------
def clean_place(place):
    """
    장소 문자열을 단순 정리
    예: '서울시 강서구 화곡동' → '서울 강서구 화곡동'
    """
    if not place:
        return ""

    # "시" 제거 (서울시 → 서울)
    place = place.replace("시 ", " ")

    # 중복 공백 제거
    place = re.sub(r"\s+", " ", place).strip()

    return place


# -------------------------------------
# 전체 데이터 전처리
# -------------------------------------
def preprocess_animals(raw_animals):
    """
    mock 데이터 리스트를 받아서
    날짜/문자열/품종 등을 모두 정리한 새 리스트 반환
    """

    processed = []

    for a in raw_animals:
        item = a.copy()  # 원본 손상 방지

        # 날짜 파싱
        item["noticeSdt_parsed"] = parse_date(item.get("noticeSdt", ""))
        item["noticeEdt_parsed"] = parse_date(item.get("noticeEdt", ""))

        # 품종 정리
        item["kindClean"] = clean_kind(item.get("kindCd", ""))

        # 발생 장소 정리
        item["placeClean"] = clean_place(item.get("happenPlace", ""))

        # 보호소 이름 소문자 버전 (검색용)
        item["careNm_lower"] = item.get("careNm", "").lower()

        processed.append(item)

    return processed


# -------------------------------------
# 빠른 테스트용 코드
# -------------------------------------
if __name__ == "__main__":
    import json

    with open("./data/sample_data_for_knime.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        raw = data["response"]["body"]["items"]["item"]

    processed = preprocess_animals(raw)

    print(f"원본: {len(raw)}개 → 전처리 완료: {len(processed)}개")

    # 예시 출력
    for a in processed[:3]:
        print("원본:", a["kindCd"], "→ 정리:", a["kindClean"])

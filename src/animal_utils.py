# src/animal_utils.py
import datetime
import re

# -----------------------------
#  날짜 관련 유틸
# -----------------------------
def parse_date(date_str):
    """
    '20250131' 같은 문자열을 datetime.date 객체로 변환
    """
    try:
        return datetime.datetime.strptime(date_str, "%Y%m%d").date()
    except:
        return None


# -----------------------------
#  1) 마감일 기준 정렬
# -----------------------------
def sort_by_end_date(animals):
    """
    animals 리스트를 보호 종료일(noticeEdt) 기준으로 오름차순 정렬
    """
    def get_end_date(a):
        return parse_date(a.get("noticeEdt", "")) or datetime.date.max

    return sorted(animals, key=get_end_date)


# -----------------------------
#  2) 품종/종 검색 (부분 검색)
# -----------------------------
def filter_by_kind(animals, keyword):
    """
    품종(keyword)이 포함된 동물만 필터링
    """
    keyword = keyword.lower()

    result = []
    for a in animals:
        kind = a.get("kindCd", "").lower()
        if keyword in kind:
            result.append(a)

    return result


# -----------------------------
#  3) 보호소명 검색
# -----------------------------
def filter_by_care_name(animals, keyword):
    """
    보호소명에 keyword가 포함된 동물만
    """
    keyword = keyword.lower()

    result = []
    for a in animals:
        care = a.get("careNm", "").lower()
        if keyword in care:
            result.append(a)
    return result


# -----------------------------
#  4) 지역 검색 (도/시 포함)
# -----------------------------
def filter_by_region(animals, keyword):
    """
    관할 지역(원래는 orgNm 등)이 keyword 포함
    mock 데이터에서는 'happenPlace'로 대체 가능
    """
    keyword = keyword.lower()
    result = []

    for a in animals:
        place = a.get("happenPlace", "").lower()
        if keyword in place:
            result.append(a)

    return result


# -----------------------------
#  5) 다중 필터 (복합 조건)
# -----------------------------
def filter_animals(animals, kind=None, region=None, care=None):
    result = animals

    if kind:
        result = filter_by_kind(result, kind)

    if region:
        result = filter_by_region(result, region)

    if care:
        result = filter_by_care_name(result, care)

    return result


# -----------------------------
#  6) 추천 시스템 예시
# -----------------------------
def recommend_animals(animals, user_region, preferred_kind=None):
    """
    - 지역 우선 필터링
    - 품종(선택)
    - 마감일 정렬
    """
    # 지역 (예: '서울', '부산')
    filtered = filter_by_region(animals, user_region)

    if preferred_kind:
        filtered = filter_by_kind(filtered, preferred_kind)

    # 마감일 빠른 순
    filtered = sort_by_end_date(filtered)

    return filtered

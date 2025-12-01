from src.fetch_animals import load_mock_animals
from src.preprocess_animals import preprocess_animals
from src.animal_utils import *

def main():
    print("🐶 유기동물 추천 시스템 시작!")

    # 1) 테스트 데이터 로드
    animals = load_mock_animals()
    print(f"👉 데이터 로드 완료: {len(animals)} 마리")

    # 2) 전처리
    animals = preprocess_animals(animals)
    print("👉 전처리 완료")

    # 3) 사용자 입력 받기
    user_region = input("📍 당신의 지역을 입력하세요 (예: 서울): ")
    preferred_kind = input("🐾 원하는 품종이 있나요? (없으면 엔터): ")

    # 4) 추천
    result = recommend_animals(animals, user_region, preferred_kind)

    print("\n===== 🐕 추천 결과 =====")
    if not result:
        print("❌ 조건에 맞는 유기동물이 없습니다.")
        return

    for a in result:
        print(f"[{a['noticeNo']}] {a['kindCd']} | {a['careNm']} | 마감일: {a['noticeEdt']}")

    print("\n🎉 추천 완료!")

if __name__ == "__main__":
    main()

import json

def load_mock_animals():
    with open("./data/animals_mock.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["response"]["body"]["items"]["item"]

if __name__ == "__main__":
    animals = load_mock_animals()
    print(f"총 {len(animals)}마리 로드됨")
    for a in animals:
        print(a["desertionNo"], a["kindCd"], a["careNm"])

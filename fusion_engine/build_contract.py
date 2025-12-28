import json
from pathlib import Path
from datetime import datetime


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def latest_json_in(dir_path: Path) -> Path:
    candidates = sorted(dir_path.glob("*.json"))
    if not candidates:
        raise FileNotFoundError(f"No json files in {dir_path}")
    return candidates[-1]


def build_interpretation_contract(
    calculation_json: dict,
    meaning_json: dict,
) -> dict:
    """
    TBOO_INTERPRETATION_CONTRACT_v1.0
    - calculation: 사주 계산 엔진 결과 (fact)
    - meaning: 의미 엔진 결과 (frame)
    """
    return {
        "meta": {
            "contract": "TBOO_INTERPRETATION_CONTRACT",
            "version": "1.0",
            "generated_at": datetime.now().isoformat(),
            "engine_stack": {
                "calculation_engine": "TBOO_SAJU_ENGINE",
                "meaning_engine": "TBOO_MEANING_ENGINE",
            },
            "language": "ko",
            "timezone": "Asia/Seoul",
        },
        "calculation": calculation_json,
        "meaning": meaning_json,
    }


def main():
    base_dir = Path(__file__).resolve().parents[1]

    # ✅ 실제 엔진 출력 폴더
    calculation_dir = base_dir / "calculation_engine" / "output"
    meaning_dir = base_dir / "meaning_engine" / "output"

    calculation_path = latest_json_in(calculation_dir)
    meaning_path = latest_json_in(meaning_dir)

    calculation = load_json(calculation_path)
    meaning = load_json(meaning_path)

    contract = build_interpretation_contract(calculation, meaning)

    # ✅ 루트 output 폴더
    output_dir = base_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = output_dir / f"tboo_interpretation_contract_{timestamp}.json"

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(contract, f, ensure_ascii=False, indent=2)

    print("✅ Fusion complete")
    print(f"   calculation: {calculation_path.name}")
    print(f"   meaning     : {meaning_path.name}")
    print(f"   output      : {out_path}")


if __name__ == "__main__":
    main()

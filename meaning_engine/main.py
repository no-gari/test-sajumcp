# meaning_engine/main.py
# Official CLI entry for TBOO Meaning Engine
# - calculation_engine 결과(JSON)를 입력으로 받아
# - meaning slots JSON을 생성하고
# - 파일명 규칙(with-hour / hour-null)을 유지해 저장한다

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from engine.engine_core import run_engine


def main() -> None:
    parser = argparse.ArgumentParser(description="TBOO Meaning Engine")
    parser.add_argument(
        "--input",
        required=True,
        help="Path to calculation_engine output JSON",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output directory (default: meaning_engine/output)",
    )

    args = parser.parse_args()

    # ─────────────────────────────────────────────
    # 입력 파일 처리
    # ─────────────────────────────────────────────
    in_path = Path(args.input).expanduser().resolve()
    if not in_path.exists():
        raise FileNotFoundError(f"Input not found: {in_path}")

# ─────────────────────────────────────────────
# [PATCH] 디렉터리 입력 지원
# ─────────────────────────────────────────────
    if in_path.is_dir():
        candidates = sorted(in_path.glob("*.json"))
        if not candidates:
            raise FileNotFoundError(f"No json files in directory: {in_path}")
        in_path = candidates[-1]  # 최신 json 선택
# ─────────────────────────────────────────────

    input_stem = in_path.stem  # 파일명 (확장자 제거)

    # 시주 유무 판단 (파일명 규칙 기반)
    if "hour-null" in input_stem:
        hour_tag = "hour-null"
    else:
        hour_tag = "with-hour"

    # ─────────────────────────────────────────────
    # 출력 디렉터리 결정
    # ─────────────────────────────────────────────
    if args.output:
        out_dir = Path(args.output).expanduser().resolve()
    else:
        out_dir = Path(__file__).resolve().parent / "output"

    out_dir.mkdir(parents=True, exist_ok=True)

    # ─────────────────────────────────────────────
    # 계산 결과 로드
    # ─────────────────────────────────────────────
    with open(in_path, "r", encoding="utf-8") as f:
        calculation_json = json.load(f)

    # ─────────────────────────────────────────────
    # 의미 엔진 실행
    # ─────────────────────────────────────────────
    meaning_slots = run_engine(calculation_json)

    # ─────────────────────────────────────────────
    # 결과 파일명 생성 (세션 합의 반영)
    # ─────────────────────────────────────────────
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_filename = f"meaning_v1_{timestamp}_{hour_tag}.json"
    out_path = out_dir / out_filename

    # ─────────────────────────────────────────────
    # 저장
    # ─────────────────────────────────────────────
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(meaning_slots, f, ensure_ascii=False, indent=2)

    # 콘솔 로그
    print("\n==============================")
    print("✅ MEANING ENGINE COMPLETED")
    print(f"📥 Input : {in_path.name}")
    print(f"📤 Output: {out_path}")
    print("==============================\n")


if __name__ == "__main__":
    main()

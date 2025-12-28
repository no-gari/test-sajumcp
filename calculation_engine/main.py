# main.py (FINAL · no-month-flow)
# - TBOO JSON Schema v3.3 (월운 제거)
# - today: base / operation 분리
# - year_2026_operation / daeun / fortune_layers 유지
# - 시주 미상 지원
# - 실행 경로 안정화

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# ------------------------------------------------------------
# 0. 경로 고정
# ------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"

# ------------------------------------------------------------
# 1. 엔진 로드
# ------------------------------------------------------------
try:
    from engine.saju_core import (
        analyze_saju,
        get_today_ganji,
        get_today_unse,
        build_today_domain_operation,
    )
except ImportError:
    from saju_core import (  # type: ignore
        analyze_saju,
        get_today_ganji,
        get_today_unse,
        build_today_domain_operation,
    )


# ------------------------------------------------------------
# 2. 유틸
# ------------------------------------------------------------
def parse_optional_int(token: str) -> Optional[int]:
    t = token.strip().lower()
    if t in ("x", "?", "na", "none", "-", ""):
        return None
    return int(t)


def ensure_output_dir() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def hour_suffix_from_state(hour_state: Dict[str, Any]) -> str:
    status = (hour_state or {}).get("status", "observed")
    return "with-hour" if status == "observed" else "hour-null"


# ------------------------------------------------------------
# 3. JSON 빌더 (월운 없음)
# ------------------------------------------------------------
def build_tboo_json_v33(
    name: str,
    gender: str,
    birth_year: int,
    birth_month: int,
    birth_day: int,
    hour: Optional[int],
    minute: Optional[int],
    saju_info: Dict[str, Any],
    today_unse: Dict[str, Any],
) -> Dict[str, Any]:
    hour_state = saju_info.get("hour_pillar_state", {}) or {}
    hour_status = hour_state.get("status", "observed")

    # birthday 포맷
    if hour_status == "observed" and hour is not None and minute is not None:
        birthday = f"{birth_year:04d}-{birth_month:02d}-{birth_day:02d} {hour:02d}:{minute:02d}"
    else:
        birthday = f"{birth_year:04d}-{birth_month:02d}-{birth_day:02d}"

    fortune_layers = {
        "daeun": {"type": "environment", "weight": 1.0},
        "year": {"type": "event", "weight": 0.7},
        "month": {"type": "environment_sub", "weight": 0.4},
        "day": {"type": "event_peak", "weight": 1.2},
    }

    # today (A안 구조)
    today_block = {
        "base": {
            "ganji": today_unse.get("ganji"),
            "sipshin": today_unse.get("sipshin"),
            "unseong": today_unse.get("unseong"),
            "reference": "day_gan",
        },
        "operation": {
            "money": today_unse.get("today_jaemul", []),
            "love": today_unse.get("today_love", []),
            "job": today_unse.get("today_job", []),
        },
    }

    raw_flow = saju_info.get("2026_flow", [])
    year_2026_operation = {
        "flow": raw_flow,
        "money": saju_info.get("2026_jaemul", []),
        "love": saju_info.get("2026_love", []),
        "job": saju_info.get("2026_job", []),
    }

    return {
        "schema_version": "3.3",
        "user_info": {
            "name": name,
            "gender": gender,
            "birthday": birthday,
        },
        "fortune_layers": fortune_layers,
        "saju": {
            "year": saju_info.get("year_ganji"),
            "month": saju_info.get("month_ganji"),
            "day": saju_info.get("day_ganji"),
            "hour": saju_info.get("hour_ganji"),
        },
        "pillars_detail": saju_info.get("pillars_detail"),
        "sipshin": saju_info.get("sipshin"),
        "unseong": saju_info.get("unseong"),
        "daeun_detail": saju_info.get("daeun_detail"),
        "daeun": {
            "labels": saju_info.get("daeun_labels"),
            "years_traditional": saju_info.get("daeun_year_traditional"),
            "ages": saju_info.get("daeun_rounded"),
        },
        "today": today_block,
        "year_2026_operation": year_2026_operation,
        "hour_pillar_state": hour_state,
        "interpretive_constraint": {
            "hour_pillar": "observed" if hour_status == "observed" else "unobserved"
        },
    }


# ------------------------------------------------------------
# 4. main
# ------------------------------------------------------------
def main() -> None:
    print("▶ 입력 형식:")
    print("  이름 YYYY MM DD HH mm 성별(1:남성, 2:여성)")
    print("  - 시간 모르면 HH mm에 x x 입력")

    raw = input().strip().split()
    if len(raw) < 7:
        print("❌ 입력 형식 오류")
        return

    name = raw[0]
    year, month, day = map(int, raw[1:4])
    hour = parse_optional_int(raw[4])
    minute = parse_optional_int(raw[5])
    gender_code = raw[6]
    gender = "남성" if gender_code == "1" else "여성"
    gender_int = int(gender_code)

    if hour is None or minute is None:
        hour = None
        minute = None

    try:
        saju_info, _ = analyze_saju(
            year, month, day, hour, minute, gender_int, name
        )
    except Exception as e:
        print("❌ 사주 계산 오류:", e)
        return

    day_gan = saju_info.get("day_gan")
    if not day_gan:
        print("❌ day_gan 없음")
        return

    try:
        today_ganji = get_today_ganji()
        today_unse = get_today_unse(day_gan, today_ganji)
        today_unse.update(
            build_today_domain_operation(day_gan, today_ganji, gender_int)
        )
    except Exception as e:
        print("❌ 오늘 운 계산 오류:", e)
        return

    tboo_json = build_tboo_json_v33(
        name=name,
        gender=gender,
        birth_year=year,
        birth_month=month,
        birth_day=day,
        hour=hour,
        minute=minute,
        saju_info=saju_info,
        today_unse=today_unse,
    )

    print(json.dumps(tboo_json, ensure_ascii=False, indent=2))

    out_dir = ensure_output_dir()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = hour_suffix_from_state(tboo_json.get("hour_pillar_state", {}))
    path = out_dir / f"{name}_saju_v33_{ts}_{suffix}.json"
    path.write_text(json.dumps(tboo_json, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n📁 저장 완료: {path}")


if __name__ == "__main__":
    main()

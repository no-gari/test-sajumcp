import pandas as pd
import json
from datetime import datetime
from pathlib import Path

CALC_DIR = Path(__file__).resolve().parent.parent   # calculation_engine/
DATA_DIR = CALC_DIR / "data"                        # calculation_engine/data/

from typing import Optional, Any, Dict, List, Tuple

from engine.daeun import (
    get_sex_direction,
    get_daeun_age_and_startpoints,
    get_daeun_ganji,
    format_daeun_entries,
    create_saju_row_with_textblock,
)
from engine.sipshin import get_sipshin, SIPSHIN_MAP
from engine.unseong import get_12un
from utils.time_utils import get_si_ji_by_clock, get_hour_gan


GAN_10 = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]


# ---------------------------------------------------------
# 📌 1) 사주 분석 (출력 X, 데이터만 반환)
# ---------------------------------------------------------
def analyze_saju(
    y: int,
    m: int,
    d: int,
    h: Optional[int],
    mi: Optional[int],
    gender: int,
    name: str = "",
    return_dataframe: bool = False,
):
    """
    - 만세력 CSV("data/manselyeog_1900.csv")를 이용해 사주 원국 간지/십신/12운성 계산
    - 대운(연해자평 방식) 계산 및 2026년(병오년) 운세용 데이터 생성
    - ✅ 확장: 시주 미상(unknown hour) 상태를 Calculation 레벨에서 명시적으로 표현
      - 추정/보정/대입 ❌
      - 관측 불가 상태(unobserved state)만 선언 ⭕
    """
    # 0. 출생 시각 (시주 미상인 경우: 날짜까지만 유효)
    if h is None or mi is None:
        hour_status = "unknown"
        birth = datetime(y, m, d, 0, 0)
    else:
        hour_status = "observed"
        birth = datetime(y, m, d, h, mi)

    # 1. 만세력에서 간지 조회 (날짜 기준)
    df = pd.read_csv(DATA_DIR / "manselyeog_1900.csv")
    df["양력일자"] = pd.to_datetime(df["양력일자"])

    row = df[df["양력일자"] == birth.replace(hour=0, minute=0)]
    if row.empty:
        print("⚠️ 해당 날짜가 만세력에 없습니다.")
        return None, None

    row = row.iloc[0]

    year_ganji = row["歲次"]
    month_ganji = row["月建"]
    day_ganji = row["日辰"]

    year_gan, year_ji = year_ganji[0], year_ganji[1]
    month_gan, month_ji = month_ganji[0], month_ganji[1]
    day_gan, day_ji = day_ganji[0], day_ganji[1]

    # 1-A. 시주 계산(조건부)
    if hour_status == "observed":
        hour_ji = get_si_ji_by_clock(h, mi)  # type: ignore[arg-type]
        hour_gan = get_hour_gan(day_gan, hour_ji)
        hour_ganji = f"{hour_gan}{hour_ji}"
    else:
        hour_ji = None
        hour_gan = None
        hour_ganji = None

    # -------------------------------------------------
    # 2. 십신 (일간 기준)
    # -------------------------------------------------
    sip_year = get_sipshin(day_gan, year_gan)
    sip_month = get_sipshin(day_gan, month_gan)

    if hour_status == "observed" and hour_gan is not None:
        sip_hour = get_sipshin(day_gan, hour_gan)
    else:
        sip_hour = None

    # 일간 십신 표기
    sip_day = "일간"

    # -------------------------------------------------
    # 3. 십이운성 (각 기둥 천간 본체 vs 해당 지지)
    # -------------------------------------------------
    un_year = get_12un(year_gan, year_ji)
    un_month = get_12un(month_gan, month_ji)
    un_day = get_12un(day_gan, day_ji)

    if hour_status == "observed" and hour_gan is not None and hour_ji is not None:
        un_hour = get_12un(hour_gan, hour_ji)
    else:
        un_hour = None

    # -------------------------------------------------
    # 3-A. 원국 네 기둥 상세 구조
    # -------------------------------------------------
    pillars_detail: Dict[str, Any] = {
        "year": {
            "label": "년주",
            "gan": year_gan,
            "ji": year_ji,
            "sipshin": sip_year,
            "un12": un_year,
            "status": "observed",
        },
        "month": {
            "label": "월주",
            "gan": month_gan,
            "ji": month_ji,
            "sipshin": sip_month,
            "un12": un_month,
            "status": "observed",
        },
        "day": {
            "label": "일주",
            "gan": day_gan,
            "ji": day_ji,
            "sipshin": "일간",
            "un12": un_day,
            "status": "observed",
        },
        "hour": {
            "label": "시주",
            "gan": hour_gan,
            "ji": hour_ji,
            "sipshin": sip_hour,
            "un12": un_hour,
            "status": hour_status,  # observed | unknown
        },
    }

    # -------------------------------------------------
    # 4. 대운 계산 (연해자평 방식)
    # -------------------------------------------------
    direction = get_sex_direction(year_gan, gender)

    with open(DATA_DIR / "solar_terms_1900_2050.json", encoding="utf-8") as f:
          solar_terms = json.load(f)


    # 대운 시작 나이 계산은 "출생 시각"을 받지만,
    # 시주 미상에서는 00:00을 사용하되, 이는 추정이 아니라 '표준 입력값' 처리임
    age_raw, daeun_start_dt, startpoints, daeun_year_traditional = (
        get_daeun_age_and_startpoints(birth, solar_terms, direction)
    )

    daeuns = get_daeun_ganji(month_gan, month_ji, direction)

    daeun_labels = format_daeun_entries(
        age_raw,
        daeuns,
        startpoints,
        y,
        round(age_raw),
    )

    # -------------------------------------------------
    # 4-A. 대운 확장 정보
    # -------------------------------------------------
    daeun_detail = []
    for i, ganji in enumerate(daeuns):
        d_gan, d_ji = ganji[0], ganji[1]
        d_sip = get_sipshin(day_gan, d_gan)
        d_un12 = get_12un(d_gan, d_ji)
        label = daeun_labels[i] if i < len(daeun_labels) else ""
        daeun_detail.append(
            {
                "index": i,
                "label": label,
                "ganji": ganji,
                "gan": d_gan,
                "ji": d_ji,
                "sipshin": d_sip,
                "un12": d_un12,
            }
        )

    # -------------------------------------------------
    # 5. 2026년 병오년 운세 (2026 = 丙午)
    # -------------------------------------------------
    운간 = "丙"
    운지 = "午"

    yearly_flow = []
    천간세트: List[Tuple[str, Optional[str]]] = [
        ("원국_월간", month_gan),
        ("원국_년간", year_gan),
        ("원국_시간", hour_gan if hour_status == "observed" else None),
        ("세운_천간_2026", 운간),
    ]

    for label, g in 천간세트:
        if g is None:
            yearly_flow.append((label, None, None, None))
            continue
        s = get_sipshin(day_gan, g)
        u = get_12un(g, 운지)
        yearly_flow.append((label, g, s, u))

    # 6. 2026 재물운(정재·편재)
    yearly_jaemul = []
    for g in GAN_10:
        s = get_sipshin(day_gan, g)
        if s in ["정재", "편재"]:
            u = get_12un(g, 운지)
            yearly_jaemul.append((s, g, u))

    # 7. 2026 연애운 (남성: 정재·편재 / 여성: 정관·편관)
    yearly_love = []
    love_keys = ["정재", "편재"] if gender == 1 else ["정관", "편관"]
    for g in GAN_10:
        s = get_sipshin(day_gan, g)
        if s in love_keys:
            u = get_12un(g, 운지)
            yearly_love.append((s, g, u))

    # 8. 2026 직업운 (정관·편관·식신·상관)
    yearly_job = []
    job_keys = ["정관", "편관", "식신", "상관"]
    for g in GAN_10:
        s = get_sipshin(day_gan, g)
        if s in job_keys:
            u = get_12un(g, 운지)
            yearly_job.append((s, g, u))

    # -------------------------------------------------
    # 9. Python 쪽에서 사용할 요약 구조 (Calculation Output)
    # -------------------------------------------------
    saju_info: Dict[str, Any] = {
        "year_ganji": year_ganji,
        "month_ganji": month_ganji,
        "day_ganji": day_ganji,
        "hour_ganji": hour_ganji,

        "day_gan": day_gan,
        "day_ji": day_ji,

        # ✅ 시주 상태 선언 (핵심)
        "hour_pillar_state": {
            "status": hour_status,  # observed | unknown
            "observability": "observed" if hour_status == "observed" else "unobserved",
            "confidence": 1.0 if hour_status == "observed" else 0.0,
            "note": "No estimation applied" if hour_status != "observed" else None,
        },

        "sipshin": {
            "원국_년간": sip_year,
            "원국_월간": sip_month,
            "원국_시간": sip_hour,  # unknown이면 None
        },

        "unseong": {
            "년지": un_year,
            "월지": un_month,
            "일지": un_day,
            "시지": un_hour,  # unknown이면 None
        },

        "pillars_detail": pillars_detail,

        "daeun_labels": daeun_labels,
        "daeun_year_traditional": daeun_year_traditional,
        "daeun_float": age_raw,
        "daeun_rounded": round(age_raw),
        "daeun_detail": daeun_detail,

        "2026_flow": yearly_flow,
        "2026_jaemul": yearly_jaemul,
        "2026_love": yearly_love,
        "2026_job": yearly_job,
    }

    # DataFrame 1행 형태 (기존 기능 유지)
    df_row = create_saju_row_with_textblock(
        name=name,
        birth_str=birth.strftime("%Y-%m-%d %H:%M"),
        gender=gender,
        year_ganji=year_ganji,
        month_ganji=month_ganji,
        day_ganji=day_ganji,
        hour_ganji=hour_ganji,
        sipshin=saju_info["sipshin"],
        unseong=saju_info["unseong"],
        daeun_labels=daeun_labels,
        daeun_year_traditional=daeun_year_traditional,
        daeun_float=age_raw,
        daeun_rounded=round(age_raw),
        daeun_ganji_list=daeuns,
        daeun_startpoints=startpoints,
    )

    if return_dataframe:
        return saju_info, df_row

    return saju_info, df_row


# ---------------------------------------------------------
# 📌 2) 오늘의 간지
# ---------------------------------------------------------
def get_today_ganji():
    df = df = pd.read_csv(DATA_DIR / "manselyeog_1900.csv")
    df["양력일자"] = pd.to_datetime(df["양력일자"])

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    row = df[df["양력일자"] == today]

    if row.empty:
        raise ValueError("오늘 날짜에 해당하는 만세력 데이터가 없습니다.")

    row = row.iloc[0]
    day_ganji = row["日辰"]
    return day_ganji


# ---------------------------------------------------------
# 📌 3) 오늘의 운세용 구조 생성 (일운)
# ---------------------------------------------------------
def get_today_unse(day_gan: str, today_ganji: str):
    today_gan, today_ji = today_ganji[0], today_ganji[1]
    today_sipshin = get_sipshin(day_gan, today_gan)
    today_un12 = get_12un(today_gan, today_ji)

    return {
        "ganji": today_ganji,
        "sipshin": today_sipshin,
        "unseong": today_un12,
    }


# ---------------------------------------------------------
# 📌 3-A) 오늘의 재물/연애/직장 작동 구조 생성 (일운 도메인)
# ---------------------------------------------------------
def build_today_domain_operation(day_gan: str, today_ganji: str, gender: int):
    today_ji = today_ganji[1]

    jaemul_keys = ["정재", "편재"]
    love_keys = ["정재", "편재"] if gender == 1 else ["정관", "편관"]
    job_keys = ["정관", "편관", "식신", "상관"]

    def _build(keys):
        out = []
        for g in GAN_10:
            s = get_sipshin(day_gan, g)
            if s in keys:
                u = get_12un(g, today_ji)
                out.append([s, g, u])
        return out

    return {
        "today_jaemul": _build(jaemul_keys),
        "today_love": _build(love_keys),
        "today_job": _build(job_keys),
    }


# ---------------------------------------------------------
# 📌 4) 월운(月運)용 구조 생성
# ---------------------------------------------------------
def get_month_unse_for_date(day_gan: str, target_date: datetime):
    df = pd.read_csv(DATA_DIR / "manselyeog_1900.csv")
    df["양력일자"] = pd.to_datetime(df["양력일자"])

    base_date = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    row = df[df["양력일자"] == base_date]

    if row.empty:
        raise ValueError("해당 날짜에 대한 월운 데이터를 찾을 수 없습니다.")

    row = row.iloc[0]
    month_ganji = row["月建"]
    month_gan, month_ji = month_ganji[0], month_ganji[1]

    month_sipshin = get_sipshin(day_gan, month_gan)
    month_un12 = get_12un(month_gan, month_ji)

    return {
        "ganji": month_ganji,
        "sipshin": month_sipshin,
        "unseong": month_un12,
    }


def get_today_month_unse(day_gan: str):
    today = datetime.now()
    return get_month_unse_for_date(day_gan, today)


# -------------------------------------------------------------
# 2026년(또는 임의 연도) 전체 월운 JSON 생성
# -------------------------------------------------------------
def get_year_month_unse(day_gan: str, year: int, df_manse) -> list:
    df_all = df_manse.copy()

    if "date" in df_all.columns:
        df_all["date"] = pd.to_datetime(df_all["date"])
    else:
        df_all["date"] = pd.to_datetime(df_all["양력일자"])

    df_all = df_all.sort_values("date").reset_index(drop=True)

    df_all["prev_month_ganji"] = df_all["月建"].shift(1)
    df_all["month_change"] = df_all["月建"] != df_all["prev_month_ganji"]

    start_range = pd.to_datetime(f"{year}-01-01")
    end_range = pd.to_datetime(f"{year + 1}-03-01")

    df_range = df_all[(df_all["date"] >= start_range) & (df_all["date"] < end_range)]
    changes = df_range[df_range["month_change"]].reset_index(drop=True)

    if len(changes) < 14:
        limit = max(0, len(changes) - 1)
    else:
        limit = 13

    month_unse_list = []

    for i in range(limit):
        row = changes.iloc[i]
        start_dt = row["date"]
        boundary_dt = changes.iloc[i + 1]["date"]
        end_dt = boundary_dt - pd.Timedelta(days=1)

        month_ganji = row["月建"]
        month_gan = month_ganji[0]
        month_ji = month_ganji[1]

        start_date_str = start_dt.strftime("%Y-%m-%d")
        end_date_str = end_dt.strftime("%Y-%m-%d")

        sipshin = get_sipshin(day_gan, month_gan)
        un12 = get_12un(month_gan, month_ji)

        note = (
            f"이 월운은 {start_date_str} ~ {end_date_str} 기간에 적용됩니다. "
            "사주 명리는 음력도 양력도 아닌 절기력으로 흐르기 때문에, "
            "새해(1월 1일)부터 입춘 전까지는 사실 지난해의 기운이 조금 더 이어집니다. "
            "그래서 TBOO는 이 구간을 포함해 13개월 월운으로 안내합니다."
        )

        month_unse_list.append(
            {
                "ganji": month_ganji,
                "sipshin": sipshin,
                "unseong": un12,
                "start_date": start_date_str,
                "end_date": end_date_str,
                "note": note,
            }
        )

    return month_unse_list


# ---------------------------------------------------------
# 📌 5) 특정 날짜 일운(日運) 계산 함수
# ---------------------------------------------------------
def get_day_unse_for_date(day_gan: str, target_date: datetime):
    df = pd.read_csv(DATA_DIR / "manselyeog_1900.csv")
    df["양력일자"] = pd.to_datetime(df["양력일자"])

    base_date = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    row = df[df["양력일자"] == base_date]

    if row.empty:
        raise ValueError("해당 날짜에 대한 일운 데이터를 찾을 수 없습니다.")

    row = row.iloc[0]
    day_ganji = row["日辰"]
    g, j = day_ganji[0], day_ganji[1]

    sip = get_sipshin(day_gan, g)
    un12 = get_12un(g, j)

    return {
        "date": base_date.strftime("%Y-%m-%d"),
        "ganji": day_ganji,
        "sipshin": sip,
        "unseong": un12,
    }

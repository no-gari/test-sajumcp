from datetime import datetime, timedelta
import pandas as pd

GAN_10 = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
JI_12 = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
YANG_GANS = ['甲','丙','戊','庚','壬']
MINUTES_PER_YEAR = 4320

def get_sex_direction(year_gan, gender):
    yang = year_gan in YANG_GANS
    return 1 if (gender == 1 and yang) or (gender == 2 and not yang) else -1

def get_daeun_age_and_startpoints(birth: datetime, solar_terms: dict, direction: int):
    year = str(birth.year)
    if year not in solar_terms:
        return 8, birth, [], birth.year + 7
    terms = solar_terms[year]
    term_list = [datetime.fromisoformat(t['datetime']).replace(tzinfo=None) for t in terms]
    term_list.sort()
    if direction == 1:
        future_terms = [dt for dt in term_list if dt > birth]
        if not future_terms:
            return 8, birth, [], birth.year + 7
        target_dt = future_terms[0]
        delta_min = (target_dt - birth).total_seconds() / 60
    else:
        past_terms = [dt for dt in term_list if dt <= birth]
        if not past_terms:
            return 8, birth, [], birth.year + 7
        target_dt = past_terms[-1]
        delta_min = (birth - target_dt).total_seconds() / 60

    age_raw = delta_min / MINUTES_PER_YEAR
    age_rounded = round(age_raw)
    age_rounded = max(1, min(age_rounded, 10))
    daeun_start_dt = birth + timedelta(days=365.25 * age_raw)
    startpoints = [daeun_start_dt + timedelta(days=365.25 * 10 * i) for i in range(10)]

    if age_rounded == 1:
        daeun_year_traditional = birth.year + 1
    else:
        daeun_year_traditional = birth.year + age_rounded - 1

    return age_raw, daeun_start_dt, startpoints, daeun_year_traditional

def get_next_ganji(gan, ji, step):
    return (GAN_10[(GAN_10.index(gan) + step) % 10], JI_12[(JI_12.index(ji) + step) % 12])

def get_daeun_ganji(start_gan, start_ji, direction, count=10):
    result = []
    gan, ji = start_gan, start_ji
    for _ in range(count):
        gan, ji = get_next_ganji(gan, ji, direction)
        result.append((gan, ji))
    return result

def get_sipshin(day_gan: str, other_gan: str, sipshin_table: dict) -> str:
    return sipshin_table.get(f"{day_gan}-{other_gan}", "")

def get_unseong_for_ji(day_gan: str, target_ji: str, unseong_table: dict) -> str:
    for unseong, mapping in unseong_table.items():
        if mapping.get(day_gan) == target_ji:
            return unseong
    return ""

def format_daeun_entries(start_age_float, ganji_list, startpoints, birth_year, daeun_rounded=None):
    labels = []
    base_age = daeun_rounded if daeun_rounded is not None else round(start_age_float)
    for i, (gan, ji) in enumerate(ganji_list):
        label_age = base_age - 1 + i * 10 if base_age > 1 else 1 + i * 10
        start_year = birth_year + label_age
        labels.append(f"만 {label_age}세부터 {gan}{ji} 대운 시작 ({start_year})")
    return labels

def create_saju_row_with_textblock(
    name: str,
    birth_str: str,
    gender: int,
    year_ganji: str,
    month_ganji: str,
    day_ganji: str,
    hour_ganji: str,
    sipshin: dict,
    unseong: dict,
    daeun_labels: list,
    daeun_year_traditional=None,
    daeun_float=None,
    daeun_rounded=None,
    daeun_ganji_list: list = None,
    daeun_startpoints: list = None,
    yearly_unse_2025: list = None,
    sipshin_table: dict = None,
    unseong_table: dict = None
) -> pd.DataFrame:

    # -------------------------------------------------
    # 기본 정보
    # -------------------------------------------------
    birth_dt = datetime.strptime(birth_str, "%Y-%m-%d %H:%M")
    gender_str = "남자" if gender == 1 else "여자"

    day_gan = day_ganji[0]
    month_gan = month_ganji[0]
    year_gan = year_ganji[0]

    # -------------------------------------------------
    # ✅ 핵심 수정: 시주 미상 방어 가드
    # -------------------------------------------------
    if hour_ganji:
        hour_gan = hour_ganji[0]
        hour_ji = hour_ganji[1]
        hour_ganji_display = hour_ganji
    else:
        hour_gan = ""
        hour_ji = ""
        hour_ganji_display = "미상"

    # -------------------------------------------------
    # 텍스트 블록 구성
    # -------------------------------------------------
    lines = []
    lines.append(
        f"이름: {name} / 출생일시: {birth_dt.strftime('%Y-%m-%d %H:%M')} / 성별: {gender_str}"
    )
    lines.append(
        f"일간: {day_gan} / 년주: {year_ganji} / 월주: {month_ganji} / "
        f"일주: {day_ganji} / 시주: {hour_ganji_display}"
    )

    lines.append(
        f"십신 - 년간: {year_gan} → {sipshin.get('년간', '')} / "
        f"월간: {month_gan} → {sipshin.get('월간', '')} / "
        f"시간: {hour_gan} → {sipshin.get('시간', '') if hour_ganji else ''}"
    )

    lines.append(
        f"십이운성 - 년지: {year_ganji[1]} → {unseong.get('년지', '')} / "
        f"월지: {month_ganji[1]} → {unseong.get('월지', '')} / "
        f"일지: {day_ganji[1]} → {unseong.get('일지', '')} / "
        f"시지: {hour_ji} → {unseong.get('시지', '') if hour_ganji else ''}"
    )

    # -------------------------------------------------
    # 대운 흐름 (기존 로직 유지)
    # -------------------------------------------------
    lines.append("☯ 대운 흐름 (전통 연해자평 기준):")
    if daeun_ganji_list:
        for i, ((gan, ji), label) in enumerate(zip(daeun_ganji_list, daeun_labels)):
            lines.append(f"  • {label}")
            if sipshin_table and unseong_table:
                lines.append(
                    f"    → 월간 {month_gan}: "
                    f"{get_sipshin(day_gan, month_gan, sipshin_table)} → "
                    f"{ji}에서 {get_unseong_for_ji(day_gan, ji, unseong_table)}"
                )
                lines.append(
                    f"    → 년간 {year_gan}: "
                    f"{get_sipshin(day_gan, year_gan, sipshin_table)} → "
                    f"{ji}에서 {get_unseong_for_ji(day_gan, ji, unseong_table)}"
                )
                if hour_ganji:
                    lines.append(
                        f"    → 시간 {hour_gan}: "
                        f"{get_sipshin(day_gan, hour_gan, sipshin_table)} → "
                        f"{ji}에서 {get_unseong_for_ji(day_gan, ji, unseong_table)}"
                    )
                lines.append(
                    f"    → 대운간 {gan}: "
                    f"{get_sipshin(day_gan, gan, sipshin_table)} → "
                    f"{ji}에서 {get_unseong_for_ji(day_gan, ji, unseong_table)}"
                )

    # -------------------------------------------------
    # 기타 정보
    # -------------------------------------------------
    lines.append(f"\n📅 전통 연해자평 대운 적용 연도: {daeun_year_traditional}년")
    lines.append(f"🧮 대운수: 실수={round(daeun_float, 2)}세 / 정수={daeun_rounded}세")

    if yearly_unse_2025:
        lines.append("\n☯ 2025년 을사년 운세 흐름:")
        for line in yearly_unse_2025:
            lines.append(f"  • {line}")

    text_block = "\n".join(lines)

    # -------------------------------------------------
    # DataFrame row
    # -------------------------------------------------
    row = {
        "텍스트_블록": text_block,
        "이름": name,
        "출생일시": birth_str,
        "성별": gender_str,
        "일간": day_gan,
        "년주": year_ganji,
        "월주": month_ganji,
        "일주": day_ganji,
        "시주": hour_ganji,  # None 그대로 유지
        "십신_년간": sipshin.get('년간', ''),
        "십신_월간": sipshin.get('월간', ''),
        "십신_시간": sipshin.get('시간', '') if hour_ganji else '',
        "운성_년지": unseong.get('년지', ''),
        "운성_월지": unseong.get('월지', ''),
        "운성_일지": unseong.get('일지', ''),
        "운성_시지": unseong.get('시지', '') if hour_ganji else '',
        "전통_대운시작연도": daeun_year_traditional,
        "대운수_실수": round(daeun_float, 2),
        "대운수_정수": daeun_rounded,
    }

    return pd.DataFrame([row])

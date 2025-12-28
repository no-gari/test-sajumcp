"""engine/core/engine_core.py

TBOO Meaning Engine (Core) — Slots Only
--------------------------------------

This module converts the **calculated saju JSON** (from the local
calculation engine) into a **meaning payload** that is safe and stable
to feed into an LLM renderer.

Key principles
1) NO prose generation here.
2) NO re-calculation of ganji/sipshin/unseong.
3) Output is **normalized meaning slots** (semantic keys + compact
   evidence), so prompt changes do not require engine changes.

Engine responsibility:
- Return deterministic meaning slots + minimal evidence.

Renderer responsibility:
- Turn slots into narrative (tone/structure/poetry).
"""

from __future__ import annotations

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent   # meaning_engine/
SCHEMA_DIR = BASE_DIR / "schemas" / "canonical"

from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------
# Paths / loaders
# ---------------------------------------------------------------------


def load_json(path: Path) -> dict:
    """Load JSON with UTF-8 encoding."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------
# Schemas (required for Ganji Ontology only)
# ---------------------------------------------------------------------
# NOTE: narrative_directives 제거 (A-2 YES)
GANJI_STEM_LEXICON = load_json(SCHEMA_DIR / "ganji_stem_lexicon_v1.0.json")
GANJI_BRANCH_LEXICON = load_json(SCHEMA_DIR / "ganji_branch_lexicon_v1.0.json")
GANJI_COMBINATION_RULES = load_json(SCHEMA_DIR / "ganji_combination_rules_v1.0.json")


# ---------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------

def safe_get(d: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    cur: Any = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def split_ganji(ganji: str) -> Tuple[Optional[str], Optional[str]]:
    if isinstance(ganji, str) and len(ganji) == 2:
        return ganji[0], ganji[1]
    return None, None


def _dedupe(seq: List[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for x in seq:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out


# ---------------------------------------------------------------------
# Phase 7 — Ganji Ontology (kept, but no prose)
# ---------------------------------------------------------------------

def judge_combination_type(stem_traits: dict, branch_env: dict) -> dict:
    rules = GANJI_COMBINATION_RULES.get("decision", {}).get("rules", [])
    fallback = {"type": "Latency", "why": ["fallback"], "rule_id": None}

    for r in rules:
        cond = r.get("if", {})
        ok = True
        for k, v in cond.items():
            src, key = k.split(".")
            if src == "stem" and stem_traits.get(key) not in v:
                ok = False
            if src == "branch" and branch_env.get(key) not in v:
                ok = False
        if ok:
            return {
                "type": r["then"]["type"],
                "why": r["then"].get("why", []),
                "rule_id": r.get("id"),
            }
    return fallback


def compute_ganji_ontology(gan: str, ji: str) -> dict:
    stem = GANJI_STEM_LEXICON.get("stems", {}).get(gan, {})
    branch = GANJI_BRANCH_LEXICON.get("branches", {}).get(ji, {})

    # NEW: stem desire vector (NO interpretation)
    stem_desire = {
        "vector": stem.get("desire_vector"),
        "existential_drive": stem.get("existential_drive"),
        "force_profile": stem.get("force_profile"),
        "tension_axis": stem.get("tension_axis"),
        "meta_archetype_refs": stem.get("meta_archetype_refs", []),
    } if stem else None

    judgement = judge_combination_type(
        stem.get("force_profile", {}),
        branch
    )

    return {
        "gan": gan,
        "ji": ji,
        "stem_desire": stem_desire,
        "branch_environment": branch,
        "combination_type": judgement["type"],
        "combination_judgement": judgement,
    }



def compute_pillars_ontology(saju: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for key in ("year", "month", "day", "hour"):
        ganji = saju.get(key, "")
        gan, ji = split_ganji(ganji)
        if gan and ji:
            out[key] = compute_ganji_ontology(gan, ji)
    return out


# ---------------------------------------------------------------------
# Meaning key maps (minimal, deterministic)
# ---------------------------------------------------------------------

COMBINATION_TO_EXISTENCE_KEY = {
    "Latency": "existence.latent",
    "Amplification": "existence.amplified",
    "Resistance": "existence.resistant",
    "Transformation": "existence.transformative",
}

UNSEONG_TO_RHYTHM_KEY = {
    "장생": "rhythm.growing",
    "목욕": "rhythm.sensitive",
    "관대": "rhythm.expanding",
    "건록": "rhythm.stable",
    "제왕": "rhythm.peak",
    "쇠": "rhythm.declining",
    "병": "rhythm.fatigue",
    "사": "rhythm.closing",
    "묘": "rhythm.resting",
    "절": "rhythm.cutoff",
    "태": "rhythm.conceiving",
    "양": "rhythm.birth",
}

SIPSHIN_TO_EMOTION_ENGINE_KEY = {
    # 관계/자기
    "비견": "emotion.self_aligned",
    "겁재": "emotion.self_competing",
    # 표현/생산
    "식신": "emotion.express_nurture",
    "상관": "emotion.express_breakthrough",
    # 재물/교환
    "정재": "emotion.exchange_stable",
    "편재": "emotion.exchange_dynamic",
    # 규범/관계(사회)
    "정관": "emotion.order_stable",
    "편관": "emotion.order_pressure",
    # 학습/내면
    "정인": "emotion.absorb_stable",
    "편인": "emotion.absorb_unique",
}


# ---------------------------------------------------------------------
# Slot derivations (NO prose, only semantic keys)
# ---------------------------------------------------------------------

def derive_existence_type(day_ontology: Dict[str, Any]) -> str:
    ctype = day_ontology.get("combination_type", "Latency")
    return COMBINATION_TO_EXISTENCE_KEY.get(ctype, "existence.latent")


def derive_desire_direction(day_ontology: Dict[str, Any]) -> Optional[str]:
    stem_desire = day_ontology.get("stem_desire")
    if not stem_desire:
        return None

    vector = stem_desire.get("vector")
    if not vector:
        return None

    return f"desire.{vector}"


def derive_action_rhythm(unseong_map: Dict[str, Any]) -> Optional[str]:
    # day pillar rhythm (best-effort)
    day_un = unseong_map.get("pillar_day") or unseong_map.get("day")
    if not day_un:
        return None
    return UNSEONG_TO_RHYTHM_KEY.get(day_un, f"rhythm.{day_un}")


def derive_emotion_engines(sipshin_map: Dict[str, Any]) -> List[str]:
    # prioritize month/year/hour (environment + strategy + practice)
    keys: List[str] = []
    for k in ("pillar_year", "pillar_month", "pillar_hour"):
        s = sipshin_map.get(k)
        if not s:
            continue
        keys.append(SIPSHIN_TO_EMOTION_ENGINE_KEY.get(s, f"emotion.{s}"))
    return _dedupe(keys)


def derive_year_theme(year_flow: List[List[Any]]) -> List[str]:
    """
    year_flow format example:
      [
        ["pillar_month","戊","상관","제왕"],
        ["pillar_year","乙","편인","장생"],
        ...
        ["세운_천간_2026","丙","겁재","제왕"]
      ]
    """
    if not year_flow:
        return ["year_theme.unknown"]

    top = year_flow[0]
    sipshin = top[2] if len(top) > 2 else None
    un12 = top[3] if len(top) > 3 else None

    theme: List[str] = []
    if sipshin:
        theme.append(f"year_theme.by_{sipshin}")
    if un12:
        theme.append(f"year_theme.state_{UNSEONG_TO_RHYTHM_KEY.get(un12, un12)}")
    return _dedupe(theme) if theme else ["year_theme.unknown"]


def derive_domain_flow(domain_ops: List[List[Any]], domain: str) -> List[str]:
    """
    domain ops example:
      [ ["정재","庚","목욕"], ["편재","辛","병"] ]
    """
    out: List[str] = []
    for row in domain_ops or []:
        sipshin = row[0] if len(row) > 0 else None
        un12 = row[2] if len(row) > 2 else None
        if sipshin:
            out.append(f"{domain}.engine_{sipshin}")
        if un12:
            out.append(f"{domain}.state_{UNSEONG_TO_RHYTHM_KEY.get(un12, un12)}")
    return _dedupe(out)


def derive_today_wave(today_block: Dict[str, Any]) -> List[str]:
    sipshin = today_block.get("sipshin")
    un12 = today_block.get("unseong")
    out: List[str] = []
    if sipshin:
        out.append(f"today.emotion_{SIPSHIN_TO_EMOTION_ENGINE_KEY.get(sipshin, sipshin)}")
    if un12:
        out.append(f"today.state_{UNSEONG_TO_RHYTHM_KEY.get(un12, un12)}")
    return _dedupe(out) if out else ["today.unknown"]


# ---------------------------------------------------------------------
# Meaning slots builder (service router)
# ---------------------------------------------------------------------

def build_meaning_slots(
    calculated: Dict[str, Any],
    context_type: str,
    *,
    pillars_ontology: Dict[str, Any],
    day_ontology: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Returns normalized semantic keys (meaning slots).
    No prose. No “you are ...” sentences.
    """
    sipshin_map = calculated.get("sipshin", {}) or {}
    unseong_map = calculated.get("unseong", {}) or {}

    if context_type == "natal":
        return {
            "existence_type": derive_existence_type(day_ontology),
            "desire_direction": derive_desire_direction(day_ontology),
            "emotion_engines": derive_emotion_engines(sipshin_map),
            "action_rhythm": derive_action_rhythm(unseong_map),
            "pillars_combination_types": {
                k: v.get("combination_type") for k, v in pillars_ontology.items()
            },
        }

    if context_type == "fortune_2026_overall":
        y = calculated.get("year_2026_operation", {}) or {}
        flow = y.get("flow", []) or []
        return {
            "year_theme": derive_year_theme(flow),
            "year_flow": [
                {
                    "source": row[0] if len(row) > 0 else None,
                    "gan": row[1] if len(row) > 1 else None,
                    "sipshin": row[2] if len(row) > 2 else None,
                    "unseong": row[3] if len(row) > 3 else None,
                }
                for row in flow
            ],
            "anchors": {
                "natal_exist": derive_existence_type(day_ontology),
                "natal_rhythm": derive_action_rhythm(unseong_map),
            },
        }

    if context_type == "fortune_2026_money":
        y = calculated.get("year_2026_operation", {}) or {}
        ops = y.get("jaemul", []) or []
        return {
            "money_flow": derive_domain_flow(ops, "money"),
            "drivers": {
                "emotion_engines": derive_emotion_engines(sipshin_map),
                "action_rhythm": derive_action_rhythm(unseong_map),
            },
        }

    if context_type == "fortune_2026_love":
        y = calculated.get("year_2026_operation", {}) or {}
        ops = y.get("love", []) or []
        return {
            "love_flow": derive_domain_flow(ops, "love"),
            "drivers": {
                "emotion_engines": derive_emotion_engines(sipshin_map),
                "action_rhythm": derive_action_rhythm(unseong_map),
            },
        }

    if context_type == "fortune_2026_job":
        y = calculated.get("year_2026_operation", {}) or {}
        ops = y.get("job", []) or []
        return {
            "job_flow": derive_domain_flow(ops, "job"),
            "drivers": {
                "emotion_engines": derive_emotion_engines(sipshin_map),
                "action_rhythm": derive_action_rhythm(unseong_map),
            },
        }

    if context_type == "today":
        today_block = calculated.get("today", {}) or {}

        # ─────────────────────────────────────────────
        # [PATCH] today contract adapter
        # - new: today.base / today.operation
        # - legacy: flat today
        # ─────────────────────────────────────────────
        if isinstance(today_block, dict) and isinstance(today_block.get("operation"), dict):
            today_ops = today_block.get("operation", {}) or {}
        else:
            # legacy flat today
            today_ops = {
                "money": today_block.get("today_jaemul", []),
                "love": today_block.get("today_love", []),
                "job": today_block.get("today_job", []),
            }

        return {
            "today_wave": derive_today_wave(today_block),  # base/legacy는 derive_today_wave에서 처리
            "today_money": derive_domain_flow(today_ops.get("money", []) or [], "money"),
            "today_love": derive_domain_flow(today_ops.get("love", []) or [], "love"),
            "today_job": derive_domain_flow(today_ops.get("job", []) or [], "job"),
        }


# ---------------------------------------------------------------------
# Engine entry
# ---------------------------------------------------------------------

def run_engine(calculated_saju_json: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry: returns meaning engine output (slots only)."""
    saju = calculated_saju_json.get("saju", {})
    day_ganji = saju.get("day", "")
    day_gan, day_ji = split_ganji(day_ganji)

    if not (day_gan and day_ji):
        raise ValueError("Invalid 'saju.day' ganji. Expected 2-char string like '丁亥'.")

    pillars_ontology = compute_pillars_ontology(saju)
    day_ontology = pillars_ontology.get("day") or compute_ganji_ontology(day_gan, day_ji)

    meaning_payload = {
        "natal": {
            "slots": build_meaning_slots(
                calculated_saju_json,
                "natal",
                pillars_ontology=pillars_ontology,
                day_ontology=day_ontology,
            ),
            "evidence": {
                "pillars": saju,
                "sipshin": calculated_saju_json.get("sipshin", {}),
                "unseong": calculated_saju_json.get("unseong", {}),
            },
        },
        "fortune_2026_overall": {
            "slots": build_meaning_slots(
                calculated_saju_json,
                "fortune_2026_overall",
                pillars_ontology=pillars_ontology,
                day_ontology=day_ontology,
            ),
            "evidence": calculated_saju_json.get("year_2026_operation", {}),
        },
        "fortune_2026_money": {
        "slots": build_meaning_slots(
            calculated_saju_json,
            "fortune_2026_money",
            pillars_ontology=pillars_ontology,
            day_ontology=day_ontology,
        ),
        # ─────────────────────────────────────────────
        # [PATCH] year_2026_operation money / jaemul alias
        # ─────────────────────────────────────────────
        "evidence": (
            safe_get(calculated_saju_json, "year_2026_operation", "money", default=None)
            or safe_get(calculated_saju_json, "year_2026_operation", "jaemul", default=[])
        ),
    },

        "fortune_2026_love": {
            "slots": build_meaning_slots(
                calculated_saju_json,
                "fortune_2026_love",
                pillars_ontology=pillars_ontology,
                day_ontology=day_ontology,
            ),
            "evidence": safe_get(calculated_saju_json, "year_2026_operation", "love", default=[]),
        },
        "fortune_2026_job": {
            "slots": build_meaning_slots(
                calculated_saju_json,
                "fortune_2026_job",
                pillars_ontology=pillars_ontology,
                day_ontology=day_ontology,
            ),
            "evidence": safe_get(calculated_saju_json, "year_2026_operation", "job", default=[]),
        },
        "today": {
            "slots": build_meaning_slots(
                calculated_saju_json,
                "today",
                pillars_ontology=pillars_ontology,
                day_ontology=day_ontology,
            ),
            "evidence": calculated_saju_json.get("today", {}),
        },
    }

    # NOTE: narrative_directives 완전 제거 (A-2 YES)
    return {
        "meta": {
            "engine": "TBOO_MEANING_ENGINE",
            "version": "meaning_slots_v1.1",
            "note": "Slots-only output. No materials, no narrative directives.",
        },
        "subject": calculated_saju_json.get("user_info", calculated_saju_json.get("subject", {})),
        "context": calculated_saju_json.get("context", {}),
        "pillars_ontology": pillars_ontology,
        "meaning_payload": meaning_payload,
    }

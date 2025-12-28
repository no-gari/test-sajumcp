# TBOO AI SAJU ENGINE (Calculation → Meaning → Fusion)

This repository contains the core engine pipeline for **TBOO AI 사주 해석 시스템**.

The system is intentionally divided into **three independent engines**:
1. Calculation Engine (사주 계산)
2. Meaning Engine (의미 슬롯 생성)
3. Fusion Engine (최종 해석 계약 생성)

Text generation, interpretation, and advice are **NOT handled here**.
They are delegated to LLM prompts and renderers outside this repository.

---

## 1. Design Philosophy

### Separation of Responsibility (Strict)

| Layer | Responsibility | What it MUST NOT do |
|-----|---------------|---------------------|
| Calculation Engine | Compute factual saju data | No interpretation |
| Meaning Engine | Build meaning slots / frames | No sentence generation |
| Fusion Engine | Merge results into one contract | No logic inference |
| LLM Layer (external) | Narrative & advice generation | No calculation |

This separation is intentional and **must not be violated**.

---

## 2. Folder Structure Overview

.
├── calculation_engine/
│ ├── data/ # Calendar, solar terms
│ ├── engine/ # Core calculation logic
│ ├── main.py # CLI entry
│ ├── output/ # Calculation results (JSON)
│ └── README.md
│
├── meaning_engine/
│ ├── engine/engine_core.py # Meaning-slot builder
│ ├── schemas/canonical/ # Ganji reference schemas
│ ├── main.py # CLI entry
│ ├── output/ # Meaning JSON results
│ └── README.md
│
├── fusion_engine/
│ └── build_contract.py # Merge calculation + meaning
│
├── contracts/
│ └── tboo_interpretation_contract_v1.json
│
├── output/
│ └── tboo_interpretation_contract_*.json
│
├── samples/
│ └── example calculation JSONs
│
└── README.md ← (this file)

yaml
코드 복사

---

## 3. Calculation Engine

### Role
- Computes saju pillars, daeun, today flow, yearly operations, etc.
- Outputs **pure factual data**.

### Output
- JSON only
- No text, no emotional meaning, no advice
- Example:
calculation_engine/output/서장원_saju_v33_YYYYMMDD_HHMMSS.json

markdown
코드 복사

---

## 4. Meaning Engine

### Role
- Transforms calculation results into **meaning slots**
- Normalizes domains (today / year / money / love / job)
- Adapts legacy keys (e.g. jaemul → money)

### Important Notes
- Empty arrays or null values are **intentional**
- `emotion_engines`, `action_rhythm` are NOT generated here
- Narrative logic belongs to LLM prompts, not this engine

### Output
- Meaning-slot JSON only
- Example:
meaning_engine/output/meaning_v1_YYYYMMDD_HHMMSS_hour-null.json

yaml
코드 복사

---

## 5. Fusion Engine

### Role
- Merges calculation JSON + meaning JSON
- Produces a **single interpretation contract**

### Output
- Final contract JSON stored in root `./output/`
- Example:
output/tboo_interpretation_contract_YYYYMMDD_HHMMSS.json

yaml
코드 복사

This file is the **only input required by LLM renderers**.

---

## 6. Execution Order (Recommended)

```bash
# 1. Run calculation
python calculation_engine/main.py

# 2. Run meaning engine
python meaning_engine/main.py --input calculation_engine/output

# 3. Build final contract
python fusion_engine/build_contract.py
If a directory is passed as input, the latest JSON is selected automatically.

Specific files can be passed explicitly for reproducible testing.

7. What This Repository Does NOT Do
❌ Generate natural language explanations

❌ Provide advice or strategy

❌ Perform RAG or document retrieval

❌ Interpret emotions or destiny in text form

Those responsibilities belong to:

LLM system prompts

Rendering / presentation layer

Application services

8. Final Note for Developers
This project prioritizes:

Determinism

Traceability

Clean separation of logic

Long-term maintainability

If you feel tempted to add “just a little interpretation” inside an engine,
do not.
That boundary is the core strength of this architecture.
# TBOO Meaning Engine

This engine transforms calculated saju data into **meaning slots** only.
It does NOT generate sentences, advice, or narratives.

## Role

- Input: JSON output from `calculation_engine`
- Output: Meaning-slot JSON for LLM interpretation
- Responsibility boundary:
  - ✔ Extract structure, flows, ontologies
  - ✔ Normalize domains (today / year / fortune)
  - ✖ No text generation
  - ✖ No emotional advice
  - ✖ No strategy suggestion

## Output Characteristics

- Slots-only design
- Empty arrays or null values are intentional
  (LLM prompt layer fills them)
- Supports:
  - Natal ontology
  - Today (base / operation)
  - Year fortune domains (money / love / job)

## Folder Structure

- `engine/engine_core.py`
  Core meaning-slot builder
- `schemas/canonical/`
  Ganji, branch, stem reference schemas
- `main.py`
  CLI entry point
- `output/`
  Generated meaning JSONs

## Usage

```bash
python meaning_engine/main.py \
  --input calculation_engine/output/서장원_saju_v33_*.json

📐 TBOO Calculation Engine

이 폴더는 TBOO AI 사주 시스템의 계산 전용 엔진입니다.
사주 계산 결과를 의미 해석이 가능한 JSON 계약 형태로 출력하는 것이 유일한 책임입니다.

1. 역할 (What this engine does)

사주 원국(년/월/일/시) 계산

시주 관측/미관측의 명시적 선언

대운 / 연운 / 일운 계산

today의 base / operation 분리 계산

결과를 TBOO JSON Schema v3.3 형태로 출력

👉 이 엔진은 의미를 만들지 않습니다.
👉 판단, 조언, 해석 문장은 생성하지 않습니다.

2. 이 엔진이 보장하는 것

계산 정확성

구조적 명확성

다음 항목의 계약(JSON) 고정:

✅ today

today.base
→ 일간 기준 오늘의 상태 (ganji / sipshin / unseong)

today.operation
→ 작동 십신/십이운성
→ 도메인 키: money / love / job

✅ year

year_2026_operation
→ 연 단위 작동 흐름 (flow + domain operation)

✅ daeun

대운 상세 흐름 + 요약 정보

✅ hour_pillar_state

시주 관측 여부 및 신뢰도

추정하지 않음, 선언만 함

3. 이 엔진이 보장하지 않는 것 (중요)

해석 문장 생성

좋고 나쁨 판단

조언, 전략, 예측

월운(JSON 출력)

⚠️ 월운 계산 로직은 엔진 내부에 존재하지만,
⚠️ 현재 서비스 단계에서는 JSON 계약에 포함되지 않습니다.

4. JSON 계약 요약 (v3.3)

계산 엔진은 **JSON 계약을 고정점(anchor)**으로 삼습니다.

key 의미:

key	의미
today.base	기준 상태
today.operation.*	작동 상태
year_2026_operation	연 단위 작동
daeun	환경적 흐름
hour_pillar_state	관측 신뢰
5. 변경 규칙 (절대 중요)

JSON key 변경 시
→ meaning engine과 반드시 동시 수정

base / operation 구조는 계약이며 임의 변경 금지

계산 엔진 내부 변수명과
JSON 출력 key는 다를 수 있음

6. 다음 단계

meaning engine은 이 JSON을 읽기 전용으로 사용

calculation engine은
meaning engine의 요청으로 구조를 임의 변경하지 않음

요약

이 엔진은 계산한다.
해석은 다른 엔진의 책임이다.
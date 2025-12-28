# TBOO Engine - 사주 분석 시스템 (Node.js MCP 서버)

한국 전통 사주명리학 기반 분석 시스템입니다. Python 엔진에서 **Node.js + TypeScript MCP 서버**로 전환되어 Vercel 배포가 가능합니다.

## 🎯 프로젝트 구조

### ⭐ New: Node.js MCP Server (메인)
- `src/` - TypeScript 기반 MCP 서버 및 사주 엔진
- `api/` - Vercel Serverless Functions
- `dist/` - 컴파일된 JavaScript 출력

### Legacy: Python Engines (참고용)
- `calculation_engine/` - Python 기반 사주 계산 엔진
- `meaning_engine/` - Python 기반 의미 해석 엔진
- `fusion_engine/` - Python 기반 데이터 융합

## 🚀 빠른 시작

### 자동 설치

```bash
./setup.sh
```

### 수동 설치

```bash
# 1. 패키지 설치
npm install

# 2. 빌드
npm run build

# 3. 환경 변수 설정
cp .env.example .env
# .env 파일에 OpenAI API 키 입력

# 4. 테스트
npm run test
```

## 📚 문서

- **[빠른 시작 가이드](QUICKSTART.md)** ⭐ 처음 시작하는 분들을 위한 가이드
- **[MCP 서버 문서](MCP_README.md)** - MCP 서버 상세 사용법
- **[Vercel 배포 가이드](VERCEL_DEPLOYMENT.md)** - Vercel 배포 방법

## ✨ 주요 기능

### MCP 서버 기능
- 🔮 사주팔자 계산 (년월일시 간지)
- 🎯 십신·12운성 분석
- 🌊 대운 계산 (연해자평 방식)
- 🤖 OpenAI GPT-4 기반 AI 해석
- ⏰ 시주 미상 지원
- 📅 2026년 운세 분석

### 제공되는 MCP 도구
1. `analyze_saju` - 상세 사주 분석 및 AI 해석
2. `get_saju_pillars` - 사주팔자 빠른 조회

## 🌐 사용 방법

### 1. MCP 서버로 사용 (Claude Desktop)

`claude_desktop_config.json` 설정:

```json
{
  "mcpServers": {
    "tboo-saju": {
      "command": "node",
      "args": ["/절대경로/tboo-engine/dist/index.js"],
      "env": {
        "OPENAI_API_KEY": "sk-..."
      }
    }
  }
}
```

Claude Desktop 재시작 후:
```
사주 분석 부탁해
- 이름: 홍길동
- 생년월일: 1990년 5월 15일 오후 2시 30분
- 성별: 남성
```

### 2. REST API로 사용 (Vercel 배포 후)

```bash
curl -X POST https://your-project.vercel.app/api/saju \
  -H "Content-Type: application/json" \
  -d '{
    "name": "홍길동",
    "year": 1990,
    "month": 5,
    "day": 15,
    "hour": 14,
    "minute": 30,
    "gender": 1,
    "detailed": true
  }'
```

## 🔧 개발

```bash
# 개발 모드 실행
npm run dev

# 빌드
npm run build

# 테스트
npm run test
```

## 📦 Vercel 배포

```bash
# 1. Vercel CLI 설치
npm install -g vercel

# 2. 로그인
vercel login

# 3. 배포
vercel --prod

# 4. 환경 변수 설정
vercel env add OPENAI_API_KEY
```

상세한 배포 가이드는 [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md)를 참조하세요.

## 🏗️ 기술 스택

- **Runtime**: Node.js 18+
- **Language**: TypeScript
- **MCP SDK**: @modelcontextprotocol/sdk ^1.0.4
- **AI**: OpenAI GPT-4
- **Deployment**: Vercel Serverless Functions
- **Data**: CSV (만세력), JSON (절기)

## 📊 데이터 소스

- **만세력**: 1900년~현재 양력-음력 변환 및 간지 정보 (55,154 rows)
- **절기**: 1900-2050년 24절기 정보 (JSON)
- **십신 맵**: 일간 기준 천간 관계 분석
- **12운성 맵**: 천간-지지 조합별 운세 상태

## 📁 프로젝트 구조

```
tboo-engine/
├── src/                           # TypeScript 소스
│   ├── engine/                    # 사주 계산 엔진
│   │   ├── constants.ts          # 십신, 12운성 상수
│   │   ├── timeUtils.ts          # 시간 변환
│   │   ├── daeun.ts              # 대운 계산
│   │   ├── manselyeogLoader.ts   # 만세력 로더
│   │   └── sajuCore.ts           # 사주 메인 엔진
│   ├── services/
│   │   └── openaiService.ts      # OpenAI 해석
│   ├── index.ts                   # MCP 서버
│   └── test.ts                    # 테스트
├── api/
│   └── saju.ts                    # Vercel Function
├── calculation_engine/data/       # 데이터 파일
│   ├── manselyeog_1900.csv
│   └── solar_terms_1900_2050.json
├── dist/                          # 빌드 출력
├── QUICKSTART.md                  # 빠른 시작 가이드
├── MCP_README.md                  # MCP 서버 문서
├── VERCEL_DEPLOYMENT.md           # 배포 가이드
├── package.json
├── tsconfig.json
└── vercel.json
```

## 🎓 학습 자료

### Python 엔진 문서 (레거시)
기존 Python 로직을 이해하려면:
- `calculation_engine/README.md`
- `meaning_engine/README.md`

### MCP 프로토콜
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [MCP SDK Docs](https://github.com/modelcontextprotocol/sdk)

## 🤝 기여

이슈와 PR을 환영합니다!

## 📄 라이선스

MIT License

## ⚠️ 주의사항

- OpenAI API 사용에 따른 비용이 발생할 수 있습니다
- 만세력 데이터는 1900년 이후만 지원합니다
- 사주 해석은 참고용이며, 전문가 상담을 권장합니다
- 시주 미상인 경우 일부 분석이 제한될 수 있습니다

## 📞 지원

프로젝트 이슈 페이지를 통해 문의해주세요.

---

Made with ❤️ for traditional Korean fortune-telling modernization

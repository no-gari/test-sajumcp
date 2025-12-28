# 사주 MCP 서버 - 빠른 시작 가이드

## 🎯 개요

Python 기반 사주 분석 로직을 **Node.js + TypeScript**로 변환하고, **MCP(Model Context Protocol) 서버**로 구현하여 **Vercel**에 배포 가능하도록 만든 프로젝트입니다.

## ✅ 완료된 작업

### 1. Node.js 엔진 구현 ✓
- ✅ 십신(十神) 계산 로직
- ✅ 12운성(十二運星) 계산 로직
- ✅ 시간 변환 유틸리티
- ✅ 대운(大運) 계산 (연해자평 방식)
- ✅ 만세력 CSV 데이터 로더
- ✅ 절기 데이터 로더
- ✅ 사주 계산 메인 엔진

### 2. MCP 서버 구현 ✓
- ✅ `@modelcontextprotocol/sdk` 통합
- ✅ `analyze_saju` 도구: 상세 사주 분석
- ✅ `get_saju_pillars` 도구: 사주팔자 조회
- ✅ OpenAI GPT-4 통합 (사주 해석)

### 3. Vercel 배포 준비 ✓
- ✅ `vercel.json` 설정
- ✅ Serverless Function (`api/saju.ts`)
- ✅ 환경 변수 설정 가이드
- ✅ CORS 설정

### 4. 문서화 ✓
- ✅ MCP 서버 사용법 (`MCP_README.md`)
- ✅ Vercel 배포 가이드 (`VERCEL_DEPLOYMENT.md`)
- ✅ 빠른 시작 가이드 (이 파일)

## 🚀 로컬에서 시작하기

### 1. 환경 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집 (OpenAI API 키 입력)
# OPENAI_API_KEY=sk-...
```

### 2. 패키지 설치 및 빌드

```bash
npm install
npm run build
```

### 3. 테스트 실행

```bash
# OpenAI 없이 기본 사주 계산 테스트
npm run test

# MCP 서버 개발 모드 실행
npm run dev
```

## 🌐 Vercel 배포

### 간단 배포 (3단계)

```bash
# 1. Vercel CLI 설치
npm install -g vercel

# 2. 로그인
vercel login

# 3. 배포
vercel --prod
```

배포 후 환경 변수 설정:

```bash
vercel env add OPENAI_API_KEY
# API 키 입력 후 Production, Preview, Development 모두 선택
```

상세한 배포 가이드는 `VERCEL_DEPLOYMENT.md`를 참조하세요.

## 🔧 Claude Desktop에서 사용

### 설정 파일 수정

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "tboo-saju": {
      "command": "node",
      "args": ["/절대경로/tboo-engine/dist/index.js"],
      "env": {
        "OPENAI_API_KEY": "sk-your-api-key-here"
      }
    }
  }
}
```

Claude Desktop 재시작 후 사용 가능합니다.

## 💡 사용 예시

### Claude에서 사용

```
사주 분석 부탁해
- 이름: 홍길동
- 생년월일: 1990년 5월 15일
- 시간: 오후 2시 30분
- 성별: 남성
```

### API로 사용 (Vercel 배포 후)

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

## 📂 주요 파일 설명

```
tboo-engine/
├── src/
│   ├── engine/          # 사주 계산 엔진
│   ├── services/        # OpenAI 서비스
│   ├── index.ts         # MCP 서버
│   └── test.ts          # 테스트 스크립트
├── api/
│   └── saju.ts          # Vercel Serverless Function
├── calculation_engine/
│   └── data/            # 만세력 & 절기 데이터
├── MCP_README.md        # MCP 서버 상세 문서
├── VERCEL_DEPLOYMENT.md # Vercel 배포 가이드
└── package.json
```

## 🎓 다음 단계

1. **환경 변수 설정**: `.env` 파일에 OpenAI API 키 추가
2. **로컬 테스트**: `npm run test` 실행
3. **Vercel 배포**: `vercel --prod` 실행
4. **Claude 연동**: `claude_desktop_config.json` 설정

## ❓ 문제 해결

### 빌드 오류
```bash
npm run build
```

### 패키지 문제
```bash
rm -rf node_modules package-lock.json
npm install
```

### API 키 문제
- `.env` 파일에 `OPENAI_API_KEY` 확인
- Vercel 환경 변수 설정 확인

## 📖 추가 문서

- **MCP 서버 상세 사용법**: `MCP_README.md`
- **Vercel 배포 가이드**: `VERCEL_DEPLOYMENT.md`
- **기존 Python 문서**: `calculation_engine/README.md`

## 🎉 완료!

이제 사주 MCP 서버가 준비되었습니다. Claude Desktop이나 API를 통해 사주 분석을 시작하세요!

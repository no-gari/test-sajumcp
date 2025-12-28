# Vercel 배포 가이드

## 📋 사전 준비

1. Vercel 계정 생성: https://vercel.com
2. OpenAI API 키 준비: https://platform.openai.com/api-keys
3. Git 저장소 (선택사항)

## 🚀 배포 방법

### 방법 1: Vercel CLI 사용 (권장)

#### 1. Vercel CLI 설치

```bash
npm install -g vercel
```

#### 2. 로그인

```bash
vercel login
```

#### 3. 프로젝트 빌드

```bash
npm install
npm run build
```

#### 4. 배포

```bash
vercel
```

첫 배포 시 설정 질문:
- Set up and deploy? **Y**
- Which scope? **your-account**
- Link to existing project? **N**
- Project name? **tboo-saju-mcp** (원하는 이름)
- In which directory is your code located? **./**

#### 5. 환경 변수 설정

```bash
vercel env add OPENAI_API_KEY
```

값 입력 후:
- Environments: **Production, Preview, Development** (모두 선택)

#### 6. 프로덕션 배포

```bash
vercel --prod
```

### 방법 2: Vercel 대시보드 사용

#### 1. GitHub 저장소에 푸시

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-username/tboo-engine.git
git push -u origin main
```

#### 2. Vercel에서 Import

1. https://vercel.com/new 접속
2. GitHub 저장소 선택
3. 프로젝트 설정:
   - Framework Preset: **Other**
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`

#### 3. 환경 변수 설정

- `OPENAI_API_KEY`: OpenAI API 키

#### 4. Deploy 클릭

## 🔧 배포 후 설정

### API 엔드포인트 확인

배포 완료 후 URL이 생성됩니다:
```
https://your-project-name.vercel.app
```

API 엔드포인트:
```
https://your-project-name.vercel.app/api/saju
```

### 테스트

```bash
curl -X POST https://your-project-name.vercel.app/api/saju \
  -H "Content-Type: application/json" \
  -d '{
    "name": "테스트",
    "year": 1990,
    "month": 1,
    "day": 1,
    "gender": 1,
    "detailed": false
  }'
```

## 🌐 MCP 서버로 사용

### 로컬 MCP 서버

Vercel에 배포된 API를 사용하는 MCP 서버 프록시를 로컬에서 실행:

```bash
npm run dev
```

### Claude Desktop 설정

`claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "tboo-saju": {
      "command": "node",
      "args": ["/absolute/path/to/tboo-engine/dist/index.js"],
      "env": {
        "OPENAI_API_KEY": "sk-..."
      }
    }
  }
}
```

## 📊 모니터링

### Vercel 대시보드

- https://vercel.com/dashboard
- 프로젝트 선택
- Deployments, Analytics, Logs 확인

### 로그 확인

```bash
vercel logs
```

## 🔄 업데이트

코드 수정 후 재배포:

```bash
npm run build
vercel --prod
```

Git 연동 시 자동 배포:
```bash
git add .
git commit -m "Update"
git push
```

## ⚙️ 고급 설정

### 커스텀 도메인

1. Vercel 대시보드 → 프로젝트 선택
2. Settings → Domains
3. 도메인 추가 및 DNS 설정

### 환경 변수 관리

```bash
# 환경 변수 목록 확인
vercel env ls

# 환경 변수 추가
vercel env add VARIABLE_NAME

# 환경 변수 제거
vercel env rm VARIABLE_NAME
```

### 성능 최적화

`vercel.json`에 설정 추가:

```json
{
  "functions": {
    "api/saju.ts": {
      "memory": 1024,
      "maxDuration": 10
    }
  }
}
```

## ❗ 문제 해결

### 빌드 실패

```bash
# 로컬에서 빌드 테스트
npm run build

# 타입 체크
npx tsc --noEmit
```

### API 오류

```bash
# Vercel 로그 확인
vercel logs --follow

# 로컬 테스트
npm run test
```

### 환경 변수 문제

1. Vercel 대시보드에서 환경 변수 확인
2. 재배포 필요할 수 있음

## 💰 비용 관리

### Vercel

- Hobby Plan: 무료 (개인 프로젝트)
- Pro Plan: $20/월

### OpenAI

- GPT-4 API 사용량에 따라 과금
- Usage Dashboard에서 모니터링: https://platform.openai.com/usage

## 🔒 보안

- API 키는 절대 코드에 하드코딩하지 마세요
- 환경 변수로만 관리
- `.env` 파일은 `.gitignore`에 포함

## 📚 추가 자료

- Vercel 문서: https://vercel.com/docs
- Vercel CLI 문서: https://vercel.com/docs/cli
- Node.js Runtime: https://vercel.com/docs/runtimes#official-runtimes/node-js

#!/bin/bash

echo "🔧 사주 MCP 서버 설치 스크립트"
echo ""

# 1. 패키지 설치
echo "📦 패키지 설치 중..."
npm install

# 2. 빌드
echo "🔨 프로젝트 빌드 중..."
npm run build

# 3. .env 파일 체크
if [ ! -f .env ]; then
  echo "⚠️  .env 파일이 없습니다."
  echo "📝 .env.example을 복사하여 .env 파일을 생성합니다."
  cp .env.example .env
  echo "✅ .env 파일이 생성되었습니다. OpenAI API 키를 입력해주세요."
else
  echo "✅ .env 파일이 이미 존재합니다."
fi

echo ""
echo "🎉 설치 완료!"
echo ""
echo "📋 다음 단계:"
echo "1. .env 파일에 OpenAI API 키를 입력하세요"
echo "   OPENAI_API_KEY=sk-..."
echo ""
echo "2. 테스트 실행:"
echo "   npm run test"
echo ""
echo "3. MCP 서버 실행:"
echo "   npm start"
echo ""
echo "4. Vercel 배포:"
echo "   vercel --prod"
echo ""

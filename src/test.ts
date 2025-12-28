// src/test.ts
// 로컬 테스트 스크립트

import { analyzeSaju } from './engine/sajuCore.js';
import { interpretSaju, getSimpleSajuSummary } from './services/openaiService.js';

async function test() {
  console.log('🧪 사주 분석 테스트 시작...\n');

  // 테스트 데이터
  const testData = {
    name: '홍길동',
    year: 1990,
    month: 5,
    day: 15,
    hour: 14,
    minute: 30,
    gender: 1
  };

  console.log(`📋 입력 정보:`);
  console.log(`- 이름: ${testData.name}`);
  console.log(`- 생년월일시: ${testData.year}년 ${testData.month}월 ${testData.day}일 ${testData.hour}시 ${testData.minute}분`);
  console.log(`- 성별: ${testData.gender === 1 ? '남성' : '여성'}\n`);

  // 사주 계산
  const result = analyzeSaju(
    testData.year,
    testData.month,
    testData.day,
    testData.hour,
    testData.minute,
    testData.gender,
    testData.name
  );

  if (!result) {
    console.error('❌ 사주 계산 실패');
    return;
  }

  console.log('✅ 사주 계산 성공!\n');
  console.log('📜 사주 정보:');
  console.log(`- 년주: ${result.year_ganji}`);
  console.log(`- 월주: ${result.month_ganji}`);
  console.log(`- 일주: ${result.day_ganji}`);
  console.log(`- 시주: ${result.hour_ganji}`);
  console.log(`- 일간: ${result.day_gan}\n`);

  console.log('🔮 대운 정보:');
  result.daeun_labels.slice(0, 3).forEach(label => {
    console.log(`- ${label}`);
  });
  console.log();

  // 간단한 요약
  const summary = await getSimpleSajuSummary(result, testData.name);
  console.log(summary);

  // OpenAI 해석 (API 키가 있는 경우에만)
  if (process.env.OPENAI_API_KEY) {
    console.log('\n🤖 AI 상세 해석 생성 중...\n');
    try {
      const interpretation = await interpretSaju(result, testData.name, testData.gender);
      console.log(interpretation);
    } catch (error) {
      console.error('⚠️ AI 해석 실패:', error instanceof Error ? error.message : error);
    }
  } else {
    console.log('\n⚠️ OPENAI_API_KEY가 설정되지 않아 AI 해석을 건너뜁니다.');
  }
}

test().catch(console.error);

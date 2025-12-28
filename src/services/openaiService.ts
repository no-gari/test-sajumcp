// src/services/openaiService.ts
// OpenAI API를 사용한 사주 해석

import OpenAI from 'openai';
import { SajuAnalysisResult } from '../engine/sajuCore.js';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY || ''
});

export async function interpretSaju(
  sajuData: SajuAnalysisResult,
  name: string,
  gender: number
): Promise<string> {
  const genderStr = gender === 1 ? '남성' : '여성';
  
  const prompt = `당신은 한국 전통 사주 명리학 전문가입니다. 다음 사주 정보를 바탕으로 종합적이고 상세한 사주 풀이를 제공해주세요.

## 사주 정보
- 이름: ${name}
- 성별: ${genderStr}
- 년주: ${sajuData.year_ganji} (${sajuData.pillars_detail.year.sipshin}, ${sajuData.pillars_detail.year.un12})
- 월주: ${sajuData.month_ganji} (${sajuData.pillars_detail.month.sipshin}, ${sajuData.pillars_detail.month.un12})
- 일주: ${sajuData.day_ganji} (일간, ${sajuData.pillars_detail.day.un12})
- 시주: ${sajuData.hour_ganji || '미상'} ${sajuData.hour_ganji ? `(${sajuData.pillars_detail.hour.sipshin}, ${sajuData.pillars_detail.hour.un12})` : ''}
- 일간: ${sajuData.day_gan}

## 대운 정보
${sajuData.daeun_labels.slice(0, 3).join('\n')}

## 2026년 운세 (병오년)
- 재물운: ${sajuData.yearly_jaemul.map(([s, g, u]) => `${g}(${s}, ${u})`).join(', ')}
- 연애운: ${sajuData.yearly_love.map(([s, g, u]) => `${g}(${s}, ${u})`).join(', ')}
- 직업운: ${sajuData.yearly_job.map(([s, g, u]) => `${g}(${s}, ${u})`).join(', ')}

다음 내용을 포함하여 풀이해주세요:
1. **기본 성격 및 성향** (일간과 일주를 중심으로)
2. **타고난 재능과 강점**
3. **인생의 주요 과제와 약점**
4. **재물운 및 재테크 조언**
5. **연애운 및 인간관계**
6. **직업 및 커리어 방향**
7. **현재 대운의 특징과 영향**
8. **2026년(병오년) 운세 및 조언**

각 항목을 명확하게 구분하여 친절하고 이해하기 쉽게 작성해주세요.`;

  try {
    const response = await openai.chat.completions.create({
      model: 'gpt-4o',
      messages: [
        {
          role: 'system',
          content: '당신은 30년 경력의 한국 전통 사주 명리학 전문가입니다. 사주를 정확하고 친절하게 풀이하며, 구체적이고 실용적인 조언을 제공합니다.'
        },
        {
          role: 'user',
          content: prompt
        }
      ],
      temperature: 0.7,
      max_tokens: 3000
    });

    return response.choices[0]?.message?.content || '해석 생성에 실패했습니다.';
  } catch (error) {
    console.error('OpenAI API 오류:', error);
    throw new Error('사주 해석 중 오류가 발생했습니다.');
  }
}

export async function getSimpleSajuSummary(
  sajuData: SajuAnalysisResult,
  name: string
): Promise<string> {
  return `
📜 ${name}님의 사주 정보

🔹 사주 원국
- 년주: ${sajuData.year_ganji}
- 월주: ${sajuData.month_ganji}
- 일주: ${sajuData.day_ganji} (일간: ${sajuData.day_gan})
- 시주: ${sajuData.hour_ganji || '미상'}

🔹 대운
${sajuData.daeun_labels.slice(0, 3).join('\n')}

🔹 2026년 병오년 운세 개요
- 재물운 관련: ${sajuData.yearly_jaemul.length}개
- 연애운 관련: ${sajuData.yearly_love.length}개
- 직업운 관련: ${sajuData.yearly_job.length}개
`;
}

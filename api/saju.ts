// api/saju.ts
// Vercel Serverless Function for Saju Analysis

import type { VercelRequest, VercelResponse } from '@vercel/node';
import { analyzeSaju } from '../dist/engine/sajuCore.js';
import { interpretSaju, getSimpleSajuSummary } from '../dist/services/openaiService.js';

interface SajuRequest {
  name: string;
  year: number;
  month: number;
  day: number;
  hour?: number | null;
  minute?: number | null;
  gender: number;
  detailed?: boolean;
}

export default async function handler(
  req: VercelRequest,
  res: VercelResponse
) {
  // CORS 설정
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
  );

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const {
      name,
      year,
      month,
      day,
      hour = null,
      minute = null,
      gender,
      detailed = true
    } = req.body as SajuRequest;

    // 입력 검증
    if (!name || !year || !month || !day || !gender) {
      return res.status(400).json({
        error: '필수 정보가 누락되었습니다. (name, year, month, day, gender)'
      });
    }

    if (gender !== 1 && gender !== 2) {
      return res.status(400).json({
        error: '성별은 1(남성) 또는 2(여성)이어야 합니다.'
      });
    }

    // 사주 계산
    const sajuResult = analyzeSaju(year, month, day, hour, minute, gender, name);

    if (!sajuResult) {
      return res.status(400).json({
        error: '사주 계산에 실패했습니다. 올바른 날짜를 입력했는지 확인해주세요.'
      });
    }

    // 상세 해석 여부
    let interpretation = '';
    
    if (detailed) {
      interpretation = await interpretSaju(sajuResult, name, gender);
    } else {
      interpretation = await getSimpleSajuSummary(sajuResult, name);
    }

    return res.status(200).json({
      success: true,
      data: {
        saju: {
          year: sajuResult.year_ganji,
          month: sajuResult.month_ganji,
          day: sajuResult.day_ganji,
          hour: sajuResult.hour_ganji,
          dayGan: sajuResult.day_gan,
        },
        pillars: sajuResult.pillars_detail,
        daeun: sajuResult.daeun_detail.slice(0, 3),
        interpretation
      }
    });
  } catch (error) {
    console.error('Error:', error);
    return res.status(500).json({
      error: '서버 오류가 발생했습니다.',
      message: error instanceof Error ? error.message : String(error)
    });
  }
}

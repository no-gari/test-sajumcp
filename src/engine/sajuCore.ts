// src/engine/sajuCore.ts
// 사주 계산 메인 엔진

import { getSipshin, get12Un, GAN_10 } from './constants.js';
import { getSiJiByClock, getHourGan } from './timeUtils.js';
import { 
  getSexDirection, 
  getDaeunAgeAndStartpoints, 
  getDaeunGanji, 
  formatDaeunEntries,
  DaeunInfo,
  SolarTerm 
} from './daeun.js';
import { findManselyeogRow } from './manselyeogLoader.js';
import { readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export interface PillarDetail {
  label: string;
  gan: string | null;
  ji: string | null;
  sipshin: string | null;
  un12: string | null;
  status: 'observed' | 'unknown';
}

export interface SajuAnalysisResult {
  // 원국 간지
  year_ganji: string;
  month_ganji: string;
  day_ganji: string;
  hour_ganji: string | null;
  
  // 일간
  day_gan: string;
  
  // 기둥 상세
  pillars_detail: {
    year: PillarDetail;
    month: PillarDetail;
    day: PillarDetail;
    hour: PillarDetail;
  };
  
  // 대운 정보
  daeun_detail: DaeunInfo[];
  daeun_labels: string[];
  daeun_age_raw: number;
  daeun_year_traditional: number;
  direction: number;
  
  // 2026년 운세 (병오년)
  yearly_flow: Array<[string, string | null, string | null, string | null]>;
  yearly_jaemul: Array<[string, string, string]>;
  yearly_love: Array<[string, string, string]>;
  yearly_job: Array<[string, string, string]>;
  
  // 시주 상태
  hour_pillar_state: {
    status: 'observed' | 'unknown';
  };
}

export function analyzeSaju(
  year: number,
  month: number,
  day: number,
  hour: number | null,
  minute: number | null,
  gender: number,
  name: string = ''
): SajuAnalysisResult | null {
  // 출생 시각
  const hourStatus: 'observed' | 'unknown' = 
    (hour !== null && minute !== null) ? 'observed' : 'unknown';
  
  const birth = new Date(year, month - 1, day, hour ?? 0, minute ?? 0);
  
  // 만세력 조회
  const row = findManselyeogRow(new Date(year, month - 1, day));
  if (!row) {
    console.error('해당 날짜가 만세력에 없습니다.');
    return null;
  }
  
  const year_ganji = row.歲次;
  const month_ganji = row.月建;
  const day_ganji = row.日辰;
  
  const year_gan = year_ganji[0];
  const year_ji = year_ganji[1];
  const month_gan = month_ganji[0];
  const month_ji = month_ganji[1];
  const day_gan = day_ganji[0];
  const day_ji = day_ganji[1];
  
  // 시주 계산
  let hour_ji: string | null = null;
  let hour_gan: string | null = null;
  let hour_ganji: string | null = null;
  
  if (hourStatus === 'observed' && hour !== null && minute !== null) {
    hour_ji = getSiJiByClock(hour, minute);
    hour_gan = getHourGan(day_gan, hour_ji);
    hour_ganji = `${hour_gan}${hour_ji}`;
  }
  
  // 십신 계산
  const sip_year = getSipshin(day_gan, year_gan);
  const sip_month = getSipshin(day_gan, month_gan);
  const sip_hour = hour_gan ? getSipshin(day_gan, hour_gan) : null;
  
  // 12운성 계산
  const un_year = get12Un(year_gan, year_ji);
  const un_month = get12Un(month_gan, month_ji);
  const un_day = get12Un(day_gan, day_ji);
  const un_hour = (hour_gan && hour_ji) ? get12Un(hour_gan, hour_ji) : null;
  
  // 기둥 상세
  const pillars_detail = {
    year: {
      label: '년주',
      gan: year_gan,
      ji: year_ji,
      sipshin: sip_year,
      un12: un_year,
      status: 'observed' as const
    },
    month: {
      label: '월주',
      gan: month_gan,
      ji: month_ji,
      sipshin: sip_month,
      un12: un_month,
      status: 'observed' as const
    },
    day: {
      label: '일주',
      gan: day_gan,
      ji: day_ji,
      sipshin: '일간',
      un12: un_day,
      status: 'observed' as const
    },
    hour: {
      label: '시주',
      gan: hour_gan,
      ji: hour_ji,
      sipshin: sip_hour,
      un12: un_hour,
      status: hourStatus
    }
  };
  
  // 대운 계산
  const direction = getSexDirection(year_gan, gender);
  
  // 절기 데이터 로드
  const solarTermsPath = join(__dirname, '../../calculation_engine/data/solar_terms_1900_2050.json');
  const solarTerms: Record<string, SolarTerm[]> = JSON.parse(readFileSync(solarTermsPath, 'utf-8'));
  
  const { ageRaw, daeunStartDt, startpoints, daeunYearTraditional } = 
    getDaeunAgeAndStartpoints(birth, solarTerms, direction);
  
  const daeuns = getDaeunGanji(month_gan, month_ji, direction);
  const daeun_labels = formatDaeunEntries(ageRaw, daeuns, startpoints, year, Math.round(ageRaw));
  
  // 대운 상세 정보
  const daeun_detail: DaeunInfo[] = daeuns.map(([gan, ji], i) => ({
    index: i,
    label: daeun_labels[i] || '',
    ganji: `${gan}${ji}`,
    gan,
    ji,
    sipshin: getSipshin(day_gan, gan),
    un12: get12Un(gan, ji)
  }));
  
  // 2026년 병오년 운세
  const 운간 = '丙';
  const 운지 = '午';
  
  const yearly_flow: Array<[string, string | null, string | null, string | null]> = [
    ['원국_월간', month_gan, getSipshin(day_gan, month_gan), get12Un(month_gan, 운지)],
    ['원국_년간', year_gan, getSipshin(day_gan, year_gan), get12Un(year_gan, 운지)],
    hour_gan 
      ? ['원국_시간', hour_gan, getSipshin(day_gan, hour_gan), get12Un(hour_gan, 운지)]
      : ['원국_시간', null, null, null],
    ['세운_천간_2026', 운간, getSipshin(day_gan, 운간), get12Un(운간, 운지)]
  ];
  
  // 재물운
  const yearly_jaemul: Array<[string, string, string]> = [];
  for (const g of GAN_10) {
    const s = getSipshin(day_gan, g);
    if (s === '정재' || s === '편재') {
      const u = get12Un(g, 운지);
      yearly_jaemul.push([s, g, u]);
    }
  }
  
  // 연애운
  const yearly_love: Array<[string, string, string]> = [];
  const love_keys = gender === 1 ? ['정재', '편재'] : ['정관', '편관'];
  for (const g of GAN_10) {
    const s = getSipshin(day_gan, g);
    if (love_keys.includes(s)) {
      const u = get12Un(g, 운지);
      yearly_love.push([s, g, u]);
    }
  }
  
  // 직업운
  const yearly_job: Array<[string, string, string]> = [];
  const job_keys = ['정관', '편관', '식신', '상관'];
  for (const g of GAN_10) {
    const s = getSipshin(day_gan, g);
    if (job_keys.includes(s)) {
      const u = get12Un(g, 운지);
      yearly_job.push([s, g, u]);
    }
  }
  
  return {
    year_ganji,
    month_ganji,
    day_ganji,
    hour_ganji,
    day_gan,
    pillars_detail,
    daeun_detail,
    daeun_labels,
    daeun_age_raw: ageRaw,
    daeun_year_traditional: daeunYearTraditional,
    direction,
    yearly_flow,
    yearly_jaemul,
    yearly_love,
    yearly_job,
    hour_pillar_state: {
      status: hourStatus
    }
  };
}

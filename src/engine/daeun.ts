// src/engine/daeun.ts
// 대운 계산 로직

import { GAN_10, JI_12, YANG_GANS } from './constants.js';

const MINUTES_PER_YEAR = 4320;

export interface SolarTerm {
  name: string;
  datetime: string;
}

export interface DaeunInfo {
  index: number;
  label: string;
  ganji: string;
  gan: string;
  ji: string;
  sipshin: string;
  un12: string;
}

// 성별과 년간으로 대운 방향 결정
export function getSexDirection(yearGan: string, gender: number): number {
  const isYang = YANG_GANS.includes(yearGan);
  return (gender === 1 && isYang) || (gender === 2 && !isYang) ? 1 : -1;
}

// 대운 시작 나이 계산
export function getDaeunAgeAndStartpoints(
  birth: Date,
  solarTerms: Record<string, SolarTerm[]>,
  direction: number
): {
  ageRaw: number;
  daeunStartDt: Date;
  startpoints: Date[];
  daeunYearTraditional: number;
} {
  const year = birth.getFullYear().toString();
  
  if (!solarTerms[year]) {
    return {
      ageRaw: 8,
      daeunStartDt: birth,
      startpoints: [],
      daeunYearTraditional: birth.getFullYear() + 7
    };
  }
  
  const terms = solarTerms[year].map(t => new Date(t.datetime));
  terms.sort((a, b) => a.getTime() - b.getTime());
  
  let targetDt: Date;
  let deltaMin: number;
  
  if (direction === 1) {
    const futureTerms = terms.filter(dt => dt > birth);
    if (futureTerms.length === 0) {
      return {
        ageRaw: 8,
        daeunStartDt: birth,
        startpoints: [],
        daeunYearTraditional: birth.getFullYear() + 7
      };
    }
    targetDt = futureTerms[0];
    deltaMin = (targetDt.getTime() - birth.getTime()) / (1000 * 60);
  } else {
    const pastTerms = terms.filter(dt => dt <= birth);
    if (pastTerms.length === 0) {
      return {
        ageRaw: 8,
        daeunStartDt: birth,
        startpoints: [],
        daeunYearTraditional: birth.getFullYear() + 7
      };
    }
    targetDt = pastTerms[pastTerms.length - 1];
    deltaMin = (birth.getTime() - targetDt.getTime()) / (1000 * 60);
  }
  
  const ageRaw = deltaMin / MINUTES_PER_YEAR;
  const ageRounded = Math.max(1, Math.min(Math.round(ageRaw), 10));
  
  const daeunStartDt = new Date(birth.getTime() + ageRaw * 365.25 * 24 * 60 * 60 * 1000);
  const startpoints = Array.from({ length: 10 }, (_, i) => 
    new Date(daeunStartDt.getTime() + i * 10 * 365.25 * 24 * 60 * 60 * 1000)
  );
  
  const daeunYearTraditional = ageRounded === 1 
    ? birth.getFullYear() + 1 
    : birth.getFullYear() + ageRounded - 1;
  
  return { ageRaw, daeunStartDt, startpoints, daeunYearTraditional };
}

// 다음 간지 계산
function getNextGanji(gan: string, ji: string, step: number): [string, string] {
  const ganIndex = GAN_10.indexOf(gan);
  const jiIndex = JI_12.indexOf(ji);
  
  const newGanIndex = (ganIndex + step + 10) % 10;
  const newJiIndex = (jiIndex + step + 12) % 12;
  
  return [GAN_10[newGanIndex], JI_12[newJiIndex]];
}

// 대운 간지 생성
export function getDaeunGanji(
  startGan: string,
  startJi: string,
  direction: number,
  count: number = 10
): Array<[string, string]> {
  const result: Array<[string, string]> = [];
  let [gan, ji] = [startGan, startJi];
  
  for (let i = 0; i < count; i++) {
    [gan, ji] = getNextGanji(gan, ji, direction);
    result.push([gan, ji]);
  }
  
  return result;
}

// 대운 라벨 생성
export function formatDaeunEntries(
  startAgeFloat: number,
  ganjiList: Array<[string, string]>,
  startpoints: Date[],
  birthYear: number,
  daeunRounded?: number
): string[] {
  const labels: string[] = [];
  const baseAge = daeunRounded ?? Math.round(startAgeFloat);
  
  for (let i = 0; i < ganjiList.length; i++) {
    const [gan, ji] = ganjiList[i];
    const labelAge = baseAge > 1 ? baseAge - 1 + i * 10 : 1 + i * 10;
    const startYear = birthYear + labelAge;
    labels.push(`만 ${labelAge}세부터 ${gan}${ji} 대운 시작 (${startYear})`);
  }
  
  return labels;
}

// src/engine/timeUtils.ts
// 시간 계산 유틸리티

import { GAN_10, JI_12 } from './constants.js';

// 시지(時支) 계산 - 시간으로부터
export function getSiJiByClock(hour: number, minute: number): string {
  const totalMin = hour * 60 + minute;
  
  const ranges: [number, number, string][] = [
    [1410, 1439, '子'],
    [0, 89, '子'],
    [90, 209, '丑'],
    [210, 329, '寅'],
    [330, 449, '卯'],
    [450, 569, '辰'],
    [570, 689, '巳'],
    [690, 809, '午'],
    [810, 929, '未'],
    [930, 1049, '申'],
    [1050, 1169, '酉'],
    [1170, 1289, '戌'],
    [1290, 1409, '亥']
  ];
  
  for (const [start, end, branch] of ranges) {
    if (totalMin >= start && totalMin <= end) {
      return branch;
    }
  }
  
  return '?';
}

// 시간(時干) 계산
export function getHourGan(dayGan: string, hourJi: string): string {
  const dayIndex = GAN_10.indexOf(dayGan);
  const jiIndex = JI_12.indexOf(hourJi);
  
  if (dayIndex === -1 || jiIndex === -1) return '?';
  
  const index = (dayIndex * 2 + jiIndex) % 10;
  return GAN_10[index];
}

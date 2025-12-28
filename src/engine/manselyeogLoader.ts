// src/engine/manselyeogLoader.ts
// 만세력 CSV 데이터 로더

import { readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import Papa from 'papaparse';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export interface ManselyeogRow {
  양력일자: string;
  음력일자: string;
  양년: string;
  양월: string;
  양일: string;
  요일: string;
  윤년: string;
  율적일: string;
  율년: string;
  율월: string;
  율일: string;
  율윤년: string;
  음년: string;
  음월: string;
  음일: string;
  음말: string;
  윤달: string;
  歲次: string;
  月建: string;
  日辰: string;
  세차: string;
  월건: string;
  일진: string;
  datetime: string;
  연간간지: string;
  월간간지: string;
}

let cachedData: ManselyeogRow[] | null = null;

export function loadManselyeog(): ManselyeogRow[] {
  if (cachedData) return cachedData;
  
  const csvPath = join(__dirname, '../../calculation_engine/data/manselyeog_1900.csv');
  const csvContent = readFileSync(csvPath, 'utf-8');
  
  const result = Papa.parse<ManselyeogRow>(csvContent, {
    header: true,
    skipEmptyLines: true
  });
  
  cachedData = result.data;
  return cachedData;
}

export function findManselyeogRow(date: Date): ManselyeogRow | null {
  const data = loadManselyeog();
  const dateStr = date.toISOString().split('T')[0];
  
  const row = data.find(r => r.양력일자 === dateStr);
  return row || null;
}

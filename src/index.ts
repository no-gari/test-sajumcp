#!/usr/bin/env node

// src/index.ts
// MCP 서버 메인 진입점

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

import { analyzeSaju } from './engine/sajuCore.js';
import { interpretSaju, getSimpleSajuSummary } from './services/openaiService.js';

// MCP 서버 설정
const server = new Server(
  {
    name: 'tboo-saju-server',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// 도구 목록 제공
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'analyze_saju',
        description: '생년월일시를 입력받아 사주를 분석하고 AI 해석을 제공합니다. 시간을 모르는 경우 hour와 minute을 null로 전달하세요.',
        inputSchema: {
          type: 'object',
          properties: {
            name: {
              type: 'string',
              description: '이름'
            },
            year: {
              type: 'number',
              description: '출생 연도 (양력, 예: 1990)'
            },
            month: {
              type: 'number',
              description: '출생 월 (양력, 1-12)'
            },
            day: {
              type: 'number',
              description: '출생 일 (양력, 1-31)'
            },
            hour: {
              type: ['number', 'null'],
              description: '출생 시간 (0-23), 모르는 경우 null'
            },
            minute: {
              type: ['number', 'null'],
              description: '출생 분 (0-59), 모르는 경우 null'
            },
            gender: {
              type: 'number',
              description: '성별 (1: 남성, 2: 여성)',
              enum: [1, 2]
            },
            detailed: {
              type: 'boolean',
              description: 'true: AI 상세 해석 포함, false: 기본 사주 정보만',
              default: true
            }
          },
          required: ['name', 'year', 'month', 'day', 'gender']
        }
      },
      {
        name: 'get_saju_pillars',
        description: '생년월일시의 사주 사주팔자(년월일시 간지)만 빠르게 조회합니다.',
        inputSchema: {
          type: 'object',
          properties: {
            year: {
              type: 'number',
              description: '출생 연도 (양력)'
            },
            month: {
              type: 'number',
              description: '출생 월 (양력, 1-12)'
            },
            day: {
              type: 'number',
              description: '출생 일 (양력, 1-31)'
            },
            hour: {
              type: ['number', 'null'],
              description: '출생 시간 (0-23), 모르는 경우 null'
            },
            minute: {
              type: ['number', 'null'],
              description: '출생 분 (0-59), 모르는 경우 null'
            },
            gender: {
              type: 'number',
              description: '성별 (1: 남성, 2: 여성)',
              enum: [1, 2]
            }
          },
          required: ['year', 'month', 'day', 'gender']
        }
      }
    ],
  };
});

// 도구 호출 처리
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    if (name === 'analyze_saju') {
      const { 
        name: personName, 
        year, 
        month, 
        day, 
        hour = null, 
        minute = null, 
        gender,
        detailed = true 
      } = args as {
        name: string;
        year: number;
        month: number;
        day: number;
        hour?: number | null;
        minute?: number | null;
        gender: number;
        detailed?: boolean;
      };

      // 사주 계산
      const sajuResult = analyzeSaju(year, month, day, hour, minute, gender, personName);
      
      if (!sajuResult) {
        return {
          content: [
            {
              type: 'text',
              text: '❌ 사주 계산에 실패했습니다. 올바른 날짜를 입력했는지 확인해주세요.'
            }
          ]
        };
      }

      // 상세 해석 옵션
      let response = '';
      
      if (detailed) {
        // OpenAI를 통한 상세 해석
        const interpretation = await interpretSaju(sajuResult, personName, gender);
        response = interpretation;
      } else {
        // 기본 요약 정보만
        response = await getSimpleSajuSummary(sajuResult, personName);
      }

      return {
        content: [
          {
            type: 'text',
            text: response
          }
        ]
      };
    }

    if (name === 'get_saju_pillars') {
      const { 
        year, 
        month, 
        day, 
        hour = null, 
        minute = null,
        gender 
      } = args as {
        year: number;
        month: number;
        day: number;
        hour?: number | null;
        minute?: number | null;
        gender: number;
      };

      const sajuResult = analyzeSaju(year, month, day, hour, minute, gender);
      
      if (!sajuResult) {
        return {
          content: [
            {
              type: 'text',
              text: '❌ 사주 계산에 실패했습니다.'
            }
          ]
        };
      }

      const pillarsText = `
📜 사주팔자

┌──────┬──────┬──────┬──────┐
│ 시주 │ 일주 │ 월주 │ 년주 │
├──────┼──────┼──────┼──────┤
│ ${sajuResult.hour_ganji || '미상'} │ ${sajuResult.day_ganji} │ ${sajuResult.month_ganji} │ ${sajuResult.year_ganji} │
└──────┴──────┴──────┴──────┘

📌 일간: ${sajuResult.day_gan}
${sajuResult.hour_ganji ? '' : '⚠️ 시주 미상 (출생 시간을 모름)'}
`;

      return {
        content: [
          {
            type: 'text',
            text: pillarsText
          }
        ]
      };
    }

    return {
      content: [
        {
          type: 'text',
          text: `❌ 알 수 없는 도구: ${name}`
        }
      ]
    };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    return {
      content: [
        {
          type: 'text',
          text: `❌ 오류 발생: ${errorMessage}`
        }
      ],
      isError: true,
    };
  }
});

// 서버 시작
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('사주 MCP 서버가 시작되었습니다.');
}

main().catch((error) => {
  console.error('서버 시작 오류:', error);
  process.exit(1);
});

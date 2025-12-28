// src/sseServer.ts
// PlayMCP 등 외부 서비스 연동을 위한 SSE 기반 MCP 서버
// 주의: 이 서버는 상태 유지가 필요하므로 Vercel Serverless가 아닌 Docker/Railway 등에 배포해야 합니다.

import express from 'express';
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { SSEServerTransport } from '@modelcontextprotocol/sdk/server/sse.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import { analyzeSaju } from './engine/sajuCore.js';
import { interpretSaju, getSimpleSajuSummary } from './services/openaiService.js';

const app = express();
const port = process.env.PORT || 3000;

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

// 도구 목록 제공 (index.ts와 동일)
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'analyze_saju',
        description: '생년월일시를 입력받아 사주를 분석하고 AI 해석을 제공합니다.',
        inputSchema: {
          type: 'object',
          properties: {
            name: { type: 'string', description: '이름' },
            year: { type: 'number', description: '출생 연도 (양력)' },
            month: { type: 'number', description: '출생 월 (양력, 1-12)' },
            day: { type: 'number', description: '출생 일 (양력, 1-31)' },
            hour: { type: ['number', 'null'], description: '출생 시간 (0-23), 모르는 경우 null' },
            minute: { type: ['number', 'null'], description: '출생 분 (0-59), 모르는 경우 null' },
            gender: { type: 'number', description: '성별 (1: 남성, 2: 여성)', enum: [1, 2] },
            detailed: { type: 'boolean', description: 'AI 상세 해석 포함 여부', default: true }
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
            year: { type: 'number', description: '출생 연도 (양력)' },
            month: { type: 'number', description: '출생 월 (양력, 1-12)' },
            day: { type: 'number', description: '출생 일 (양력, 1-31)' },
            hour: { type: ['number', 'null'], description: '출생 시간 (0-23), 모르는 경우 null' },
            minute: { type: ['number', 'null'], description: '출생 분 (0-59), 모르는 경우 null' },
            gender: { type: 'number', description: '성별 (1: 남성, 2: 여성)', enum: [1, 2] }
          },
          required: ['year', 'month', 'day', 'gender']
        }
      }
    ],
  };
});

// 도구 호출 처리 (index.ts와 동일)
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    if (name === 'analyze_saju') {
      const { name: pName, year, month, day, hour = null, minute = null, gender, detailed = true } = args as any;
      const sajuResult = analyzeSaju(year, month, day, hour, minute, gender, pName);
      
      if (!sajuResult) return { content: [{ type: 'text', text: '❌ 사주 계산 실패' }] };

      const response = detailed 
        ? await interpretSaju(sajuResult, pName, gender)
        : await getSimpleSajuSummary(sajuResult, pName);

      return { content: [{ type: 'text', text: response }] };
    }

    if (name === 'get_saju_pillars') {
      const { year, month, day, hour = null, minute = null, gender } = args as any;
      const sajuResult = analyzeSaju(year, month, day, hour, minute, gender);
      
      if (!sajuResult) return { content: [{ type: 'text', text: '❌ 사주 계산 실패' }] };

      const pillarsText = `
📜 사주팔자
년주: ${sajuResult.year_ganji}
월주: ${sajuResult.month_ganji}
일주: ${sajuResult.day_ganji}
시주: ${sajuResult.hour_ganji || '미상'}
일간: ${sajuResult.day_gan}
`;
      return { content: [{ type: 'text', text: pillarsText }] };
    }

    return { content: [{ type: 'text', text: `❌ 알 수 없는 도구: ${name}` }] };
  } catch (error) {
    return { content: [{ type: 'text', text: `❌ 오류: ${error}` }], isError: true };
  }
});

// SSE 연결 관리
let transport: SSEServerTransport;

app.get('/sse', async (req, res) => {
  console.log('SSE connection received');
  transport = new SSEServerTransport('/messages', res);
  await server.connect(transport);
});

app.post('/messages', async (req, res) => {
  console.log('Message received');
  if (transport) {
    await transport.handlePostMessage(req, res);
  } else {
    res.status(404).send('Session not found');
  }
});

app.listen(port, () => {
  console.log(`SSE MCP Server running on port ${port}`);
});

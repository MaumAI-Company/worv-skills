---
name: council
description: 여러 AI(Gemini, GPT)에게 병렬로 조언을 구하고 종합합니다. "council 소집", "여러 AI한테 물어봐", "다양한 관점", "세컨드 오피니언" 등의 요청 시 사용. Team Attention의 Agent Council에서 영감을 받음.
allowed-tools:
  - Bash
  - Read
---

# AI Council

여러 AI(Gemini, GPT)에게 **병렬로** 조언을 구하고 결과를 종합하는 스킬입니다.

Team Attention의 [Agent Council](https://github.com/team-attention/agent-council)에서 영감을 받았습니다.

## 사용법

```bash
~/.claude/.venv/bin/python ~/.claude/skills/council/scripts/council.py "질문"
~/.claude/.venv/bin/python ~/.claude/skills/council/scripts/council.py "질문" --context "코드"
~/.claude/.venv/bin/python ~/.claude/skills/council/scripts/council.py "질문" --file src/main.ts
```

## 워크플로우

1. **Stage 1**: Gemini와 GPT에게 동시에 질문 (병렬 실행)
2. **Stage 2**: 각 AI의 응답 수집 및 표시
3. **Stage 3**: Claude(Chairman)가 모든 의견을 종합하여 최종 권고

## 응답 형식

```
💎 Gemini의 의견:
[Gemini 응답]

🤖 GPT의 의견:
[GPT 응답]

---
📋 Council Summary:
[각 AI 응답 요약 - Chairman이 종합]
```

## 설정

- `~/.claude/.env`의 `GEMINI_API_KEY` 및 `OPENAI_API_KEY` 필요
- Gemini: `gemini-3-pro-preview` (2026 최신)
- GPT: `gpt-4.1` (Chat API 최강)

## 장점

- CLI 설치 불필요 (API 직접 호출)
- 병렬 실행으로 빠른 응답
- 다양한 관점에서 코드 리뷰/조언 획득

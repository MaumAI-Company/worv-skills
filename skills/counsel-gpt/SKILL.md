---
name: counsel-gpt
description: GPT에게 코딩 조언을 구합니다. 코드 리뷰, 아키텍처 조언, 디버깅 힌트 등 다양한 관점을 얻을 때 사용합니다. "gpt한테 물어봐", "openai한테" 등의 요청 시 사용.
allowed-tools:
  - Bash
  - Read
---

# Counsel GPT

OpenAI GPT에게 코딩 관련 조언을 구하는 스킬입니다.

## 사용법

```bash
~/.claude/.venv/bin/python ~/.claude/skills/counsel-gpt/scripts/counsel.py "질문"
~/.claude/.venv/bin/python ~/.claude/skills/counsel-gpt/scripts/counsel.py "질문" --context "코드"
~/.claude/.venv/bin/python ~/.claude/skills/counsel-gpt/scripts/counsel.py "질문" --file src/main.ts
~/.claude/.venv/bin/python ~/.claude/skills/counsel-gpt/scripts/counsel.py "질문" --model gpt-4o
```

## 응답 형식

🤖 이모지로 GPT 응답임을 표시합니다.

## 설정

- API 키: `~/.claude/.env`의 `OPENAI_API_KEY`
- 기본 모델: `gpt-4.1` (Chat API 최강, SWE-bench 55%)

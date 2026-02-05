---
name: counsel-gemini
description: Gemini AI에게 코딩 조언을 구합니다. 코드 리뷰, 아키텍처 조언, 디버깅 힌트 등 다양한 관점을 얻을 때 사용합니다. "gemini한테 물어봐", "다른 관점" 등의 요청 시 사용.
allowed-tools:
  - Bash
  - Read
---

# Counsel Gemini

Gemini AI에게 코딩 관련 조언을 구하는 스킬입니다.

## 사용법

```bash
~/.claude/.venv/bin/python ~/.claude/skills/counsel-gemini/scripts/counsel.py "질문"
~/.claude/.venv/bin/python ~/.claude/skills/counsel-gemini/scripts/counsel.py "질문" --context "코드"
~/.claude/.venv/bin/python ~/.claude/skills/counsel-gemini/scripts/counsel.py "질문" --file src/main.ts
~/.claude/.venv/bin/python ~/.claude/skills/counsel-gemini/scripts/counsel.py "질문" --model gemini-2.5-pro
```

## 응답 형식

💎 이모지로 Gemini 응답임을 표시합니다.

## 설정

- API 키: `~/.claude/.env`의 `GEMINI_API_KEY`
- 기본 모델: `gemini-3-pro-preview` (2026 최신, 추론 능력 최강)

---
name: calendar-reader
description: Google Calendar에서 캘린더 목록, 이벤트, 빈 시간을 조회하는 스킬. 일정 확인, 미팅 조회, 빈 시간 찾기에 활용.
version: 1.0.0
author: 서인근
tags:
  - google-calendar
  - read
  - api
skill_type: managed
---

# calendar-reader

Google Calendar API를 통해 캘린더 데이터를 조회하는 스킬입니다.

## 사용 시점

다음과 같은 요청 시 사용:

1. **"오늘 일정 뭐야?"**
2. **"이번 주 미팅 보여줘"**
3. **"캘린더 목록 조회"**
4. **"빈 시간 찾아줘"**
5. **"내일 일정 확인해줘"**

## 실행 명령어

```bash
~/.claude/.venv/bin/python ~/.claude/skills/calendar-reader/scripts/read_calendar.py \
  --date="2026-01-27" \
  --days=7
```

## 인자

| 인자 | 필수 | 설명 | 기본값 |
|------|------|------|--------|
| `--token` | - | OAuth 토큰 pickle 경로 | 자동 탐색 |
| `--list-calendars` | - | 캘린더 목록만 출력 | - |
| `--calendar-id` | - | 캘린더 ID | primary |
| `--date` | - | 조회 시작일 (YYYY-MM-DD) | 오늘 |
| `--days` | - | 조회 기간 (일) | 7 |
| `--query` | - | 검색 키워드 | - |
| `--max-results` | - | 최대 이벤트 수 | 50 |
| `--freebusy` | - | 빈 시간/바쁜 시간 조회 | - |
| `--format` | - | 출력 형식 (json/table) | table |

## 사용 예시

### 캘린더 목록 조회

```bash
~/.claude/.venv/bin/python ~/.claude/skills/calendar-reader/scripts/read_calendar.py \
  --list-calendars
```

### 오늘부터 7일간 일정 조회

```bash
~/.claude/.venv/bin/python ~/.claude/skills/calendar-reader/scripts/read_calendar.py \
  --days=7
```

### 특정 날짜 일정 조회

```bash
~/.claude/.venv/bin/python ~/.claude/skills/calendar-reader/scripts/read_calendar.py \
  --date="2026-01-27" \
  --days=1
```

### 키워드 검색

```bash
~/.claude/.venv/bin/python ~/.claude/skills/calendar-reader/scripts/read_calendar.py \
  --query="TYM" \
  --days=30
```

### 빈 시간 조회

```bash
~/.claude/.venv/bin/python ~/.claude/skills/calendar-reader/scripts/read_calendar.py \
  --freebusy \
  --date="2026-01-27" \
  --days=5
```

### JSON 출력

```bash
~/.claude/.venv/bin/python ~/.claude/skills/calendar-reader/scripts/read_calendar.py \
  --format=json \
  --days=3
```

## 토큰 위치

OAuth 토큰 파일은 다음 순서로 탐색:

1. `--token` 인자
2. `GOOGLE_CALENDAR_TOKEN` 환경변수
3. `~/work/vault-worv/.credentials/calendar_token.pickle`
4. `~/.credentials/calendar_token.pickle`

## 의존성

```bash
~/.claude/.venv/bin/pip install google-api-python-client google-auth
```

## 출력 예시

### Table (기본)

```
Calendar: primary
Period: 2026-01-27 ~ 2026-02-03
--------------------------------------------------------------------------------

📅 2026-01-27 (월)
----------------------------------------
  09:00 - 10:00   TYM ICT Daily Sync
                  📍 Google Meet
  14:00 - 15:00   1:1 미팅

📅 2026-01-28 (화)
----------------------------------------
  10:00 - 11:00   Weekly Leads Sync
```

### JSON

```json
[
  {
    "id": "abc123",
    "summary": "TYM ICT Daily Sync",
    "start": "2026-01-27T09:00:00+09:00",
    "end": "2026-01-27T10:00:00+09:00",
    "location": "Google Meet",
    "attendees": [...]
  }
]
```

## 관련 스킬

- `calendar-writer` - 캘린더 이벤트 생성/수정/삭제
- `coffeechat` - 커피챗 미팅 예약

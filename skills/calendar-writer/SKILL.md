---
name: calendar-writer
description: Google Calendar에 이벤트를 생성, 수정, 삭제하는 스킬. 미팅 예약, 일정 추가, Google Meet 생성에 활용.
version: 1.0.0
author: 서인근
tags:
  - google-calendar
  - write
  - api
skill_type: managed
---

# calendar-writer

Google Calendar API를 통해 이벤트를 생성, 수정, 삭제하는 스킬입니다.

## 사용 시점

다음과 같은 요청 시 사용:

1. **"미팅 잡아줘"**
2. **"일정 추가해줘"**
3. **"캘린더에 등록해줘"**
4. **"미팅 취소해줘"**
5. **"일정 수정해줘"**

## 실행 명령어

```bash
~/.claude/.venv/bin/python ~/.claude/skills/calendar-writer/scripts/write_calendar.py \
  --action=create \
  --summary="TYM ICT 미팅" \
  --start="2026-01-28T14:00:00" \
  --end="2026-01-28T15:00:00"
```

## 인자

| 인자 | 필수 | 설명 | 기본값 |
|------|------|------|--------|
| `--token` | - | OAuth 토큰 pickle 경로 | 자동 탐색 |
| `--action` | ✅ | 작업 종류 (create/update/delete/quick-add) | - |
| `--calendar-id` | - | 캘린더 ID | primary |
| `--event-id` | update/delete | 이벤트 ID | - |
| `--summary` | create | 이벤트 제목 | - |
| `--start` | create | 시작 시간 | - |
| `--end` | create | 종료 시간 | - |
| `--description` | - | 설명 | - |
| `--location` | - | 장소 | - |
| `--attendees` | - | 참석자 이메일 (쉼표 구분) | - |
| `--timezone` | - | 타임존 | Asia/Seoul |
| `--all-day` | - | 종일 이벤트 | - |
| `--meet` | - | Google Meet 링크 생성 | - |
| `--no-notify` | - | 알림 미발송 | - |
| `--text` | quick-add | 자연어 텍스트 | - |

## 사용 예시

### 이벤트 생성 (기본)

```bash
~/.claude/.venv/bin/python ~/.claude/skills/calendar-writer/scripts/write_calendar.py \
  --action=create \
  --summary="팀 미팅" \
  --start="2026-01-28T14:00:00" \
  --end="2026-01-28T15:00:00"
```

### 이벤트 생성 (Google Meet 포함)

```bash
~/.claude/.venv/bin/python ~/.claude/skills/calendar-writer/scripts/write_calendar.py \
  --action=create \
  --summary="화상 미팅" \
  --start="2026-01-28T10:00:00" \
  --end="2026-01-28T11:00:00" \
  --meet \
  --attendees="colleague@maum.ai,partner@company.com"
```

### 이벤트 생성 (참석자 + 장소)

```bash
~/.claude/.venv/bin/python ~/.claude/skills/calendar-writer/scripts/write_calendar.py \
  --action=create \
  --summary="점심 미팅" \
  --start="2026-01-28T12:00:00" \
  --end="2026-01-28T13:00:00" \
  --location="성수동 카페" \
  --attendees="friend@gmail.com" \
  --description="신년 인사"
```

### 종일 이벤트 생성

```bash
~/.claude/.venv/bin/python ~/.claude/skills/calendar-writer/scripts/write_calendar.py \
  --action=create \
  --summary="연차" \
  --start="2026-02-01" \
  --end="2026-02-02" \
  --all-day
```

### Quick Add (자연어)

```bash
~/.claude/.venv/bin/python ~/.claude/skills/calendar-writer/scripts/write_calendar.py \
  --action=quick-add \
  --text="Meeting with TYM tomorrow at 3pm for 1 hour"
```

### 이벤트 수정

```bash
~/.claude/.venv/bin/python ~/.claude/skills/calendar-writer/scripts/write_calendar.py \
  --action=update \
  --event-id="abc123xyz" \
  --summary="수정된 제목" \
  --start="2026-01-28T15:00:00" \
  --end="2026-01-28T16:00:00"
```

### 이벤트 삭제

```bash
~/.claude/.venv/bin/python ~/.claude/skills/calendar-writer/scripts/write_calendar.py \
  --action=delete \
  --event-id="abc123xyz"
```

## 토큰 위치

OAuth 토큰 파일은 다음 순서로 탐색:

1. `--token` 인자
2. `GOOGLE_CALENDAR_TOKEN` 환경변수
3. `~/work/vault-worv/.credentials/calendar_token.pickle`
4. `~/.credentials/calendar_token.pickle`

## 시간 형식

| 형식 | 예시 | 설명 |
|------|------|------|
| DateTime | `2026-01-28T14:00:00` | 특정 시간 |
| DateTime + TZ | `2026-01-28T14:00:00+09:00` | 타임존 명시 |
| Date | `2026-01-28` | 종일 이벤트 |

## 의존성

```bash
~/.claude/.venv/bin/pip install google-api-python-client google-auth
```

## 출력 예시

```json
{
  "id": "abc123xyz",
  "summary": "TYM ICT 미팅",
  "start": {"dateTime": "2026-01-28T14:00:00+09:00"},
  "end": {"dateTime": "2026-01-28T15:00:00+09:00"},
  "htmlLink": "https://calendar.google.com/event?eid=xxx",
  "hangoutLink": "https://meet.google.com/xxx-xxx-xxx",
  "status": "created"
}
```

## 필수 규칙: 외부 발송 전 사용자 확인

**⚠️ 참석자가 있는 이벤트 생성/수정 시 반드시 사용자 확인을 받아야 합니다.**

Claude는 다음 상황에서 실행 전 사용자에게 확인을 받아야 합니다:

1. **이벤트 생성 시** (참석자 포함): 제목, 시간, 참석자, 설명 내용을 보여주고 확인
2. **이벤트 수정 시** (참석자에게 알림 발송되는 경우): 변경 내용을 보여주고 확인
3. **설명/메시지 변경 시**: 새 메시지 내용을 보여주고 확인

**확인 없이 실행 가능한 경우:**
- `--no-notify` 옵션 사용 시 (알림 미발송)
- 참석자 없는 개인 일정

**확인 형식 예시:**
```
📅 캘린더 이벤트를 수정합니다:
- 제목: 인근 ☕ 윤식
- 시간: 2/2(월) 13:30-14:00
- 참석자: yoonshik1205@maum.ai (알림 발송됨)
- 설명: [변경된 설명 내용]

진행할까요?
```

## 주의사항

1. **참석자 초대**: `--attendees` 사용 시 참석자에게 이메일 알림 발송
2. **알림 비활성화**: `--no-notify`로 알림 없이 생성/수정/삭제 가능
3. **이벤트 ID 확인**: update/delete 시 `calendar-reader`로 먼저 이벤트 ID 확인

## 관련 스킬

- `calendar-reader` - 캘린더 이벤트 조회
- `coffeechat` - 커피챗 미팅 예약 (빈 시간 자동 탐색)

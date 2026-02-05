# meeting-scheduler

마음AI 직원들과 회의를 쉽게 잡는 대화형 스킬입니다.

## 사용 시점

다음과 같은 요청 시 사용:
- "회의 잡아줘"
- "미팅 예약해줘"
- "김선후랑 회의 잡아줘"
- "다음주에 팀 미팅 잡아줘"

## 워크플로우

### Phase 1: 참석자 확인

사용자에게 참석자를 질문합니다.

```
AskUserQuestion: "누구와 회의하시나요? (이름 또는 이메일)"
```

입력받은 이름/이메일을 처리:
- 이름인 경우: 인물사전에서 이메일 조회
- 이메일인 경우: 그대로 사용
- 여러 명인 경우: 쉼표로 구분

**인물사전 조회 스크립트:**
```bash
~/.claude/.venv/bin/python ~/.claude/skills/meeting-scheduler/scripts/person_lookup.py \
  --names "김선후,조용준,이윤성"
```

### Phase 2: 회의 시간 확인

```
AskUserQuestion: "회의 시간은 얼마나 필요하세요?"
options: 30분, 1시간, 1시간 30분, 2시간
```

```
AskUserQuestion: "언제쯤 원하세요?"
options: 이번주, 다음주, 특정 날짜 입력
```

### Phase 3: 빈 시간 조회

참석자들의 freebusy를 조회하여 공통 빈 시간을 찾습니다.

```bash
~/.claude/.venv/bin/python ~/.claude/skills/meeting-scheduler/scripts/find_free_time.py \
  --attendees "sunhoo.kim@maum.ai,cyjun0304@maum.ai,sung@maum.ai" \
  --duration 60 \
  --start-date "2026-02-09" \
  --end-date "2026-02-13" \
  --working-hours "09:00-18:00"
```

출력: 상위 3개 가능한 시간 슬롯

### Phase 4: 시간 선택

```
AskUserQuestion: "다음 중 원하는 시간을 선택하세요"
options: [조회된 3개 시간 슬롯]
```

### Phase 5: 회의실 선택

선택된 시간에 가용한 회의실을 조회합니다.

```bash
~/.claude/.venv/bin/python ~/.claude/skills/meeting-scheduler/scripts/list_rooms.py \
  --start "2026-02-09T14:00:00" \
  --end "2026-02-09T15:00:00" \
  --min-capacity 5
```

```
AskUserQuestion: "회의실을 선택하세요"
options: [가용한 회의실 목록]
```

### Phase 6: 회의 제목 및 설명

```
AskUserQuestion: "회의 제목을 입력하세요"
```

선택적으로 설명도 입력받음.

### Phase 7: 이벤트 생성

```bash
~/.claude/.venv/bin/python ~/.claude/skills/meeting-scheduler/scripts/create_meeting.py \
  --summary "회의 제목" \
  --start "2026-02-09T14:00:00" \
  --end "2026-02-09T15:00:00" \
  --attendees "sunhoo.kim@maum.ai,cyjun0304@maum.ai" \
  --room-id "c_xxx@resource.calendar.google.com" \
  --description "회의 설명" \
  --meet
```

### Phase 8: 완료 안내

생성된 이벤트 정보를 사용자에게 안내:
- 제목
- 일시
- 참석자
- 회의실
- Google Meet 링크
- 캘린더 링크

## 인물사전 이메일 매핑

마음AI 직원 이메일은 인물사전에서 조회합니다.

**조회 우선순위:**
1. 프로젝트 인물사전: `~/work/vault-worv/20_Areas/00_인물사전/`
2. 개인 인물사전: `~/obsidian/10_Projects/Active/2511 취업작전/마음AI_WoRV/`

**알려진 이메일 (fallback):**
- 김선후: sunhoo.kim@maum.ai
- 조용준: cyjun0304@maum.ai
- 이윤성: sung@maum.ai
- 김윤식: yoonshik1205@maum.ai
- 성삼우: samwoose@maum.ai
- 서인근: inkeun.seo@maum.ai
- 박유빈: yubeen.park@maum.ai

## 회의실 리소스 ID

**알려진 회의실:**
- Silicon Valley (8명): `c_18841ts7pgvskhnujrglhn2jgnor8@resource.calendar.google.com`

새로운 회의실 ID는 기존 이벤트에서 추출하거나 Calendar API로 조회합니다.

## 의존성

기존 calendar-reader, calendar-writer 스킬의 인증 정보 사용:
- OAuth 토큰: `~/work/vault-worv/.credentials/calendar_token.pickle`

## 주의사항

1. **시간대**: 모든 시간은 Asia/Seoul (KST) 기준
2. **근무시간**: 기본 09:00-18:00, 점심시간(12:00-13:00) 제외
3. **최소 간격**: 회의 시작은 30분 단위로 제안
4. **Google Meet**: 기본 생성 (--no-meet으로 비활성화 가능)

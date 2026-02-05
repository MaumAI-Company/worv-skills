---
name: gmail-sender
description: Gmail API를 통해 이메일을 발송합니다. 커피챗 리마인더, 후속 연락, 네트워킹 메일 발송에 활용.
version: 1.0.0
author: claude
triggers:
  - 메일 보내줘
  - 이메일 발송해줘
  - 리마인더 메일 보내줘
  - "[인물명]에게 메일 보내줘"
tools:
  - Bash
  - Read
---

# Gmail Sender 스킬

Gmail API를 활용하여 이메일을 발송하는 스킬입니다.

## 주요 기능

1. **이메일 발송** - 수신자, 제목, 본문 지정하여 발송
2. **미리보기** - 발송 전 내용 확인 (dry-run)
3. **확인 프롬프트** - 실수 방지를 위한 발송 전 확인

## 사전 설정 (최초 1회)

### 기존 gmail-reader 사용자

기존 OAuth 클라이언트가 있으면 발송용 토큰만 새로 생성하면 됩니다.

```bash
source /Users/inkeun/projects/obsidian/.venv/bin/activate && \
  python /Users/inkeun/projects/obsidian/.claude/skills/gmail-sender/scripts/gmail_client.py
```

- 브라우저가 열리고 Google 계정 로그인 요청
- **발송 권한 포함** 동의 필요
- 토큰이 `gmail_send_token.pickle`로 저장됨

### 신규 사용자

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. **APIs & Services > Library**에서 **Gmail API** 활성화
3. **APIs & Services > Credentials**에서 OAuth client ID 생성 (Desktop app)
4. JSON 다운로드 → `/Users/inkeun/projects/obsidian/.creds/oauth_client.json`
5. 위 명령어로 인증 실행

## 사용법

### 기본 발송

```bash
source /Users/inkeun/projects/obsidian/.venv/bin/activate && \
  python /Users/inkeun/projects/obsidian/.claude/skills/gmail-sender/scripts/send_email.py \
    --to "recipient@example.com" \
    --subject "제목" \
    --body "본문 내용"
```

### 미리보기 (실제 발송 안 함)

```bash
python .claude/skills/gmail-sender/scripts/send_email.py \
  --to "recipient@example.com" \
  --subject "테스트" \
  --body "테스트 본문" \
  --dry-run
```

### 확인 없이 바로 발송

```bash
python .claude/skills/gmail-sender/scripts/send_email.py \
  --to "recipient@example.com" \
  --subject "제목" \
  --body "본문" \
  --yes
```

### 파일에서 본문 읽기

```bash
python .claude/skills/gmail-sender/scripts/send_email.py \
  --to "recipient@example.com" \
  --subject "제목" \
  --body "" \
  --body-file /path/to/body.txt
```

## 활용 시나리오

### 1. 커피챗 리마인더

```bash
source /Users/inkeun/projects/obsidian/.venv/bin/activate && \
  python .claude/skills/gmail-sender/scripts/send_email.py \
    --to "stashby.me@gmail.com" \
    --subject "[리마인더] 오늘 17시 커피챗 안내드립니다" \
    --body "안녕하세요, 서인근입니다.

오늘 17시 커피챗 리마인더 드립니다.

일시: 2026년 1월 14일 (화) 17:00-18:00
장소: Google Meet (https://meet.google.com/uvq-gkag-ehk)

혹시 변동사항 있으시면 편하게 알려주세요.
오늘 뵙겠습니다!

서인근 드림"
```

### 2. 후속 연락 (Thank you 메일)

```bash
python .claude/skills/gmail-sender/scripts/send_email.py \
  --to "contact@example.com" \
  --subject "좋은 대화 감사했습니다" \
  --body "안녕하세요, 서인근입니다.

오늘 커피챗에서 좋은 대화 나눌 수 있어 감사했습니다.
말씀하신 [주제]에 대해 더 생각해보고 공유드리겠습니다.

앞으로도 종종 연락드리겠습니다.

감사합니다.
서인근 드림"
```

### 3. 네트워킹 첫 연락

```bash
python .claude/skills/gmail-sender/scripts/send_email.py \
  --to "new.contact@example.com" \
  --subject "[앤틀러 5기] 커피챗 요청드립니다" \
  --body "안녕하세요, 앤틀러 5기 서인근입니다.
..."
```

## 파일 구조

```
.claude/skills/gmail-sender/
├── SKILL.md                    # 이 파일
└── scripts/
    ├── gmail_client.py         # Gmail API 클라이언트 (인증, 발송 권한)
    └── send_email.py           # 이메일 발송 스크립트
```

## 필요 패키지

```bash
# 루트 venv에 설치 (gmail-reader와 동일)
source /Users/inkeun/projects/obsidian/.venv/bin/activate
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## 필수 규칙: 발송 전 사용자 확인

**⚠️ 이메일 발송 전 반드시 사용자 확인을 받아야 합니다.**

Claude는 이메일을 발송하기 전에 다음 정보를 보여주고 확인을 받아야 합니다:

1. **수신자** (To)
2. **제목** (Subject)
3. **본문 내용** (Body) - 전체 또는 요약

**확인 형식 예시:**
```
📧 이메일을 발송합니다:
- 수신자: recipient@example.com
- 제목: [리마인더] 오늘 17시 커피챗 안내드립니다
- 본문:
  안녕하세요, 서인근입니다.
  오늘 17시 커피챗 리마인더 드립니다.
  ...

발송할까요?
```

**주의: `--yes` 옵션은 사용자가 명시적으로 요청한 경우에만 사용합니다.**

## 주의사항

- **발송 전 확인**: 기본적으로 발송 전 확인 프롬프트 표시 (`--yes`로 스킵 가능)
- **별도 토큰**: gmail-reader와 별도 토큰 사용 (`gmail_send_token.pickle`)
- **되돌리기 불가**: 발송된 이메일은 취소할 수 없음
- **개인 계정용**: OAuth2 인증이므로 개인 Gmail 계정에서 사용

## 트러블슈팅

### "OAuth credentials 파일이 없습니다" 오류
→ Google Cloud Console에서 OAuth 클라이언트 생성 후 JSON 다운로드 필요

### "Insufficient Permission" 오류
→ 기존 토큰에 발송 권한이 없음. 토큰 삭제 후 재인증:
```bash
rm /Users/inkeun/projects/obsidian/.creds/gmail_send_token.pickle
python .claude/skills/gmail-sender/scripts/gmail_client.py
```

### "Access blocked" 오류
→ Google Cloud Console > OAuth consent screen > Test users에 본인 이메일 추가

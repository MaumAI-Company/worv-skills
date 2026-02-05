# WoRV Skills

WoRV팀 Claude Code 스킬 모음입니다.

## 설치 방법

### 개별 스킬 설치

```bash
git clone https://github.com/MaumAI-Company/worv-skills.git
cp -r worv-skills/skills/[skill-name] ~/.claude/skills/
```

### 전체 스킬 설치

```bash
git clone https://github.com/MaumAI-Company/worv-skills.git ~/.claude/plugins/worv-skills
```

## 환경변수 설정

스킬마다 필요한 API 키와 설정이 다릅니다. `.env.sample`을 참고하여 `~/.claude/.env` 파일을 생성하세요.

```bash
cp .env.sample ~/.claude/.env
# 이후 실제 값으로 수정
```

### Google Calendar API (meeting-scheduler, calendar-reader, calendar-writer)

**필요한 환경변수:**
```bash
GOOGLE_CALENDAR_TOKEN=~/.credentials/calendar_token.pickle
```

**토큰 발급 방법:**

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. **API 및 서비스 > 라이브러리**에서 "Google Calendar API" 검색 후 **사용 설정**
4. **API 및 서비스 > 사용자 인증 정보 > + 사용자 인증 정보 만들기 > OAuth 클라이언트 ID**
   - 애플리케이션 유형: **데스크톱 앱**
   - 이름: 원하는 이름 입력
5. **OAuth 동의 화면** 설정 (처음인 경우)
   - 사용자 유형: 내부 (조직) 또는 외부
   - 앱 이름, 이메일 입력
   - 범위 추가: `https://www.googleapis.com/auth/calendar`
6. 생성된 클라이언트 ID에서 **JSON 다운로드** → `credentials.json`으로 저장
7. 아래 스크립트 실행하여 `token.pickle` 생성:

```python
# generate_token.py
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/calendar']

flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
creds = flow.run_local_server(port=0)

import pickle
with open('calendar_token.pickle', 'wb') as f:
    pickle.dump(creds, f)

print("토큰 생성 완료: calendar_token.pickle")
```

```bash
# 실행
pip install google-auth-oauthlib
python generate_token.py
mv calendar_token.pickle ~/.credentials/
```

### OpenAI API (audio-transcriber)

**필요한 환경변수:**
```bash
OPENAI_API_KEY=sk-xxx
```

**발급 방법:**
1. [OpenAI Platform](https://platform.openai.com/) 로그인
2. **API Keys** 메뉴에서 **Create new secret key**
3. 생성된 키를 `.env`에 저장

### Google Gemini API (gemini-image, counsel-gemini)

**필요한 환경변수:**
```bash
GEMINI_API_KEY=xxx
```

**발급 방법:**
1. [Google AI Studio](https://aistudio.google.com/) 접속
2. **Get API Key** 클릭
3. 새 키 생성 또는 기존 키 사용
4. 생성된 키를 `.env`에 저장

### 인물사전 경로 (meeting-scheduler)

**필요한 환경변수:**
```bash
PERSON_DICTIONARY_PATH=~/obsidian/20_Areas/00_인물사전/
```

이름으로 이메일을 조회하는 기능에 사용됩니다. Obsidian 인물사전 폴더 경로를 지정하세요.

---

## 스킬 목록

### 📅 캘린더 & 미팅
- **meeting-scheduler**: 마음AI 캘린더 미팅 스케줄링 (freebusy, 회의실 예약, Google Meet)
- **calendar-reader**: Google Calendar 일정 조회, 빈 시간 찾기
- **calendar-writer**: Google Calendar 이벤트 생성/수정/삭제

### 🎙️ 미팅 & 녹음
- **audio-transcriber**: OpenAI Whisper API 기반 STT (화자분리 지원)

### 📄 문서 처리
- **ppt-generator**: 한국어 최적화 미니멀 PPT 생성 (Pretendard/Noto Serif KR)
- **pptx**: PPT 편집, 슬라이드 조작, 노트 추가
- **pdf**: PDF 텍스트/테이블 추출, 병합/분할, 폼 처리

### 📊 Google Sheets
- **gsheet-reader**: Google Sheets 읽기 (JSON/CSV/테이블 형식)
- **gsheet-writer**: Google Sheets 쓰기 (단일/배치 업데이트)

### 🖼️ 이미지
- **gemini-image**: Gemini API 이미지 생성 (Nano Banana/Pro)

### 📧 이메일
- **gmail-reader**: Gmail 검색/조회
- **gmail-sender**: Gmail 발송

### 🔧 Git & 개발
- **git-commit-push**: Git 커밋 메시지 자동 작성 + 푸시
- **worktree-setup**: Git worktree 기반 병렬 개발 환경 셋업
- **worktree-cleanup**: Git worktree 정리

### 📋 요구사항
- **clarify**: 모호한 요구사항 → 명확한 스펙 변환

### 🤖 AI 상담
- **counsel-gemini**: Gemini AI에게 코딩 조언
- **counsel-gpt**: GPT에게 코딩 조언
- **council**: 여러 AI에게 병렬로 조언 구하기

### ☁️ GCP 인프라
- **gcp-vm-create**: GCP VM 생성 마법사
- **gcp-project-setup**: GCP 프로젝트 생성/설정 자동화

---

## 기여 가이드

### 사전 요구사항

- **Claude Code** CLI 설치
- **GitHub CLI** (`gh`) 설치 및 인증
- **MaumAI-Company** 조직 접근 권한

```bash
# gh CLI 설치 (macOS)
brew install gh

# 인증
gh auth login
```

### 스킬 구조

새 스킬은 다음 구조를 따라야 합니다:

```
skills/
└── my-skill/
    ├── SKILL.md           # 필수: 스킬 정의 및 워크플로우
    ├── scripts/           # Python/Bash 스크립트
    │   └── main.py
    ├── requirements.txt   # Python 의존성 (있는 경우)
    └── references/        # 참조 문서 (선택)
```

### SKILL.md 형식

```yaml
---
name: my-skill
description: >
  스킬 설명 (1-2문장).
  트리거 키워드 포함 권장.
tools:              # 선택: 사용할 도구 제한
  - Bash
  - Read
  - Write
argument-hint: "[arg1] [--option]"  # 선택: 인자 힌트
---

# 스킬 제목

## 사용 시점

- "트리거 문구 1"
- "트리거 문구 2"

## 워크플로우

### Phase 1: 첫 번째 단계

실행할 작업 설명...

### Phase 2: 두 번째 단계

...
```

### 게시 방법

#### 방법 1: /publish-worv 사용 (권장)

```bash
# 1. 로컬에서 스킬 개발
~/.claude/skills/my-skill/

# 2. Claude Code에서 게시
/publish-worv my-skill
```

#### 방법 2: 수동 PR

```bash
# 1. 레포 클론
git clone https://github.com/MaumAI-Company/worv-skills.git
cd worv-skills

# 2. 스킬 추가
cp -r ~/.claude/skills/my-skill skills/

# 3. 민감 정보 제거
rm -f skills/my-skill/.env
rm -f skills/my-skill/*credentials*
rm -f skills/my-skill/*.pickle

# 4. 커밋 & 푸시
git add .
git commit -m "feat: add my-skill"
git push
```

### 코드 스타일

**Python 스크립트**
- Python 3.9+ 호환
- 타입 힌트 권장
- 의존성은 `requirements.txt`에 명시
- 환경변수/시크릿은 `.env`에서 로드 (`python-dotenv`)

**SKILL.md**
- Phase 단위로 워크플로우 정의
- 각 Phase에 명확한 실행 지침
- 에러 처리 섹션 포함 권장

### 민감 정보 처리

다음 파일/패턴은 **절대 커밋하지 마세요**:

- `.env`, `.env.*`
- `*credentials*.json`
- `*token*.pickle`, `*.pickle`
- API 키가 포함된 파일

### 테스트

게시 전 로컬에서 테스트:

```bash
# 스킬이 로드되는지 확인
ls ~/.claude/skills/my-skill/SKILL.md

# Claude Code에서 실행 테스트
/my-skill --help  # 또는 트리거 문구 사용
```

### 업데이트

기존 스킬 업데이트 시:

```bash
# /publish-worv가 자동으로 변경사항 감지
/publish-worv my-skill

# "기존 스킬을 덮어쓰시겠습니까?" 확인 후 업데이트
```

---

## 문의

- **관리자**: @inkeun (서인근)
- **Slack**: #worv-claude-code

## 라이선스

MIT

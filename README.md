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

## 기여 방법

1. 스킬 개발: `~/.claude/skills/[skill-name]/`
2. 게시: `/publish-worv [skill-name]`

## 라이선스

MIT

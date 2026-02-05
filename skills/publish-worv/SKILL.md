---
name: publish-worv
description: WoRV팀 공용 스킬 레포(MaumAI-Company/worv-skills)에 스킬을 게시. 팀원들이 공유할 수 있는 Claude Code 스킬 배포용.
tools:
  - Bash
  - Read
  - Glob
  - Write
  - Edit
  - AskUserQuestion
argument-hint: "[skill-name] | --list | --dry-run [skill-name]"
---

# /publish-worv 스킬

로컬 또는 전역 **스킬**을 WoRV팀 공용 레포 `MaumAI-Company/worv-skills`에 게시합니다.

## /publish vs /publish-worv

- **/publish**: 개인 GitHub 레포에 개별 스킬 게시 (1 스킬 = 1 레포)
- **/publish-worv**: WoRV팀 공용 레포에 스킬 추가 (N 스킬 = 1 레포)

## 사용법

```bash
/publish-worv --list              # 게시 가능한 스킬 목록
/publish-worv --dry-run [name]    # 미리보기 (실제 게시 안 함)
/publish-worv [skill-name]        # 해당 스킬을 worv-skills 레포에 게시
```

---

## 설정

- **대상 레포**: `MaumAI-Company/worv-skills`
- **스킬 위치**: `skills/{skill-name}/`
- **커밋 형식**: `feat: add {skill-name}` (신규) / `feat: update {skill-name}` (업데이트)

---

## 실행 워크플로우

### Phase 1: 인자 파싱

**인자:** `$ARGUMENTS`

- `--list`: 게시 가능한 스킬 목록 표시
- `--dry-run [name]`: 미리보기 (실제 게시 안 함)
- `[name]`: 해당 스킬을 게시
- 인자 없으면 `--list` 모드로 동작

### Phase 2: 스킬 탐색

다음 순서로 스킬을 탐색합니다 (로컬 우선):

1. `.claude/skills/[name]/SKILL.md` (로컬)
2. `~/.claude/skills/[name]/SKILL.md` (전역)

**필수 검증:**
- SKILL.md 존재 여부
- `name`, `description` 필드 존재

### Phase 3: gh CLI 및 권한 확인

```bash
# gh CLI 설치 확인
which gh || echo "gh CLI not found"

# 인증 상태 확인
gh auth status

# MaumAI-Company 조직 접근 권한 확인
gh api orgs/MaumAI-Company --jq '.login' 2>/dev/null || echo "NO_ACCESS"
```

**접근 권한 없으면:**
- "MaumAI-Company 조직 접근 권한이 없습니다. 관리자에게 문의하세요." 메시지 출력 후 종료

### Phase 4: 레포 존재 여부 확인

```bash
# worv-skills 레포 존재 확인
gh repo view MaumAI-Company/worv-skills 2>/dev/null && echo "EXISTS" || echo "NOT_FOUND"
```

**레포 없으면 (첫 실행 시):**
1. AskUserQuestion으로 확인: "MaumAI-Company/worv-skills 레포를 생성하시겠습니까?"
2. 승인 시:
   ```bash
   gh repo create MaumAI-Company/worv-skills --public \
     --description "WoRV팀 Claude Code 스킬 모음" \
     --clone
   ```
3. 기본 README.md 생성 후 push

### Phase 5: 기존 스킬 존재 확인

```bash
# 레포 clone (shallow)
TEMP_DIR=$(mktemp -d)
gh repo clone MaumAI-Company/worv-skills $TEMP_DIR -- --depth 1

# 스킬 폴더 존재 확인
ls $TEMP_DIR/skills/[skill-name] 2>/dev/null && echo "EXISTS" || echo "NEW"
```

**기존 스킬 존재 시:**
- 변경사항 diff 표시
- AskUserQuestion: "기존 스킬을 덮어쓰시겠습니까?"
  - 예: 계속 진행
  - 아니오: 작업 취소

### Phase 6: 파일 복사

```bash
# 스킬 폴더 생성
mkdir -p $TEMP_DIR/skills/[skill-name]

# 스킬 파일 전체 복사
cp -r [source-skill]/* $TEMP_DIR/skills/[skill-name]/

# 민감 정보 제거
rm -f $TEMP_DIR/skills/[skill-name]/.env
rm -f $TEMP_DIR/skills/[skill-name]/*credentials*
rm -f $TEMP_DIR/skills/[skill-name]/*token*
rm -f $TEMP_DIR/skills/[skill-name]/*.pickle
```

### Phase 7: 루트 README 업데이트

루트 `README.md`에 스킬 목록 자동 업데이트:

```markdown
# WoRV Skills

WoRV팀 Claude Code 스킬 모음입니다.

## 설치 방법

```bash
# 전체 레포 clone 후 원하는 스킬 복사
git clone https://github.com/MaumAI-Company/worv-skills.git
cp -r worv-skills/skills/[skill-name] ~/.claude/skills/
```

## 스킬 목록

- **meeting-scheduler**: 마음AI 캘린더 미팅 스케줄링
- **[새 스킬 이름]**: [설명]
...
```

### Phase 8: 커밋 & 푸시

```bash
cd $TEMP_DIR

git add .

# 신규 스킬
git commit -m "feat: add [skill-name]

[description]

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"

# 또는 업데이트
git commit -m "feat: update [skill-name]

[변경 사항 요약]

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"

git push
```

### Phase 9: 결과 보고

```
✅ 스킬이 게시되었습니다!

레포: https://github.com/MaumAI-Company/worv-skills
스킬: skills/[skill-name]/

설치 명령:
  git clone https://github.com/MaumAI-Company/worv-skills.git
  cp -r worv-skills/skills/[skill-name] ~/.claude/skills/
```

### Phase 10: 정리

```bash
rm -rf $TEMP_DIR
```

---

## --list 모드

게시 가능한 스킬을 목록으로 표시:

```
게시 가능한 스킬:

- **meeting-scheduler** (전역)
  마음AI 캘린더 미팅 스케줄링

- **audio-transcriber** (전역)
  OpenAI Whisper로 오디오 전사

- **my-custom-skill** (로컬)
  프로젝트별 커스텀 스킬
```

---

## --dry-run 모드

실제 게시 없이 다음을 표시:

1. 스킬 정보 (이름, 설명, 위치)
2. 복사될 파일 목록
3. 민감 정보 파일 (제외될 항목)
4. 커밋 메시지 미리보기

---

## 에러 처리

- **gh CLI 미설치**: `brew install gh` 안내 후 종료
- **gh 인증 안됨**: `gh auth login` 안내
- **MaumAI-Company 접근 권한 없음**: 관리자 문의 안내
- **SKILL.md 없음**: `/skill-creator` 사용 안내
- **description 없음**: frontmatter 수정 요청

---

## 민감 정보 제외 패턴

다음 파일/패턴은 게시에서 제외:

**파일명:**
- `.env`, `.env.*`
- `*credentials*.json`
- `*token*.pickle`
- `*.pickle`
- `*_secret*`

**내용 패턴 (경고만):**
- `sk-...` (OpenAI API 키)
- `AIza...` (Google API 키)
- `ghp_...`, `gho_...` (GitHub 토큰)

---

## 레포 초기 생성 시 기본 파일

### README.md

```markdown
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

(자동 업데이트됨)

## 기여 방법

1. 스킬 개발: `~/.claude/skills/[skill-name]/`
2. 게시: `/publish-worv [skill-name]`

## 라이선스

MIT
```

### .gitignore

```
.env
.env.*
*.pickle
*.pyc
__pycache__/
*.log
.DS_Store
credentials.json
*_token.pickle
```

### LICENSE (MIT)

```
MIT License

Copyright (c) 2026 maum.ai WoRV Team

Permission is hereby granted, free of charge, to any person obtaining a copy...
```

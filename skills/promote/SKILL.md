---
name: promote
description: 프로젝트의 스킬/에이전트/커맨드를 전역(~/.claude) 또는 공유 저장소(~/projects/claudesystem/.claude)에 배포
tools:
  - Bash
  - Read
  - Glob
  - AskUserQuestion
argument-hint: "[name] | --list"
---

# Promote: 스킬/에이전트/커맨드 배포

프로젝트 로컬 `.claude/` 폴더의 스킬, 에이전트, 커맨드를 전역 또는 공유 저장소로 배포합니다.

## 인자

`$ARGUMENTS`

## 워크플로우

### 1. 인자 파싱

인자를 분석하여 모드 결정:
- `--list`: 배포 가능한 항목 목록 조회
- 그 외: 해당 이름의 스킬/에이전트/커맨드 배포

### 2. 프로젝트 폴더 확인

현재 프로젝트의 `.claude/` 폴더 존재 확인:
- 없으면 에러 메시지 출력 후 종료

### 3. `--list` 모드 처리

`--list` 인자가 주어진 경우:

1. Glob으로 배포 가능 항목 탐색:
   - `.claude/skills/*/SKILL.md` → skills
   - `.claude/agents/*.md` → agents
   - `.claude/commands/*.md` → commands

2. 각 항목의 description 추출 (YAML frontmatter)

3. 테이블 형식으로 출력:
   ```
   ## 배포 가능한 항목

   | 타입 | 이름 | 설명 |
   |------|------|------|
   | skill | hook-creator | 훅 생성 가이드 |
   | agent | project-initializer | 프로젝트 초기화 |
   ```

4. 여기서 종료

### 4. 배포 모드 처리 (특정 항목 배포)

항목 이름이 주어진 경우:

#### 4.1 타입 자동 감지

다음 순서로 확인:
1. `.claude/skills/[name]/SKILL.md` 존재 → **skill** (폴더 단위)
2. `.claude/agents/[name].md` 존재 → **agent** (단일 파일)
3. `.claude/commands/[name].md` 존재 → **command** (단일 파일)
4. 없으면 에러: "항목을 찾을 수 없습니다. /promote --list 로 확인하세요."

#### 4.2 배포 대상 선택

AskUserQuestion으로 사용자에게 질문:
```
배포 대상을 선택해주세요:
1. 전역 (~/.claude/) - 모든 프로젝트에서 사용
2. 공유 저장소 (~/projects/claudesystem/.claude/) - 공개/공유용
3. 둘 다
```

#### 4.3 일반화 확인 (선택적)

파일 내용에서 프로젝트 특화 경로 검색:
- `/Users/*/projects/*/` 패턴

발견 시 AskUserQuestion으로 질문:
```
프로젝트 특화 경로가 발견되었습니다:
- [경로들...]

일반화하시겠습니까? (./ 또는 플레이스홀더로 치환)
1. 예
2. 아니오
```

#### 4.4 충돌 확인 및 버전 비교

대상 경로에 동일 이름 항목이 존재하면 **버전 비교** 수행:

**4.4.1 버전 정보 수집**

로컬과 대상 모두에서 SKILL.md (또는 .md 파일) 파싱:
```bash
# YAML frontmatter에서 추출
- name
- description
- version (있으면)
```

**4.4.2 비교 분석**

다음 항목들을 비교:
1. **version 필드**: 시맨틱 버전 비교 (1.2.0 > 1.1.0)
2. **description 길이/트리거 수**: 더 상세한 버전이 좋음
3. **파일 크기/라인 수**: 더 많은 내용 = 더 완성도 높음
4. **최종 수정일**: 최신 버전 확인

**4.4.3 비교 결과 표시**

```
'[name]' 버전 비교:

| 항목 | 로컬 | 전역 |
|------|------|------|
| version | 1.2.0 | 1.1.0 |
| description | 7개 트리거 | 5개 트리거 |
| 파일 크기 | 8.5KB | 6.2KB |
| 수정일 | 2025-01-16 | 2025-01-10 |

차이점:
- 로컬: 한국어 트리거 추가 ("커밋 푸시해줘", "변경사항 저장해줘")
- 로컬: "Bash 대신 이 스킬 우선 사용" 안내 포함

추천: 로컬 버전 (더 최신, 더 상세)
```

**4.4.4 사용자 선택**

AskUserQuestion으로 질문:
```
어떤 버전을 사용하시겠습니까?

1. 로컬 버전으로 덮어쓰기 (추천)
2. 전역 버전 유지 (로컬 삭제만)
3. 직접 확인 후 결정 (diff 표시)
4. 스킵 (아무것도 안함)
```

"직접 확인" 선택 시:
```bash
diff -u [전역 SKILL.md] [로컬 SKILL.md] | head -50
```

#### 4.5 배포 실행

**중요: Python 스킬의 venv 경로 변환**

전역 배포 시, Python 스킬의 가상환경 경로를 자동 변환:
- `$PROJECT_ROOT/.venv` → `~/.claude/venv`
- `source $PROJECT_ROOT/.venv/bin/activate && python` → `~/.claude/venv/bin/python`

```bash
# SKILL.md 및 Python 스크립트에서 경로 치환
sed -i '' 's|\$PROJECT_ROOT/\.venv|~/.claude/venv|g' [파일들]
sed -i '' 's|source \$PROJECT_ROOT/\.venv/bin/activate && python|~/.claude/venv/bin/python|g' [파일들]
```

**Skill 배포** (폴더 복사):
```bash
mkdir -p [target]/skills/
cp -r .claude/skills/[name] [target]/skills/
# 전역 배포 시 venv 경로 변환 실행
```

**Agent 배포** (파일 복사):
```bash
mkdir -p [target]/agents/
cp .claude/agents/[name].md [target]/agents/
```

**Command 배포** (파일 복사):
```bash
mkdir -p [target]/commands/
cp .claude/commands/[name].md [target]/commands/
```

#### 4.6 로컬 삭제 확인 (필수)

배포 완료 후, AskUserQuestion으로 로컬 삭제 여부 확인:
```
배포가 완료되었습니다.

로컬의 원본을 삭제하시겠습니까?
(전역/공유 저장소에 배포되었으므로 로컬 중복 제거 권장)

삭제 대상:
- [로컬 경로 목록]

1. 예 - 로컬 삭제 (권장)
2. 아니오 - 로컬 유지
```

**삭제 실행** (사용자가 "예" 선택 시):

**Skill 삭제** (폴더):
```bash
rm -rf .claude/skills/[name]
```

**Agent 삭제** (파일):
```bash
rm .claude/agents/[name].md
```

**Command 삭제** (파일):
```bash
rm .claude/commands/[name].md
```

**관련 항목 검색 및 삭제 (선택적)**:
- 스킬 배포 시, 관련 에이전트/커맨드 존재 여부 확인
- 발견 시 추가 삭제 제안 (별도 AskUserQuestion)

#### 4.7 다른 프로젝트 중복 정리 (전역 배포 시)

**전역(~/.claude/) 배포 선택 시에만 실행**

1. **다른 프로젝트 스캔**:
```bash
find ~/projects -path "*/node_modules" -prune -o \
  -path "*/.venv" -prune -o \
  -path "*/venv" -prune -o \
  \( -name "[name].md" -o -name "[name]" \) -print 2>/dev/null \
  | grep -E "\.claude/(commands|skills|agents)"
```

2. **발견된 버전들 비교** (중요!):

각 프로젝트의 버전 정보 수집 및 비교:
```
'[name]' 전체 버전 비교:

| 위치 | version | description | 크기 |
|------|---------|-------------|------|
| 전역 (현재) | 1.1.0 | 5개 트리거 | 6.2KB |
| projectA | 1.2.0 | 7개 트리거 | 8.5KB |
| projectB | 1.0.0 | 3개 트리거 | 4.1KB |

⭐ 최적 버전: projectA (v1.2.0, 가장 상세)
```

3. **최적 버전이 전역과 다른 경우 AskUserQuestion**:
```
다른 프로젝트에 더 좋은 버전이 있습니다!

현재 전역: v1.1.0 (5개 트리거)
projectA: v1.2.0 (7개 트리거) ⭐ 추천

1. projectA 버전으로 전역 업데이트 후 모두 삭제 (추천)
2. 현재 전역 버전 유지, 나머지 삭제
3. 직접 확인 후 결정 (각 버전 diff 표시)
4. 유지 - 삭제하지 않음
```

4. **전역 업데이트 실행** (최적 버전 선택 시):
```bash
# 최적 버전으로 전역 덮어쓰기
cp -r [최적버전경로] ~/.claude/skills/[name]
```

5. **중복 삭제**:
```bash
# 전역 외 모든 로컬 복사본 삭제
rm -rf [각 프로젝트 경로]
```

6. **각 프로젝트에서 커밋** (삭제된 경우):

삭제된 프로젝트마다 git 상태 확인 후 커밋 제안:
```
다음 프로젝트에서 변경사항 커밋이 필요합니다:
- ~/projects/projectA: 1 deletion
- ~/projects/projectB: 1 deletion

각 프로젝트에서 커밋하시겠습니까?
1. 예 - 자동 커밋 (메시지: "Remove [name] promoted to global scope")
2. 아니오 - 수동으로 커밋
```

7. **결과에 포함**:
   - 전역 버전 상태 (업데이트됨/유지됨)
   - 삭제된 다른 프로젝트 경로 목록
   - 커밋된 프로젝트 목록

### 5. 결과 보고

```
## 배포 완료

### 배포된 항목
- [name] ([type])

### 버전 선택
- 선택된 버전: [위치] v[version]
- 이유: [더 최신/더 상세/사용자 선택]

### 배포 위치
- [대상 경로들]

### 복사된 파일
- [파일 목록]

### 로컬 정리
- 삭제됨: [삭제된 로컬 경로] (또는 "로컬 유지됨")

### 다른 프로젝트 정리 (전역 배포 시)
- 스캔된 프로젝트: [N]개
- 중복 발견: [N]개
- 전역 업데이트: [예/아니오] (업데이트된 경우 출처 표시)
- 삭제됨: [삭제된 경로 목록]
- 커밋됨: [커밋된 프로젝트 목록]
```

## 경로 정보

| 구분 | 경로 |
|------|------|
| 전역 | `~/.claude/skills/`, `~/.claude/agents/`, `~/.claude/commands/` |
| 공유 | `~/projects/claudesystem/.claude/skills/`, `agents/`, `commands/` |

## 에러 처리

- `.claude/` 폴더 없음 → "현재 프로젝트에 .claude/ 폴더가 없습니다."
- 항목 없음 → "/promote --list 로 배포 가능한 항목을 확인하세요."
- 권한 오류 → 에러 메시지 그대로 출력

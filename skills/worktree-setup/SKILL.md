---
name: worktree-setup
description: |
  Git worktree 기반 새 기능 개발 환경 셋업. 다음 상황에서 사용:
  - 사용자가 새로운 기능 개발을 시작하려 할 때
  - "feature 브랜치 만들어줘", "새 기능 개발 시작", "worktree 셋업" 등의 요청
  - fix 브랜치로 버그 수정 작업을 시작할 때
---

# Worktree Setup

새 기능 개발을 위한 Git worktree 환경을 셋업한다.

## Workflow

1. **기능 이름 확인**: 사용자에게 기능 이름을 물어본다 (없으면)
2. **브랜치 타입 결정**: feature 또는 fix
3. **Worktree 생성**: 스크립트 실행
4. **작업 계속**: cd로 worktree 경로로 이동 후 요청된 작업 진행

## 셋업 스크립트 실행

```bash
bash <skill-dir>/scripts/setup-worktree.sh <feature-name> [branch-type]
```

- `feature-name`: 기능 이름 (예: add-inventory-sort)
- `branch-type`: `feature` (기본값) 또는 `fix`

## 스크립트가 수행하는 작업

1. main 브랜치 최신화 (`git fetch && git pull`)
2. `.worktrees/<repo-name>/` 디렉토리 생성 (없으면)
3. worktree 생성 (`.worktrees/<repo-name>/<type>-<name>/`)
4. 새 브랜치 생성 (`<type>/<name>`)
5. 의존성 설치 (조건부):
   - `package.json` 있으면 `npm install`
   - `requirements.txt` 있으면 `pip install`

## Worktree 디렉토리 구조

```
~/projects/
├── my-repo/                    # 메인 레포
└── .worktrees/
    └── my-repo/
        ├── feature-login/      # feature/login 브랜치
        └── fix-bug/            # fix/bug 브랜치
```

## 완료 후 행동

셋업 완료 후 **현재 세션에서 바로 작업을 계속한다**:

1. `cd <worktree-path>`로 디렉토리 변경
2. 사용자가 요청한 작업 진행

**새 세션을 시작하지 않는다.** 현재 세션에서 경로만 바꿔서 작업한다.

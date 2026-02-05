---
name: worktree-cleanup
description: |
  Git worktree 상태 확인 및 정리. 다음 상황에서 사용:
  - "worktree 정리해줘", "완료된 worktree 삭제" 등의 요청
  - 병렬 개발 후 머지 완료된 worktree 정리
  - worktree 상태 확인이 필요할 때
---

# Worktree Cleanup

완료된 worktree를 안전하게 정리한다.

## Workflow

### 1. 상태 조회

```bash
bash <skill-dir>/scripts/list-worktrees.sh
```

스크립트 출력 예시:
```
Worktree 상태:

✅ feature-add-chat
   Branch: feature/add-chat
   PR: #12 (merged)
   Changes: none
   → 정리 가능

⚠️ feature-new-building
   Branch: feature/new-building
   PR: #15 (open)
   Changes: 2 uncommitted files
   → 작업 중

⚠️ fix-collision
   Branch: fix/collision
   PR: none
   Changes: none, 3 unpushed commits
   → 푸시 필요
```

**Worktree 경로 규칙:**
```
~/.worktrees/<repo-name>/<type>-<name>/
```

### 2. 안전 기준

**정리 가능 (✅)** - 모든 조건 충족:
- PR이 머지됨 (merged)
- 커밋되지 않은 변경사항 없음
- 푸시되지 않은 커밋 없음

**주의 필요 (⚠️)** - 하나라도 해당:
- PR이 아직 열려있음
- 커밋되지 않은 변경사항 있음
- 푸시되지 않은 커밋 있음
- PR이 없음

### 3. 정리 실행

사용자가 정리할 worktree를 선택하면:

```bash
# 1. worktree 삭제
git worktree remove ../.worktrees/<repo-name>/<type>-<name>

# 2. 로컬 브랜치 삭제
git branch -d <type>/<name>

# 3. 원격 브랜치 삭제 (머지된 PR인 경우 기본 포함)
git push origin --delete <type>/<name>
```

**원격 브랜치 삭제 정책:**
- PR이 머지된 경우: 별도 확인 없이 원격 브랜치도 함께 삭제
- PR이 열려있거나 없는 경우: 사용자에게 확인 후 삭제

### 4. 일괄 정리

```bash
# 잘못된 worktree 참조 정리
git worktree prune
```

## 주의사항

- **절대 자동 삭제하지 않음** - 항상 사용자 확인 필요
- 현재 세션의 worktree는 정리 대상에서 제외
- ⚠️ 표시된 worktree는 강제 삭제 전 이유를 명확히 안내
- 강제 삭제 시: `git worktree remove --force`, `git branch -D`

---
name: gsheet-writer
description: 구글 시트에 데이터를 쓰는 범용 스킬. 단일/배치 업데이트, 행 추가, 범위 삭제 지원.
version: 1.0.0
author: 서인근
tags:
  - google-sheets
  - write
  - api
skill_type: managed
---

# gsheet-writer

구글 시트에 데이터를 쓰는 원자적 스킬입니다.

## 사용 시점

다음과 같은 요청 시 사용:

1. **"구글 시트에 써줘"**
2. **"시트에 데이터 추가해줘"**
3. **"스프레드시트 업데이트해줘"**
4. **"시트 데이터 삭제해줘"**

## 실행 명령어

```bash
~/.claude/venv/bin/python ~/.claude/skills/gsheet-writer/scripts/write_sheet.py \
  --sheet-id="SHEET_ID" \
  --range="A1" \
  --data='[["이름","이메일"],["홍길동","hong@ex.com"]]'
```

## 인자

| 인자 | 필수 | 설명 | 기본값 |
|------|------|------|--------|
| `--sheet-id` | ✅ | 구글 시트 ID | - |
| `--range` | ✅ | 쓸 범위 (A1 notation) | - |
| `--data` | △ | JSON 2D 배열 또는 파일 경로 | - |
| `--credentials` | - | 서비스 계정 JSON 경로 | `$GOOGLE_CREDENTIALS_PATH` |
| `--mode` | - | 쓰기 모드 (update/append/clear) | update |
| `--sheet-name` | - | 특정 시트(탭) 이름 | 첫 번째 시트 |
| `--stdin` | - | stdin에서 데이터 읽기 | - |

## 쓰기 모드

| 모드 | 설명 |
|------|------|
| `update` | 지정 범위 덮어쓰기 |
| `append` | 지정 범위 끝에 행 추가 |
| `clear` | 지정 범위 데이터 삭제 |

## 사용 예시

### 데이터 업데이트

```bash
~/.claude/venv/bin/python ~/.claude/skills/gsheet-writer/scripts/write_sheet.py \
  --sheet-id="1ABC123xyz" \
  --range="A1" \
  --data='[["이름","이메일"],["홍길동","hong@example.com"]]'
```

### 행 추가 (append)

```bash
~/.claude/venv/bin/python ~/.claude/skills/gsheet-writer/scripts/write_sheet.py \
  --sheet-id="1ABC123xyz" \
  --range="A1" \
  --mode=append \
  --data='[["김철수","kim@example.com"]]'
```

### 특정 시트 탭에 쓰기

```bash
~/.claude/venv/bin/python ~/.claude/skills/gsheet-writer/scripts/write_sheet.py \
  --sheet-id="1ABC123xyz" \
  --sheet-name="Sheet2" \
  --range="A1" \
  --data='[["데이터1","데이터2"]]'
```

### 범위 삭제

```bash
~/.claude/venv/bin/python ~/.claude/skills/gsheet-writer/scripts/write_sheet.py \
  --sheet-id="1ABC123xyz" \
  --range="A2:D100" \
  --mode=clear
```

### 파일에서 데이터 읽기

```bash
~/.claude/venv/bin/python ~/.claude/skills/gsheet-writer/scripts/write_sheet.py \
  --sheet-id="1ABC123xyz" \
  --range="A1" \
  --data=/path/to/data.json
```

### stdin에서 데이터 읽기

```bash
echo '[["A","B"],["1","2"]]' | ~/.claude/venv/bin/python \
  ~/.claude/skills/gsheet-writer/scripts/write_sheet.py \
  --sheet-id="1ABC123xyz" \
  --range="A1" \
  --stdin
```

## 환경변수

```bash
# 서비스 계정 JSON 경로 (--credentials 대신 사용 가능)
export GOOGLE_CREDENTIALS_PATH=/path/to/credentials.json
```

## 의존성

- gspread
- google-auth
- google-api-python-client

```bash
~/.claude/venv/bin/pip install gspread google-auth google-api-python-client
```

## 데이터 형식

JSON 2D 배열:

```json
[
  ["헤더1", "헤더2", "헤더3"],
  ["값1", "값2", "값3"],
  ["값4", "값5", "값6"]
]
```

## 관련 스킬

- `gsheet-reader` - 구글 시트 읽기

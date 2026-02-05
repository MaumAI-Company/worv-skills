---
name: gsheet-reader
description: 구글 시트에서 데이터를 읽어오는 범용 스킬. 시트 목록 조회, 특정 범위 읽기, JSON/CSV/테이블 형식 출력 지원.
version: 1.0.0
author: 서인근
tags:
  - google-sheets
  - read
  - api
skill_type: managed
---

# gsheet-reader

구글 시트에서 데이터를 읽어오는 원자적 스킬입니다.

## 사용 시점

다음과 같은 요청 시 사용:

1. **"구글 시트 읽어줘"**
2. **"시트 데이터 가져와"**
3. **"스프레드시트 조회해줘"**
4. **"시트 목록 보여줘"**

## 실행 명령어

```bash
~/.claude/venv/bin/python ~/.claude/skills/gsheet-reader/scripts/read_sheet.py \
  --sheet-id="SHEET_ID" \
  --range="A1:Z100" \
  --format=json
```

## 인자

| 인자 | 필수 | 설명 | 기본값 |
|------|------|------|--------|
| `--sheet-id` | ✅ | 구글 시트 ID | - |
| `--range` | - | 읽을 범위 (A1 notation) | A1:Z1000 |
| `--credentials` | - | 서비스 계정 JSON 경로 | `$GOOGLE_CREDENTIALS_PATH` |
| `--format` | - | 출력 형식 (json/csv/table) | json |
| `--sheet-name` | - | 특정 시트(탭) 이름 | 첫 번째 시트 |
| `--list-sheets` | - | 시트 목록만 출력 | - |

## 사용 예시

### 시트 목록 조회

```bash
~/.claude/venv/bin/python ~/.claude/skills/gsheet-reader/scripts/read_sheet.py \
  --sheet-id="1ABC123xyz" \
  --list-sheets
```

### 특정 범위 읽기 (JSON)

```bash
~/.claude/venv/bin/python ~/.claude/skills/gsheet-reader/scripts/read_sheet.py \
  --sheet-id="1ABC123xyz" \
  --range="A1:D50" \
  --format=json
```

### 특정 시트 탭에서 읽기

```bash
~/.claude/venv/bin/python ~/.claude/skills/gsheet-reader/scripts/read_sheet.py \
  --sheet-id="1ABC123xyz" \
  --sheet-name="Sheet2" \
  --range="A1:C10"
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

## 출력 형식

### JSON (기본)

첫 행을 헤더로 사용하여 객체 배열로 변환:

```json
[
  {"이름": "홍길동", "이메일": "hong@example.com"},
  {"이름": "김철수", "이메일": "kim@example.com"}
]
```

### CSV

```csv
"이름","이메일"
"홍길동","hong@example.com"
```

### Table

```
이름     | 이메일
-----------------
홍길동   | hong@example.com
```

## 관련 스킬

- `gsheet-writer` - 구글 시트 쓰기

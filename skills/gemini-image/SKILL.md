---
name: gemini-image
description: Gemini API를 활용하여 문서/발표자료용 이미지를 생성합니다. Nano Banana (빠른 생성) 및 Nano Banana Pro (고품질) 모델 지원.
version: 1.0.0
author: claude
triggers:
  - 이미지 생성해줘
  - 그림 만들어줘
  - 일러스트 생성
  - 다이어그램 이미지
  - 발표자료 이미지
  - 문서용 이미지
tools:
  - Bash
  - Read
  - Write
---

# Gemini Image Generator 스킬

Gemini API를 활용하여 문서 작업, 발표자료, 설명 자료에 사용할 이미지를 생성하는 스킬입니다.

## 주요 기능

1. **텍스트-이미지 생성** - 프롬프트로 이미지 생성
2. **이미지 편집** - 기존 이미지 기반 수정/변형
3. **다양한 비율 지원** - 1:1, 16:9, 4:3 등 문서용 비율
4. **고해상도 옵션** - 1K, 2K, 4K 해상도 지원

## 사용 가능한 모델

| 모델 | ID | 특징 |
|------|-----|------|
| **Nano Banana** | `gemini-2.5-flash-image` | 빠른 생성, 효율적 |
| **Nano Banana Pro** | `gemini-3-pro-image-preview` | 고품질, 복잡한 이미지 |

## 사전 설정

### 1. Gemini API 키 설정

`~/.claude/.env` 파일에 API 키 추가:

```bash
GEMINI_API_KEY=your_api_key_here
```

### 2. 패키지 설치

```bash
~/.claude/.venv/bin/pip install google-genai Pillow python-dotenv
```

## 사용법

### 기본 이미지 생성

```bash
~/.claude/.venv/bin/python ~/.claude/skills/gemini-image/scripts/generate_image.py \
  --prompt "자율주행 트랙터가 논에서 작업하는 미래적인 일러스트" \
  --output "./generated_image.png"
```

### 모델 선택

```bash
# Nano Banana Pro 사용 (고품질)
~/.claude/.venv/bin/python ~/.claude/skills/gemini-image/scripts/generate_image.py \
  --prompt "센서 융합 아키텍처 다이어그램" \
  --model pro \
  --output "./sensor_diagram.png"

# Nano Banana 사용 (빠른 생성, 기본값)
~/.claude/.venv/bin/python ~/.claude/skills/gemini-image/scripts/generate_image.py \
  --prompt "간단한 플로우차트" \
  --model flash \
  --output "./flowchart.png"
```

### 비율 및 해상도 설정

```bash
# 16:9 비율 (프레젠테이션용)
~/.claude/.venv/bin/python ~/.claude/skills/gemini-image/scripts/generate_image.py \
  --prompt "발표 슬라이드용 배경 이미지" \
  --aspect-ratio "16:9" \
  --output "./slide_bg.png"

# 4:3 비율, 2K 해상도
~/.claude/.venv/bin/python ~/.claude/skills/gemini-image/scripts/generate_image.py \
  --prompt "기술 문서용 인포그래픽" \
  --aspect-ratio "4:3" \
  --size "2K" \
  --output "./infographic.png"
```

### 이미지 편집 (기존 이미지 기반)

```bash
~/.claude/.venv/bin/python ~/.claude/skills/gemini-image/scripts/generate_image.py \
  --prompt "이 다이어그램을 더 현대적인 스타일로 변경해주세요" \
  --input "./original_diagram.png" \
  --output "./updated_diagram.png"
```

## 지원 비율

| 비율 | 용도 |
|------|------|
| `1:1` | 아이콘, SNS 프로필 |
| `4:3` | 문서, 블로그 |
| `3:4` | 세로형 문서 |
| `16:9` | 프레젠테이션, 와이드스크린 |
| `9:16` | 모바일, 스토리 |
| `3:2` | 사진 비율 |
| `21:9` | 울트라와이드 배너 |

## 해상도 옵션

| 옵션 | 설명 | 지원 모델 |
|------|------|----------|
| `1K` | 기본 해상도 | 모든 모델 |
| `2K` | 고해상도 | Pro 모델 |
| `4K` | 최고 해상도 | Pro 모델 |

## 파일 구조

```
~/.claude/skills/gemini-image/
├── SKILL.md                    # 이 파일
├── requirements.txt            # 의존 패키지
└── scripts/
    └── generate_image.py       # 이미지 생성 스크립트
```

## 주의사항

- **API 비용**: Imagen 3 기준 이미지당 약 $0.03
- **SynthID 워터마크**: 모든 생성 이미지에 비가시 워터마크 포함
- **콘텐츠 정책**: Google의 콘텐츠 정책 준수 필요
- **API 키 보안**: `.env` 파일은 `.gitignore`에 포함되어야 함

## 트러블슈팅

### "API key not found" 오류
→ `~/.claude/.env` 파일에 `GEMINI_API_KEY` 설정 확인

### "Model not available" 오류
→ API 키의 모델 접근 권한 확인

### 이미지가 생성되지 않음
→ 프롬프트가 콘텐츠 정책에 위배될 수 있음. 프롬프트 수정 후 재시도

## 참고 자료

- [Gemini API 이미지 생성 문서](https://ai.google.dev/gemini-api/docs/image-generation)
- [Imagen 3 가이드](https://ai.google.dev/gemini-api/docs/imagen)

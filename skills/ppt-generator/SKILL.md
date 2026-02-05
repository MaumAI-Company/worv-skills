---
name: ppt-generator
description: >
  한국어에 최적화된 미니멀 프레젠테이션 생성.
  "PPT 만들어줘", "발표자료 생성", "프레젠테이션 제작" 요청 시 사용.
  python-pptx 기반, Pretendard/Noto Serif KR 폰트, 3가지 컬러 팔레트(Sage/Mono/Navy),
  7가지 레이아웃 패턴 제공. 미니멀하고 고급스러운 디자인 스타일.
  이미지 검색/다운로드, 프로젝트 맥락 파악, 검토 루프까지 통합된 E2E 워크플로우.
---

# PPT Generator - 한국어 프레젠테이션 생성 스킬

한국어 프레젠테이션을 위한 미니멀 디자인 시스템 기반 PPTX 생성 스킬입니다.

## 사용 시점

- "PPT 만들어줘"
- "발표자료 생성해줘"
- "프레젠테이션 제작해줘"
- "슬라이드 만들어줘"
- "[파일명].md를 PPT로 만들어줘"

## 핵심 특징

- **한국어 최적화**: Pretendard(본문) + Noto Serif KR(제목) 폰트
- **3가지 팔레트**: Sage(기본), Mono, Navy
- **7가지 레이아웃**: Cover, Section, Stats Grid, Two Column, Three Column, Image+Text, Closing
- **다양한 비율 지원**: 16:9(기본), 4:3, 1:1(정사각형), 4:5, 9:16
- **이미지 자동 수집**: 웹 검색으로 관련 이미지 다운로드 및 검토
- **검토 루프**: pptx-to-image로 변환하여 시각적 검토 후 개선
- **원라이너 필수**: 서술형 한 문장으로 스토리 전달 (원라이너만 읽어도 전체 내용 이해 가능)

---

## 워크플로우 (E2E)

### 0단계: 출력 폴더 생성 (필수)

**모든 PPT 작업은 전용 폴더에서 진행합니다.**

폴더 명명 규칙:
```
{문서폴더}/PPT_{YYYYMMDD}_{순번}_{제목}/
```

예시:
```
문서/PPT_20260205_01_Thor성능평가/
├── Thor_성능평가.pptx          # 최종 PPT
├── slides_config.json          # 슬라이드 설정
├── images/                     # 수집된 이미지
│   ├── nvidia_thor_soc.jpg
│   ├── eagle_n_board.png
│   └── ...
└── preview/                    # 검토용 이미지 (선택)
    ├── slide-01.png
    ├── slide-02.png
    └── ...
```

**폴더 생성 스크립트:**
```bash
# 오늘 날짜 + 순번 자동 계산
DATE=$(date +%Y%m%d)
BASE_DIR="/path/to/문서/폴더"
TITLE="제목"

# 순번 계산 (같은 날짜에 이미 있는 PPT 폴더 수 + 1)
SEQ=$(ls -d ${BASE_DIR}/PPT_${DATE}_* 2>/dev/null | wc -l | tr -d ' ')
SEQ=$((SEQ + 1))
SEQ=$(printf "%02d" $SEQ)

# 폴더 생성
OUTPUT_DIR="${BASE_DIR}/PPT_${DATE}_${SEQ}_${TITLE}"
mkdir -p "${OUTPUT_DIR}/images"
```

### 1단계: 소스 분석 및 맥락 파악

**소스 문서 분석:**
- 입력된 마크다운, 텍스트 파일 읽기
- 핵심 내용, 데이터, 수치 추출

**프로젝트 맥락 검색 (중요!):**
- 프로젝트 내 관련 문서 검색 (Grep/Glob)
- 용어사전, 인물사전, 조직사전 확인
- 기존 PPT 설정 파일 참조 (있다면)

예시:
```bash
# 관련 문서 검색
grep -r "Thor\|Eagle-N\|NPU" /path/to/project --include="*.md"

# 용어사전 확인
cat /path/to/project/용어사전/Thor.md
```

### 2단계: 이미지 수집

**이미지 수집 우선순위:**
1. **프로젝트 내 이미지** - 기존 이미지 폴더 확인
2. **공식 사이트** - 제품/서비스 공식 이미지
3. **뉴스/기사** - 관련 기사에서 이미지 추출
4. **무료 스톡** - Unsplash, Pexels (일반적 이미지)

**웹 검색 및 다운로드:**
```bash
# Unsplash에서 검색
# WebSearch: "site:unsplash.com [키워드]"

# 이미지 다운로드
curl -L -o "images/이미지명.jpg" "https://images.unsplash.com/photo-xxx?w=1920&q=80"
```

**이미지 검토 필수:**
- 다운로드 후 Read 도구로 이미지 확인
- 품질, 관련성, 저작권 검토
- 부적절한 이미지는 교체

### 3단계: 슬라이드 구조 설계

**필수 정보:**
- 주제: 발표의 핵심 주제
- 대상: 청중 (내부/외부, 기술/비기술)
- 목표: 유도하고 싶은 행동/결정
- 슬라이드 수: 전체 개수

**설계 원칙:**
- 초반 30%: 배경 및 문제 인식
- 중반 40%: 핵심 내용 및 데이터
- 후반 30%: 결론 및 제안

**원라이너 필수 (가장 중요!):**
- 모든 콘텐츠 슬라이드에 원라이너 추가
- 제목 아래 줄바꿈(`\n`)으로 원라이너 포함
- **원라이너는 서술형 한 문장**이어야 함
- **원라이너만 처음부터 끝까지 읽어도 전체 스토리를 이해할 수 있어야 함**

**원라이너 작성 원칙:**
- 명사형(X): "성능과 효율의 최적 균형"
- 서술형(O): "FP8은 메모리를 35% 절감하면서 12 FPS로 가장 높은 성능을 보였습니다."
- 각 원라이너는 독립적으로 읽어도 의미가 전달되어야 함
- 전체 원라이너를 연결하면 발표의 핵심 스토리가 완성됨

예시:
```json
{
  "layout": "stats_grid",
  "title": "FP8 Quantization (권장)\nFP8은 메모리를 35% 절감하면서 12 FPS로 가장 높은 성능을 보였습니다.",
  "stats": [...]
}
```

### 4단계: 팔레트 선택

- **Sage**: 차분, 자연스러움 (웰빙, ESG)
- **Mono**: 세련, 프로페셔널 (테크, 스타트업)
- **Navy**: 신뢰, 안정 (금융, 컨설팅, 기업) - **권장**

상세 컬러값: [`references/color-palettes.md`](references/color-palettes.md)

### 5단계: JSON 설정 파일 생성

출력 폴더에 `slides_config.json` 저장:

```json
{
  "title": "발표 제목",
  "author": "마음AI",
  "palette": "navy",
  "slides": [
    {
      "layout": "cover",
      "title": "메인 제목",
      "subtitle": "이 발표에서는 A와 B를 비교 평가한 결과를 공유합니다.",
      "author": "발표자",
      "date": "2026.02"
    },
    {
      "layout": "section",
      "badge": "SECTION 1",
      "title": "섹션 제목"
    },
    {
      "layout": "two_column",
      "title": "비교 제목\nA는 성능이 우수하지만 비용이 높고, B는 비용이 합리적이지만 성능이 낮습니다.",
      "left": {"heading": "좌측", "items": ["항목1", "항목2"]},
      "right": {"heading": "우측", "items": ["항목1", "항목2"]}
    },
    {
      "layout": "image_text",
      "title": "이미지 슬라이드\n제품 A는 2000 TFLOPS의 최고 성능을 제공하는 표준 플랫폼입니다.",
      "image_path": "/absolute/path/to/images/image.png",
      "text": "설명 텍스트"
    },
    {
      "layout": "stats_grid",
      "title": "통계 제목\nFP8은 메모리를 35% 절감하면서 12 FPS로 가장 높은 성능을 보였습니다.",
      "stats": [
        {"number": "250", "label": "간결한 레이블"},
        {"number": "12", "label": "FPS"}
      ]
    },
    {
      "layout": "closing",
      "title": "A는 12 FPS를 달성했고,\nB는 4 FPS 이상을 목표로 합니다.",
      "contact": "추가 정보"
    }
  ]
}
```

**레이블 작성 규칙:**
- stats_grid 레이블은 **3글자 이내** 권장
- 긴 레이블은 잘림 현상 발생
- 예: "메모리 사용량" → "메모리", "Decode 속도" → "Decode"

### 6단계: PPTX 생성

```bash
~/.claude/.venv/bin/python ~/.claude/skills/ppt-generator/scripts/generate_pptx.py \
    --config "{출력폴더}/slides_config.json" \
    --output "{출력폴더}/발표제목.pptx" \
    --palette navy
```

### 7단계: 검토 루프 (필수, 최소 2회)

**PPTX를 이미지로 변환:**
```bash
~/.claude/.venv/bin/python ~/.claude/skills/pptx-to-image/scripts/convert.py \
    --input "{출력폴더}/발표제목.pptx" \
    --output "{출력폴더}/preview"
```

**검토 포인트:**
- 텍스트 잘림 현상 확인
- 이미지 배치 및 품질 확인
- 원라이너 가독성 확인
- 레이아웃 균형 확인

**개선 및 재생성:**
- 문제 발견 시 JSON 수정
- PPTX 재생성
- 이미지 재변환 및 재검토
- **최소 2회 루프 반복**

---

## 레이아웃 가이드

### 7가지 레이아웃

1. **Cover** - 표지 (subtitle로 원라이너)
2. **Section** - 섹션 구분 (다크 배경, 원라이너 불필요)
3. **Stats Grid** - 숫자/통계 강조 (레이블 간결하게)
4. **Two Column** - 비교/대조
5. **Three Column** - 기능 나열
6. **Image + Text** - 스토리텔링 (이미지 절대경로)
7. **Closing** - 마무리

레이아웃 상세: [`references/layouts.md`](references/layouts.md)

### 비즈니스 표현 가이드

**금지 표현:**
- "확신합니다" → "달성 가능합니다"
- "반드시" → "목표로"
- "완벽한" → "최적의"

**권장 표현:**
- "제안드립니다"
- "검토 결과"
- "기술적 근거"

---

## CLI 옵션

```bash
~/.claude/.venv/bin/python ~/.claude/skills/ppt-generator/scripts/generate_pptx.py \
    --config slides.json \    # JSON 설정 파일 경로 (필수)
    --output output.pptx \    # 출력 PPTX 파일 경로
    --palette navy \          # 컬러 팔레트 (sage/mono/navy)
    --size 16:9               # 슬라이드 비율
```

**비율 옵션:**
- `16:9`: 기본 와이드스크린 (프레젠테이션)
- `4:3`: 전통적 비율 (프로젝터)
- `1:1`: 정사각형 (LinkedIn, Instagram)
- `4:5`: 세로형 (Instagram 피드)
- `9:16`: 세로형 (스토리, 릴스)

---

## 체크리스트

### PPT 생성 전
- [ ] 출력 폴더 생성 (날짜_순번_제목)
- [ ] 소스 문서 분석 완료
- [ ] 프로젝트 맥락 파악 (관련 문서 검색)
- [ ] 이미지 수집 및 검토 완료

### JSON 작성 시
- [ ] 모든 콘텐츠 슬라이드에 서술형 원라이너 포함
- [ ] 원라이너만 읽어도 전체 스토리가 이해되는지 확인
- [ ] stats_grid 레이블 3글자 이내
- [ ] 이미지 경로는 절대경로
- [ ] 비즈니스 표현 사용 (확신 → 가능)

### PPT 생성 후
- [ ] pptx-to-image로 변환하여 검토
- [ ] 텍스트 잘림 확인
- [ ] 최소 2회 검토 루프 완료

---

## 주의사항

- 한 슬라이드에 텍스트 과다 배치 금지 - 여백 충분히 확보
- 각 슬라이드는 **하나의 핵심 메시지**만 전달
- 제목은 설명이 아닌 **메시지를 전달하는 단정형 문장**으로 작성
- 폰트가 설치되지 않은 경우 시스템 기본 폰트로 대체됨
- 이미지 검토 없이 PPT 완성하지 않기

---

## 환경 설정

**전역 가상환경 사용**: 이 스킬은 `~/.claude/.venv`를 사용합니다.

의존성 설치 (최초 1회):
```bash
~/.claude/.venv/bin/pip install python-pptx Pillow
# 또는 uv 사용
uv pip install --python ~/.claude/.venv/bin/python python-pptx Pillow
```

---

## 예시: Thor 성능 평가 PPT (실제 사례)

**폴더 구조:**
```
문서/PPT_20260205_01_Thor성능평가/
├── Thor_InternVL3_성능평가.pptx
├── slides_config.json
├── images/
│   ├── nvidia_drive_thor_soc.jpg
│   ├── 보스반도체_Eagle-N_개발보드.png
│   └── ...
└── preview/
    └── slide-01.png ~ slide-23.png
```

**검토 루프 요약:**
- 루프 1: 원라이너 추가, 레이블 간결화
- 루프 2: 텍스트 길이 최적화
- 루프 3: 최종 검토 완료

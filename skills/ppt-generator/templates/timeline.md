# Timeline Layout Template

타임라인/로드맵 표현을 위한 레이아웃. 단계별 진행 상황을 화살표와 원형 아이콘으로 시각화합니다.

## 사용 예시

```json
{
  "layout": "timeline",
  "title": "NPU 전환 로드맵",
  "oneliner": "3년 개발 기간 중 Thor로 시작하여 26년 9월 B0 출시 후 보스반도체로 전환합니다.",
  "steps": [
    {
      "number": "26.02",
      "title": "Thor 개발 시작",
      "description": "B0 출시 전 Thor로 개발 진행"
    },
    {
      "number": "26.09",
      "title": "B0 샘플 출시",
      "description": "보스반도체 B0 ES 입수"
    },
    {
      "number": "26.12",
      "title": "성능 검증",
      "description": "B0 성능 테스트 완료"
    },
    {
      "number": "27.02",
      "title": "양산 전환",
      "description": "Eagle-N B0 기반 양산"
    }
  ],
  "footnotes": ["* ES: Engineering Sample"]
}
```

## 디자인 특징

1. **화살표 도형 (CHEVRON)**: 단계별 진행 방향을 표현
2. **원형 아이콘**: 각 단계를 시각적으로 구분 (위/아래 교대 배치)
3. **연결선**: 원과 화살표를 연결하여 흐름 표현
4. **그라데이션 색상**: 진한 청록 → 연한 청록으로 진행감 표현

## 참조 디자인

원본 참조: `Green Corporate Timeline Infographic Presentation.pptx`
- Canva 템플릿 기반
- 화살표 + 원형 아이콘 + 텍스트 조합

## 제약사항

- 최대 5단계까지 지원
- 너무 긴 텍스트는 잘릴 수 있음
- 단계 설명은 2줄 이내 권장

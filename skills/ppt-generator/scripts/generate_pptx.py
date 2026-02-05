#!/usr/bin/env python3
"""
PPT Generator - 한국어 최적화 미니멀 프레젠테이션 생성

python-pptx를 사용하여 PPTX 파일을 직접 생성합니다.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE


# 컬러 팔레트 정의
PALETTES = {
    "sage": {
        "surface": "#f5f5f0",
        "surface_foreground": "#1a1a1a",
        "primary": "#b8c4b8",
        "accent": "#2d2d2d",
        "muted": "#e8e8e3",
        "muted_foreground": "#666666",
        "dark_bg": "#2d2d2d",
        "dark_fg": "#f5f5f0",
    },
    "mono": {
        "surface": "#ffffff",
        "surface_foreground": "#111111",
        "primary": "#f0f0f0",
        "accent": "#111111",
        "muted": "#f5f5f5",
        "muted_foreground": "#666666",
        "dark_bg": "#111111",
        "dark_fg": "#ffffff",
    },
    "navy": {
        "surface": "#f8f9fc",
        "surface_foreground": "#1a1f36",
        "primary": "#dce3f0",
        "accent": "#1a1f36",
        "muted": "#eef1f6",
        "muted_foreground": "#5c6478",
        "dark_bg": "#1a1f36",
        "dark_fg": "#f8f9fc",
    },
}

# 폰트 설정
FONTS = {
    "display": "Noto Serif KR",  # 제목용
    "content": "Pretendard",      # 본문용
    "fallback_display": "맑은 고딕",
    "fallback_content": "맑은 고딕",
}

# 슬라이드 크기 프리셋
SLIDE_SIZES = {
    "16:9": (Inches(13.333), Inches(7.5)),    # 기본 와이드스크린
    "4:3": (Inches(10), Inches(7.5)),          # 전통적 비율
    "1:1": (Inches(10), Inches(10)),           # 정사각형 (모바일/SNS)
    "4:5": (Inches(8), Inches(10)),            # 세로형 (인스타그램)
    "9:16": (Inches(5.625), Inches(10)),       # 세로형 (스토리)
}

# 기본 슬라이드 크기 (16:9)
SLIDE_WIDTH = Inches(13.333)
SLIDE_HEIGHT = Inches(7.5)

# 여백
MARGIN = Inches(0.75)


def hex_to_rgb(hex_color: str) -> RGBColor:
    """HEX 컬러를 RGBColor로 변환"""
    hex_color = hex_color.lstrip('#')
    return RGBColor(
        int(hex_color[0:2], 16),
        int(hex_color[2:4], 16),
        int(hex_color[4:6], 16)
    )


def set_text_frame_properties(text_frame, font_name: str, font_size: int,
                               font_color: str, bold: bool = False,
                               alignment: PP_ALIGN = PP_ALIGN.LEFT):
    """텍스트 프레임 속성 설정"""
    text_frame.word_wrap = True
    for paragraph in text_frame.paragraphs:
        paragraph.alignment = alignment
        paragraph.font.name = font_name
        paragraph.font.size = Pt(font_size)
        paragraph.font.color.rgb = hex_to_rgb(font_color)
        paragraph.font.bold = bold


def add_text_box(slide, left: float, top: float, width: float, height: float,
                 text: str, font_name: str, font_size: int, font_color: str,
                 bold: bool = False, alignment: PP_ALIGN = PP_ALIGN.LEFT,
                 vertical_anchor: MSO_ANCHOR = MSO_ANCHOR.TOP) -> None:
    """텍스트 박스 추가"""
    txBox = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    tf = txBox.text_frame
    tf.word_wrap = True
    tf.paragraphs[0].text = text
    tf.paragraphs[0].alignment = alignment
    tf.paragraphs[0].font.name = font_name
    tf.paragraphs[0].font.size = Pt(font_size)
    tf.paragraphs[0].font.color.rgb = hex_to_rgb(font_color)
    tf.paragraphs[0].font.bold = bold

    # 수직 정렬
    txBox.text_frame.auto_size = None
    txBox.text_frame.word_wrap = True


def add_shape_with_fill(slide, left: float, top: float, width: float,
                        height: float, fill_color: str) -> None:
    """배경 사각형 추가"""
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = hex_to_rgb(fill_color)
    shape.line.fill.background()


def get_dimensions():
    """현재 슬라이드 크기에서 인치 단위 값 반환"""
    width = SLIDE_WIDTH.inches
    height = SLIDE_HEIGHT.inches
    margin = MARGIN.inches
    content_width = width - (2 * margin)
    return width, height, margin, content_width


def create_cover_slide(prs: Presentation, data: Dict, palette: Dict) -> None:
    """표지 슬라이드 생성"""
    slide_layout = prs.slide_layouts[6]  # Blank
    slide = prs.slides.add_slide(slide_layout)

    width, height, margin, content_width = get_dimensions()

    # 배경색
    background = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT
    )
    background.fill.solid()
    background.fill.fore_color.rgb = hex_to_rgb(palette["surface"])
    background.line.fill.background()

    # 제목 (수직 중앙보다 약간 위)
    title_y = height * 0.33
    add_text_box(
        slide, margin, title_y, content_width, 1.5,
        data.get("title", "제목"),
        FONTS["display"], 44, palette["surface_foreground"],
        bold=True, alignment=PP_ALIGN.CENTER
    )

    # 부제목
    if data.get("subtitle"):
        subtitle_y = height * 0.50
        add_text_box(
            slide, margin, subtitle_y, content_width, 0.8,
            data["subtitle"],
            FONTS["content"], 20, palette["muted_foreground"],
            alignment=PP_ALIGN.CENTER
        )

    # 발표자 / 날짜
    footer_text = ""
    if data.get("author"):
        footer_text = data["author"]
    if data.get("date"):
        footer_text += f"  |  {data['date']}" if footer_text else data["date"]

    if footer_text:
        footer_y = height * 0.85
        add_text_box(
            slide, margin, footer_y, content_width, 0.5,
            footer_text,
            FONTS["content"], 14, palette["muted_foreground"],
            alignment=PP_ALIGN.CENTER
        )


def create_section_slide(prs: Presentation, data: Dict, palette: Dict) -> None:
    """섹션 구분 슬라이드 생성 (다크 배경)"""
    slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(slide_layout)

    width, height, margin, content_width = get_dimensions()

    # 다크 배경
    background = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT
    )
    background.fill.solid()
    background.fill.fore_color.rgb = hex_to_rgb(palette["dark_bg"])
    background.line.fill.background()

    # 배지
    if data.get("badge"):
        badge_y = height * 0.38
        add_text_box(
            slide, margin, badge_y, content_width, 0.5,
            data["badge"],
            FONTS["content"], 14, palette["muted_foreground"],
            alignment=PP_ALIGN.CENTER
        )

    # 섹션 제목
    title_y = height * 0.45
    add_text_box(
        slide, margin, title_y, content_width, 1.2,
        data.get("title", "섹션 제목"),
        FONTS["display"], 36, palette["dark_fg"],
        bold=True, alignment=PP_ALIGN.CENTER
    )


def create_stats_grid_slide(prs: Presentation, data: Dict, palette: Dict) -> None:
    """통계 그리드 슬라이드 생성"""
    slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(slide_layout)

    width, height, margin, content_width = get_dimensions()

    # 배경
    background = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT
    )
    background.fill.solid()
    background.fill.fore_color.rgb = hex_to_rgb(palette["surface"])
    background.line.fill.background()

    # 슬라이드 제목
    add_text_box(
        slide, margin, margin, content_width, 0.8,
        data.get("title", "핵심 지표"),
        FONTS["display"], 32, palette["surface_foreground"],
        bold=True
    )

    # 통계 항목들
    stats = data.get("stats", [])
    num_stats = len(stats)

    if num_stats > 0:
        # 그리드 계산 - 상대적 위치
        col_width = content_width / min(num_stats, 4)
        start_y = height * 0.35

        for i, stat in enumerate(stats[:4]):  # 최대 4개
            col_x = margin + (i * col_width)

            # 숫자
            add_text_box(
                slide, col_x, start_y, col_width - 0.3, 1.2,
                stat.get("number", "0"),
                FONTS["display"], 48, palette["accent"],
                bold=True, alignment=PP_ALIGN.CENTER
            )

            # 레이블
            add_text_box(
                slide, col_x, start_y + 1.3, col_width - 0.3, 0.8,
                stat.get("label", ""),
                FONTS["content"], 14, palette["muted_foreground"],
                alignment=PP_ALIGN.CENTER
            )


def create_two_column_slide(prs: Presentation, data: Dict, palette: Dict) -> None:
    """2단 비교 슬라이드 생성"""
    slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(slide_layout)

    width, height, margin, content_width = get_dimensions()

    # 배경
    background = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT
    )
    background.fill.solid()
    background.fill.fore_color.rgb = hex_to_rgb(palette["surface"])
    background.line.fill.background()

    # 슬라이드 제목
    add_text_box(
        slide, margin, margin, content_width, 0.8,
        data.get("title", "비교 분석"),
        FONTS["display"], 32, palette["surface_foreground"],
        bold=True
    )

    # 2컬럼 계산
    gap = 0.5
    col_width = (content_width - gap) / 2
    left_x = margin
    right_x = margin + col_width + gap
    header_y = height * 0.25
    items_start_y = height * 0.35

    # 왼쪽 컬럼
    left_data = data.get("left", {})
    add_text_box(
        slide, left_x, header_y, col_width, 0.6,
        left_data.get("heading", "왼쪽"),
        FONTS["display"], 24, palette["surface_foreground"],
        bold=True
    )

    left_items = left_data.get("items", [])
    for j, item in enumerate(left_items[:5]):
        add_text_box(
            slide, left_x, items_start_y + (j * 0.6), col_width, 0.5,
            f"• {item}",
            FONTS["content"], 16, palette["surface_foreground"]
        )

    # 오른쪽 컬럼
    right_data = data.get("right", {})
    add_text_box(
        slide, right_x, header_y, col_width, 0.6,
        right_data.get("heading", "오른쪽"),
        FONTS["display"], 24, palette["surface_foreground"],
        bold=True
    )

    right_items = right_data.get("items", [])
    for j, item in enumerate(right_items[:5]):
        add_text_box(
            slide, right_x, items_start_y + (j * 0.6), col_width, 0.5,
            f"• {item}",
            FONTS["content"], 16, palette["surface_foreground"]
        )


def create_three_column_slide(prs: Presentation, data: Dict, palette: Dict) -> None:
    """3단 컬럼 슬라이드 생성"""
    slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(slide_layout)

    width, height, margin, content_width = get_dimensions()

    # 배경
    background = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT
    )
    background.fill.solid()
    background.fill.fore_color.rgb = hex_to_rgb(palette["surface"])
    background.line.fill.background()

    # 슬라이드 제목
    add_text_box(
        slide, margin, margin, content_width, 0.8,
        data.get("title", "핵심 기능"),
        FONTS["display"], 32, palette["surface_foreground"],
        bold=True
    )

    columns = data.get("columns", [])
    gap = 0.3
    col_width = (content_width - (2 * gap)) / 3
    header_y = height * 0.28
    desc_y = height * 0.38

    for i, col in enumerate(columns[:3]):
        col_x = margin + (i * (col_width + gap))

        # 컬럼 제목
        add_text_box(
            slide, col_x, header_y, col_width, 0.6,
            col.get("heading", f"기능 {i+1}"),
            FONTS["display"], 20, palette["surface_foreground"],
            bold=True
        )

        # 컬럼 설명
        add_text_box(
            slide, col_x, desc_y, col_width, 2.5,
            col.get("description", ""),
            FONTS["content"], 14, palette["muted_foreground"]
        )


def create_image_text_slide(prs: Presentation, data: Dict, palette: Dict) -> None:
    """이미지 + 텍스트 슬라이드 생성"""
    slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(slide_layout)

    width, height, margin, content_width = get_dimensions()

    # 배경
    background = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT
    )
    background.fill.solid()
    background.fill.fore_color.rgb = hex_to_rgb(palette["surface"])
    background.line.fill.background()

    # 슬라이드 제목
    add_text_box(
        slide, margin, margin, content_width, 0.8,
        data.get("title", "스토리텔링"),
        FONTS["display"], 32, palette["surface_foreground"],
        bold=True
    )

    # 2컬럼 계산
    gap = 0.5
    col_width = (content_width - gap) / 2
    content_y = height * 0.25
    content_height = height * 0.55

    # 이미지 영역 (왼쪽)
    image_path = data.get("image_path")
    if image_path and os.path.exists(image_path):
        try:
            slide.shapes.add_picture(
                image_path,
                Inches(margin), Inches(content_y),
                width=Inches(col_width)
            )
        except Exception as e:
            # 이미지 로드 실패 시 placeholder
            placeholder = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                Inches(margin), Inches(content_y), Inches(col_width), Inches(content_height)
            )
            placeholder.fill.solid()
            placeholder.fill.fore_color.rgb = hex_to_rgb(palette["muted"])
            placeholder.line.fill.background()
    else:
        # 이미지 없을 때 placeholder
        placeholder = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(margin), Inches(content_y), Inches(col_width), Inches(content_height)
        )
        placeholder.fill.solid()
        placeholder.fill.fore_color.rgb = hex_to_rgb(palette["muted"])
        placeholder.line.fill.background()

    # 텍스트 영역 (오른쪽)
    right_x = margin + col_width + gap
    add_text_box(
        slide, right_x, content_y, col_width, content_height,
        data.get("text", "설명 텍스트"),
        FONTS["content"], 16, palette["surface_foreground"]
    )


def create_closing_slide(prs: Presentation, data: Dict, palette: Dict) -> None:
    """마무리 슬라이드 생성"""
    slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(slide_layout)

    width, height, margin, content_width = get_dimensions()

    # 배경
    background = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT
    )
    background.fill.solid()
    background.fill.fore_color.rgb = hex_to_rgb(palette["surface"])
    background.line.fill.background()

    # 감사 메시지 (수직 중앙)
    title_y = height * 0.38
    add_text_box(
        slide, margin, title_y, content_width, 1.2,
        data.get("title", "감사합니다"),
        FONTS["display"], 44, palette["surface_foreground"],
        bold=True, alignment=PP_ALIGN.CENTER
    )

    # 연락처
    if data.get("contact"):
        contact_y = height * 0.58
        add_text_box(
            slide, margin, contact_y, content_width, 0.6,
            data["contact"],
            FONTS["content"], 16, palette["muted_foreground"],
            alignment=PP_ALIGN.CENTER
        )


def create_content_slide(prs: Presentation, data: Dict, palette: Dict) -> None:
    """일반 콘텐츠 슬라이드 생성 (기본 레이아웃)"""
    slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(slide_layout)

    width, height, margin, content_width = get_dimensions()

    # 배경
    background = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT
    )
    background.fill.solid()
    background.fill.fore_color.rgb = hex_to_rgb(palette["surface"])
    background.line.fill.background()

    # 슬라이드 제목
    add_text_box(
        slide, margin, margin, content_width, 0.8,
        data.get("title", "제목"),
        FONTS["display"], 32, palette["surface_foreground"],
        bold=True
    )

    # 본문 내용
    content = data.get("content", "")
    if isinstance(content, list):
        content = "\n".join([f"• {item}" for item in content])

    content_y = height * 0.22
    content_height = height * 0.65
    add_text_box(
        slide, margin, content_y, content_width, content_height,
        content,
        FONTS["content"], 16, palette["surface_foreground"]
    )


# 레이아웃 타입별 생성 함수 매핑
LAYOUT_CREATORS = {
    "cover": create_cover_slide,
    "section": create_section_slide,
    "stats_grid": create_stats_grid_slide,
    "two_column": create_two_column_slide,
    "three_column": create_three_column_slide,
    "image_text": create_image_text_slide,
    "closing": create_closing_slide,
    "content": create_content_slide,
}


def generate_pptx(config: Dict, output_path: str, palette_name: str = "sage",
                  size: str = "16:9") -> str:
    """PPTX 파일 생성 메인 함수"""
    global SLIDE_WIDTH, SLIDE_HEIGHT

    # 팔레트 선택
    palette = PALETTES.get(palette_name, PALETTES["sage"])

    # 슬라이드 크기 설정
    if size in SLIDE_SIZES:
        SLIDE_WIDTH, SLIDE_HEIGHT = SLIDE_SIZES[size]
    else:
        SLIDE_WIDTH, SLIDE_HEIGHT = SLIDE_SIZES["16:9"]

    # 프레젠테이션 생성
    prs = Presentation()
    prs.slide_width = SLIDE_WIDTH
    prs.slide_height = SLIDE_HEIGHT

    # 슬라이드 생성
    slides_data = config.get("slides", [])

    for slide_data in slides_data:
        layout = slide_data.get("layout", "content")
        creator_func = LAYOUT_CREATORS.get(layout, create_content_slide)
        creator_func(prs, slide_data, palette)

    # 파일 저장
    output_path = os.path.expanduser(output_path)
    prs.save(output_path)

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="한국어 최적화 미니멀 PPTX 생성기"
    )
    parser.add_argument(
        "--config", "-c",
        required=True,
        help="슬라이드 설정 JSON 파일 경로"
    )
    parser.add_argument(
        "--output", "-o",
        default="output.pptx",
        help="출력 PPTX 파일 경로 (기본: output.pptx)"
    )
    parser.add_argument(
        "--palette", "-p",
        choices=["sage", "mono", "navy"],
        default="sage",
        help="컬러 팔레트 (기본: sage)"
    )
    parser.add_argument(
        "--size", "-s",
        choices=["16:9", "4:3", "1:1", "4:5", "9:16"],
        default="16:9",
        help="슬라이드 비율 (기본: 16:9, 모바일: 1:1 또는 4:5)"
    )

    args = parser.parse_args()

    # JSON 설정 파일 로드
    config_path = os.path.expanduser(args.config)
    if not os.path.exists(config_path):
        print(f"Error: Config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # 팔레트 오버라이드 (config에서 지정된 경우)
    palette_name = config.get("palette", args.palette)

    # 사이즈 오버라이드 (config에서 지정된 경우)
    size = config.get("size", args.size)

    # PPTX 생성
    try:
        output_path = generate_pptx(config, args.output, palette_name, size)
        print(f"PPTX 생성 완료: {output_path}")
        print(f"슬라이드 수: {len(config.get('slides', []))}")
        print(f"팔레트: {palette_name}")
        print(f"사이즈: {size}")
    except Exception as e:
        print(f"Error: PPTX 생성 실패: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Gemini Image Generator - 직접 Gemini API를 사용한 이미지 생성
문서/발표자료용 이미지 생성 스크립트

모델:
- pro: gemini-3-pro-image-preview (Nano Banana Pro, 고품질, 기본값)
- flash: gemini-2.5-flash-image (Nano Banana, 빠른 생성)

사전 설정:
  ~/.claude/.env에 GEMINI_API_KEY 설정

사용법:
  python generate_image.py --prompt "설명" --output "output.png"
  python generate_image.py --prompt "설명" --model flash --output "output.png"
"""

import argparse
import base64
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# 전역 .env 파일에서 설정 로드
env_path = Path.home() / ".claude" / ".env"
load_dotenv(env_path)


def get_api_key() -> str | None:
    """API 키 로드 (환경변수 → ~/.claude/.env)"""
    api_key = os.environ.get("GEMINI_API_KEY_FOR_AGENT") or os.environ.get("GEMINI_API_KEY")
    if api_key:
        return api_key.strip()
    return None


# 모델 매핑
MODELS = {
    "pro": "gemini-3-pro-image-preview",
    "flash": "gemini-2.5-flash-image",
}

# 지원 비율
ASPECT_RATIOS = ["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"]

# 지원 해상도
IMAGE_SIZES = ["1K", "2K", "4K"]


def generate_image(
    prompt: str,
    model_key: str = "pro",
    aspect_ratio: str = "1:1",
    image_size: str = "1K",
    input_images: list[str] | None = None,
    output_path: str = "generated_image.png",
) -> str:
    """
    Gemini API를 사용하여 이미지 생성

    Args:
        prompt: 이미지 생성 프롬프트
        model_key: 모델 선택 (pro 또는 flash)
        aspect_ratio: 이미지 비율
        image_size: 해상도 (1K, 2K, 4K)
        input_images: 참조 이미지 경로 리스트 (선택사항)
        output_path: 출력 파일 경로

    Returns:
        생성된 이미지 파일 경로
    """
    from google import genai
    from google.genai import types

    # API 키 확인
    api_key = get_api_key()
    if not api_key:
        print("오류: GEMINI_API_KEY가 설정되지 않았습니다.")
        print(f"다음 경로의 .env 파일에 API 키를 추가하세요: {env_path}")
        print("예: GEMINI_API_KEY=your_api_key_here")
        return ""

    # 모델 선택
    model_id = MODELS.get(model_key, MODELS["pro"])

    # 비율 검증
    if aspect_ratio not in ASPECT_RATIOS:
        print(f"경고: 지원되지 않는 비율 '{aspect_ratio}'. 기본값 '1:1' 사용.")
        aspect_ratio = "1:1"

    # 직접 API 클라이언트 초기화
    client = genai.Client(api_key=api_key)

    # 입력 컨텐츠 구성
    contents = []

    # 참조 이미지가 있으면 먼저 추가
    if input_images:
        for img_path in input_images:
            if os.path.exists(img_path):
                with open(img_path, 'rb') as f:
                    img_data = f.read()
                suffix = Path(img_path).suffix.lower()
                mime_types = {
                    '.png': 'image/png',
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.gif': 'image/gif',
                    '.webp': 'image/webp',
                }
                mime_type = mime_types.get(suffix, 'image/png')
                contents.append(types.Part.from_bytes(data=img_data, mime_type=mime_type))
                print(f"참조 이미지 추가: {img_path}")
            else:
                print(f"경고: 이미지 파일을 찾을 수 없음: {img_path}")

    # 프롬프트 추가
    contents.append(prompt)

    # 설정 구성
    config = types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
    )

    print(f"\n이미지 생성 중...")
    print(f"  모델: {model_id}")
    print(f"  비율: {aspect_ratio}")
    print(f"  해상도: {image_size}")
    print(f"  프롬프트: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")

    try:
        # 이미지 생성 요청
        response = client.models.generate_content(
            model=model_id,
            contents=contents,
            config=config,
        )

        # 응답 처리
        image_saved = False
        for part in response.parts:
            if part.text is not None:
                print(f"\n모델 응답: {part.text}")
            elif part.inline_data is not None:
                # 이미지 저장
                image = part.as_image()

                # 출력 디렉토리 확인
                output_dir = os.path.dirname(output_path)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                image.save(output_path)
                image_saved = True

                file_size_kb = os.path.getsize(output_path) / 1024
                print(f"\n이미지 저장 완료: {output_path} ({file_size_kb:.1f} KB)")

        if not image_saved:
            print("\n경고: 이미지가 생성되지 않았습니다.")
            print("프롬프트가 콘텐츠 정책에 위배되었거나 다른 문제가 있을 수 있습니다.")
            return ""

        return output_path

    except Exception as e:
        print(f"\n오류 발생: {e}")
        return ""


def main():
    parser = argparse.ArgumentParser(
        description="Gemini API를 사용하여 문서/발표자료용 이미지 생성",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사전 설정:
  ~/.claude/.env 파일에 API 키 추가:
  GEMINI_API_KEY=your_api_key_here

예시:
  # 기본 이미지 생성 (Pro 모델)
  %(prog)s --prompt "자율주행 트랙터 일러스트" --output "./tractor.png"

  # Flash 모델 사용 (빠른 생성)
  %(prog)s --prompt "간단한 플로우차트" --model flash --output "./flowchart.png"

  # 16:9 비율 (프레젠테이션용)
  %(prog)s --prompt "발표 배경" --aspect-ratio "16:9" --output "./slide_bg.png"

  # 4K 고해상도
  %(prog)s --prompt "기술 문서용 인포그래픽" --size 4K --output "./infographic.png"

  # 기존 이미지 편집
  %(prog)s --prompt "더 밝게 수정" --input "./original.png" --output "./edited.png"
        """
    )

    parser.add_argument(
        "--prompt", "-p",
        required=True,
        help="이미지 생성 프롬프트"
    )

    parser.add_argument(
        "--model", "-m",
        choices=["pro", "flash"],
        default="pro",
        help="모델 선택: pro (고품질, 기본값) 또는 flash (빠른 생성)"
    )

    parser.add_argument(
        "--aspect-ratio", "-a",
        choices=ASPECT_RATIOS,
        default="1:1",
        help="이미지 비율. 기본: 1:1"
    )

    parser.add_argument(
        "--size", "-s",
        choices=IMAGE_SIZES,
        default="1K",
        help="해상도. 기본: 1K"
    )

    parser.add_argument(
        "--input", "-i",
        nargs="*",
        help="참조 이미지 경로 (여러 개 가능)"
    )

    parser.add_argument(
        "--output", "-o",
        default="generated_image.png",
        help="출력 파일 경로. 기본: generated_image.png"
    )

    args = parser.parse_args()

    # 이미지 생성 실행
    result = generate_image(
        prompt=args.prompt,
        model_key=args.model,
        aspect_ratio=args.aspect_ratio,
        image_size=args.size,
        input_images=args.input,
        output_path=args.output,
    )

    if result:
        print(f"\n완료: {result}")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

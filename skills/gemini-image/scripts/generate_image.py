#!/usr/bin/env python3
"""
Gemini Image Generator (Vertex AI 버전)
문서/발표자료용 이미지 생성 스크립트

Vertex AI를 사용하여 한국(서울 리전)에서 이미지 생성 지원

모델:
- flash: gemini-2.0-flash-preview-image-generation - 빠른 생성
- pro: gemini-2.0-flash-preview-image-generation - 고품질 (동일 모델, 설정 차이)

사전 설정:
  1. gcloud auth application-default login
  2. ~/.claude/.env에 GOOGLE_CLOUD_PROJECT 설정

사용법:
  python generate_image.py --prompt "설명" --output "output.png"
  python generate_image.py --prompt "설명" --location us-central1 --output "output.png"
"""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# 전역 .env 파일에서 설정 로드
env_path = Path.home() / ".claude" / ".env"
load_dotenv(env_path)

# Google Cloud 프로젝트 ID 확인
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT")
if not PROJECT_ID:
    print("오류: GOOGLE_CLOUD_PROJECT가 설정되지 않았습니다.")
    print(f"다음 경로의 .env 파일에 프로젝트 ID를 추가하세요: {env_path}")
    print("예: GOOGLE_CLOUD_PROJECT=your-project-id")
    print()
    print("또는 --project 옵션으로 지정하세요.")
    # 환경변수 없이도 --project로 지정 가능하도록 일단 진행

from google import genai
from google.genai import types
from PIL import Image


# Vertex AI 지원 리전 (이미지 생성 가능)
SUPPORTED_LOCATIONS = [
    "us-central1",      # 미국 중부 (기본, 가장 안정적)
    "us-east4",         # 미국 동부
    "us-west1",         # 미국 서부
    "europe-west1",     # 유럽 서부
    "asia-northeast1",  # 도쿄
    # "asia-northeast3",  # 서울 - 이미지 생성 미지원 가능성
]

# 모델 매핑 (Vertex AI용)
MODELS = {
    "flash": "gemini-2.0-flash-preview-image-generation",
    "pro": "gemini-2.0-flash-preview-image-generation",  # Vertex AI에서는 동일 모델
}

# 지원 비율
ASPECT_RATIOS = ["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"]

# 지원 해상도
IMAGE_SIZES = ["1K", "2K", "4K"]


def generate_image(
    prompt: str,
    project_id: str,
    location: str = "us-central1",
    model_key: str = "flash",
    aspect_ratio: str = "1:1",
    image_size: str = "1K",
    input_images: list[str] | None = None,
    output_path: str = "generated_image.png",
) -> str:
    """
    Vertex AI Gemini API를 사용하여 이미지 생성

    Args:
        prompt: 이미지 생성 프롬프트
        project_id: Google Cloud 프로젝트 ID
        location: Vertex AI 리전 (기본: us-central1)
        model_key: 모델 선택 (flash 또는 pro)
        aspect_ratio: 이미지 비율
        image_size: 해상도 (1K, 2K, 4K)
        input_images: 참조 이미지 경로 리스트 (선택사항)
        output_path: 출력 파일 경로

    Returns:
        생성된 이미지 파일 경로
    """
    # 모델 선택
    model_id = MODELS.get(model_key, MODELS["flash"])

    # 비율 검증
    if aspect_ratio not in ASPECT_RATIOS:
        print(f"경고: 지원되지 않는 비율 '{aspect_ratio}'. 기본값 '1:1' 사용.")
        aspect_ratio = "1:1"

    # 리전 검증
    if location not in SUPPORTED_LOCATIONS:
        print(f"경고: '{location}'은 이미지 생성을 지원하지 않을 수 있습니다.")
        print(f"권장 리전: {', '.join(SUPPORTED_LOCATIONS)}")

    # Vertex AI 클라이언트 초기화
    print(f"Vertex AI 클라이언트 초기화...")
    print(f"  프로젝트: {project_id}")
    print(f"  리전: {location}")

    client = genai.Client(
        vertexai=True,
        project=project_id,
        location=location,
    )

    # 입력 컨텐츠 구성
    contents = [prompt]

    # 참조 이미지가 있으면 추가
    if input_images:
        for img_path in input_images:
            if os.path.exists(img_path):
                img = Image.open(img_path)
                contents.append(img)
                print(f"참조 이미지 추가: {img_path}")
            else:
                print(f"경고: 이미지 파일을 찾을 수 없음: {img_path}")

    # 설정 구성
    config = types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
        image_config=types.ImageConfig(
            aspect_ratio=aspect_ratio,
            image_size=image_size,
        ),
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
                print(f"\n이미지 저장 완료: {output_path}")

        if not image_saved:
            print("\n경고: 이미지가 생성되지 않았습니다.")
            print("프롬프트가 콘텐츠 정책에 위배되었거나 다른 문제가 있을 수 있습니다.")
            return ""

        return output_path

    except Exception as e:
        print(f"\n오류 발생: {e}")
        if "not supported" in str(e).lower() or "not available" in str(e).lower():
            print("\n힌트: 다른 리전을 시도해보세요.")
            print(f"  --location us-central1")
        return ""


def main():
    parser = argparse.ArgumentParser(
        description="Vertex AI Gemini를 사용하여 문서/발표자료용 이미지 생성",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사전 설정:
  1. Google Cloud 인증:
     gcloud auth application-default login

  2. 환경변수 설정 (~/.claude/.env):
     GOOGLE_CLOUD_PROJECT=your-project-id

예시:
  # 기본 이미지 생성 (us-central1 리전)
  %(prog)s --prompt "자율주행 트랙터 일러스트" --output "./tractor.png"

  # 특정 리전 지정
  %(prog)s --prompt "기술 다이어그램" --location us-central1 --output "./diagram.png"

  # 16:9 비율 (프레젠테이션용)
  %(prog)s --prompt "발표 배경" --aspect-ratio "16:9" --output "./slide_bg.png"

  # 기존 이미지 편집
  %(prog)s --prompt "더 밝게 수정" --input "./original.png" --output "./edited.png"

지원 리전:
  us-central1 (권장), us-east4, us-west1, europe-west1, asia-northeast1
        """
    )

    parser.add_argument(
        "--prompt", "-p",
        required=True,
        help="이미지 생성 프롬프트"
    )

    parser.add_argument(
        "--project",
        default=PROJECT_ID,
        help="Google Cloud 프로젝트 ID (기본: 환경변수 GOOGLE_CLOUD_PROJECT)"
    )

    parser.add_argument(
        "--location", "-l",
        default="us-central1",
        help="Vertex AI 리전. 기본: us-central1 (이미지 생성에 가장 안정적)"
    )

    parser.add_argument(
        "--model", "-m",
        choices=["flash", "pro"],
        default="flash",
        help="모델 선택: flash (빠름) 또는 pro (고품질). 기본: flash"
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

    # 프로젝트 ID 확인
    if not args.project:
        print("오류: Google Cloud 프로젝트 ID가 필요합니다.")
        print("--project 옵션 또는 GOOGLE_CLOUD_PROJECT 환경변수를 설정하세요.")
        sys.exit(1)

    # 이미지 생성 실행
    result = generate_image(
        prompt=args.prompt,
        project_id=args.project,
        location=args.location,
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

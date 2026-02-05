#!/usr/bin/env python3
"""
Gemini Counsel - Gemini AI에게 코딩 조언을 구하는 스킬

Usage:
    counsel.py "질문"
    counsel.py "질문" --context "코드 또는 컨텍스트"
    counsel.py "질문" --file path/to/file.py
    counsel.py "질문" --model gemini-2.5-pro
"""

import argparse
import json
import os
import sys
from pathlib import Path

# 전역 venv에서 실행되므로 dotenv 로드
try:
    from dotenv import load_dotenv
    load_dotenv(Path.home() / ".claude" / ".env")
except ImportError:
    pass  # dotenv 없으면 환경변수에서 직접 읽기

import urllib.request
import urllib.error


def call_gemini(prompt: str, model: str = "gemini-3-pro-preview") -> str:
    """Gemini API 호출"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "❌ Error: GEMINI_API_KEY not found in ~/.claude/.env"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    # 시스템 프롬프트 + 사용자 질문
    system_prompt = """당신은 숙련된 시니어 소프트웨어 엔지니어입니다.
코드 리뷰, 아키텍처 조언, 디버깅 힌트를 제공합니다.
답변은 실용적이고 구체적이어야 합니다.
한국어로 답변하되, 코드와 기술 용어는 원어 그대로 사용합니다."""

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": f"{system_prompt}\n\n---\n\n{prompt}"}]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 8192,
        }
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))

            # 응답 파싱
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    text = candidate["content"]["parts"][0].get("text", "")
                    return text

            return f"❌ Unexpected response format: {json.dumps(result, indent=2)}"

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        return f"❌ HTTP Error {e.code}: {error_body}"
    except urllib.error.URLError as e:
        return f"❌ URL Error: {e.reason}"
    except Exception as e:
        return f"❌ Error: {str(e)}"


def main():
    parser = argparse.ArgumentParser(description="Gemini AI에게 코딩 조언을 구합니다")
    parser.add_argument("question", help="질문 내용")
    parser.add_argument("--context", "-c", help="추가 컨텍스트 (코드 등)")
    parser.add_argument("--file", "-f", help="컨텍스트로 사용할 파일 경로")
    parser.add_argument("--model", "-m", default="gemini-3-pro-preview",
                        help="사용할 모델 (default: gemini-3-pro-preview)")

    args = parser.parse_args()

    # 프롬프트 구성
    prompt = args.question

    if args.file:
        file_path = Path(args.file)
        if file_path.exists():
            content = file_path.read_text(encoding="utf-8")
            prompt = f"{args.question}\n\n### 파일: {args.file}\n```\n{content}\n```"
        else:
            print(f"❌ File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
    elif args.context:
        prompt = f"{args.question}\n\n### 컨텍스트\n```\n{args.context}\n```"

    # Gemini 호출
    print(f"💎 **Gemini의 조언:** (model: `{args.model}`)\n")
    response = call_gemini(prompt, args.model)
    print(response)


if __name__ == "__main__":
    main()

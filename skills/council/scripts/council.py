#!/usr/bin/env python3
"""
Counsel (AI Council) - 여러 AI에게 병렬로 조언을 구하는 스킬

Team Attention의 Agent Council에서 영감을 받음
https://github.com/team-attention/agent-council

Usage:
    counsel.py "질문"
    counsel.py "질문" --context "코드 또는 컨텍스트"
    counsel.py "질문" --file path/to/file.py
"""

import argparse
import json
import os
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any

try:
    from dotenv import load_dotenv
    load_dotenv(Path.home() / ".claude" / ".env")
except ImportError:
    pass

import urllib.request
import urllib.error


SYSTEM_PROMPT = """당신은 숙련된 시니어 소프트웨어 엔지니어입니다.
코드 리뷰, 아키텍처 조언, 디버깅 힌트를 제공합니다.
답변은 실용적이고 구체적이어야 합니다.
한국어로 답변하되, 코드와 기술 용어는 원어 그대로 사용합니다."""


def call_gemini(prompt: str, model: str = "gemini-3-pro-preview") -> Dict[str, Any]:
    """Gemini API 호출"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"name": "gemini", "success": False, "error": "GEMINI_API_KEY not found"}

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": f"{SYSTEM_PROMPT}\n\n---\n\n{prompt}"}]}
        ],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 8192}
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=90) as response:
            result = json.loads(response.read().decode("utf-8"))
            if "candidates" in result and len(result["candidates"]) > 0:
                text = result["candidates"][0]["content"]["parts"][0].get("text", "")
                return {"name": "gemini", "success": True, "response": text}
            return {"name": "gemini", "success": False, "error": "Unexpected response"}
    except Exception as e:
        return {"name": "gemini", "success": False, "error": str(e)}


def call_gpt(prompt: str, model: str = "gpt-4.1") -> Dict[str, Any]:
    """OpenAI API 호출"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"name": "gpt", "success": False, "error": "OPENAI_API_KEY not found"}

    url = "https://api.openai.com/v1/chat/completions"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 4096
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=90) as response:
            result = json.loads(response.read().decode("utf-8"))
            if "choices" in result and len(result["choices"]) > 0:
                return {"name": "gpt", "success": True, "response": result["choices"][0]["message"]["content"]}
            return {"name": "gpt", "success": False, "error": "Unexpected response"}
    except Exception as e:
        return {"name": "gpt", "success": False, "error": str(e)}


GEMINI_MODEL = "gemini-3-pro-preview"
GPT_MODEL = "gpt-4.1"


def run_council(prompt: str) -> None:
    """병렬로 모든 AI 호출"""
    print("🏛️ **AI Council 소집 중...**\n")
    print(f"   💎 Gemini: `{GEMINI_MODEL}`")
    print(f"   🤖 GPT: `{GPT_MODEL}`\n")
    print("=" * 60)

    results = {}

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(call_gemini, prompt, GEMINI_MODEL): "gemini",
            executor.submit(call_gpt, prompt, GPT_MODEL): "gpt"
        }

        for future in as_completed(futures):
            result = future.result()
            results[result["name"]] = result

            if result["success"]:
                emoji = "💎" if result["name"] == "gemini" else "🤖"
                name = "Gemini" if result["name"] == "gemini" else "GPT"
                print(f"\n{emoji} **{name}의 의견:**\n")
                print(result["response"])
                print("\n" + "-" * 60)
            else:
                emoji = "💎" if result["name"] == "gemini" else "🤖"
                name = "Gemini" if result["name"] == "gemini" else "GPT"
                print(f"\n{emoji} **{name}**: ❌ {result['error']}")
                print("-" * 60)

    # Summary
    print("\n" + "=" * 60)
    print("\n📋 **Council Summary:**\n")

    successful = [r for r in results.values() if r["success"]]
    if len(successful) == 2:
        print("✅ Gemini와 GPT 모두 응답 완료")
        print("👆 위 두 의견을 참고하여 종합적으로 판단하세요.")
    elif len(successful) == 1:
        name = successful[0]["name"].upper()
        print(f"⚠️ {name}만 응답 완료. 다른 AI는 오류 발생.")
    else:
        print("❌ 모든 AI 호출 실패")


def main():
    parser = argparse.ArgumentParser(description="여러 AI에게 병렬로 조언을 구합니다")
    parser.add_argument("question", help="질문 내용")
    parser.add_argument("--context", "-c", help="추가 컨텍스트 (코드 등)")
    parser.add_argument("--file", "-f", help="컨텍스트로 사용할 파일 경로")

    args = parser.parse_args()

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

    run_council(prompt)


if __name__ == "__main__":
    main()

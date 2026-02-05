#!/usr/bin/env python3
"""
인물사전에서 이름으로 이메일을 조회합니다.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


# 알려진 마음AI 직원 이메일 (fallback)
KNOWN_EMAILS = {
    "김선후": "sunhoo.kim@maum.ai",
    "선후": "sunhoo.kim@maum.ai",
    "조용준": "cyjun0304@maum.ai",
    "용준": "cyjun0304@maum.ai",
    "이윤성": "sung@maum.ai",
    "윤성": "sung@maum.ai",
    "김윤식": "yoonshik1205@maum.ai",
    "윤식": "yoonshik1205@maum.ai",
    "성삼우": "samwoose@maum.ai",
    "삼우": "samwoose@maum.ai",
    "서인근": "inkeun.seo@maum.ai",
    "인근": "inkeun.seo@maum.ai",
    "박유빈": "yubeen.park@maum.ai",
    "유빈": "yubeen.park@maum.ai",
    "최정섭": "cjs@maum.ai",
    "정섭": "cjs@maum.ai",
}

# 인물사전 검색 경로
PERSON_DICT_PATHS = [
    Path.home() / "work/vault-worv/20_Areas/00_인물사전",
    Path.home() / "obsidian/20_Areas/00_인물사전",
    Path.home() / "obsidian/10_Projects/Active/2511 취업작전/마음AI_WoRV",
]


def extract_email_from_file(file_path: Path) -> str | None:
    """마크다운 파일에서 이메일 추출"""
    try:
        content = file_path.read_text(encoding='utf-8')

        # YAML frontmatter에서 email 필드 찾기
        yaml_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
        if yaml_match:
            yaml_content = yaml_match.group(1)
            email_match = re.search(r'email:\s*(\S+@\S+)', yaml_content)
            if email_match:
                return email_match.group(1)

        # 본문에서 이메일 패턴 찾기 (표 형식)
        email_patterns = [
            r'\*\*이메일\*\*\s*\|\s*(\S+@\S+)',
            r'이메일[:\s]+(\S+@maum\.ai)',
            r'(\S+@maum\.ai)',
        ]

        for pattern in email_patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)

        return None
    except Exception:
        return None


def find_person_file(name: str) -> Path | None:
    """인물 이름으로 파일 찾기"""
    for base_path in PERSON_DICT_PATHS:
        if not base_path.exists():
            continue

        # 파일명에 이름이 포함된 파일 찾기
        for md_file in base_path.glob("**/*.md"):
            if name in md_file.stem:
                return md_file

    return None


def lookup_email(name: str) -> dict:
    """이름으로 이메일 조회"""
    result = {
        "name": name,
        "email": None,
        "source": None,
    }

    # 이미 이메일 형식이면 그대로 반환
    if '@' in name:
        result["email"] = name
        result["source"] = "direct"
        return result

    # 알려진 이메일에서 찾기
    if name in KNOWN_EMAILS:
        result["email"] = KNOWN_EMAILS[name]
        result["source"] = "known"
        return result

    # 인물사전에서 찾기
    person_file = find_person_file(name)
    if person_file:
        email = extract_email_from_file(person_file)
        if email:
            result["email"] = email
            result["source"] = f"file:{person_file.name}"
            return result

    return result


def main():
    parser = argparse.ArgumentParser(description="인물사전에서 이메일 조회")
    parser.add_argument("--names", required=True, help="조회할 이름들 (쉼표 구분)")
    parser.add_argument("--format", choices=["json", "text"], default="text")

    args = parser.parse_args()

    names = [n.strip() for n in args.names.split(",") if n.strip()]
    results = []

    for name in names:
        result = lookup_email(name)
        results.append(result)

    if args.format == "json":
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        found = []
        not_found = []

        for r in results:
            if r["email"]:
                found.append(f"{r['name']}: {r['email']}")
            else:
                not_found.append(r["name"])

        if found:
            print("✅ 찾은 이메일:")
            for f in found:
                print(f"  {f}")

        if not_found:
            print("\n❌ 찾지 못함:")
            for n in not_found:
                print(f"  {n}")

        # 이메일 목록만 출력 (스크립트 연동용)
        emails = [r["email"] for r in results if r["email"]]
        if emails:
            print(f"\n📧 이메일 목록: {','.join(emails)}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Gmail 메일 상태 변경 스크립트 - 읽음/읽지않음 처리
"""

import argparse
import sys
from gmail_client import get_gmail_service, mark_as_read, mark_as_unread


def search_and_mark(query: str, action: str = 'read', max_results: int = 100, dry_run: bool = False):
    """
    쿼리로 메일 검색 후 상태 변경.

    Args:
        query: Gmail 검색 쿼리
        action: 'read' 또는 'unread'
        max_results: 최대 검색 결과 수
        dry_run: True면 실제 변경 없이 미리보기만
    """
    service = get_gmail_service()

    # 메일 검색
    print(f"검색 중: {query}")
    results = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=max_results
    ).execute()

    messages = results.get('messages', [])
    if not messages:
        print("검색 결과가 없습니다.")
        return 0

    print(f"총 {len(messages)}개 메일 발견")

    if dry_run:
        print("\n[Dry Run] 실제 변경 없이 미리보기:")
        for i, msg in enumerate(messages[:10], 1):
            detail = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='metadata',
                metadataHeaders=['Subject', 'From', 'Date']
            ).execute()
            headers = {h['name']: h['value'] for h in detail.get('payload', {}).get('headers', [])}
            print(f"  [{i}] {headers.get('Subject', '(제목 없음)')[:60]}")
        if len(messages) > 10:
            print(f"  ... 외 {len(messages) - 10}개")
        return len(messages)

    # 상태 변경
    message_ids = [msg['id'] for msg in messages]
    if action == 'read':
        success = mark_as_read(service, message_ids)
        print(f"\n{success}/{len(messages)}개 메일을 읽음 처리했습니다.")
    else:
        success = mark_as_unread(service, message_ids)
        print(f"\n{success}/{len(messages)}개 메일을 읽지 않음 처리했습니다.")

    return success


def main():
    parser = argparse.ArgumentParser(description='Gmail 메일 읽음/읽지않음 처리')
    parser.add_argument('--query', '-q', required=True, help='Gmail 검색 쿼리 (예: from:vercel)')
    parser.add_argument('--action', '-a', choices=['read', 'unread'], default='read',
                        help='처리 방식 (기본: read)')
    parser.add_argument('--max', '-m', type=int, default=100,
                        help='최대 처리 메일 수 (기본: 100)')
    parser.add_argument('--dry-run', '-n', action='store_true',
                        help='실제 변경 없이 미리보기만')
    parser.add_argument('--yes', '-y', action='store_true',
                        help='확인 없이 바로 실행')

    args = parser.parse_args()

    # Dry run 먼저 실행
    if args.dry_run:
        search_and_mark(args.query, args.action, args.max, dry_run=True)
        return

    # 확인 프롬프트
    if not args.yes:
        count = search_and_mark(args.query, args.action, args.max, dry_run=True)
        if count == 0:
            return
        action_text = '읽음' if args.action == 'read' else '읽지 않음'
        confirm = input(f"\n위 {count}개 메일을 '{action_text}' 처리하시겠습니까? (y/N): ")
        if confirm.lower() != 'y':
            print("취소되었습니다.")
            return

    # 실행
    search_and_mark(args.query, args.action, args.max, dry_run=False)


if __name__ == '__main__':
    main()

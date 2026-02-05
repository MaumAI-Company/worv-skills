#!/usr/bin/env python3
"""
Google Sheets Writer

범용 구글 시트 쓰기 스크립트.
"""

import argparse
import json
import os
import sys

# Add parent directory to path for google_api import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google_api.sheets import GoogleSheetAPIManager

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


def find_credentials():
    """자동으로 credentials 경로를 찾습니다."""
    candidates = [
        # 1. 현재 작업 디렉토리의 .credentials
        os.path.join(os.getcwd(), '.credentials', 'google-service-account.json'),
        # 2. 전역 ~/.claude/.credentials
        os.path.expanduser('~/.claude/.credentials/google-service-account.json'),
        # 3. 레거시: obsidian 볼트 경로
        os.path.expanduser('~/projects/obsidian/.credentials/google-service-account.json'),
    ]

    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def main():
    parser = argparse.ArgumentParser(description='Google Sheets Writer')
    parser.add_argument('--sheet-id', required=True, help='Google Sheet ID')
    parser.add_argument('--range', required=True, help='Range to write (A1 notation)')
    parser.add_argument('--credentials', help='Path to service account JSON')
    parser.add_argument('--data', help='JSON data to write (2D array or file path)')
    parser.add_argument('--mode', choices=['update', 'append', 'clear'], default='update',
                        help='Write mode')
    parser.add_argument('--sheet-name', help='Specific sheet name (tab)')
    parser.add_argument('--stdin', action='store_true', help='Read data from stdin')

    args = parser.parse_args()

    # Credentials path: 명시적 인자 > 환경변수 > 자동 탐색
    creds_path = args.credentials or os.environ.get('GOOGLE_CREDENTIALS_PATH') or find_credentials()
    if not creds_path:
        print("Error: credentials를 찾을 수 없습니다.", file=sys.stderr)
        print("다음 중 하나를 설정하세요:", file=sys.stderr)
        print("  1. --credentials 옵션", file=sys.stderr)
        print("  2. GOOGLE_CREDENTIALS_PATH 환경변수", file=sys.stderr)
        print("  3. .credentials/google-service-account.json 파일 생성", file=sys.stderr)
        sys.exit(1)

    try:
        manager = GoogleSheetAPIManager(creds_path, SCOPES)
        manager.set_spreadsheet_id(args.sheet_id)

        # 시트 이름이 지정되면 자동으로 생성 (없는 경우)
        if args.sheet_name:
            created = manager.ensure_sheet_exists(args.sheet_name)
            if created:
                print(f"📋 Created new sheet: '{args.sheet_name}'", file=sys.stderr)

        # Build range with sheet name if provided
        range_name = args.range
        if args.sheet_name:
            range_name = f"'{args.sheet_name}'!{args.range}"

        # Clear mode
        if args.mode == 'clear':
            result = manager.clear_values(range_name)
            print(f"✅ Cleared range: {range_name}")
            return

        # Get data
        if args.stdin:
            data_str = sys.stdin.read()
        elif args.data:
            if os.path.isfile(args.data):
                with open(args.data, 'r', encoding='utf-8') as f:
                    data_str = f.read()
            else:
                data_str = args.data
        else:
            print("Error: --data or --stdin required for update/append", file=sys.stderr)
            sys.exit(1)

        # Parse data
        try:
            values = json.loads(data_str)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON data: {e}", file=sys.stderr)
            sys.exit(1)

        # Ensure 2D array
        if not isinstance(values, list):
            print("Error: Data must be a 2D array", file=sys.stderr)
            sys.exit(1)
        if values and not isinstance(values[0], list):
            values = [values]  # Wrap single row

        # Write
        if args.mode == 'update':
            result = manager.update_values(range_name, values)
            updated = result.get('updatedCells', 0)
            print(f"✅ Updated {updated} cells in {range_name}")
        elif args.mode == 'append':
            result = manager.append_values(range_name, values)
            updates = result.get('updates', {})
            updated_rows = updates.get('updatedRows', 0)
            print(f"✅ Appended {updated_rows} rows to {range_name}")

        # Print result
        print(json.dumps({
            "success": True,
            "range": range_name,
            "mode": args.mode,
            "rows": len(values)
        }, ensure_ascii=False, indent=2))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

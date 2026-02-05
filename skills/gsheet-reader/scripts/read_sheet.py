#!/usr/bin/env python3
"""
Google Sheets Reader

범용 구글 시트 읽기 스크립트.
"""

import argparse
import json
import os
import sys

# Add parent directory to path for google_api import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google_api.sheets import GoogleSheetAPIManager

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']


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
    parser = argparse.ArgumentParser(description='Google Sheets Reader')
    parser.add_argument('--sheet-id', required=True, help='Google Sheet ID')
    parser.add_argument('--range', default='A1:Z1000', help='Range to read (A1 notation)')
    parser.add_argument('--credentials', help='Path to service account JSON')
    parser.add_argument('--format', choices=['json', 'csv', 'table'], default='json',
                        help='Output format')
    parser.add_argument('--sheet-name', help='Specific sheet name (tab) to read')
    parser.add_argument('--list-sheets', action='store_true', help='List all sheet names')

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

        # List sheets mode
        if args.list_sheets:
            sheets = manager.get_all_sheets()
            print(json.dumps({"sheets": sheets}, ensure_ascii=False, indent=2))
            return

        # Build range with sheet name if provided
        range_name = args.range
        if args.sheet_name:
            range_name = f"'{args.sheet_name}'!{args.range}"

        # Read values
        values = manager.get_values(range_name)

        if not values:
            print("No data found.", file=sys.stderr)
            sys.exit(0)

        # Output formatting
        if args.format == 'json':
            # First row as headers
            if len(values) > 1:
                headers = values[0]
                data = []
                for row in values[1:]:
                    row_dict = {}
                    for i, header in enumerate(headers):
                        row_dict[header] = row[i] if i < len(row) else ''
                    data.append(row_dict)
                print(json.dumps(data, ensure_ascii=False, indent=2))
            else:
                print(json.dumps(values, ensure_ascii=False, indent=2))

        elif args.format == 'csv':
            for row in values:
                print(','.join(f'"{cell}"' for cell in row))

        elif args.format == 'table':
            # Simple table format
            if values:
                col_widths = []
                for col_idx in range(len(values[0])):
                    max_width = 0
                    for row in values:
                        if col_idx < len(row):
                            max_width = max(max_width, len(str(row[col_idx])))
                    col_widths.append(min(max_width, 30))

                for row_idx, row in enumerate(values):
                    formatted = []
                    for col_idx, cell in enumerate(row):
                        width = col_widths[col_idx] if col_idx < len(col_widths) else 10
                        formatted.append(str(cell)[:width].ljust(width))
                    print(' | '.join(formatted))
                    if row_idx == 0:
                        print('-' * (sum(col_widths) + 3 * (len(col_widths) - 1)))

        print(f"\n✅ {len(values)} rows read from sheet", file=sys.stderr)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

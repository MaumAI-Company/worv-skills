#!/usr/bin/env python3
"""
Google Calendar Reader

캘린더 목록 조회, 이벤트 조회, 빈 시간 조회 스크립트.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google_api.calendar import GoogleCalendarManager


def get_kst_now():
    """Get current time in KST."""
    return datetime.now(ZoneInfo('Asia/Seoul'))


def format_datetime_kst(dt_str):
    """Format datetime string for display in KST."""
    if not dt_str:
        return ''
    if 'T' in dt_str:
        # DateTime format
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        dt_kst = dt.astimezone(ZoneInfo('Asia/Seoul'))
        return dt_kst.strftime('%Y-%m-%d %H:%M')
    else:
        # Date only (all-day event)
        return dt_str + ' (종일)'


def main():
    parser = argparse.ArgumentParser(description='Google Calendar Reader')
    parser.add_argument('--token', help='Path to calendar_token.pickle')
    parser.add_argument('--list-calendars', action='store_true',
                        help='List all calendars')
    parser.add_argument('--calendar-id', default='primary',
                        help='Calendar ID (default: primary)')
    parser.add_argument('--date', help='Date to query (YYYY-MM-DD, default: today)')
    parser.add_argument('--days', type=int, default=7,
                        help='Number of days to query (default: 7)')
    parser.add_argument('--query', help='Search query')
    parser.add_argument('--max-results', type=int, default=50,
                        help='Maximum number of events')
    parser.add_argument('--freebusy', action='store_true',
                        help='Get free/busy info instead of events')
    parser.add_argument('--format', choices=['json', 'table'], default='table',
                        help='Output format')

    args = parser.parse_args()

    # Token path
    token_path = args.token or os.environ.get('GOOGLE_CALENDAR_TOKEN')
    if not token_path:
        # Default path
        default_paths = [
            os.path.expanduser('~/work/vault-worv/.credentials/calendar_token.pickle'),
            os.path.expanduser('~/.credentials/calendar_token.pickle')
        ]
        for path in default_paths:
            if os.path.exists(path):
                token_path = path
                break

    if not token_path or not os.path.exists(token_path):
        print("Error: --token or GOOGLE_CALENDAR_TOKEN required", file=sys.stderr)
        print("Or place token at ~/work/vault-worv/.credentials/calendar_token.pickle", file=sys.stderr)
        sys.exit(1)

    try:
        manager = GoogleCalendarManager(token_path)

        # List calendars mode
        if args.list_calendars:
            calendars = manager.list_calendars()
            if args.format == 'json':
                print(json.dumps(calendars, ensure_ascii=False, indent=2))
            else:
                print(f"{'Primary':<8} {'ID':<40} {'Name':<30}")
                print('-' * 80)
                for cal in calendars:
                    primary = '✓' if cal['primary'] else ''
                    print(f"{primary:<8} {cal['id'][:38]:<40} {cal['summary'][:28]:<30}")
            return

        # Calculate time range
        kst = ZoneInfo('Asia/Seoul')
        if args.date:
            start_date = datetime.strptime(args.date, '%Y-%m-%d')
            start_date = start_date.replace(tzinfo=kst)
        else:
            start_date = get_kst_now().replace(hour=0, minute=0, second=0, microsecond=0)

        end_date = start_date + timedelta(days=args.days)

        time_min = start_date.isoformat()
        time_max = end_date.isoformat()

        # Free/busy mode
        if args.freebusy:
            cal_ids = [args.calendar_id]
            freebusy = manager.get_freebusy(cal_ids, time_min, time_max)
            if args.format == 'json':
                print(json.dumps(freebusy, ensure_ascii=False, indent=2))
            else:
                print(f"Free/Busy for {args.calendar_id}")
                print(f"Period: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
                print('-' * 60)
                for cal_id, info in freebusy.items():
                    busy_times = info.get('busy', [])
                    if busy_times:
                        for slot in busy_times:
                            start = format_datetime_kst(slot.get('start'))
                            end = format_datetime_kst(slot.get('end'))
                            print(f"  Busy: {start} ~ {end}")
                    else:
                        print("  No busy times (all free)")
            return

        # Get events
        events = manager.get_events(
            calendar_id=args.calendar_id,
            time_min=time_min,
            time_max=time_max,
            max_results=args.max_results,
            query=args.query
        )

        if args.format == 'json':
            print(json.dumps(events, ensure_ascii=False, indent=2))
        else:
            print(f"Calendar: {args.calendar_id}")
            print(f"Period: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
            if args.query:
                print(f"Search: {args.query}")
            print('-' * 80)

            if not events:
                print("No events found.")
            else:
                current_date = None
                for event in events:
                    start = event['start']
                    if start:
                        event_date = start[:10]
                        if event_date != current_date:
                            current_date = event_date
                            # Parse and format date with weekday
                            dt = datetime.strptime(event_date, '%Y-%m-%d')
                            weekdays = ['월', '화', '수', '목', '금', '토', '일']
                            weekday = weekdays[dt.weekday()]
                            print(f"\n📅 {event_date} ({weekday})")
                            print('-' * 40)

                    start_fmt = format_datetime_kst(event['start'])
                    end_fmt = format_datetime_kst(event['end'])

                    # Time only for display
                    if 'T' in (event['start'] or ''):
                        start_time = start_fmt.split(' ')[1] if ' ' in start_fmt else start_fmt
                        end_time = end_fmt.split(' ')[1] if ' ' in end_fmt else end_fmt
                        time_str = f"{start_time} - {end_time}"
                    else:
                        time_str = "종일"

                    print(f"  {time_str:15} {event['summary'][:40]}")
                    if event['location']:
                        print(f"  {'':15} 📍 {event['location'][:35]}")

        print(f"\n✅ {len(events)} events found", file=sys.stderr)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

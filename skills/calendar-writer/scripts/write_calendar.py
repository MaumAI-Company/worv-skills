#!/usr/bin/env python3
"""
Google Calendar Writer

캘린더 이벤트 생성, 수정, 삭제 스크립트.
"""

import argparse
import json
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google_api.calendar import GoogleCalendarWriter


def main():
    parser = argparse.ArgumentParser(description='Google Calendar Writer')
    parser.add_argument('--token', help='Path to calendar_token.pickle')
    parser.add_argument('--calendar-id', default='primary',
                        help='Calendar ID (default: primary)')

    # Action
    parser.add_argument('--action', choices=['create', 'update', 'delete', 'quick-add'],
                        required=True, help='Action to perform')

    # Event details
    parser.add_argument('--event-id', help='Event ID (for update/delete)')
    parser.add_argument('--summary', help='Event title')
    parser.add_argument('--start', help='Start time (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)')
    parser.add_argument('--end', help='End time')
    parser.add_argument('--description', help='Event description')
    parser.add_argument('--location', help='Event location')
    parser.add_argument('--attendees', help='Comma-separated attendee emails')
    parser.add_argument('--timezone', default='Asia/Seoul', help='Timezone')
    parser.add_argument('--all-day', action='store_true', help='All-day event')
    parser.add_argument('--meet', action='store_true', help='Add Google Meet link')
    parser.add_argument('--no-notify', action='store_true',
                        help='Do not send notifications')
    parser.add_argument('--text', help='Natural language text for quick-add')

    args = parser.parse_args()

    # Token path
    token_path = args.token or os.environ.get('GOOGLE_CALENDAR_TOKEN')
    if not token_path:
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
        sys.exit(1)

    try:
        writer = GoogleCalendarWriter(token_path)
        send_notifications = not args.no_notify

        if args.action == 'create':
            if not args.summary or not args.start or not args.end:
                print("Error: --summary, --start, --end required for create", file=sys.stderr)
                sys.exit(1)

            attendees = args.attendees.split(',') if args.attendees else None

            result = writer.create_event(
                summary=args.summary,
                start=args.start,
                end=args.end,
                calendar_id=args.calendar_id,
                description=args.description,
                location=args.location,
                attendees=attendees,
                timezone=args.timezone,
                all_day=args.all_day,
                send_notifications=send_notifications,
                conference=args.meet
            )

            print(json.dumps(result, ensure_ascii=False, indent=2))
            print(f"\n✅ Event created: {result['summary']}", file=sys.stderr)
            print(f"   Link: {result['htmlLink']}", file=sys.stderr)
            if result.get('hangoutLink'):
                print(f"   Meet: {result['hangoutLink']}", file=sys.stderr)

        elif args.action == 'update':
            if not args.event_id:
                print("Error: --event-id required for update", file=sys.stderr)
                sys.exit(1)

            attendees = args.attendees.split(',') if args.attendees else None

            result = writer.update_event(
                event_id=args.event_id,
                calendar_id=args.calendar_id,
                summary=args.summary,
                start=args.start,
                end=args.end,
                description=args.description,
                location=args.location,
                attendees=attendees,
                timezone=args.timezone,
                send_notifications=send_notifications
            )

            print(json.dumps(result, ensure_ascii=False, indent=2))
            print(f"\n✅ Event updated: {result['summary']}", file=sys.stderr)

        elif args.action == 'delete':
            if not args.event_id:
                print("Error: --event-id required for delete", file=sys.stderr)
                sys.exit(1)

            result = writer.delete_event(
                event_id=args.event_id,
                calendar_id=args.calendar_id,
                send_notifications=send_notifications
            )

            print(json.dumps(result, ensure_ascii=False, indent=2))
            print(f"\n✅ Event deleted: {args.event_id}", file=sys.stderr)

        elif args.action == 'quick-add':
            if not args.text:
                print("Error: --text required for quick-add", file=sys.stderr)
                sys.exit(1)

            result = writer.quick_add(
                text=args.text,
                calendar_id=args.calendar_id,
                send_notifications=send_notifications
            )

            print(json.dumps(result, ensure_ascii=False, indent=2))
            print(f"\n✅ Event created: {result['summary']}", file=sys.stderr)
            print(f"   Link: {result['htmlLink']}", file=sys.stderr)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

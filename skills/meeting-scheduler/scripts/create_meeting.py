#!/usr/bin/env python3
"""
캘린더 이벤트를 생성합니다.
"""

import argparse
import json
import os
import pickle
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import pytz
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


# 설정
TIMEZONE = 'Asia/Seoul'
TOKEN_PATHS = [
    Path.home() / "work/vault-worv/.credentials/calendar_token.pickle",
    Path.home() / ".credentials/calendar_token.pickle",
]


def get_calendar_service():
    """OAuth 토큰으로 Calendar API 서비스 반환"""
    creds = None
    token_file = None

    for path in TOKEN_PATHS:
        if path.exists():
            token_file = path
            break

    if not token_file:
        raise FileNotFoundError("Calendar OAuth 토큰을 찾을 수 없습니다.")

    with open(token_file, 'rb') as f:
        creds = pickle.load(f)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_file, 'wb') as f:
            pickle.dump(creds, f)

    return build('calendar', 'v3', credentials=creds)


def create_event(
    service,
    summary: str,
    start: datetime,
    end: datetime,
    attendees: Optional[List[str]] = None,
    room_id: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
    create_meet: bool = True,
) -> dict:
    """캘린더 이벤트 생성"""
    tz = pytz.timezone(TIMEZONE)

    if start.tzinfo is None:
        start = tz.localize(start)
    if end.tzinfo is None:
        end = tz.localize(end)

    event = {
        'summary': summary,
        'start': {
            'dateTime': start.isoformat(),
            'timeZone': TIMEZONE,
        },
        'end': {
            'dateTime': end.isoformat(),
            'timeZone': TIMEZONE,
        },
    }

    if description:
        event['description'] = description

    if location:
        event['location'] = location

    # 참석자 구성
    all_attendees = []
    if attendees:
        for email in attendees:
            all_attendees.append({'email': email})

    if room_id:
        all_attendees.append({'email': room_id, 'resource': True})

    if all_attendees:
        event['attendees'] = all_attendees

    # Google Meet 링크 생성
    if create_meet:
        event['conferenceData'] = {
            'createRequest': {
                'requestId': str(uuid.uuid4()),
                'conferenceSolutionKey': {'type': 'hangoutsMeet'},
            }
        }

    # 이벤트 생성
    created = service.events().insert(
        calendarId='primary',
        body=event,
        conferenceDataVersion=1 if create_meet else 0,
        sendUpdates='all' if all_attendees else 'none',
    ).execute()

    return created


def main():
    parser = argparse.ArgumentParser(description="캘린더 이벤트 생성")
    parser.add_argument("--summary", required=True, help="이벤트 제목")
    parser.add_argument("--start", required=True, help="시작 시간 (YYYY-MM-DDTHH:MM:SS)")
    parser.add_argument("--end", required=True, help="종료 시간 (YYYY-MM-DDTHH:MM:SS)")
    parser.add_argument("--attendees", help="참석자 이메일 (쉼표 구분)")
    parser.add_argument("--room-id", help="회의실 리소스 ID")
    parser.add_argument("--description", help="이벤트 설명")
    parser.add_argument("--location", help="장소")
    parser.add_argument("--no-meet", action="store_true", help="Google Meet 생성 안함")
    parser.add_argument("--format", choices=["json", "text"], default="text")

    args = parser.parse_args()

    # 시간 파싱
    tz = pytz.timezone(TIMEZONE)
    start = tz.localize(datetime.strptime(args.start, "%Y-%m-%dT%H:%M:%S"))
    end = tz.localize(datetime.strptime(args.end, "%Y-%m-%dT%H:%M:%S"))

    # 참석자 파싱
    attendees = None
    if args.attendees:
        attendees = [a.strip() for a in args.attendees.split(",") if a.strip()]

    try:
        service = get_calendar_service()

        event = create_event(
            service,
            summary=args.summary,
            start=start,
            end=end,
            attendees=attendees,
            room_id=args.room_id,
            description=args.description,
            location=args.location,
            create_meet=not args.no_meet,
        )

        if args.format == "json":
            print(json.dumps(event, ensure_ascii=False, indent=2))
        else:
            print("✅ 이벤트가 생성되었습니다!")
            print(f"\n📅 {event.get('summary')}")

            # 시간 표시
            start_dt = event['start'].get('dateTime', '')
            if start_dt:
                dt = datetime.fromisoformat(start_dt)
                weekday = ['월', '화', '수', '목', '금', '토', '일'][dt.weekday()]
                print(f"🕐 {dt.strftime('%Y-%m-%d')} ({weekday}) {dt.strftime('%H:%M')} ~ {end.strftime('%H:%M')}")

            # 참석자 표시
            attendee_list = event.get('attendees', [])
            if attendee_list:
                emails = [a['email'] for a in attendee_list if not a['email'].endswith('calendar.google.com')]
                if emails:
                    print(f"👥 참석자: {', '.join(emails)}")

            # Google Meet 링크
            hangout_link = event.get('hangoutLink', '')
            if hangout_link:
                print(f"🔗 Google Meet: {hangout_link}")

            # 캘린더 링크
            html_link = event.get('htmlLink', '')
            if html_link:
                print(f"📎 캘린더: {html_link}")

            print(f"\n이벤트 ID: {event.get('id')}")

    except FileNotFoundError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ 오류: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

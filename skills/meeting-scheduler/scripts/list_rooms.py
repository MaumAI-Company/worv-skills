#!/usr/bin/env python3
"""
회의실 목록을 조회하고 가용성을 확인합니다.
"""

import argparse
import json
import os
import pickle
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

import pytz
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


# 설정
TIMEZONE = 'Asia/Seoul'
TOKEN_PATHS = [
    Path.home() / "work/vault-worv/.credentials/calendar_token.pickle",
    Path.home() / ".credentials/calendar_token.pickle",
]

# 알려진 회의실 리소스 ID
# preferred: True인 회의실이 우선 추천됨
KNOWN_ROOMS = {
    # === 선호 회의실 (우선 추천) ===
    "Silicon Valley": {
        "id": "c_18841ts7pgvskhnujrglhn2jgnor8@resource.calendar.google.com",
        "capacity": 8,
        "type": "중회의실",
        "location": "maumai",
        "preferred": True,
    },
    "Edmonton": {
        "id": "c_1887lphdporkii72ll8hsid9uc410@resource.calendar.google.com",
        "capacity": 6,
        "type": "중회의실",
        "location": "maumai",
        "preferred": True,
    },
    # === 마음AI 본사 (maumai) ===
    "Toronto": {
        "id": "c_1881cvo6akpmqjvnm2oj3ht8r8vi6@resource.calendar.google.com",
        "capacity": 10,
        "type": "대회의실",
        "location": "maumai",
    },
    "London": {
        "id": "c_1886gsmm0vlrcjcbkqrjeui24cc04@resource.calendar.google.com",
        "capacity": 8,
        "type": "중회의실",
        "location": "maumai",
    },
    "NewYork": {
        "id": "c_18875rvtng67ih2klnmjpnmi6qum4@resource.calendar.google.com",
        "capacity": 8,
        "type": "중회의실",
        "location": "maumai",
    },
    "Tokyo": {
        "id": "c_18897kknt7a68hp0hkivg46asdv5u@resource.calendar.google.com",
        "capacity": 8,
        "type": "중회의실",
        "location": "maumai",
    },
    "CEO실": {
        "id": "c_1884i3n5hs7keh0fjogog6ktrc7qi@resource.calendar.google.com",
        "capacity": 6,
        "type": "중회의실",
        "location": "maumai",
    },
    "MUH 라운지": {
        "id": "c_1882u8i9f1a5cgm2itn8eatrbkupg@resource.calendar.google.com",
        "capacity": 100,
        "type": "라운지",
        "location": "maumai",
    },
    # === CW 빌딩 (5층) ===
    "CW Board Room": {
        "id": "c_1884c8tu594oihv3k31644040ljn4@resource.calendar.google.com",
        "capacity": 8,
        "type": "회의실",
        "location": "cw-5층",
    },
    "CW Works 회의실": {
        "id": "c_1887ur99i9ph2jobhss4ndhthstiq@resource.calendar.google.com",
        "capacity": 10,
        "type": "회의실",
        "location": "cw-5층",
    },
    # === 테헤란로 ===
    "Teheran Room 1": {
        "id": "c_188e30525cst6grulqi28pconqt3q@resource.calendar.google.com",
        "capacity": 6,
        "type": "회의실",
        "location": "테헤란 242-3",
    },
    # === 4층 임원실 ===
    "CEO Office": {
        "id": "c_1888ejgvn5jjggjkgl77k8hg1hb52@resource.calendar.google.com",
        "capacity": 10,
        "type": "임원실",
        "location": "4층",
    },
    "CTO Office": {
        "id": "c_188akaaeo5ihkh9jmsbjjhq1m60ns@resource.calendar.google.com",
        "capacity": 6,
        "type": "임원실",
        "location": "4층",
    },
    "Next 대회의실": {
        "id": "c_188ajksptvrr6iq7g0mh4m07udno8@resource.calendar.google.com",
        "capacity": 16,
        "type": "대회의실",
        "location": "4층",
    },
}


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


def check_room_availability(
    service,
    room_id: str,
    start: datetime,
    end: datetime,
) -> bool:
    """회의실 가용성 확인"""
    tz = pytz.timezone(TIMEZONE)

    if start.tzinfo is None:
        start = tz.localize(start)
    if end.tzinfo is None:
        end = tz.localize(end)

    body = {
        'timeMin': start.isoformat(),
        'timeMax': end.isoformat(),
        'items': [{'id': room_id}],
        'timeZone': TIMEZONE,
    }

    result = service.freebusy().query(body=body).execute()
    busy = result.get('calendars', {}).get(room_id, {}).get('busy', [])

    return len(busy) == 0


def discover_rooms_from_events(service, days: int = 90) -> Dict[str, Dict]:
    """기존 이벤트에서 회의실 리소스 ID 추출"""
    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)
    time_min = now - timedelta(days=days)
    time_max = now + timedelta(days=30)

    discovered = {}

    try:
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min.isoformat(),
            timeMax=time_max.isoformat(),
            singleEvents=True,
            maxResults=500,
        ).execute()

        for event in events_result.get('items', []):
            location = event.get('location', '')
            for attendee in event.get('attendees', []):
                email = attendee.get('email', '')
                if 'resource.calendar.google.com' in email and email not in discovered:
                    # 위치 정보에서 회의실 이름 추출
                    name = location if location else email.split('@')[0]
                    discovered[email] = {
                        'id': email,
                        'name': name,
                        'source': 'discovered',
                    }

    except Exception as e:
        print(f"이벤트 조회 중 오류: {e}", file=sys.stderr)

    return discovered


def get_available_rooms(
    service,
    start: datetime,
    end: datetime,
    min_capacity: int = 0,
    preferred_only: bool = False,
    location: Optional[str] = None,
) -> List[Dict]:
    """가용한 회의실 목록 반환 (선호 회의실 우선)"""
    available = []

    # 알려진 회의실 확인
    for name, info in KNOWN_ROOMS.items():
        if min_capacity > 0 and info.get('capacity', 0) < min_capacity:
            continue

        if preferred_only and not info.get('preferred', False):
            continue

        if location and info.get('location', '') != location:
            continue

        if check_room_availability(service, info['id'], start, end):
            available.append({
                'name': name,
                'id': info['id'],
                'capacity': info.get('capacity', 0),
                'type': info.get('type', ''),
                'location': info.get('location', ''),
                'preferred': info.get('preferred', False),
                'available': True,
            })

    # 선호 회의실 우선, 그 다음 수용 인원 순
    available.sort(key=lambda x: (not x['preferred'], -x['capacity']))
    return available


from datetime import timedelta


def main():
    parser = argparse.ArgumentParser(description="회의실 목록 및 가용성 조회")
    parser.add_argument("--start", help="시작 시간 (YYYY-MM-DDTHH:MM:SS)")
    parser.add_argument("--end", help="종료 시간 (YYYY-MM-DDTHH:MM:SS)")
    parser.add_argument("--min-capacity", type=int, default=0, help="최소 수용 인원")
    parser.add_argument("--discover", action="store_true", help="이벤트에서 회의실 발견")
    parser.add_argument("--format", choices=["json", "text"], default="text")

    args = parser.parse_args()

    try:
        service = get_calendar_service()

        if args.discover:
            # 이벤트에서 회의실 발견
            discovered = discover_rooms_from_events(service)

            if args.format == "json":
                print(json.dumps(list(discovered.values()), ensure_ascii=False, indent=2))
            else:
                print("발견된 회의실:")
                for room_id, info in discovered.items():
                    print(f"  {info['name']}: {room_id}")

        elif args.start and args.end:
            # 특정 시간대 가용 회의실 조회
            tz = pytz.timezone(TIMEZONE)
            start = tz.localize(datetime.strptime(args.start, "%Y-%m-%dT%H:%M:%S"))
            end = tz.localize(datetime.strptime(args.end, "%Y-%m-%dT%H:%M:%S"))

            available = get_available_rooms(service, start, end, args.min_capacity)

            if args.format == "json":
                print(json.dumps(available, ensure_ascii=False, indent=2))
            else:
                if not available:
                    print("❌ 가용한 회의실이 없습니다.")
                else:
                    print(f"✅ 가용한 회의실 ({len(available)}개)")
                    print(f"시간: {args.start} ~ {args.end}\n")

                    for i, room in enumerate(available, 1):
                        capacity = f" ({room['capacity']}명)" if room['capacity'] else ""
                        room_type = f" [{room['type']}]" if room['type'] else ""
                        print(f"  {i}. {room['name']}{capacity}{room_type}")
                        print(f"     ID: {room['id']}")

        else:
            # 알려진 회의실 목록만 출력
            if args.format == "json":
                rooms = [
                    {'name': name, **info}
                    for name, info in KNOWN_ROOMS.items()
                ]
                print(json.dumps(rooms, ensure_ascii=False, indent=2))
            else:
                print("알려진 회의실:")
                for name, info in KNOWN_ROOMS.items():
                    capacity = f" ({info['capacity']}명)" if info.get('capacity') else ""
                    room_type = f" [{info['type']}]" if info.get('type') else ""
                    print(f"  {name}{capacity}{room_type}")
                    print(f"    ID: {info['id']}")

    except FileNotFoundError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ 오류: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

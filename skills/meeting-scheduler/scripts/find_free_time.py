#!/usr/bin/env python3
"""
참석자들의 freebusy를 조회하여 공통 빈 시간을 찾습니다.
"""

import argparse
import json
import os
import pickle
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple

import pytz
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
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


def get_freebusy(service, calendars: List[str], time_min: datetime, time_max: datetime) -> Dict:
    """여러 캘린더의 freebusy 조회"""
    tz = pytz.timezone(TIMEZONE)

    if time_min.tzinfo is None:
        time_min = tz.localize(time_min)
    if time_max.tzinfo is None:
        time_max = tz.localize(time_max)

    body = {
        'timeMin': time_min.isoformat(),
        'timeMax': time_max.isoformat(),
        'items': [{'id': cal} for cal in calendars],
        'timeZone': TIMEZONE,
    }

    result = service.freebusy().query(body=body).execute()
    return result.get('calendars', {})


def parse_busy_periods(freebusy_result: Dict) -> List[Tuple[datetime, datetime]]:
    """모든 참석자의 바쁜 시간을 합친 리스트 반환"""
    tz = pytz.timezone(TIMEZONE)
    all_busy = []

    for cal_id, cal_data in freebusy_result.items():
        for busy in cal_data.get('busy', []):
            start = datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
            end = datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))
            all_busy.append((start.astimezone(tz), end.astimezone(tz)))

    # 시간순 정렬
    all_busy.sort(key=lambda x: x[0])
    return all_busy


def merge_busy_periods(busy_periods: List[Tuple[datetime, datetime]]) -> List[Tuple[datetime, datetime]]:
    """겹치는 바쁜 시간 병합"""
    if not busy_periods:
        return []

    merged = [busy_periods[0]]

    for start, end in busy_periods[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:
            # 겹치면 병합
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))

    return merged


def find_free_slots(
    busy_periods: List[Tuple[datetime, datetime]],
    date_start: datetime,
    date_end: datetime,
    duration_minutes: int,
    working_hours: Tuple[int, int] = (9, 18),
    lunch_break: Tuple[int, int] = (12, 13),
    slot_interval: int = 30,
) -> List[Tuple[datetime, datetime]]:
    """빈 시간 슬롯 찾기"""
    tz = pytz.timezone(TIMEZONE)
    free_slots = []

    current_date = date_start.date()
    end_date = date_end.date()

    while current_date <= end_date:
        # 주말 제외
        if current_date.weekday() >= 5:
            current_date += timedelta(days=1)
            continue

        # 근무 시간 내 슬롯 생성
        day_start = tz.localize(datetime.combine(current_date, datetime.min.time().replace(hour=working_hours[0])))
        day_end = tz.localize(datetime.combine(current_date, datetime.min.time().replace(hour=working_hours[1])))

        current_slot = day_start
        while current_slot + timedelta(minutes=duration_minutes) <= day_end:
            slot_end = current_slot + timedelta(minutes=duration_minutes)

            # 점심시간 체크
            slot_hour = current_slot.hour
            if lunch_break[0] <= slot_hour < lunch_break[1]:
                current_slot = tz.localize(
                    datetime.combine(current_date, datetime.min.time().replace(hour=lunch_break[1]))
                )
                continue

            # 바쁜 시간과 겹치는지 체크
            is_free = True
            for busy_start, busy_end in busy_periods:
                if not (slot_end <= busy_start or current_slot >= busy_end):
                    is_free = False
                    break

            if is_free:
                free_slots.append((current_slot, slot_end))

            current_slot += timedelta(minutes=slot_interval)

        current_date += timedelta(days=1)

    return free_slots


def format_slot(slot: Tuple[datetime, datetime]) -> str:
    """슬롯을 읽기 쉬운 형식으로 변환"""
    start, end = slot
    weekday = ['월', '화', '수', '목', '금', '토', '일'][start.weekday()]
    return f"{start.strftime('%m/%d')} ({weekday}) {start.strftime('%H:%M')} ~ {end.strftime('%H:%M')}"


def main():
    parser = argparse.ArgumentParser(description="참석자들의 공통 빈 시간 찾기")
    parser.add_argument("--attendees", required=True, help="참석자 이메일 (쉼표 구분)")
    parser.add_argument("--duration", type=int, default=60, help="회의 시간 (분)")
    parser.add_argument("--start-date", required=True, help="시작일 (YYYY-MM-DD)")
    parser.add_argument("--end-date", required=True, help="종료일 (YYYY-MM-DD)")
    parser.add_argument("--working-hours", default="09:00-18:00", help="근무 시간")
    parser.add_argument("--top", type=int, default=3, help="상위 N개 슬롯만 출력")
    parser.add_argument("--format", choices=["json", "text"], default="text")

    args = parser.parse_args()

    # 참석자 파싱
    attendees = [a.strip() for a in args.attendees.split(",") if a.strip()]
    if not attendees:
        print("❌ 참석자가 필요합니다.", file=sys.stderr)
        sys.exit(1)

    # 날짜 파싱
    tz = pytz.timezone(TIMEZONE)
    start_date = tz.localize(datetime.strptime(args.start_date, "%Y-%m-%d"))
    end_date = tz.localize(datetime.strptime(args.end_date, "%Y-%m-%d").replace(hour=23, minute=59))

    # 근무 시간 파싱
    wh_parts = args.working_hours.replace("~", "-").split("-")
    working_hours = (int(wh_parts[0].split(":")[0]), int(wh_parts[1].split(":")[0]))

    try:
        service = get_calendar_service()

        # freebusy 조회
        freebusy = get_freebusy(service, attendees, start_date, end_date)

        # 바쁜 시간 추출 및 병합
        busy_periods = parse_busy_periods(freebusy)
        merged_busy = merge_busy_periods(busy_periods)

        # 빈 시간 찾기
        free_slots = find_free_slots(
            merged_busy,
            start_date,
            end_date,
            args.duration,
            working_hours,
        )

        # 상위 N개만
        top_slots = free_slots[:args.top]

        if args.format == "json":
            output = [
                {
                    "start": slot[0].isoformat(),
                    "end": slot[1].isoformat(),
                    "display": format_slot(slot),
                }
                for slot in top_slots
            ]
            print(json.dumps(output, ensure_ascii=False, indent=2))
        else:
            if not top_slots:
                print("❌ 공통 빈 시간이 없습니다.")
                print(f"\n참석자: {', '.join(attendees)}")
                print(f"기간: {args.start_date} ~ {args.end_date}")
                print(f"회의 시간: {args.duration}분")
            else:
                print(f"✅ 공통 빈 시간 (상위 {len(top_slots)}개)")
                print(f"참석자: {', '.join(attendees)}")
                print(f"회의 시간: {args.duration}분\n")

                for i, slot in enumerate(top_slots, 1):
                    print(f"  {i}. {format_slot(slot)}")

                # 첫 번째 슬롯 정보 출력 (스크립트 연동용)
                first = top_slots[0]
                print(f"\n📅 추천: {format_slot(first)}")
                print(f"   시작: {first[0].strftime('%Y-%m-%dT%H:%M:%S')}")
                print(f"   종료: {first[1].strftime('%Y-%m-%dT%H:%M:%S')}")

    except FileNotFoundError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ 오류: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

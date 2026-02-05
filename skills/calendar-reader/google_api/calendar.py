"""
Google Calendar API Manager

OAuth 토큰 기반 Calendar API 접근을 제공합니다.
"""

import pickle
from pathlib import Path
from googleapiclient.discovery import build


class GoogleCalendarManager:
    """Google Calendar API Manager using OAuth token."""

    def __init__(self, token_path: str):
        """
        Initialize Calendar Manager.

        Args:
            token_path: Path to calendar_token.pickle file
        """
        token_file = Path(token_path)
        if not token_file.exists():
            raise FileNotFoundError(f"Token file not found: {token_path}")

        with open(token_file, 'rb') as f:
            credentials = pickle.load(f)

        self.service = build('calendar', 'v3', credentials=credentials)

    def list_calendars(self):
        """
        Get list of all calendars.

        Returns:
            List of calendar summary dicts
        """
        result = self.service.calendarList().list().execute()
        calendars = result.get('items', [])
        return [
            {
                'id': cal['id'],
                'summary': cal.get('summary', ''),
                'primary': cal.get('primary', False),
                'accessRole': cal.get('accessRole', '')
            }
            for cal in calendars
        ]

    def get_events(
        self,
        calendar_id: str = 'primary',
        time_min: str = None,
        time_max: str = None,
        max_results: int = 100,
        query: str = None,
        single_events: bool = True,
        order_by: str = 'startTime'
    ):
        """
        Get events from a calendar.

        Args:
            calendar_id: Calendar ID (default: 'primary')
            time_min: Start time (RFC3339, e.g., '2026-01-01T00:00:00+09:00')
            time_max: End time (RFC3339)
            max_results: Maximum number of events
            query: Free text search query
            single_events: Expand recurring events
            order_by: Order by 'startTime' or 'updated'

        Returns:
            List of event dicts
        """
        params = {
            'calendarId': calendar_id,
            'maxResults': max_results,
            'singleEvents': single_events,
        }

        if time_min:
            params['timeMin'] = time_min
        if time_max:
            params['timeMax'] = time_max
        if query:
            params['q'] = query
        if single_events and order_by:
            params['orderBy'] = order_by

        result = self.service.events().list(**params).execute()
        events = result.get('items', [])

        return [
            {
                'id': event['id'],
                'summary': event.get('summary', '(제목 없음)'),
                'start': event.get('start', {}).get('dateTime') or event.get('start', {}).get('date'),
                'end': event.get('end', {}).get('dateTime') or event.get('end', {}).get('date'),
                'location': event.get('location', ''),
                'description': event.get('description', ''),
                'attendees': [
                    {'email': a.get('email'), 'responseStatus': a.get('responseStatus')}
                    for a in event.get('attendees', [])
                ],
                'hangoutLink': event.get('hangoutLink', ''),
                'htmlLink': event.get('htmlLink', '')
            }
            for event in events
        ]

    def get_event(self, event_id: str, calendar_id: str = 'primary'):
        """
        Get a single event by ID.

        Args:
            event_id: Event ID
            calendar_id: Calendar ID

        Returns:
            Event dict
        """
        event = self.service.events().get(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()

        return {
            'id': event['id'],
            'summary': event.get('summary', '(제목 없음)'),
            'start': event.get('start', {}),
            'end': event.get('end', {}),
            'location': event.get('location', ''),
            'description': event.get('description', ''),
            'attendees': event.get('attendees', []),
            'hangoutLink': event.get('hangoutLink', ''),
            'htmlLink': event.get('htmlLink', ''),
            'status': event.get('status', ''),
            'created': event.get('created', ''),
            'updated': event.get('updated', '')
        }

    def get_freebusy(
        self,
        calendar_ids: list,
        time_min: str,
        time_max: str
    ):
        """
        Get free/busy information for calendars.

        Args:
            calendar_ids: List of calendar IDs
            time_min: Start time (RFC3339)
            time_max: End time (RFC3339)

        Returns:
            Dict with busy times per calendar
        """
        body = {
            'timeMin': time_min,
            'timeMax': time_max,
            'items': [{'id': cal_id} for cal_id in calendar_ids]
        }

        result = self.service.freebusy().query(body=body).execute()
        return result.get('calendars', {})

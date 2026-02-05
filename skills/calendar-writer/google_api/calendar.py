"""
Google Calendar API Manager (Writer)

OAuth 토큰 기반 Calendar API 쓰기 기능을 제공합니다.
"""

import pickle
from pathlib import Path
from googleapiclient.discovery import build


class GoogleCalendarWriter:
    """Google Calendar API Writer using OAuth token."""

    def __init__(self, token_path: str):
        """
        Initialize Calendar Writer.

        Args:
            token_path: Path to calendar_token.pickle file
        """
        token_file = Path(token_path)
        if not token_file.exists():
            raise FileNotFoundError(f"Token file not found: {token_path}")

        with open(token_file, 'rb') as f:
            credentials = pickle.load(f)

        self.service = build('calendar', 'v3', credentials=credentials)

    def create_event(
        self,
        summary: str,
        start: str,
        end: str,
        calendar_id: str = 'primary',
        description: str = None,
        location: str = None,
        attendees: list = None,
        timezone: str = 'Asia/Seoul',
        all_day: bool = False,
        send_notifications: bool = True,
        conference: bool = False
    ):
        """
        Create a new calendar event.

        Args:
            summary: Event title
            start: Start time (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
            end: End time
            calendar_id: Calendar ID (default: 'primary')
            description: Event description
            location: Event location
            attendees: List of attendee emails
            timezone: Timezone (default: 'Asia/Seoul')
            all_day: Whether this is an all-day event
            send_notifications: Send email notifications to attendees
            conference: Add Google Meet link

        Returns:
            Created event dict
        """
        event = {
            'summary': summary,
        }

        # Time format
        if all_day or 'T' not in start:
            event['start'] = {'date': start[:10]}
            event['end'] = {'date': end[:10]}
        else:
            # Ensure timezone suffix
            if not ('+' in start or 'Z' in start):
                start = start + '+09:00'
            if not ('+' in end or 'Z' in end):
                end = end + '+09:00'
            event['start'] = {'dateTime': start, 'timeZone': timezone}
            event['end'] = {'dateTime': end, 'timeZone': timezone}

        if description:
            event['description'] = description

        if location:
            event['location'] = location

        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]

        if conference:
            event['conferenceData'] = {
                'createRequest': {
                    'requestId': f"meet-{start.replace(':', '').replace('-', '')}",
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            }

        # Create event
        params = {
            'calendarId': calendar_id,
            'body': event,
            'sendNotifications': send_notifications
        }

        if conference:
            params['conferenceDataVersion'] = 1

        result = self.service.events().insert(**params).execute()

        return {
            'id': result['id'],
            'summary': result.get('summary'),
            'start': result.get('start'),
            'end': result.get('end'),
            'htmlLink': result.get('htmlLink'),
            'hangoutLink': result.get('hangoutLink', ''),
            'status': 'created'
        }

    def update_event(
        self,
        event_id: str,
        calendar_id: str = 'primary',
        summary: str = None,
        start: str = None,
        end: str = None,
        description: str = None,
        location: str = None,
        attendees: list = None,
        timezone: str = 'Asia/Seoul',
        send_notifications: bool = True
    ):
        """
        Update an existing event.

        Args:
            event_id: Event ID to update
            calendar_id: Calendar ID
            summary: New title (optional)
            start: New start time (optional)
            end: New end time (optional)
            description: New description (optional)
            location: New location (optional)
            attendees: New attendee list (optional)
            timezone: Timezone
            send_notifications: Send notifications

        Returns:
            Updated event dict
        """
        # Get existing event
        event = self.service.events().get(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()

        # Update fields if provided
        if summary:
            event['summary'] = summary

        if start:
            if 'T' not in start:
                event['start'] = {'date': start}
            else:
                if not ('+' in start or 'Z' in start):
                    start = start + '+09:00'
                event['start'] = {'dateTime': start, 'timeZone': timezone}

        if end:
            if 'T' not in end:
                event['end'] = {'date': end}
            else:
                if not ('+' in end or 'Z' in end):
                    end = end + '+09:00'
                event['end'] = {'dateTime': end, 'timeZone': timezone}

        if description is not None:
            event['description'] = description

        if location is not None:
            event['location'] = location

        if attendees is not None:
            event['attendees'] = [{'email': email} for email in attendees]

        result = self.service.events().update(
            calendarId=calendar_id,
            eventId=event_id,
            body=event,
            sendNotifications=send_notifications
        ).execute()

        return {
            'id': result['id'],
            'summary': result.get('summary'),
            'start': result.get('start'),
            'end': result.get('end'),
            'htmlLink': result.get('htmlLink'),
            'status': 'updated'
        }

    def delete_event(
        self,
        event_id: str,
        calendar_id: str = 'primary',
        send_notifications: bool = True
    ):
        """
        Delete an event.

        Args:
            event_id: Event ID to delete
            calendar_id: Calendar ID
            send_notifications: Send cancellation notifications

        Returns:
            Deletion status dict
        """
        self.service.events().delete(
            calendarId=calendar_id,
            eventId=event_id,
            sendNotifications=send_notifications
        ).execute()

        return {
            'id': event_id,
            'status': 'deleted'
        }

    def quick_add(
        self,
        text: str,
        calendar_id: str = 'primary',
        send_notifications: bool = True
    ):
        """
        Quick add event using natural language.

        Args:
            text: Natural language event description
                  e.g., "Meeting with John tomorrow at 3pm"
            calendar_id: Calendar ID
            send_notifications: Send notifications

        Returns:
            Created event dict
        """
        result = self.service.events().quickAdd(
            calendarId=calendar_id,
            text=text,
            sendNotifications=send_notifications
        ).execute()

        return {
            'id': result['id'],
            'summary': result.get('summary'),
            'start': result.get('start'),
            'end': result.get('end'),
            'htmlLink': result.get('htmlLink'),
            'status': 'created'
        }

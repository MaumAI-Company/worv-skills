"""
Google Sheets API Manager - Writer

This module provides write operations for Google Sheets.
"""

import googleapiclient.discovery
from .base import GoogleAPIManager

class GoogleSheetAPIManager(GoogleAPIManager):
    """
    Manager for Google Sheets API write operations.
    """

    def __init__(self, key_file, scopes):
        super().__init__(key_file, scopes)
        self.sheet_service = googleapiclient.discovery.build(
            'sheets', 'v4', credentials=self.credentials)
        self.spreadsheet_id = None

    def set_spreadsheet_id(self, spreadsheet_id):
        if not spreadsheet_id:
            raise ValueError("Spreadsheet ID must be provided")
        self.spreadsheet_id = spreadsheet_id

    def update_values(self, range_name, values, spreadsheet_id=None):
        """Update values in a range."""
        sheet_id = spreadsheet_id or self.spreadsheet_id
        if not sheet_id:
            raise ValueError("Spreadsheet ID must be provided")

        body = {
            'values': values,
            'majorDimension': 'ROWS'
        }
        return self.sheet_service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range=range_name,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()

    def append_values(self, range_name, values, spreadsheet_id=None):
        """Append values to a range."""
        sheet_id = spreadsheet_id or self.spreadsheet_id
        if not sheet_id:
            raise ValueError("Spreadsheet ID must be provided")

        body = {
            'values': values,
            'majorDimension': 'ROWS'
        }
        return self.sheet_service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range=range_name,
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()

    def batch_update_values(self, data, spreadsheet_id=None):
        """Update multiple ranges in a single batch request."""
        sheet_id = spreadsheet_id or self.spreadsheet_id
        if not sheet_id:
            raise ValueError("Spreadsheet ID must be provided")

        batch_data = []
        for item in data:
            batch_data.append({
                'range': item['range'],
                'values': item['values'],
                'majorDimension': item.get('majorDimension', 'ROWS')
            })

        body = {
            'valueInputOption': 'USER_ENTERED',
            'data': batch_data
        }

        return self.sheet_service.spreadsheets().values().batchUpdate(
            spreadsheetId=sheet_id, body=body).execute()

    def clear_values(self, range_name, spreadsheet_id=None):
        """Clear values in a range."""
        sheet_id = spreadsheet_id or self.spreadsheet_id
        if not sheet_id:
            raise ValueError("Spreadsheet ID must be provided")

        return self.sheet_service.spreadsheets().values().clear(
            spreadsheetId=sheet_id,
            range=range_name
        ).execute()

    def get_all_sheets(self, spreadsheet_id=None):
        """Get all sheet names in the spreadsheet."""
        sheet_id = spreadsheet_id or self.spreadsheet_id
        if not sheet_id:
            raise ValueError("Spreadsheet ID must be provided")

        metadata = self.sheet_service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        return [sheet['properties']['title'] for sheet in metadata.get('sheets', [])]

    def create_sheet(self, sheet_name, spreadsheet_id=None):
        """Create a new sheet (tab) in the spreadsheet."""
        sheet_id = spreadsheet_id or self.spreadsheet_id
        if not sheet_id:
            raise ValueError("Spreadsheet ID must be provided")

        body = {
            'requests': [{
                'addSheet': {
                    'properties': {
                        'title': sheet_name
                    }
                }
            }]
        }
        return self.sheet_service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id, body=body).execute()

    def ensure_sheet_exists(self, sheet_name, spreadsheet_id=None):
        """Ensure a sheet exists, create if not."""
        existing_sheets = self.get_all_sheets(spreadsheet_id)
        if sheet_name not in existing_sheets:
            self.create_sheet(sheet_name, spreadsheet_id)
            return True  # Created
        return False  # Already exists

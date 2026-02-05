"""
Google Sheets API Manager

This module provides a manager for Google Sheets API operations.
"""

import googleapiclient.discovery
from .base import GoogleAPIManager

class GoogleSheetAPIManager(GoogleAPIManager):
    """
    Manager for Google Sheets API operations.
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

    def get_sheet(self, spreadsheet_id=None):
        """Get spreadsheet metadata."""
        sheet_id = spreadsheet_id or self.spreadsheet_id
        if not sheet_id:
            raise ValueError("Spreadsheet ID must be provided")
        return self.sheet_service.spreadsheets().get(spreadsheetId=sheet_id).execute()

    def get_values(self, range_name, spreadsheet_id=None):
        """Get values from a range."""
        sheet_id = spreadsheet_id or self.spreadsheet_id
        if not sheet_id:
            raise ValueError("Spreadsheet ID must be provided")
        result = self.sheet_service.spreadsheets().values().get(
            spreadsheetId=sheet_id, range=range_name).execute()
        return result.get('values', [])

    def get_all_sheets(self, spreadsheet_id=None):
        """Get all sheet names in the spreadsheet."""
        metadata = self.get_sheet(spreadsheet_id)
        return [sheet['properties']['title'] for sheet in metadata.get('sheets', [])]

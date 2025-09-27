"""
Calendar management tool for scheduling events.
"""

import json
import pytz
from datetime import datetime, timedelta
from typing import Optional
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun


class CalendarTool(BaseTool):
    """LangChain tool for calendar operations."""
    
    name = "calendar_scheduler"
    description = "Schedule calendar events. Input should be JSON with title, date, and time."
    calendar_service: object = None
    
    def __init__(self, calendar_service):
        super().__init__()
        self.calendar_service = calendar_service
    
    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Schedule a calendar event."""
        try:
            # Parse the query as JSON
            params = json.loads(query) if query.startswith('{') else {'title': query}
            
            if not self.calendar_service:
                return "Google Calendar is not configured."
            
            ist = pytz.timezone('Asia/Kolkata')
            title = params.get('title', 'New Event')
            date_str = params.get('date', 'today')
            time_str = params.get('time', '10:00 AM')
            
            # Calculate event datetime
            if date_str == 'today':
                event_date = datetime.now(ist)
            elif date_str == 'tomorrow':
                event_date = datetime.now(ist) + timedelta(days=1)
            else:
                event_date = datetime.now(ist)
            
            # Parse time
            try:
                time_obj = datetime.strptime(time_str.upper(), '%I:%M %p').time()
                start_datetime = datetime.combine(event_date.date(), time_obj)
                end_datetime = start_datetime + timedelta(hours=1)
            except ValueError:
                start_datetime = event_date.replace(hour=10, minute=0, second=0, microsecond=0)
                end_datetime = start_datetime + timedelta(hours=1)
            
            # Create event
            event = {
                'summary': title,
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': 'Asia/Kolkata',
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': 'Asia/Kolkata',
                },
                'description': 'Event created by Jarvis AI Assistant',
            }
            
            event = self.calendar_service.events().insert(calendarId='primary', body=event).execute()
            return f"Successfully scheduled '{title}' for {start_datetime.strftime('%B %d at %I:%M %p')}"
            
        except Exception as e:
            return f"Error scheduling event: {str(e)}"
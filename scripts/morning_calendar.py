#!/usr/bin/env python3
"""
Morning Calendar Script
Fetches iCal calendar from URL and displays today's events
"""

import urllib.request
from datetime import datetime, date
import sys

def fetch_ical(url):
    """Fetch iCal content from URL"""
    try:
        with urllib.request.urlopen(url) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching calendar: {e}", file=sys.stderr)
        sys.exit(1)

def parse_ical_line(line):
    """Parse a single iCal line into key and value"""
    if ':' not in line:
        return None, None
    key, value = line.split(':', 1)
    return key, value

def parse_datetime(dt_string):
    """Parse iCal datetime string to datetime object"""
    # Remove TZID parameter if present
    if ';' in dt_string:
        dt_string = dt_string.split(':', 1)[1]

    # Handle different datetime formats
    dt_string = dt_string.strip()

    # Format: YYYYMMDDTHHMMSS or YYYYMMDDTHHMMSSZ
    if 'T' in dt_string:
        dt_string = dt_string.rstrip('Z')
        if len(dt_string) == 15:  # YYYYMMDDTHHMMSS
            return datetime.strptime(dt_string, '%Y%m%dT%H%M%S')
    # Format: YYYYMMDD (all-day event)
    elif len(dt_string) == 8:
        return datetime.strptime(dt_string, '%Y%m%d')

    return None

def parse_events(ical_content):
    """Parse iCal content and extract events"""
    events = []
    lines = ical_content.split('\n')

    in_event = False
    current_event = {}

    for line in lines:
        line = line.strip()

        if line == 'BEGIN:VEVENT':
            in_event = True
            current_event = {}
        elif line == 'END:VEVENT':
            in_event = False
            if current_event:
                events.append(current_event)
        elif in_event:
            key, value = parse_ical_line(line)
            if key is None:
                continue
            if key == 'SUMMARY':
                current_event['summary'] = value
            elif key.startswith('DTSTART'):
                current_event['start'] = parse_datetime(value)
            elif key.startswith('DTEND'):
                current_event['end'] = parse_datetime(value)

    return events

def format_time(dt):
    """Format datetime to HH:MM CET"""
    return dt.strftime('%H:%M')

def get_todays_events(events):
    """Filter events for today"""
    today = date.today()
    todays_events = []

    for event in events:
        if event.get('start') and event['start'].date() == today:
            todays_events.append(event)

    # Sort by start time
    todays_events.sort(key=lambda x: x['start'])

    return todays_events

def main():
    if len(sys.argv) < 2:
        print("Error: No iCal URL provided", file=sys.stderr)
        sys.exit(1)

    ical_url = sys.argv[1]

    # Fetch and parse calendar
    ical_content = fetch_ical(ical_url)
    events = parse_events(ical_content)
    todays_events = get_todays_events(events)

    if not todays_events:
        print("NOUPDATE")
        return

    # Print greeting and header
    today = datetime.now()
    day_name = today.strftime('%A')
    month_day = today.strftime('%b %d')

    print(f"Good morning Sandor!")
    print()
    print(f"📅Today's Schedule — {day_name}, {month_day}:")
    print()

    # Print events
    for event in todays_events:
        summary = event.get('summary', 'Untitled Event')
        start_time = format_time(event['start'])
        end_time = format_time(event['end']) if event.get('end') else '??:??'

        print(f"{summary} — {start_time}–{end_time}")

if __name__ == '__main__':
    main()

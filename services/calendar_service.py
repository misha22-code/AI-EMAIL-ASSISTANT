from datetime import datetime, timedelta


# ---------------- GET UPCOMING EVENTS ----------------
def get_upcoming_events(service):
    try:
        now = datetime.utcnow().isoformat() + "Z"

        events_result = service.events().list(
            calendarId="primary",
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        events = events_result.get("items", [])
        return events

    except Exception as e:
        print("Calendar Fetch Error:", e)
        return []


# ---------------- CREATE EVENT ----------------
def create_event(service, summary, description, start_time, end_time):
    try:
        # If no end_time provided, auto add +1 hour
        if not end_time:
            start_dt = datetime.fromisoformat(start_time)
            end_dt = start_dt + timedelta(hours=1)
            end_time = end_dt.isoformat()

        event = {
            "summary": summary or "Meeting",
            "description": description or "Created from AI Email Assistant",
            "start": {
                "dateTime": start_time,
                "timeZone": "UTC",
            },
            "end": {
                "dateTime": end_time,
                "timeZone": "UTC",
            },
        }

        created_event = service.events().insert(
            calendarId="primary",
            body=event
        ).execute()

        return created_event

    except Exception as e:
        print("Calendar Create Error:", e)
        return None
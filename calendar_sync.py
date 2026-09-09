import hashlib
import json
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def event_body(code, now=None):
    now = now or datetime.now(ZoneInfo("Asia/Seoul"))
    now = now.astimezone(ZoneInfo("Asia/Seoul"))
    monday = (now - timedelta(days=now.weekday())).date()
    # The date is stable for a review week, even if an Actions retry is delayed.
    start = datetime.combine(monday, datetime.min.time(), tzinfo=ZoneInfo("Asia/Seoul")).replace(hour=20)
    identity = hashlib.sha256(f"planx:{code}:{monday}".encode()).hexdigest()
    return {"id": identity, "summary": f"[PlanX] {code} 주간 투자 점검",
            "description": "저장된 투자일지에서 실적 변화·경쟁사·엣지 근거와 보유 조건을 확인하세요. 이 일정은 매수 신호가 아닙니다.",
            "start": {"dateTime": start.isoformat(), "timeZone": "Asia/Seoul"},
            "end": {"dateTime": (start + timedelta(minutes=15)).isoformat(), "timeZone": "Asia/Seoul"},
            "reminders": {"useDefault": False, "overrides": [{"method": "popup", "minutes": 10}]}}


def connect():
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    creds = service_account.Credentials.from_service_account_info(info,
        scopes=["https://www.googleapis.com/auth/calendar.events"])
    return build("calendar", "v3", credentials=creds, cache_discovery=False)


def upsert(service, calendar_id, body):
    from googleapiclient.errors import HttpError
    events = service.events()
    try:
        return events.insert(calendarId=calendar_id, body=body, sendUpdates="none").execute()
    except HttpError as error:
        if error.resp.status != 409:
            raise
        patch = {k: v for k, v in body.items() if k != "id"}
        return events.patch(calendarId=calendar_id, eventId=body["id"], body=patch, sendUpdates="none").execute()

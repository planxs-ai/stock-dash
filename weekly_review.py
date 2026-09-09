"""Run manually first. DRY_RUN defaults true and never writes DB or Calendar."""
import os
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from analysis import score
from calendar_sync import connect, event_body, upsert
from providers import Official, demo
from storage import Store


def run(store, provider, dry=True, service=None, calendar_id=None):
    state = store.read()
    failures, processed = 0, 0
    now = datetime.now(ZoneInfo("Asia/Seoul"))
    for stock in state["stocks"]:
        if not stock.get("review_enabled", False):
            continue
        try:
            report = provider.report(stock["code"], stock["year"])
            peers = [provider.report(code, stock["year"]) for code in stock.get("peers", [])]
            result = score(report, stock.get("assumptions"), stock.get("evidence"), peers)
            old = stock.get("report")
            changes = {"price_before": old.get("price") if old else None, "price_after": report["price"],
                       "profit_before": old["years"][-1]["profit"] if old else None,
                       "profit_after": report["years"][-1]["profit"]}
            body = event_body(stock["code"], now)
            if not dry:
                if report.get("sample"):
                    raise ValueError("Sample cannot be written")
                upsert(service, calendar_id, body)
                store.save_stock({"code": stock["code"], "report": report, "peer_reports": peers, "result": result,
                                  "last_success": now.isoformat(), "event_id": body["id"]})
                store.log("journal", {"code": stock["code"], "at": now.isoformat(), "kind": "weekly",
                                      "report": report, "result": result, "changes": changes, "event_id": body["id"]})
            processed += 1
        except Exception:
            # Never print raw provider exceptions: they can contain authentication URLs.
            failures += 1
    if not dry:
        store.log("runs", {"at": now.isoformat(), "processed": processed, "failed": failures})
    return {"processed": processed, "failed": failures, "dry_run": dry}


if __name__ == "__main__":
    load_dotenv()
    dry = os.getenv("DRY_RUN", "true").lower() != "false"
    try:
        store = Store()
        if not dry and not store.cloud:
            raise RuntimeError("Live runner requires cloud DB")
        provider = Official()
        service = None if dry else connect()
        calendar_id = os.getenv("GOOGLE_CALENDAR_ID")
        if not dry and not calendar_id:
            raise RuntimeError("Calendar id missing")
        result = run(store, provider, dry, service, calendar_id)
        print(result)
        raise SystemExit(1 if result["failed"] else 0)
    except Exception:
        print("예약 점검 실패: DB·공식 API·캘린더 권한 설정을 확인하세요. 인증값은 출력하지 않습니다.")
        raise SystemExit(1)

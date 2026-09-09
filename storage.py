"""Single-owner persistent state. Cloud writes use optimistic concurrency."""
import json
import os
from pathlib import Path

import requests
from filelock import FileLock


def empty():
    return {"stocks": [], "journal": [], "runs": []}


class Store:
    def __init__(self, path="data/state.json"):
        self.path = Path(path)
        self.url = os.getenv("SUPABASE_URL", "").rstrip("/")
        self.key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
        if bool(self.url) != bool(self.key):
            raise ValueError("클라우드 DB 주소와 키를 모두 설정하세요.")
        self.cloud = bool(self.url and self.key)
        if self.cloud and not self.url.startswith("https://"):
            raise ValueError("DB 주소는 HTTPS여야 합니다.")

    def request(self, method, **kwargs):
        try:
            response = requests.request(method, self.url + "/rest/v1/stock_dash_state",
                headers={"apikey": self.key, "Authorization": "Bearer " + self.key,
                         "Prefer": "return=representation"}, timeout=25, **kwargs)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError):
            raise RuntimeError("DB 연결 실패: 설정과 schema.sql 실행 여부를 확인하세요.") from None

    def read(self):
        if self.cloud:
            rows = self.request("GET", params={"id": "eq.personal", "select": "payload,version"})
            if not rows:
                raise RuntimeError("DB 초기 행이 없습니다. schema.sql을 실행하세요.")
            return rows[0]["payload"]
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with FileLock(str(self.path) + ".lock"):
            return json.loads(self.path.read_text()) if self.path.exists() else empty()

    def change(self, operation):
        if self.cloud:
            for _ in range(5):
                rows = self.request("GET", params={"id": "eq.personal", "select": "payload,version"})
                if not rows:
                    raise RuntimeError("schema.sql 초기화가 필요합니다.")
                row = rows[0]
                operation(row["payload"])
                updated = self.request("PATCH", params={"id": "eq.personal", "version": "eq." + str(row["version"])},
                    json={"payload": row["payload"], "version": row["version"] + 1})
                if updated:
                    return
            raise RuntimeError("다른 작업이 저장 중입니다. 잠시 후 다시 저장하세요.")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with FileLock(str(self.path) + ".lock"):
            data = json.loads(self.path.read_text()) if self.path.exists() else empty()
            operation(data)
            temp = self.path.with_suffix(".tmp")
            temp.write_text(json.dumps(data, ensure_ascii=False, allow_nan=False), encoding="utf-8")
            temp.replace(self.path)

    def save_stock(self, stock):
        def update(data):
            for index, old in enumerate(data["stocks"]):
                if old["code"] == stock["code"]:
                    data["stocks"][index] = {**old, **stock}
                    return
            data["stocks"].append(stock)
        self.change(update)

    def log(self, collection, item):
        def update(data):
            data[collection].append(item)
        self.change(update)

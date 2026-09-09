import io
import os
import zipfile
from datetime import date, timedelta
from xml.etree import ElementTree

import requests


class DataError(RuntimeError):
    pass


def get(url, params):
    try:
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        return r
    except requests.RequestException:
        raise DataError("공식 API 통신 실패. 키·활용승인·호출 한도를 확인하세요.") from None


def number(value):
    try:
        return int(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return None


class Official:
    def __init__(self):
        self.dart_key = os.getenv("DART_CRTFC_KEY", "")
        self.price_key = os.getenv("DATA_GO_KR_SERVICE_KEY", "")
        if not self.dart_key or not self.price_key:
            raise DataError("시세·DART 키가 모두 필요합니다.")
        self.corps = None

    def dart(self, endpoint, **params):
        try:
            payload = get("https://opendart.fss.or.kr/api/" + endpoint,
                          {"crtfc_key": self.dart_key, **params}).json()
        except ValueError:
            raise DataError("DART 응답 형식 오류") from None
        if payload.get("status") == "013":
            return None
        if payload.get("status") != "000":
            raise DataError("DART 조회 실패. 승인·연도·한도를 확인하세요.")
        return payload

    def corp(self, code):
        if self.corps is None:
            raw = get("https://opendart.fss.or.kr/api/corpCode.xml", {"crtfc_key": self.dart_key}).content
            try:
                with zipfile.ZipFile(io.BytesIO(raw)) as z:
                    root = ElementTree.fromstring(z.read("CORPCODE.xml"))
                self.corps = {(n.findtext("stock_code") or "").strip(): n.findtext("corp_code") for n in root.findall("list")}
            except (zipfile.BadZipFile, ElementTree.ParseError, KeyError):
                raise DataError("DART 기업 목록을 읽을 수 없습니다. 키 승인을 확인하세요.") from None
        if code not in self.corps:
            raise DataError("상장 종목코드를 찾지 못했습니다.")
        return self.corps[code]

    def price(self, code, asof):
        for days in range(10):
            target = (asof - timedelta(days=days)).strftime("%Y%m%d")
            try:
                payload = get("https://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService/getStockPriceInfo",
                    {"serviceKey": self.price_key, "resultType": "json", "numOfRows": 100,
                     "basDt": target, "likeSrtnCd": code}).json()
                response = payload["response"]
                if str(response["header"].get("resultCode")) not in ("00", "0"):
                    raise DataError("시세 API 승인·인증 오류")
                items = (response.get("body", {}).get("items") or {}).get("item", [])
                if isinstance(items, dict):
                    items = [items]
                for row in items:
                    if str(row.get("srtnCd", "")).removeprefix("A").zfill(6) == code:
                        price = number(row.get("clpr"))
                        if price is not None and price > 0:
                            return price, row["basDt"], row["itmsNm"]
            except (ValueError, KeyError, TypeError):
                raise DataError("시세 응답 형식 오류") from None
        raise DataError("최근 10일 안에 시세가 없습니다.")

    def annual(self, corp, year, basis):
        result = self.dart("fnlttSinglAcntAll.json", corp_code=corp, bsns_year=str(year), reprt_code="11011", fs_div=basis)
        if not result:
            return None
        rows = result.get("list", [])
        def account(ids, names):
            for row in rows:
                if row.get("sj_div") not in ("IS", "CIS"):
                    continue
                if row.get("account_id") in ids or row.get("account_nm") in names:
                    raw = number(row.get("thstrm_amount"))
                    if raw is not None:
                        return raw / 100_000_000
            return None
        receipt = next((r.get("rcept_no") for r in rows if r.get("rcept_no")), "")
        return {"year": year, "revenue": account(["ifrs-full_Revenue"], ["매출액", "수익(매출액)"]),
                "profit": account(["dart_OperatingIncomeLoss"], ["영업이익", "영업이익(손실)"]),
                "url": "https://dart.fss.or.kr/dsaf001/main.do?rcpNo=" + receipt}

    def report(self, code, year, asof=None):
        asof = asof or date.today()
        corp = self.corp(code)
        price, price_date, name = self.price(code, asof)
        annuals = None
        for basis in ("CFS", "OFS"):
            series = [self.annual(corp, y, basis) for y in range(year - 2, year + 1)]
            if all(series):
                annuals = series
                break
        if annuals is None:
            raise DataError("동일 연결/별도 기준의 3개년 보고서가 부족합니다. 사업연도를 바꿔보세요.")
        disclosures = self.dart("list.json", corp_code=corp,
            bgn_de=(asof - timedelta(days=90)).strftime("%Y%m%d"), end_de=asof.strftime("%Y%m%d"), page_count=20)
        return {"code": code, "name": name, "price": price, "price_date": price_date,
                "basis": basis, "years": annuals, "fetched": asof.isoformat(), "sample": False,
                "disclosures": [{"title": r["report_nm"], "date": r["rcept_dt"],
                    "url": "https://dart.fss.or.kr/dsaf001/main.do?rcpNo=" + r["rcept_no"]} for r in (disclosures or {}).get("list", [])]}


def demo():
    return {"code": "SAMPLE", "name": "가상 반도체", "price": 52000, "price_date": "가상",
            "basis": "CFS", "sample": True, "fetched": "가상 예시", "disclosures": [],
            "years": [{"year": 2023, "revenue": 10000, "profit": 1100, "url": ""},
                      {"year": 2024, "revenue": 12500, "profit": 1600, "url": ""},
                      {"year": 2025, "revenue": 15000, "profit": 2100, "url": ""}]}

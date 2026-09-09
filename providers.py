import io
import os
import re
import html
import zipfile
from datetime import date, timedelta
from xml.etree import ElementTree
from urllib.parse import unquote, urlsplit

import requests


class DataError(RuntimeError):
    pass


DART_ERRORS = {
    "010": "등록되지 않은 DART 키입니다. DART_CRTFC_KEY 값을 확인하세요.",
    "011": "DART 키가 사용 중지 상태입니다. 인증키 관리에서 상태를 확인하세요.",
    "012": "DART가 접속 IP를 허용하지 않았습니다. 인증키의 IP 제한과 앱 서버 IP를 확인하세요.",
    "020": "DART 호출 한도를 초과했습니다. 추가 조회를 멈추고 한도를 확인하세요.",
    "100": "DART 요청 항목이 올바르지 않습니다.",
    "800": "DART 시스템 점검 중입니다. 잠시 후 다시 시도하세요.",
    "901": "DART 계정의 개인정보 보유기간이 만료됐습니다. DART에서 계정을 확인하세요.",
}


def dart_error(code):
    return DART_ERRORS.get(str(code), "DART가 정상 데이터를 반환하지 않았습니다. 승인 상태와 조회 조건을 확인하세요.")


def get(url, params):
    path = urlsplit(url).path
    labels = {"corpCode.xml": "DART 기업명·종목코드 목록", "document.xml": "DART 사업보고서 원문",
              "company.json": "DART 기업개황", "fnlttSinglAcntAll.json": "DART 결산 실적", "list.json": "DART 공시 목록"}
    label = labels.get(path.rsplit("/",1)[-1], "공공데이터포털 주식시세")
    for attempt in range(2):
        try:
            r = requests.get(url, params=params, timeout=(10,60) if path.endswith(("corpCode.xml","document.xml")) else (10,30))
            if r.status_code in (502,503,504) and attempt == 0:
                continue
            status = r.status_code
            if status >= 400:
                if status in (401,403):
                    hint = "접근이 거절됐습니다. 해당 서비스의 키·활용승인·IP 제한을 확인하세요."
                elif status == 429:
                    hint = "요청 제한에 걸렸습니다. 잠시 조회를 멈춘 뒤 다시 시도하세요."
                elif status >= 500:
                    hint = "제공 서버 오류입니다. 키를 바꾸지 말고 잠시 후 다시 시도하세요."
                else:
                    hint = "요청을 처리하지 못했습니다. 해당 API의 주소와 설정을 확인하세요."
                raise DataError(f"{label} · HTTP {status}: {hint}")
            # Error responses can be XML even when JSON or a ZIP was requested.
            if r.content.lstrip().startswith(b"<") and len(r.content) < 10000:
                try:
                    root = ElementTree.fromstring(r.content)
                    code = root.findtext(".//status")
                    if code and code != "000":
                        raise DataError(label+": "+dart_error(code))
                    reason = root.findtext(".//returnReasonCode")
                    if reason:
                        hints = {"30":"등록되지 않은 시세 키입니다. 일반 인증키와 활용신청을 확인하세요.",
                                 "31":"시세 키 사용기간을 확인하세요.","32":"허용되지 않은 IP입니다.",
                                 "22":"시세 조회 한도를 초과했습니다.","20":"요청한 서비스 접근이 거절됐습니다."}
                        raise DataError(label+": "+hints.get(reason,"서비스가 오류를 반환했습니다. 시세 활용승인과 인증키를 확인하세요."))
                except ElementTree.ParseError:
                    pass
            return r
        except requests.Timeout:
            if attempt == 0:
                continue
            raise DataError(label+": 응답 시간이 초과됐습니다. 한 차례 재시도했으며, 키 오류로 확정할 수 없습니다.") from None
        except requests.exceptions.SSLError:
            raise DataError(label+": 보안 연결(TLS)에 실패했습니다. 서버 연결 환경을 확인하세요.") from None
        except requests.ConnectionError:
            if attempt == 0:
                continue
            raise DataError(label+": 서버에 연결하지 못했습니다. 네트워크·DNS·제공 서버 상태를 확인하세요.") from None
        except requests.RequestException:
            raise DataError(label+": 요청 전송에 실패했습니다. 서버 연결 환경을 확인하세요.") from None


def number(value):
    try:
        return int(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return None


class Official:
    def __init__(self):
        self.dart_key = os.getenv("DART_CRTFC_KEY", "").strip()
        self.price_key = unquote(os.getenv("DATA_GO_KR_SERVICE_KEY", "").strip())
        if not self.dart_key or not self.price_key:
            raise DataError("시세·DART 키가 모두 필요합니다.")
        self.corps = None
        self.names = {}
        self.price_rows = {}
        self.annual_cache = {}

    def dart(self, endpoint, **params):
        try:
            payload = get("https://opendart.fss.or.kr/api/" + endpoint,
                          {"crtfc_key": self.dart_key, **params}).json()
        except ValueError:
            raise DataError("DART 응답 형식 오류") from None
        if payload.get("status") == "013":
            return None
        if payload.get("status") != "000":
            raise DataError(dart_error(payload.get("status")))
        return payload

    def corp(self, code):
        if self.corps is None:
            raw = get("https://opendart.fss.or.kr/api/corpCode.xml", {"crtfc_key": self.dart_key}).content
            try:
                with zipfile.ZipFile(io.BytesIO(raw)) as z:
                    root = ElementTree.fromstring(z.read("CORPCODE.xml"))
                self.corps = {(n.findtext("stock_code") or "").strip(): n.findtext("corp_code") for n in root.findall("list")}
                self.names = {(n.findtext("stock_code") or "").strip(): n.findtext("corp_name") for n in root.findall("list") if (n.findtext("stock_code") or "").strip()}
            except (zipfile.BadZipFile, ElementTree.ParseError, KeyError):
                raise DataError("DART 기업 목록을 읽을 수 없습니다. 키 승인을 확인하세요.") from None
        if code not in self.corps:
            raise DataError("상장 종목코드를 찾지 못했습니다.")
        return self.corps[code]

    def search(self, query):
        if self.corps is None:
            return self.search_prices(query)
        # Load the same official directory used to resolve financial statements.
        if self.corps is None:
            try:
                self.corp("__load__")
            except DataError:
                if self.corps is None:
                    raise
        q = re.sub(r"\s+", "", query).casefold()
        if not q:
            return []
        matches = [{"code": c, "name": n} for c, n in self.names.items()
                   if q in re.sub(r"\s+", "", n).casefold() or q == c]
        exact = [r for r in matches if q in (r["code"], re.sub(r"\s+", "", r["name"]).casefold())]
        return exact or matches[:30]

    def search_prices(self, query):
        """Search the smaller price response without downloading DART's directory."""
        q = query.strip()
        if not q:
            return []
        numeric = len(q) == 6 and q.isascii() and q.isdigit()
        params = {"serviceKey": self.price_key, "resultType": "json", "numOfRows": 100,
                  "likeSrtnCd" if numeric else "likeItmsNm": q}
        for days in range(10):
            target = (date.today()-timedelta(days=days)).strftime("%Y%m%d")
            try:
                response = get("https://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService/getStockPriceInfo", {**params,"basDt":target}).json()["response"]
                if str(response["header"].get("resultCode")) not in ("00","0"):
                    raise DataError("공공데이터포털 종목 검색: 시세 서비스 승인과 인증키를 확인하세요.")
                items = (response.get("body",{}).get("items") or {}).get("item",[])
                if isinstance(items,dict):
                    items=[items]
                matches={}
                for row in items:
                    code=str(row.get("srtnCd","")).removeprefix("A")
                    if len(code)==6 and code.isdigit():
                        matches[code]={"code":code,"name":row["itmsNm"]}
                if matches:
                    exact=[r for r in matches.values() if r["name"].casefold()==q.casefold() or r["code"]==q]
                    return exact or list(matches.values())[:30]
            except (ValueError,KeyError,TypeError):
                raise DataError("공공데이터포털 종목 검색 응답을 읽지 못했습니다.") from None
        return []

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
                            self.price_rows[(code, asof.isoformat())] = row
                            return price, row["basDt"], row["itmsNm"]
            except (ValueError, KeyError, TypeError):
                raise DataError("시세 응답 형식 오류") from None
        raise DataError("최근 10일 안에 시세가 없습니다.")

    def annual(self, corp, year, basis):
        cache_key = (corp, year, basis)
        if cache_key in self.annual_cache:
            return self.annual_cache[cache_key]
        result = self.dart("fnlttSinglAcntAll.json", corp_code=corp, bsns_year=str(year), reprt_code="11011", fs_div=basis)
        if not result:
            self.annual_cache[cache_key] = None
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
        value = {"year": year, "revenue": account(["ifrs-full_Revenue"], ["매출액", "수익(매출액)"]),
                "profit": account(["dart_OperatingIncomeLoss"], ["영업이익", "영업이익(손실)"]),
                "receipt": receipt,
                "net_income": account(["ifrs-full_ProfitLossAttributableToOwnersOfParent"] if basis == "CFS" else ["ifrs-full_ProfitLoss"],
                    ["지배기업의 소유주에게 귀속되는 당기순이익(손실)"] if basis == "CFS" else ["당기순이익", "당기순이익(손실)"]),
                "url": "https://dart.fss.or.kr/dsaf001/main.do?rcpNo=" + receipt}
        self.annual_cache[cache_key] = value
        return value

    def business_excerpt(self, receipt):
        if not receipt:
            return ""
        raw = get("https://opendart.fss.or.kr/api/document.xml", {"crtfc_key": self.dart_key, "rcept_no": receipt}).content
        try:
            with zipfile.ZipFile(io.BytesIO(raw)) as z:
                files = [f for f in z.infolist() if f.filename.lower().endswith('.xml') and f.file_size < 30_000_000]
                if not files:
                    return ""
                document = z.read(max(files, key=lambda f: f.file_size))
                encoding = "euc-kr" if b'euc-kr' in document[:200].lower() else "utf-8"
                text = document.decode(encoding, errors="replace")
            text = html.unescape(re.sub(r"<[^>]+>", " ", text))
            text = re.sub(r"\s+", " ", text)
            # A bounded source excerpt, not a generated business claim.
            match = re.search(r"(?:II\.?\s*사업의 내용|1\.?\s*사업의 개요|주요 제품 및 서비스)", text)
            return text[match.start():match.start()+14000] if match else ""
        except (zipfile.BadZipFile, KeyError):
            return ""

    def automatic(self, code):
        asof = date.today()
        corp = self.corp(code)
        latest = None
        for year in range(asof.year-1, asof.year-4, -1):
            for basis in ("CFS", "OFS"):
                if self.annual(corp, year, basis):
                    latest = year
                    break
            if latest:
                break
        if latest is None:
            raise DataError("최근 결산 보고서를 찾지 못했습니다.")
        report = self.report(code, latest, asof)
        row = self.price_rows.get((code, asof.isoformat()), {})
        report["shares"] = number(row.get("lstgStCnt"))
        report["market_cap"] = number(row.get("mrktTotAmt"))
        report["warnings"] = []
        try:
            info = self.dart("company.json", corp_code=corp) or {}
            report["company"] = {k: info.get(k, "") for k in ["corp_name", "induty_code", "hm_url", "est_dt", "acc_mt"]}
        except DataError:
            report["company"] = {}
            report["warnings"].append("기업개황 조회 실패")
        report["anchors"] = []
        for yr in report["years"][:-1]:
            if not yr.get("receipt") or not yr.get("profit") or yr["profit"] <= 0:
                continue
            try:
                published = date.fromisoformat(f'{yr["receipt"][:4]}-{yr["receipt"][4:6]}-{yr["receipt"][6:8]}')
                reference = published + timedelta(days=7)
                if reference > asof:
                    continue
                p, day, _ = self.price(code, reference)
                if day < published.strftime("%Y%m%d"):
                    continue
                hist = self.price_rows.get((code, reference.isoformat()), {})
                cap = number(hist.get("mrktTotAmt"))
                if cap and cap > 0:
                    report["anchors"].append({"year": yr["year"], "price_date": day, "price": p,
                        "profit": yr["profit"], "market_cap": cap, "multiple": cap / (yr["profit"]*1e8)})
            except (DataError, ValueError):
                pass
        try:
            report["business_excerpt"] = self.business_excerpt(report["years"][-1].get("receipt"))
        except DataError:
            report["business_excerpt"] = ""
        if not report["business_excerpt"]:
            report["warnings"].append("사업 원문을 자동 추출하지 못했습니다. 공시 링크에서 확인하세요.")
        return report

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
            "shares": 30_000_000, "market_cap": 1_560_000_000_000,
            "company": {"corp_name": "가상 반도체 · 실존 기업 아님", "induty_code": "가상"},
            "business_excerpt": "가상 교육 예시: 반도체 메모리와 검사 부품을 만드는 기업을 가정합니다. 아래 수치와 과거 배수는 모두 가상이며 실제 투자 분석이 아닙니다.",
            "anchors": [{"year":2023,"price_date":"가상","multiple":8}, {"year":2024,"price_date":"가상","multiple":10}],
            "years": [{"year": 2023, "revenue": 10000, "profit": 1100, "url": ""},
                      {"year": 2024, "revenue": 12500, "profit": 1600, "url": ""},
                      {"year": 2025, "revenue": 15000, "profit": 2100, "url": ""}]}

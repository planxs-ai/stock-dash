import hmac
import os
from datetime import date, datetime
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from analysis import AXES, EDGE, score
from providers import Official, demo
from storage import Store

load_dotenv()
st.set_page_config(page_title="PlanX · 내 관심종목", page_icon="📊", layout="wide")
# Streamlit root-level secrets become env vars, but explicit loading is clearer.
try:
    for key in ["APP_PASSWORD", "SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY", "DATA_GO_KR_SERVICE_KEY", "DART_CRTFC_KEY"]:
        if key in st.secrets:
            os.environ[key] = str(st.secrets[key])
except FileNotFoundError:
    pass

st.title("내 관심종목 퀀트 보드")
st.caption("내 종목의 사업과 실적을 확인하고, 판단 기준을 기록합니다.")
st.markdown("<style>.stMetric{border:1px solid #e7d9c4;padding:16px;border-radius:14px}h1,h2,h3{letter-spacing:-.03em}</style>", unsafe_allow_html=True)

password = os.getenv("APP_PASSWORD", "")
if password and not st.session_state.get("authorized"):
    with st.form("login"):
        entered = st.text_input("나의 대시보드 비밀번호", type="password")
        if st.form_submit_button("열기"):
            if hmac.compare_digest(entered.encode(), password.encode()):
                st.session_state.authorized = True
                st.rerun()
            else:
                st.error("비밀번호를 확인하세요.")
    st.stop()

class SessionStore:
    """Explicit opt-in practice storage, isolated to this browser session."""
    cloud = False

    def read(self):
        return st.session_state.setdefault("practice_data", {"stocks": [], "journal": [], "runs": []})

    def save_stock(self, stock):
        data = self.read()
        for index, old in enumerate(data["stocks"]):
            if old["code"] == stock["code"]:
                data["stocks"][index] = {**old, **stock}
                return
        data["stocks"].append(stock)

    def log(self, collection, item):
        self.read()[collection].append(item)


sample_mode = not password
try:
    if sample_mode or st.session_state.get("practice_mode"):
        store = SessionStore()
    else:
        store = Store()
    state = {"stocks": [], "journal": [], "runs": []} if sample_mode else store.read()
except Exception:
    st.error("비밀번호 확인은 통과했지만, 종목 저장 공간을 열지 못했습니다.")
    url_set = bool(os.getenv("SUPABASE_URL", "").strip())
    key_set = bool(os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip())
    if url_set != key_set:
        st.info("Supabase 주소와 키 중 하나만 설정되어 있습니다. DB를 사용하지 않으려면 Secrets에서 SUPABASE_URL과 SUPABASE_SERVICE_ROLE_KEY 두 항목을 모두 지우고 앱을 재시작하세요.")
    elif url_set:
        st.info("Supabase 설정이 감지됐습니다. 프로젝트 주소·서버 키·schema.sql 실행 여부를 확인하세요. DB를 사용하지 않으려면 두 Supabase 항목을 모두 지우고 앱을 재시작하세요.")
    else:
        st.info("앱이 실행되는 서버의 저장 파일을 열지 못했습니다. 기존 데이터는 덮어쓰지 않았습니다. 아래 버튼으로 별도의 임시 실습을 시작할 수 있습니다.")
    st.caption("임시 실습은 현재 접속에서만 유지됩니다. 새로고침·로그아웃 시 사라질 수 있으며 기존 저장 자료와 합쳐지지 않습니다.")
    if st.button("저장 연결 없이 임시 실습 시작", type="primary"):
        st.session_state.practice_mode = True
        st.rerun()
    st.stop()

if sample_mode:
    st.info("가상 데이터로 둘러보기 · APP_PASSWORD 설정 후 개인 종목 저장과 실데이터 조회가 열립니다.")
elif st.session_state.get("practice_mode"):
    st.warning("임시 실습 · 현재 접속에서만 저장됩니다. 중요한 판단은 개인 문서에 복사해 두세요.")
else:
    st.caption("클라우드 저장 · 다른 기기에서도 이어 사용" if store.cloud else "실행 서버에 저장 · 웹 호스팅 재시작 시 사라질 수 있습니다.")

with st.sidebar:
    st.header("내 종목 보관함")
    if not sample_mode:
        with st.form("add"):
            name = st.text_input("종목명")
            code = st.text_input("종목코드 6자리", max_chars=6)
            kind = st.selectbox("구분", ["관심", "보유"])
            reason = st.text_area("관심을 가진 이유")
            if st.form_submit_button("종목 저장"):
                if name.strip() and len(code) == 6 and code.isascii() and code.isdigit():
                    try:
                        store.save_stock({"name": name.strip(), "code": code, "kind": kind, "reason": reason,
                                          "year": date.today().year - 1})
                        st.rerun()
                    except Exception:
                        st.error("저장 실패. 입력 내용을 보관한 뒤 다시 시도하세요.")
                else:
                    st.error("종목명과 숫자 6자리 코드를 확인하세요.")
    choices = {s["code"]: s for s in state["stocks"]}
    if choices:
        selected = st.selectbox("저장된 종목", list(choices), format_func=lambda c: f"{choices[c]['kind']} · {choices[c]['name']}")
        stock = choices[selected]
    else:
        stock = {"code": "SAMPLE", "name": "가상 반도체", "year": 2025}
    if password and st.button("로그아웃"):
        st.session_state.clear()
        st.rerun()

is_demo = stock["code"] == "SAMPLE"
report = demo() if is_demo else stock.get("report")
st.subheader(stock["name"])
overview, journal, automation = st.tabs(["분석·비교", "투자일지", "자동 점검"])

with overview:
    if not is_demo:
        with st.form("query"):
            year = st.number_input("비교 기준 사업연도 · 결산 3개년", 2015, date.today().year - 1, stock.get("year", date.today().year - 1))
            peers_text = st.text_input("같은 업종 경쟁사 코드 · 최대 3개, 쉼표 구분", ",".join(stock.get("peers", [])))
            if st.form_submit_button("공식 데이터 분석"):
                peers = list(dict.fromkeys(c.strip() for c in peers_text.split(",") if c.strip()))
                if len(peers) > 3 or any(len(c) != 6 or not c.isascii() or not c.isdigit() or c == stock["code"] for c in peers):
                    st.error("본인을 제외한 종목코드 6자리, 최대 3개를 입력하세요.")
                else:
                    try:
                        with st.spinner("시세와 공시를 확인합니다…"):
                            provider = Official()
                            r = provider.report(stock["code"], year)
                            peer_reports = [provider.report(c, year) for c in peers]
                            result = score(r, stock.get("assumptions"), stock.get("evidence"), peer_reports)
                            store.save_stock({"code": stock["code"], "year": year, "peers": peers,
                                              "report": r, "peer_reports": peer_reports, "result": result})
                            store.log("journal", {"code": stock["code"], "at": datetime.now(ZoneInfo("Asia/Seoul")).isoformat(),
                                                  "kind": "analysis", "report": r, "result": result})
                        st.rerun()
                    except Exception:
                        st.error("분석을 완료하지 못했습니다. 키·기준연도·경쟁사 보고서를 확인하세요. 이전 결과는 유지됩니다.")
    if report:
        st.caption(f"시세 기준일 {report['price_date']} · 재무 {report['basis']} · 단위 억원 · 조회일 {report['fetched']}")
        if report.get("sample"):
            st.warning("이 종목과 숫자는 가상 예시입니다.")
        last = report["years"][-1]
        for col, label, value in zip(st.columns(3), ["기준 종가 · 원", "결산 매출 · 억원", "결산 영업이익 · 억원"], [report["price"], last["revenue"], last["profit"]]):
            col.metric(label, f"{value:,.0f}" if value is not None else "자료 없음")
        st.subheader("결산 실적 추이")
        chart = pd.DataFrame(report["years"])[["year", "revenue", "profit"]].rename(columns={"year": "연도", "revenue": "매출", "profit": "영업이익"})
        chart["연도"] = chart["연도"].astype(str)
        st.bar_chart(chart.set_index("연도"), color=["#b8872e", "#65866f"])
        st.caption("연간 결산 실적입니다. 분기 실적이나 올해 전망으로 해석하지 않습니다.")
        for row in report["years"]:
            if row["url"]:
                st.link_button(f"{row['year']} 공시 원문", row["url"])
        st.subheader("경쟁사 비교")
        peers = stock.get("peer_reports", [])
        if peers:
            rows = []
            for r in [report, *peers]:
                metrics = score(r)
                rows.append({"기업": r["name"], "연결/별도": r["basis"], "결산연도": r["years"][-1]["year"],
                             "매출성장률 %": metrics["revenue_growth"], "영업이익률 %": metrics["margin"]})
            st.dataframe(rows, hide_index=True)
        else:
            st.info("경쟁사 2개 이상을 지정하면 동일 결산연도·연결/별도 기준으로 경쟁력 점수를 계산합니다.")
        assumptions = stock.get("assumptions")
        with st.form("value"):
            st.subheader("적정주가 · 내가 정하는 가정")
            defaults = assumptions or {"profit": max(last["profit"] or 1, 1), "multiple": 7., "debt": 0., "shares": 100.}
            fields = [("profit", "예상 연간 영업이익 · 억원"), ("multiple", "EV/영업이익 배수"), ("debt", "순차입금 · 억원, 순현금은 음수"), ("shares", "희석 반영 주식수 · 백만주")]
            draft = {key: st.number_input(label, value=float(defaults[key])) for key, label in fields}
            confirmed = st.checkbox("예상치·배수·순차입금·주식수의 단위와 근거를 확인했습니다.")
            if st.form_submit_button("가정으로 계산·저장", disabled=is_demo):
                if confirmed and min(draft["profit"], draft["multiple"], draft["shares"]) > 0:
                    try:
                        store.save_stock({"code": stock["code"], "assumptions": draft})
                        st.rerun()
                    except Exception:
                        st.error("가정 저장 실패. 다시 시도하세요.")
                else:
                    st.error("이익·배수·주식수는 양수여야 하며 근거 확인이 필요합니다.")
        results = score(report, assumptions, stock.get("evidence"), peers)
        if results["valuation"]:
            v = results["valuation"]
            for col, key in zip(st.columns(3), ["Bear", "Base", "Bull"]):
                col.metric(key, f"{v[key]:,.0f}원")
            st.caption("(예상 영업이익 × EV/영업이익 배수 − 순차입금) ÷ 주식수. 금융업·복수 주식종류 기업에는 별도 모델이 필요합니다.")
        for col, axis in zip(st.columns(5), AXES):
            value = results["scores"][axis]
            col.metric(axis, f"{value}/20" if value is not None else "보류")
        st.write(f"종합 {results['total']}/100" if results["total"] is not None else "미확인 항목이 있어 종합 점수는 보류합니다.")
    else:
        st.info("저장한 종목의 ‘공식 데이터 분석’을 눌러 주세요. 연결 전에는 숫자를 만들지 않습니다.")

    if not is_demo:
        st.subheader("주요 사업과 엣지 근거")
        st.caption("AI가 임의로 점수를 부여하지 않습니다. 공시 원문을 읽고 근거를 기록하세요.")
        with st.form("evidence"):
            business = st.text_area("주요 사업 · 공시에서 확인한 내용", stock.get("business", ""))
            evidence = {}
            for axis in EDGE:
                old = stock.get("evidence", {}).get(axis, {})
                with st.expander(axis):
                    reviewed = st.checkbox("이 항목 검토 완료", old.get("reviewed", False), key=axis+"reviewed")
                    checked = st.checkbox("원문에서 근거 확인", old.get("checked", False), key=axis+"checked")
                    url = st.text_input("DART 공시 링크", old.get("url", ""), key=axis+"url")
                    excerpt = st.text_area("근거 문장", old.get("excerpt", ""), key=axis+"text")
                    evidence[axis] = {"reviewed": reviewed, "checked": checked, "url": url, "excerpt": excerpt, "date": date.today().isoformat()}
            if st.form_submit_button("사업·근거 저장"):
                try:
                    store.save_stock({"code": stock["code"], "business": business, "evidence": evidence})
                    st.rerun()
                except Exception:
                    st.error("저장 실패. 입력 내용을 확인한 뒤 다시 시도하세요.")
        if report:
            for item in report.get("disclosures", []):
                st.link_button(f"{item['date']} · {item['title']}", item["url"])

with journal:
    if not is_demo:
        with st.form("note"):
            note = st.text_area("오늘의 판단 · 보유 이유와 재검토 조건")
            if st.form_submit_button("일지 기록") and note.strip():
                try:
                    store.log("journal", {"code": stock["code"], "at": datetime.now(ZoneInfo("Asia/Seoul")).isoformat(), "kind": "note", "note": note})
                    st.rerun()
                except Exception:
                    st.error("기록 실패. 내용을 복사해 보관하고 다시 시도하세요.")
        for item in reversed(state["journal"]):
            if item["code"] == stock["code"]:
                with st.expander(item["at"] + " · " + item["kind"]):
                    st.json(item)
    else:
        st.info("개인 종목을 저장하면 분석 이력과 나의 판단을 기록할 수 있습니다.")

with automation:
    st.write("매주 월요일 오전 8시 17분 예약 점검 → 같은 날 오후 8시 달력 점검 일정")
    st.caption("GitHub Actions 설정은 README를 따릅니다. 예약 실행은 지연될 수 있습니다.")
    if not is_demo:
        st.write("마지막 성공:", stock.get("last_success", "아직 없음"))
        with st.form("review"):
            enabled = st.checkbox("이 종목을 주간 점검에 포함", stock.get("review_enabled", False))
            if st.form_submit_button("점검 설정 저장"):
                try:
                    store.save_stock({"code": stock["code"], "review_enabled": enabled})
                    st.rerun()
                except Exception:
                    st.error("설정 저장 실패")
    st.info("캘린더 쓰기는 기본 비활성입니다. 수동 미리보기 후 Actions에서 기록 모드를 직접 선택하세요.")
    if state["runs"]:
        st.dataframe(state["runs"][-20:], hide_index=True)

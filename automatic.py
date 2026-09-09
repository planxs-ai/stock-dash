"""Source-based automatic brief; valuation is historical equity/OP repricing."""
from statistics import median
from analysis import growth, margin, bound


SECTORS = [
    ("반도체", ("반도체", "메모리", "웨이퍼"), ["제품 가격·재고", "고객사 설비투자", "수율·가동률"], "가격·출하 증가가 매출을, 가동률 상승이 이익률을 개선하는지 확인합니다."),
    ("전력기기", ("변압기", "배전반", "전력기기"), ["수주잔고", "납기·증설", "원자재와 계약 가격"], "수주가 실제 매출로 전환되는 시점과 원가 상승을 가격에 반영하는지 확인합니다."),
    ("배터리", ("이차전지", "양극재", "배터리"), ["EV·ESS 매출 구분", "재고·가동률", "소재 가격"], "수요 회복이 판매량과 가동률 개선으로 연결되는지 확인합니다."),
    ("로봇", ("로봇", "감속기", "액추에이터"), ["유상 납품", "반복 주문", "고객사 양산 채택"], "개발 협약과 실제 매출이 발생하는 공급계약을 구분합니다."),
    ("조선", ("선박", "조선업", "조선사업"), ["선가", "수주잔고·인도", "강재·인건비"], "과거 수주한 선박이 현재 원가 조건에서 이익을 남기는지 확인합니다."),
    ("방산", ("방위산업", "방산", "방산부문"), ["확정 계약", "수출 인도 일정", "현지 생산 조건"], "계약 총액과 실제 매출 인식·현금 유입 시점을 구분합니다."),
    ("바이오·제약", ("의약품", "임상시험", "바이오"), ["제품 매출", "연구개발 비용", "계약금과 조건부 금액"], "반복 제품 매출과 일회성 기술료 수익을 분리합니다."),
    ("소프트웨어", ("소프트웨어", "클라우드", "SaaS"), ["유료 고객", "반복 매출", "판매·개발 비용"], "사용자 증가가 반복 매출과 영업이익 증가로 이어지는지 확인합니다."),
]


def sector_brief(report):
    text = report.get("business_excerpt", "")
    found = []
    for label, words, signals, logic in SECTORS:
        hits = [w for w in words if w in text]
        if hits:
            found.append({"sector": label, "keywords": hits, "signals": signals, "logic": logic})
    return found


def brief(report):
    last, prev = report["years"][-1], report["years"][-2]
    rg, pg, opm = growth(last["revenue"], prev["revenue"]), growth(last["profit"], prev["profit"]), margin(last)
    anchors = report.get("anchors", [])
    positive = [a["multiple"] for a in anchors if 0 < a["multiple"] < float('inf')]
    shares = report.get("shares")
    financial = str(report.get("company", {}).get("induty_code", ""))[:2] in {"64", "65", "66"}
    fair = None
    reason = "비교 가능한 과거 흑자 결산·시가총액 자료가 2개 필요합니다."
    if financial:
        reason = "금융업은 영업이익 배수 대신 업종별 평가 모형이 필요합니다."
    elif not shares or not last.get("profit") or last["profit"] <= 0:
        reason = "양수의 최근 결산 영업이익과 현재 상장주식수가 필요합니다."
    elif len(positive) >= 2:
        prices = [m * last["profit"] * 1e8 / shares for m in positive]
        base = median(prices)
        fair = {"low": min(prices), "base": base, "high": max(prices),
                "gap": (base/report["price"]-1)*100, "multiple": median(positive)}
        reason = "과거 결산 발표 이후 시가총액/영업이익 배수를 최근 결산 이익에 적용한 참고 가격입니다."
    growth_score = None if rg is None or pg is None else round((bound((rg+10)/4,10)+bound((pg+20)/7,10))*1.5,1)
    profit_score = None if opm is None else bound(opm/25*30,30)
    value_score = None if fair is None else bound(20+fair["gap"]/2,40)
    scores = {"성장": growth_score, "수익성": profit_score, "가치": value_score}
    total = round(sum(scores.values()),1) if all(x is not None for x in scores.values()) else None
    if last.get("profit") is not None and prev.get("profit") is not None and prev["profit"] <= 0 < last["profit"]:
        growth_label = "흑자 전환"
    elif last.get("profit") is not None and last["profit"] < 0:
        growth_label = "적자 · 회복 확인"
    elif rg is not None and pg is not None:
        growth_label = "매출·이익 동반 성장" if rg > 0 and pg > 0 else "실적 변화 점검"
    else:
        growth_label = "자료 확인 필요"
    value_label = "평가 보류" if fair is None else ("참고가 대비 낮음" if fair["gap"] > 0 else "참고가 대비 높음")
    sentences = [growth_label + "."]
    if rg is not None:
        sentences.append(f"{last['year']}년 결산 매출은 전년 대비 {rg:+.1f}% 변했습니다.")
    if pg is not None:
        sentences.append(f"영업이익은 {pg:+.1f}% 변했습니다.")
    if opm is not None:
        sentences.append(f"영업이익률은 {opm:.1f}%입니다.")
    if fair:
        sentences.append(f"현재가는 역사적 배수 참고가와 {fair['gap']:+.1f}% 차이가 있습니다. 저평가 확정이나 매수 신호는 아닙니다.")
    cap, net = report.get("market_cap"), last.get("net_income")
    per = cap / (net*1e8) if cap and net and net > 0 else None
    return {"growth": growth_label, "value": value_label, "fair": fair, "fair_reason": reason,
            "scores": scores, "total": total, "summary": " ".join(sentences), "revenue_growth": rg,
            "profit_growth": pg, "margin": opm, "per": per, "sectors": sector_brief(report)}

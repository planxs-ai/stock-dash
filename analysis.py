"""Transparent teaching scores. No rating is investment advice."""
import math
from urllib.parse import urlparse


AXES = ["성장성", "수익성", "경쟁력", "엣지", "가치"]
EDGE = ["수주", "고객 인증", "기술·특허", "반복매출", "가격결정력"]


def growth(current, prior):
    if current is None or prior is None or prior <= 0:
        return None
    return (current / prior - 1) * 100


def margin(row):
    r, p = row.get("revenue"), row.get("profit")
    return p / r * 100 if r is not None and r > 0 and p is not None else None


def bound(value, limit=20):
    return round(max(0, min(limit, value)), 1)


def valuation(price, assumptions):
    names = ("profit", "multiple", "debt", "shares")
    if not assumptions or any(assumptions.get(n) is None for n in names):
        return None
    p, m, d, s = [float(assumptions[n]) for n in names]
    if not all(math.isfinite(v) for v in [p, m, d, s]) or min(p, m, s) <= 0:
        return None
    # profit/debt: KRW 100 million; shares: million shares
    result = {label: max(0, (p * pf * m * mf - d) * 100 / s)
              for label, pf, mf in [("Bear", .85, .9), ("Base", 1, 1), ("Bull", 1.15, 1.1)]}
    result["gap"] = (result["Base"] / price - 1) * 100 if price and price > 0 else None
    return result


def valid_evidence(item):
    host = (urlparse(item.get("url", "")).hostname or "").lower()
    return bool(item.get("checked") and item.get("excerpt", "").strip()
                and item.get("date") and host in {"dart.fss.or.kr", "opendart.fss.or.kr"})


def score(report, assumptions=None, evidence=None, peers=None):
    years = report["years"]
    now, prev = years[-1], years[-2]
    rg, pg = growth(now["revenue"], prev["revenue"]), growth(now["profit"], prev["profit"])
    m = margin(now)
    v = valuation(report["price"], assumptions)
    values = {name: None for name in AXES}
    if rg is not None and pg is not None:
        values["성장성"] = bound((rg + 10) / 4, 10) + bound((pg + 20) / 7, 10)
    if m is not None:
        values["수익성"] = bound(m / 25 * 20)
    comparable = [p for p in (peers or []) if p["basis"] == report["basis"] and
                  [x["year"] for x in p["years"]] == [x["year"] for x in years]]
    peer_metrics = [(growth(p["years"][-1]["revenue"], p["years"][-2]["revenue"]), margin(p["years"][-1])) for p in comparable]
    peer_metrics = [(g, pm) for g, pm in peer_metrics if g is not None and pm is not None]
    if len(peer_metrics) >= 2 and rg is not None and m is not None:
        def rank(v, other):
            return sum(1 if v > o else .5 if v == o else 0 for o in other) / len(other) * 10
        values["경쟁력"] = round(rank(rg, [x[0] for x in peer_metrics]) + rank(m, [x[1] for x in peer_metrics]), 1)
    if evidence and all(name in evidence for name in EDGE):
        # A completed review of all five axes is needed; unchecked = unresolved.
        reviewed = all(evidence[n].get("reviewed") for n in EDGE)
        if reviewed:
            values["엣지"] = 4 * sum(valid_evidence(evidence[n]) for n in EDGE)
    if v and v["gap"] is not None:
        values["가치"] = bound(v["gap"] / 2)
    return {"scores": values, "total": round(sum(values.values()), 1) if all(x is not None for x in values.values()) else None,
            "valuation": v, "revenue_growth": rg, "profit_growth": pg, "margin": m}

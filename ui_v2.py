from __future__ import annotations

import html
import streamlit as st


NAV_ITEMS = [
    ("홈", "⌂"),
    ("시장 현황", "▥"),
    ("종목 분석", "◫"),
    ("공시 분석", "▤"),
    ("테마 & 섹터", "◇"),
    ("포트폴리오", "▣"),
    ("관심 종목", "☆"),
    ("AI 인사이트", "✦"),
    ("데이터 연결 관리", "⚙"),
]


def apply_theme():
    st.markdown(
        """
<style>
:root {
  --bg: #F7F9FC;
  --surface: #FFFFFF;
  --surface-soft: #F9FBFF;
  --line: #E6EAF0;
  --line-strong: #D8DEE8;
  --text: #0F172A;
  --muted: #64748B;
  --blue: #2563EB;
  --blue-soft: #EFF6FF;
  --green: #059669;
  --red: #DC2626;
}
html, body, [class*="css"] {
  font-family: Pretendard, "Noto Sans KR", "Apple SD Gothic Neo", sans-serif;
}
.stApp {
  background: var(--bg);
  color: var(--text);
}
.block-container {
  max-width: 1480px;
  padding-top: 1.4rem;
  padding-bottom: 4rem;
}
header[data-testid="stHeader"] {
  background: rgba(247,249,252,.88);
  backdrop-filter: blur(12px);
}
section[data-testid="stSidebar"] {
  background: #FFFFFF;
  border-right: 1px solid var(--line);
}
section[data-testid="stSidebar"] > div {
  padding-top: .9rem;
}
[data-testid="stSidebar"] .stRadio > label {
  display: none;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
  gap: .18rem;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
  border-radius: 12px;
  padding: .45rem .55rem;
  transition: all .15s ease;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
  background: #F3F6FB;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) {
  background: #EAF2FF;
  color: #1D4ED8;
  font-weight: 700;
}
h1, h2, h3, h4 {
  color: var(--text);
  letter-spacing: -.035em;
}
h1 { font-weight: 800; }
h2, h3 { font-weight: 760; }
p, li { line-height: 1.62; }
[data-testid="stCaptionContainer"] {
  color: var(--muted);
}
[data-testid="stMetric"] {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 16px 18px;
  box-shadow: 0 8px 24px rgba(15,23,42,.035);
}
[data-testid="stMetricLabel"] {
  color: var(--muted);
}
[data-testid="stMetricValue"] {
  color: var(--text);
  font-weight: 750;
}
[data-testid="stVerticalBlockBorderWrapper"] {
  border-color: var(--line) !important;
  border-radius: 16px !important;
  background: var(--surface);
  box-shadow: 0 8px 24px rgba(15,23,42,.03);
}
.stButton > button, .stFormSubmitButton > button {
  border-radius: 11px;
  min-height: 2.7rem;
  font-weight: 700;
}
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {
  background: var(--blue);
  border-color: var(--blue);
}
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
  border-radius: 12px !important;
}
.stTabs [data-baseweb="tab-list"] {
  gap: 8px;
}
.stTabs [data-baseweb="tab"] {
  border-radius: 10px;
  padding: 8px 12px;
}
.stDataFrame {
  border: 1px solid var(--line);
  border-radius: 14px;
  overflow: hidden;
}
.planx-brand {
  display:flex; align-items:center; gap:10px; margin: 2px 0 18px 0;
}
.planx-brand-mark {
  width:32px; height:32px; border-radius:10px;
  display:flex; align-items:center; justify-content:center;
  background:linear-gradient(145deg,#2563EB,#60A5FA);
  color:white; font-size:18px; font-weight:800;
}
.planx-brand-title {
  font-size:18px; line-height:1.15; font-weight:800; letter-spacing:-.03em;
}
.planx-brand-sub {
  font-size:10px; color:#94A3B8; margin-top:2px;
}
.planx-hero {
  background: linear-gradient(135deg, #FFFFFF 0%, #F8FBFF 55%, #EFF6FF 100%);
  border: 1px solid #E2E8F0;
  border-radius: 22px;
  padding: 28px 30px;
  margin-bottom: 18px;
  box-shadow: 0 14px 38px rgba(15,23,42,.045);
}
.planx-eyebrow {
  color:#2563EB; font-size:12px; font-weight:800; letter-spacing:.08em;
  text-transform:uppercase; margin-bottom:8px;
}
.planx-hero h1 {
  margin:0; font-size:34px; line-height:1.18;
}
.planx-hero p {
  margin:9px 0 0; color:#64748B; font-size:14px;
}
.planx-card {
  background:#FFFFFF;
  border:1px solid #E6EAF0;
  border-radius:16px;
  padding:17px 18px;
  min-height:116px;
  box-shadow:0 8px 24px rgba(15,23,42,.03);
}
.planx-card-title {
  font-size:12px; color:#64748B; margin-bottom:8px; font-weight:700;
}
.planx-card-value {
  font-size:22px; color:#0F172A; font-weight:800; letter-spacing:-.03em;
}
.planx-card-note {
  margin-top:7px; font-size:11px; color:#94A3B8;
}
.planx-empty {
  background: #FFFFFF;
  border:1px dashed #CBD5E1;
  border-radius:16px;
  padding:22px;
  color:#64748B;
}
.planx-source {
  display:inline-flex; align-items:center; gap:5px;
  color:#64748B; background:#F8FAFC; border:1px solid #E2E8F0;
  padding:4px 8px; border-radius:999px; font-size:10px;
}
.planx-status-ok { color:#047857; background:#ECFDF5; border-color:#A7F3D0; }
.planx-status-wait { color:#92400E; background:#FFFBEB; border-color:#FDE68A; }
.planx-status-bad { color:#B91C1C; background:#FEF2F2; border-color:#FECACA; }
hr { border-color:#E6EAF0 !important; }
@media (max-width: 900px) {
  .block-container { padding-left:1rem; padding-right:1rem; }
  .planx-hero { padding:22px 20px; }
  .planx-hero h1 { font-size:28px; }
}
/* Quiet, readable research workspace. */
.block-container { max-width:1240px; padding-top:2rem; }
.stApp { background:#f8f6f1; }
section[data-testid="stSidebar"] { background:#eee7da; border-right:0; }
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color:#493e2f; }
section[data-testid="stSidebar"] .planx-brand-title { color:#493e2f; font-size:22px; }
section[data-testid="stSidebar"] .planx-brand-sub { color:#806e50; font-size:13px; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] { gap:10px; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label { padding:14px 12px; border-radius:8px; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover { background:#e7ddc9; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) { background:#dfcea8; box-shadow:inset 3px 0 #ad873f; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) p { color:#493e2f; }
[data-testid="stSidebar"] .stButton button p { color:#1b2c45; }
.planx-brand { margin:12px 0 36px; }
.planx-brand-mark { background:#a17c36; border-radius:9px; width:38px; height:38px; }
.planx-hero { background:transparent; border:0; border-radius:0; padding:0 0 18px; box-shadow:none; margin-bottom:6px; }
.planx-hero h1 { font-size:36px; font-weight:750; }
.planx-hero p { font-size:16px; color:#77674e; max-width:650px; }
.planx-eyebrow { font-size:12px; color:#98763a; letter-spacing:.12em; }
.planx-card { box-shadow:none; min-height:132px; border-radius:12px; padding:22px; border-top:3px solid #b1883c; }
.planx-card-title { font-size:14px; font-weight:500; }
.planx-card-value { font-size:28px; font-variant-numeric:tabular-nums; }
.planx-card-note { font-size:13px; color:#5d6d82; }
[data-testid="stMetric"] { box-shadow:none; border-radius:12px; }
[data-testid="stExpander"] { background:#fff; border-radius:10px; }
[data-testid="stExpander"] summary p { font-size:15px; }
[data-testid="stMarkdownContainer"] p { font-size:16px; line-height:1.75; }
[data-testid="stCaptionContainer"] p { font-size:14px; }
.stTabs [data-baseweb="tab-list"] { gap:4px; overflow-x:auto; }
.stTabs [data-baseweb="tab"] { font-size:15px; padding:12px 14px; white-space:nowrap; }
.stTextInput input { min-height:46px; font-size:16px; background:#fff; }
.stButton > button, .stFormSubmitButton > button { min-height:44px; border-radius:8px; }
@media (max-width:640px) {
  .block-container { padding-top:1.3rem; }
  .planx-hero h1 { font-size:28px; }
  .planx-card { min-height:100px; padding:14px; }
  .planx-card-value { font-size:23px; }
}
</style>
""",
        unsafe_allow_html=True,
    )


def brand():
    st.markdown(
        """
<div class="planx-brand">
  <div class="planx-brand-mark">↗</div>
  <div>
    <div class="planx-brand-title">StockDash</div>
    <div class="planx-brand-sub">Data to Insight.</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str, eyebrow: str = "PLANX INVESTMENT OS"):
    st.markdown(
        f"""
<div class="planx-hero">
  <div class="planx-eyebrow">{html.escape(eyebrow)}</div>
  <h1>{html.escape(title)}</h1>
  <p>{html.escape(subtitle)}</p>
</div>
""",
        unsafe_allow_html=True,
    )


def card(title: str, value: str, note: str = "", status: str = ""):
    status_html = f'<div class="planx-card-note">{html.escape(status)}</div>' if status else ""
    st.markdown(
        f"""
<div class="planx-card">
  <div class="planx-card-title">{html.escape(title)}</div>
  <div class="planx-card-value">{html.escape(value)}</div>
  <div class="planx-card-note">{html.escape(note)}</div>
  {status_html}
</div>
""",
        unsafe_allow_html=True,
    )


def empty_state(title: str, message: str):
    st.markdown(
        f"""
<div class="planx-empty">
  <strong style="color:#334155">{html.escape(title)}</strong><br>
  <span>{html.escape(message)}</span>
</div>
""",
        unsafe_allow_html=True,
    )


def source_badge(label: str, state: str = "wait"):
    cls = {"ok": "planx-status-ok", "bad": "planx-status-bad"}.get(state, "planx-status-wait")
    st.markdown(
        f'<span class="planx-source {cls}">{html.escape(label)}</span>',
        unsafe_allow_html=True,
    )

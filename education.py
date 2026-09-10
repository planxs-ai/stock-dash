"""Serve the versioned course from this repository; never cache its contents."""
import hashlib
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

COURSE = Path(__file__).resolve().parent / "course" / "index.html"


def read_course():
    content = COURSE.read_text(encoding="utf-8")
    return content, hashlib.sha256(content.encode("utf-8")).hexdigest()


@st.fragment(run_every="60s")
def watch_course(displayed_version):
    """Do not remount the lesson iframe unless the repository file changes."""
    try:
        _, latest = read_course()
    except OSError:
        return
    if latest != displayed_version:
        st.rerun()


def render_education():
    try:
        content, version = read_course()
    except OSError:
        st.info("교육자료를 준비하고 있습니다. 잠시 후 다시 열어 주세요.")
        return
    st.header("교육자료")
    expanded = st.toggle("전체 보기", key="education_expanded", help="대시보드 목차를 접고 교육자료를 화면 너비로 펼칩니다.")
    if expanded:
        st.markdown('''<style>
        [data-testid="stSidebar"], [data-testid="stHeader"]{display:none!important}
        .block-container{max-width:100%!important;padding:0.6rem 1rem!important}
        iframe[title="st.iframe"]{height:calc(100vh - 150px)!important;min-height:600px}
        </style>''', unsafe_allow_html=True)
    st.caption("프로필 · 강의 요약 · 1~12강 · 오른쪽 아래에서 필기 도구를 켤 수 있습니다.")
    components.html(content, height=1000, scrolling=True)
    watch_course(version)

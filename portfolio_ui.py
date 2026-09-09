"""Account holdings stay in this authenticated session; public reports use existing storage."""
import hashlib
import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from automatic import brief
from broker_kis import BrokerError, KIS
from providers import Official


def render_portfolio(store, sample_mode):
    st.header('내 계좌 자동 분석')
    st.caption('한국투자증권 국내주식 · 잔고 조회와 분석 · 조회 시점 기준')
    with st.expander('처음 한 번 · 계좌 연결 방법'):
        st.markdown('1. 한국투자증권 Open API를 신청하고 사용할 계좌의 App Key와 App Secret을 발급받습니다.\n2. Streamlit 앱 관리 → Settings → Secrets에 아래 항목을 추가합니다.\n3. 저장 후 앱을 다시 열고 계좌 불러오기·분석을 누릅니다.')
        st.link_button('한국투자증권 API 신청 안내', 'https://apiportal.koreainvestment.com/intro')
        st.code('KIS_ENV = "demo"\nKIS_APP_KEY = "발급받은 App Key"\nKIS_APP_SECRET = "발급받은 App Secret"\nKIS_CANO = "계좌 앞 8자리"\nKIS_ACNT_PRDT_CD = "계좌 뒤 2자리"', language='toml')
        st.write('실제 계좌는 KIS_ENV를 real로 설정하고 실전용 키를 사용합니다. 계좌번호와 키는 채팅이나 GitHub 코드에 넣지 마세요.')
        st.caption('수량·매입가·계좌 잔고는 현재 로그인 세션에서만 보관합니다. 공개 기업 분석과 투자일지는 기존 저장소에 저장합니다. 매매 주문 기능은 없습니다.')
    if sample_mode:
        st.info('APP_PASSWORD를 설정하고 로그인하면 개인 계좌 연결을 사용할 수 있습니다.')
        return
    if st.button('계좌 불러오기·자동 분석', type='primary'):
        signature = hashlib.sha256('|'.join(os.getenv(k, '') for k in ['KIS_ENV', 'KIS_APP_KEY', 'KIS_APP_SECRET', 'KIS_CANO', 'KIS_ACNT_PRDT_CD']).encode()).hexdigest()
        try:
            if st.session_state.get('kis_signature') != signature:
                st.session_state.kis_client = KIS()
                st.session_state.kis_signature = signature
            with st.spinner('보유종목과 잔고를 불러옵니다…'):
                snapshot = st.session_state.kis_client.balance()
            st.session_state.account_snapshot = snapshot
            st.session_state.account_results = {}
        except BrokerError as error:
            st.error(str(error))
            snapshot = None
        if snapshot is not None:
            positions = snapshot['positions']
            progress = st.progress(0, text='종목별 공식 자료를 확인합니다.')
            provider = Official()
            for index, position in enumerate(positions):
                code = position['code']
                item = {'code': code, 'name': position['name']}
                try:
                    if not re.fullmatch(r'[0-9]{6}', code):
                        raise ValueError()
                    report = provider.automatic(code)
                    result = brief(report)
                    item.update(report=report, automatic_brief=result, analyzed_at=datetime.now(ZoneInfo('Asia/Seoul')).isoformat())
                    try:
                        store.save_stock({**item, 'analysis_error': None})
                    except Exception:
                        item['save_error'] = True
                except Exception:
                    item['error'] = '기업 분석 미완료 · 공식 자료/상품 유형 확인 필요'
                st.session_state.account_results[code] = item
                progress.progress((index + 1) / len(positions), text=f"{index + 1}/{len(positions)} 종목 확인")
            progress.empty()
            st.caption('계좌 조회를 마쳤습니다. 분석 완료 여부는 종목별로 표시합니다.')
    snapshot = st.session_state.get('account_snapshot')
    if not snapshot:
        st.info('계좌를 연결하면 보유종목이 자동으로 들어옵니다. 종목코드·수량·매입가를 직접 입력하지 않아도 됩니다.')
        return
    st.caption(('실전' if snapshot['mode'] == 'real' else '모의') + ' 계좌 · 조회 ' + snapshot['fetched'])
    cols = st.columns(4)
    cols[0].metric('국내주식 평가액', f"{snapshot['value']:,.0f}원")
    cols[1].metric('평가손익', f"{snapshot['pnl']:+,.0f}원")
    cols[2].metric('예수금', f"{snapshot['cash']:,.0f}원" if snapshot['cash'] is not None else '미수집')
    cols[3].metric('보유종목', f"{len(snapshot['positions'])}개")
    st.caption('비중은 조회된 국내주식 평가액 기준입니다. 예수금은 출금 가능 금액과 다를 수 있습니다.')
    if not snapshot['positions']:
        st.info('조회된 계좌에 보유수량이 있는 국내주식이 없습니다.')
        return
    results = st.session_state.get('account_results', {})
    rows = []
    for p in snapshot['positions']:
        item = results.get(p['code'], {})
        b = item.get('automatic_brief', {})
        rows.append({'종목': p['name'], '코드': p['code'], '수량': p['quantity'], '평균매입가': p['average_cost'],
                     '평가액': p['value'], '평가손익': p['pnl'], '비중 %': round(p['weight'], 1),
                     '성장': b.get('growth', '분석 미완료'), '가치': b.get('value', '평가 보류')})
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
    largest = max(snapshot['positions'], key=lambda p: p['weight'])
    st.write(f"가장 큰 보유 비중은 {largest['name']} {largest['weight']:.1f}%입니다. 이 종목의 변화가 계좌에 미치는 영향을 먼저 확인하세요.")
    selected = st.selectbox('자세히 볼 보유종목', snapshot['positions'], format_func=lambda p: p['name'] + ' · ' + p['code'])
    item = results.get(selected['code'], {})
    if item.get('error'):
        st.warning(item['error'])
    if item.get('save_error'):
        st.warning('분석 결과를 저장하지 못했습니다. 현재 접속에서는 확인할 수 있습니다.')
    if item.get('report'):
        r, b = item['report'], item['automatic_brief']
        st.write(b['summary'])
        st.caption('기업 자료 수집일 ' + r.get('fetched', '') + ' · 계좌 조회일과 다를 수 있습니다.')
        st.subheader('실적 추이 · 억원')
        st.dataframe(pd.DataFrame(r['years'])[['year', 'revenue', 'profit']].rename(columns={'year':'연도','revenue':'매출','profit':'영업이익'}), hide_index=True)
        with st.expander('주요 사업 · 공식 보고서 발췌'):
            st.write(r.get('business_excerpt') or '사업 원문 미수집')
        st.subheader('최근 공시')
        for notice in sorted(r.get('disclosures', []), key=lambda n:n['date'], reverse=True)[:6]:
            st.link_button(notice['date'] + ' · ' + notice['title'], notice['url'])
    with st.form('account_note'):
        note = st.text_area('투자일지 · 보유 이유와 다음 확인 조건')
        if st.form_submit_button('일지 저장'):
            if note.strip():
                try:
                    store.log('journal', {'code': selected['code'], 'kind': 'note', 'note': note.strip(), 'at': datetime.now(ZoneInfo('Asia/Seoul')).isoformat()})
                    st.success('일지를 저장했습니다.')
                except Exception:
                    st.error('일지 저장에 실패했습니다. 입력 내용을 복사해 두세요.')

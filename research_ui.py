import hashlib
import json
from datetime import date

import pandas as pd
import streamlit as st

from automatic import brief
from chat_research import published, parse_bundle, trends, growth, request_text


def render_research(store, state, sample_mode):
    st.header('내 종목 통합 분석')
    st.caption('계좌 보유종목과 직접 추가한 종목을 함께 비교합니다. AI 해설은 이 채팅에서 조사한 결과입니다.')
    if sample_mode:
        st.info('개인 목록 저장은 APP_PASSWORD 설정 후 사용할 수 있습니다. 조사 방법은 아래에서 확인할 수 있습니다.')
    else:
        with st.expander('종목 직접 추가 · 증권사 API 없이 사용', expanded=not state.get('stocks')):
            with st.form('research_manual'):
                name = st.text_input('종목명', placeholder='예: 삼성전자')
                code = st.text_input('종목코드 · 모르면 비워두세요', max_chars=6)
                if st.form_submit_button('내 목록에 추가'):
                    import re
                    if not name.strip() or (code and not re.fullmatch(r'[0-9]{6}', code)):
                        st.error('종목명과 숫자 6자리 코드를 확인하세요. 코드는 생략할 수 있습니다.')
                    else:
                        known = next((s for s in state.get('stocks', []) if s['name'].strip().casefold() == name.strip().casefold()), {})
                        identity = known.get('code') or code or 'pending-' + hashlib.sha256(name.strip().casefold().encode()).hexdigest()[:16]
                        try:
                            store.save_stock({'code':identity, 'name':name.strip(), 'kind':known.get('kind','관심')})
                            st.rerun()
                        except Exception: st.error('목록 저장에 실패했습니다. 저장 공간 설정을 확인하세요.')
    research = published()
    for r in state.get('chat_research', []):
        if r['code'] not in research or r['as_of'] >= research[r['code']]['as_of']: research[r['code']] = r
    stocks = {s['code']:s for s in state.get('stocks', [])}
    for p in st.session_state.get('account_snapshot', {}).get('positions', []):
        stocks[p['code']] = {**stocks.get(p['code'], {}), 'code':p['code'], 'name':p['name']}
    with st.expander('채팅으로 조사 요청하기', expanded=True):
        st.write('① 종목을 추가하거나 포트폴리오에서 계좌를 불러옵니다. ② 아래 요청문을 복사해 지금 대화창에 보냅니다. ③ 조사 결과가 반영되면 이 화면을 새로고침합니다.')
        st.code(request_text(list(stocks.values())), language=None)
        st.caption('현재 접속의 개인 목록을 제가 직접 읽을 수는 없습니다. 요청문에는 종목명·코드만 들어가며 계좌번호·수량·매입가는 제외됩니다. 이 화면은 별도의 AI API를 호출하지 않습니다.')
        if st.button('반영된 조사 결과 다시 읽기'): st.rerun()
        if not sample_mode:
            upload = st.file_uploader('별도로 받은 조사 JSON 가져오기 · 선택', type=['json'])
            if upload and st.button('조사 파일 검증·저장'):
                try:
                    reports = parse_bundle(upload.getvalue())
                    def save(data):
                        merged = {r['code']:r for r in data.get('chat_research', [])}
                        for r in reports:
                            if r['code'] not in merged or r['as_of'] >= merged[r['code']]['as_of']: merged[r['code']] = r
                        data['chat_research'] = list(merged.values())
                    store.change(save)
                    st.rerun()
                except (ValueError, KeyError, TypeError): st.error('조사 파일의 형식·출처·기간을 확인하세요. 기존 결과는 유지했습니다.')
                except Exception: st.error('저장에 실패했습니다. 기존 결과는 유지했습니다.')
    if not stocks:
        st.info('분석할 종목이 없습니다. 위에서 종목을 추가하거나 포트폴리오에서 계좌를 불러오세요.')
        return
    rows, details = [], {}
    for key, stock in stocks.items():
        r = research.get(key)
        if not r and key.startswith('pending-'):
            matches = [v for v in research.values() if v['name'].strip().casefold() == stock['name'].strip().casefold()]
            if len(matches) == 1: r = matches[0]
        r = r or {}
        f, v, flow = r.get('financial') or {}, r.get('valuation') or {}, r.get('flow') or {}
        trend, frame = trends(r.get('prices'), r.get('as_of', date.today().isoformat()))
        row = {'종목':stock['name'], '코드':r.get('code', key if not key.startswith('pending-') else '확인 필요'),
               '누적 매출 성장':growth(f['revenue'], f['prior_revenue']) if f else '조사 필요',
               '누적 영업이익 성장':growth(f['operating_profit'], f['prior_operating_profit']) if f else '조사 필요',
               '외국인 / 기관':f"{flow['foreign']:+,.0f} / {flow['institution']:+,.0f} {flow['unit']}" if flow else '조사 필요',
               '적정주가 참고':f"{v['base']:,.0f}원" if v else '조사 필요',
               '일봉':trend['daily'], '주봉':trend['weekly'], '조사일':r.get('as_of','미조사')}
        rows.append(row);details[key]=(stock, r, trend, frame)
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
    selected = st.selectbox('종목 상세', list(details), format_func=lambda k:stocks[k]['name'], key='research_selected')
    stock, r, trend, frame = details[selected]
    if not r:
        st.info('이 종목의 채팅 조사 결과가 아직 없습니다. 위 요청문을 대화창에 보내면 조사 결과를 채울 수 있습니다.')
        if stock.get('report'):
            st.write('기존 공식 결산 분석: ' + brief(stock['report'])['summary'])
        return
    st.caption('조사일 ' + r['as_of'] + ' · 각 표의 자료 기간은 아래에 별도 표시합니다. 실시간 분석이 아닙니다.')
    tabs = st.tabs(['기업 특징·주력사업', '실적·경쟁사', '수급·추세', '가치·확인할 사항'])
    with tabs[0]:
        for label, key in [('AI 핵심 해설','summary'), ('매출 주력사업과 종목 특징','business')]:
            st.subheader(label)
            entry = r.get(key)
            if entry:
                st.write(entry['text']); st.link_button('설명의 원문 근거', entry['source'], key='research_'+key)
            else: st.info('조사 필요')
    with tabs[1]:
        f = r.get('financial')
        if f:
            st.caption(f"누적 {f['period']} / 전년 {f['prior_period']} · {f['basis']} · {f['currency']} {f['unit']}")
            st.dataframe([{'항목':'매출','이번 누적':f['revenue'],'전년 누적':f['prior_revenue'],'변화':growth(f['revenue'],f['prior_revenue'])},
                          {'항목':'영업이익','이번 누적':f['operating_profit'],'전년 누적':f['prior_operating_profit'],'변화':growth(f['operating_profit'],f['prior_operating_profit'])}], hide_index=True)
            st.link_button('실적 근거', f['source'])
        else: st.info('전년 같은 기간 누적 실적 조사 필요')
        peers = r.get('peers')
        st.subheader('경쟁사 영업이익 순위')
        if peers and peers['rows']:
            st.write(peers['selection_reason'])
            st.caption(f"비교 표본 내 순위 · {peers['period']} · {peers['basis']} · {peers['currency']} {peers['unit']}")
            df = pd.DataFrame(peers['rows']);df['순위'] = df['operating_profit'].rank(method='min', ascending=False).astype(int)
            st.dataframe(df.sort_values('순위')[['순위','name','operating_profit','source']].rename(columns={'name':'기업','operating_profit':'영업이익','source':'출처'}), hide_index=True)
        else: st.info('같은 기간·회계기준의 경쟁사 실적 조사 필요')
    with tabs[2]:
        flow = r.get('flow')
        if flow:
            st.caption(flow['start'] + ' ~ ' + flow['end'] + ' · 순매수 ' + flow['unit'])
            a,b=st.columns(2);a.metric('외국인 순매수', f"{flow['foreign']:+,.0f}");b.metric('기관 순매수', f"{flow['institution']:+,.0f}")
            st.link_button('수급 근거', flow['source'])
        else: st.info('외국인·기관 수급 조사 필요')
        a,b=st.columns(2);a.metric('일봉 추세',trend['daily']);b.metric('완료 주봉 추세',trend['weekly'])
        st.caption('수정종가 기준: 일봉 20·60일, 주봉 10·20주 평균과 장기 평균 기울기를 함께 확인합니다. 진행 중인 주는 제외합니다.')
        if frame is not None:
            st.caption('가격 자료 마지막 거래일 ' + str(frame['date'].iloc[-1]))
            st.line_chart(frame.set_index('date')['close'])
            st.link_button('가격 자료 근거', r['prices']['source'])
    with tabs[3]:
        v = r.get('valuation')
        if v:
            a,b,c=st.columns(3)
            for col,key,label in [(a,'low','낮은 참고가'),(b,'base','기본 참고가'),(c,'high','높은 참고가')]: col.metric(label,f"{v[key]:,.0f}원")
            st.write(v['method']);st.caption(f"비교 가격 {v['current_price']:,.0f}원 · {v['price_date']} · 기본 참고가 대비 차이 {(v['base']/v['current_price']-1)*100:+.1f}%")
            st.link_button('평가 근거', v['source'])
        else: st.info('평가 가정과 가격 근거 조사 필요')
        for gap in r.get('data_gaps', []): st.write('확인 필요 · ' + str(gap))
    if not sample_mode:
        with st.form('research_note'):
            note=st.text_area('투자일지 · 다음 확인할 조건')
            if st.form_submit_button('기록 저장') and note.strip():
                try:
                    from datetime import datetime, timezone
                    store.log('journal', {'code':selected,'at':datetime.now(timezone.utc).isoformat(),'kind':'note','note':note.strip()})
                    st.success('일지를 저장했습니다.')
                except Exception: st.error('저장 실패. 입력 내용을 보관하세요.')

# 채팅으로 조사하고 대시보드에 반영하기

## 사용자 순서

1. 통합 분석에서 종목명을 직접 추가합니다. 증권사 API는 없어도 됩니다. 계좌를 연결했다면 포트폴리오의 조회 목록도 함께 표시됩니다.
2. 통합 분석 → 채팅으로 조사 요청하기의 요청문을 복사해서 지금 채팅에 보냅니다. 종목명·코드만 전달됩니다.
3. 연결된 GitHub를 사용할 수 있는 AI가 공식 자료를 조사하고 이 저장소의 research/에 JSON을 기록합니다. Streamlit에 변경이 적용된 뒤 화면을 다시 읽습니다. 별도 AI API 비용을 요구하지 않습니다.
4. 저장소 연결을 사용할 수 없는 채팅에서는 같은 형식의 조사 JSON을 받아 화면에 업로드할 수 있습니다.

대시보드 버튼은 ChatGPT 대화를 자동 실행하지 않습니다. 사용자 요청을 받은 채팅 AI가 실제 조사와 파일 갱신을 수행해야 합니다. 개인 저장소·Supabase의 관심목록이 채팅에 자동 공유되는 것도 아닙니다.

## 작성 AI의 작업 지침

현재 앱과 연구 파일을 먼저 읽습니다. 공개 기업 조사만 research/에 기록합니다. 계좌번호·키·수량·매입가·개인 일지는 공개 저장소에 기록하지 않습니다. 사용자가 준 종목 목록을 별도 공개 명단 파일로 만들지 않습니다.

각 항목은 공식 공시, 거래소, 증권사 공식 데이터와 기업 IR 등 원문으로 확인합니다. AI 추론은 설명에서 구분하며 숫자는 만들지 않습니다. null 또는 항목 생략은 미수집입니다. 이유를 data_gaps에 적습니다. 자료를 못 구했다는 이유로 전체 실패로 표시하지 않습니다.

파일 전체 형태는 {"schema_version": 1, "reports": [...]}입니다. 기존 파일과 종목이 겹치면 해당 종목의 최신 파일을 업데이트합니다. 같은 조사일의 중복 파일은 만들지 않습니다. 저장 전에 chat_research.parse_bundle로 검증합니다. publication date와 자료 대상 기간을 혼동하지 않습니다.

## report 필드

| 필드 | 내용 |
|---|---|
| code / name / as_of | 6자리 코드, 공식 기업명, 조사일 YYYY-MM-DD |
| summary | {text: AI 핵심 설명, source: HTTPS 원문} |
| business | {text: 종목 특징·주력 매출 사업 설명, source: HTTPS 원문} |
| financial | period, prior_period, basis, currency, unit, revenue, prior_revenue, operating_profit, prior_operating_profit, source |
| flow | start, end, unit(주/원/억원), foreign, institution, source |
| valuation | low, base, high, current_price, price_date, method, source |
| prices | adjusted: true, source, rows: [{date: YYYY-MM-DD, close: 수정종가}] |
| peers | period, basis, currency, unit, selection_reason, source, rows |
| data_gaps | 미확인 자료와 필요한 다음 확인 사항 문자열 목록 |

financial의 period는 YYYY-03/06/09/12, prior_period는 전년도 같은 월입니다. 두 숫자는 해당 연도 시작일부터 누적한 값이며 단일 분기 금액을 혼용하지 않습니다. 전년 영업이익이 0 이하이면 일반 성장률 대신 흑자 전환·적자 축소 등으로 표시합니다. 매출·영업이익은 같은 기준의 자료를 사용합니다.

peers.rows 각 행은 name, operating_profit, period, basis, currency, unit, source가 필요합니다. 비교군과 모든 행의 기간·회계기준·통화·단위를 일치시켜야 합니다. 누락 기업을 0으로 처리하지 않습니다. 순위는 비교 표본 내 영업이익 절대액 순위이며 사업 경쟁력 순위와 구별합니다.

일봉 추세는 종가 > 20일평균 > 60일평균이고 60일평균 기울기가 양수일 때 상승 정렬, 반대는 하락 정렬입니다. 주봉은 완료한 주의 마지막 수정종가와 10·20주 평균을 사용합니다. 최소 61거래일·21완료주 데이터가 필요합니다. 당주와 가격 누락을 주의하고, 원천자료가 충분하지 않으면 기간 부족으로 둡니다. 거래일 데이터가 불연속이면 조사 시 보완한 후 제출합니다.

valuation.method에는 사용자의 평가 공식과 계산 가정·연도·추정/확정 구분을 명시합니다. 임의의 배수나 순이익·영업이익 혼용을 피합니다. 공시 이익과 검증된 시가총액·주식수로 재현 가능한 계산을 제공합니다. 가격 기준일은 price_date입니다.

## 초기 자료

initial-examples.json은 삼성전자·SK하이닉스 2025/2024 연간 결산과 사업 설명을 확인하는 초기 자료입니다. 최신 분기·현재 수급·현재 일봉/주봉·적정주가 조사를 완료한 자료가 아닙니다. 두 기업 전사 영업이익 순위는 사업 구성 차이가 있으므로 반도체 사업 경쟁력 순위로 해석하지 않습니다.

실적·가격 계산은 Python에서 수행하고, 채팅 AI는 근거 수집과 해설을 담당합니다. 누적 매출·이익 변화는 (이번 누적/전년 누적-1)×100입니다.

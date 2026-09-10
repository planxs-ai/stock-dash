# PlanX 최종 실습 교재 · 내 종목을 이해하고 기록하기

## 처음 읽기 · 우리가 만드는 대시보드

**공식 API가 자료를 가져옵니다 → 코드가 숫자를 계산합니다 → 채팅 AI가 근거를 해석합니다 → GitHub에 반영합니다 → Streamlit에서 봅니다.**

API는 다른 기관의 자료를 프로그램으로 가져오는 통로입니다. 인증키는 그 통로를 사용할 수 있는 열쇠입니다. GitHub는 코드와 공개 조사 결과의 보관함, Streamlit은 그 코드를 실행해 화면으로 보여주는 서비스입니다.

수강생의 기본 흐름은 **내 GitHub 만들기 → 시세·DART 키 준비 → 내 Streamlit 열기 → 종목 추가 → 조사 요청 → 판단 기록**입니다. KRX와 증권사 계좌 연결은 기본 화면 사용 후 확장합니다. 별도의 AI API 키는 사용하지 않습니다.

## API 안내 · 어디서 무엇을 가져오나요?

| 기관·신청 링크 | 가져올 데이터 | 대시보드에서 하는 일 | 현재 교재 코드의 상태 |
|---|---|---|---|
| [공공데이터포털 주식시세정보](https://www.data.go.kr/data/15094808/openapi.do) | 기준일별 종가·거래량·시가총액·상장주식수 등 | 종목 검색, 가격 확인, 가치 계산의 기초 | 연결 코드 있음 |
| [DART OpenAPI](https://opendart.fss.or.kr/) | 기업 정보·재무제표·사업보고서·공시 | 매출·영업이익 비교, 사업 설명, 공시 확인 | 연결 코드 있음. 통신 지연 시 공개 수집본으로 보완 |
| [KRX OpenAPI](https://openapi.krx.co.kr/) | 승인한 상품의 지수·주식 등 시장 데이터 | 시장·종목 흐름을 추가 분석 | 신청과 승인 범위 확인 후 수집 기능 추가 필요 |
| [한국투자증권 Open API](https://apiportal.koreainvestment.com/intro) | 본인 계좌의 보유종목·수량·매입가·평가손익 | 계좌 종목을 자동으로 가져오기 | 선택 연결 코드 있음. 실계좌 대조 필요 |

공공데이터포털의 가격을 실시간 체결가로 부르지 않습니다. 화면의 시세 기준일을 봅니다. DART는 사업보고서·반기보고서·분기보고서의 기간을 구분합니다. KRX 키 하나로 모든 수급 자료가 제공되는 것은 아니므로 투자자별 순매수의 제공 여부와 조회 기간은 승인 상품에서 따로 확인합니다.

**분석 항목과 필요한 근거**

| 보고 싶은 내용 | 필요한 자료와 확인 기준 |
|---|---|
| 실적 상승률 | DART의 같은 회계기준 매출·영업이익 |
| 누적 영업이익 성장 | 올해 1~6월이면 전년도 1~6월과 비교. 단일 2분기와 혼용하지 않기 |
| 수급 동향 | 외국인·기관 순매수의 기간과 단위. 가격 상승만으로 수급을 추정하지 않기 |
| 일봉·주봉 추세 | 수정주가와 충분한 기간. 진행 중인 주와 완료한 주 구분 |
| 적정주가 | 검증한 실적·가격·주식수와 명시한 평가 공식. 예상 수치는 추정으로 표시 |
| 경쟁사 영업이익 순위 | 같은 기간·통화·단위·회계기준의 비교군. 표본 내 순위로 표시 |
| 종목 특징·주력 매출 사업 | 사업보고서·기업 IR 원문을 AI가 쉬운 말로 설명 |

**완료 확인:** 가격은 어디서, 이익은 어디서, 계좌는 어디서 가져오는지 설명할 수 있습니다. API가 있다고 자료의 시점과 비교 기준이 자동으로 맞아지는 것은 아닙니다.

## GitHub와 AI 연결 · 읽기와 수정 구분하기

GitHub 가입: https://github.com/signup

① 아래 01단계에서 강사의 stock-dash를 Fork해 내 저장소를 만듭니다. Fork는 코드를 내 계정으로 복사하는 기능입니다. 강사의 API 키와 서비스 연결까지 복사하지는 않습니다.

② ChatGPT의 설정 → 앱 또는 플러그인 → GitHub에서 계정을 연결합니다. GitHub 승인 화면에서 내 stock-dash 저장소의 접근을 허용합니다. 메뉴 이름은 사용 환경에 따라 다를 수 있습니다.

③ 먼저 아래 문장으로 **읽기 연결**을 확인합니다.

```text
내 GitHub의 [내아이디/stock-dash]를 열어서
START-HERE.md와 app.py를 읽고, 지금 사용할 수 있는 기능을 설명해줘.
```

④ **직접 수정·반영은 Codex의 GitHub 쓰기 기능을 사용할 수 있는 환경에서 진행합니다.** 그 환경에서 GitHub 계정과 대상 저장소를 선택하고 접근 권한을 확인합니다. 일반 ChatGPT의 GitHub 읽기 연결만으로 파일 수정·커밋이 된다고 생각하지 마세요.

```text
[내아이디/stock-dash]의 현재 코드를 먼저 확인해줘.
내 종목 화면의 안내 문장을 더 쉽게 고치고 기존 기능을 유지해줘.
변경 파일과 동작을 확인한 뒤 내 저장소에 반영해줘.
완료 후 변경 내용과 확인하지 못한 항목을 알려줘.
```

⑤ GitHub 저장소의 최근 커밋과 실제 파일 변경을 확인합니다. AI 답변에 '완료'라고 적혔다는 사실만으로 반영을 판단하지 않습니다.

**막히면:** 저장소가 안 보일 때는 연결한 GitHub 계정과 허용 저장소를 확인합니다. 읽기는 되지만 쓰기가 지원되지 않으면 Codex 환경으로 이동하거나 수정 파일을 받아 직접 업로드합니다.

공식 연결 안내: https://help.openai.com/en/articles/11145903-connecting-github-to-chatgpt

## 배포 서비스 선택 · 수업에서는 Streamlit

| 서비스 | 이 수업에서의 선택 |
|---|---|
| [Streamlit](https://share.streamlit.io/) | 현재 Python 앱을 그대로 실행하므로 기본 선택 |
| [Vercel](https://vercel.com/) | 다른 웹 화면으로 확장할 때 검토. 현재 앱을 그대로 옮기는 절차와 다름 |
| [Cloudflare](https://www.cloudflare.com/) | 해당 실행 환경에 맞춘 웹사이트·서버 구성으로 확장할 때 검토 |

수업에서는 세 서비스를 모두 연결하지 않습니다. Streamlit 한 곳만 사용합니다. GitHub가 소스 보관함이고 Streamlit이 실행 화면이라는 차이만 먼저 이해하면 됩니다.

공식 배포 안내: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app

## 키는 어디에 입력하나요?

| 실행하는 곳 | 키 입력 장소 | 쓰는 경우 |
|---|---|---|
| 내 Streamlit 앱 | 앱 관리 → Settings → Secrets | 앱이 시세·DART·본인 계좌를 직접 조회 |
| GitHub의 수집 작업 | 저장소 Settings → Secrets and variables → Actions | 강사용 Public DART data 수집 작업 실행 |
| GitHub 코드·교재·채팅 | 입력하지 않음 | 실제 키와 계좌번호를 공개 파일에 넣지 않음 |

GitHub Secrets와 Streamlit Secrets는 자동으로 서로 복사되지 않습니다. AI는 GitHub Secrets의 실제 값을 읽지 않고, 해당 키를 사용하도록 작성된 작업을 수정할 수 있습니다. 수집 작업을 실행하는 기능이 현재 AI 환경에 없으면 Actions에서 직접 Run workflow를 누릅니다.

공식 Streamlit 키 설정: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management

**새 이용 흐름:** 내 종목에서 직접 종목 추가 또는 계좌 연결에서 계좌 불러오기 → 조사 요청문을 이 채팅에 전달 → AI가 공식 자료 조사·결과 반영 → 내 종목에서 확인합니다. 별도의 AI API는 사용하지 않습니다. [채팅 조사와 화면 반영 방법](CHAT-RESEARCH.md)을 참고하세요.

**최종 프로젝트 · 내 계좌 자동 분석:** 기본 실습을 마치면 [증권사 계좌 연결 안내](BROKER-START.md)를 따라 계좌 연결에서 보유종목을 불러옵니다. 종목·수량·매입가를 직접 입력하지 않고 실적·가치·최근 공시를 확인하고 일지를 남깁니다.

**오늘 목표: 종목 한 개 입력 → 공식 숫자 확인 → 나의 판단 한 문장 기록.**

처음에는 01부터 07까지 순서대로 진행하세요. 각 단계의 ‘완료 확인’이 되면 다음으로 넘어갑니다. 설정을 마친 다음 수업부터는 06과 07만 반복하면 됩니다.

**완성할 결과물:** 나만의 관심 종목 대시보드와 투자일지. 주요 사업 → 최근 공시 → 3개년 실적 → 점수와 가치 참고 범위 → 재검토 조건을 한 화면에서 읽습니다.

캘린더 API·서비스 계정·JSON 키·GitHub 예약 설정은 수강생 실습에서 제외합니다. Supabase도 필수가 아닙니다. 먼저 화면과 데이터 분석을 익히고, 기기 간 영구 저장은 선택 확장으로 진행합니다.

## 01 · 내 프로젝트 복사하기

**이번 목표:** 내 GitHub 보관함을 만듭니다.

① https://github.com/planxs-ai/stock-dash 를 엽니다.

② GitHub에 로그인하고 오른쪽 위 Fork → Create fork를 누릅니다.

③ Owner가 내 계정인지 확인합니다. 이름은 stock-dash로 둡니다.


**완료 확인:** 주소가 github.com/내아이디/stock-dash로 바뀌었습니다.

**막히면:** 원본 planxs-ai 화면에 머물러 있다면 내 프로필의 Repositories에서 stock-dash를 여세요.

## 02 · 시세 API 키 발급받기

**이번 목표:** 종목의 기준 종가를 가져올 열쇠를 준비합니다.

① https://www.data.go.kr 에 가입하고 로그인합니다.

② 금융위원회_주식시세정보를 검색하고 활용신청을 누릅니다.

③ 승인 여부를 확인한 뒤 마이페이지에서 일반 인증키의 Decoding 값을 확인합니다.

④ 키는 지금 AI 채팅이나 코드에 붙이지 않습니다. 05단계에서 발급 화면을 다시 열어 입력합니다.


**완료 확인:** 신청 상태와 일반 인증키를 확인했습니다.

**막히면:** 승인 대기라면 여기서 멈추고 강사에게 알려 주세요. 키 없이 실제 조회는 진행하지 않습니다.

## 03 · DART API 키 발급받기

**이번 목표:** 기업의 공시 재무제표를 가져올 열쇠를 준비합니다.

① https://opendart.fss.or.kr 에 가입하고 로그인합니다.

② 인증키 신청 메뉴에서 개인 학습 목적을 입력합니다.

③ 인증키 관리에서 발급 상태와 키를 확인합니다.

④ 05단계에서 이 키를 DART_CRTFC_KEY라는 이름으로 입력합니다.


**완료 확인:** 시세 키와 DART 키를 각각 어디서 확인하는지 알고 있습니다.

**막히면:** 두 키는 서로 다릅니다. DART 키 칸에 공공데이터포털 키를 넣지 마세요.

## 03-B · KRX 신청하기 · 확장 단계

① https://openapi.krx.co.kr/ 를 열고 이용 안내를 확인한 뒤 회원가입·로그인합니다.

② 인증키 신청 절차를 진행합니다. 신청 목적과 이용 조건을 확인하고 승인 상태를 봅니다.

③ 사용할 데이터 상품을 선택하고 해당 API의 이용 신청·승인이 별도로 필요한지 확인합니다. 키 발급과 개별 API 사용 승인을 구분합니다.

④ 제공 항목·조회 기간·호출 제한·이용 범위를 기록합니다. 외국인·기관 수급이 필요하면 해당 항목이 실제 응답에 포함되는지 확인합니다.

⑤ 강사에게 **API 이름과 문서 링크·승인 상태**를 전달합니다. 실제 키는 보내지 않습니다. 수집 코드가 연결된 후 그 코드가 사용하는 정확한 설정명으로 키를 입력합니다.

**완료 확인:** 승인된 데이터 상품과 가져올 항목을 설명할 수 있습니다. 현재 stock-dash의 KRX 수집 기능은 추가 연결 단계이므로, 키를 넣기만 하면 모든 KRX 지표가 표시된다고 안내하지 않습니다.

**강사용 기술 메모:** DART 인증 매개변수는 crtfc_key이며 예제 코드의 설정명은 DART_CRTFC_KEY입니다. 주식시세 인증 매개변수는 serviceKey이며 설정명은 DATA_GO_KR_SERVICE_KEY입니다. KRX는 승인한 API 문서의 AUTH_KEY 헤더와 호출 주소를 확인합니다. 현재 교재에는 동작하지 않는 KRX 설정명을 임의로 추가하지 않습니다.

## 04 · 내 대시보드 주소 만들기

**이번 목표:** 설치 없이 브라우저에서 여는 화면을 만듭니다.

① https://share.streamlit.io 에서 GitHub 계정으로 로그인합니다.

② Create app에서 내아이디/stock-dash 저장소를 고릅니다.

③ Branch는 main, Main file path는 app.py로 정하고 배포합니다.

④ 첫 화면의 내 종목·계좌 연결·설정 메뉴를 살펴봅니다.

**입력 예시:** Repository는 내아이디/stock-dash, Branch는 main, Main file path는 app.py입니다. 배포 화면의 Advanced settings에서 Secrets를 넣거나 배포 후 05단계에서 설정할 수 있습니다.

첫 화면은 내 종목·계좌 연결·설정 메뉴입니다. 데이터나 개인 목록이 없으면 시작 안내가 보일 수 있습니다. 자신의 .streamlit.app 주소를 즐겨찾기에 저장하세요. 강사의 샘플 주소와 내 앱 주소를 구분합니다.

**GitHub 수정 후:** 연결된 저장소·브랜치의 변경이 앱에 적용될 때까지 기다린 뒤 새로고침합니다. 반영되지 않으면 먼저 Streamlit이 내 저장소의 main과 app.py를 보고 있는지 확인하고, 앱 관리 화면의 실행 오류를 확인합니다.


**완료 확인:** 나만의 앱 주소와 첫 화면이 열립니다.

**막히면:** 저장소가 안 보이면 Streamlit의 GitHub 접근 권한에 내 stock-dash가 포함되어 있는지 확인하세요.

## 05 · 화면에서 사용할 키 넣기

**이번 목표:** 시세·재무 키 두 개와 화면 비밀번호만 설정합니다.

① Streamlit의 내 앱 관리 화면 → Settings → Secrets를 엽니다.

② 아래 내용을 복사하고 따옴표 안을 내 값으로 바꿉니다.

```toml
APP_PASSWORD = "나만의 긴 비밀번호"
DATA_GO_KR_SERVICE_KEY = "공공데이터포털 Decoding 인증키"
DART_CRTFC_KEY = "DART 인증키"
```

③ Save 후 앱을 다시 열고 내가 정한 비밀번호를 입력합니다.

**완료 확인:** 로그인 후 내 종목에서 ‘＋ 종목 추가’를 열 수 있습니다.

**막히면:** 이름·등호·따옴표가 예시와 같은지 확인합니다. Supabase를 사용하지 않으면 SUPABASE_URL과 SUPABASE_SERVICE_ROLE_KEY 둘 다 입력하지 않습니다. 기존에 넣었다면 둘 다 지워야 합니다.

**저장 범위:** 이 설정은 실행 서버의 파일에 저장합니다. 웹 호스팅에서는 서버 재시작·재배포로 데이터가 사라질 수 있습니다. 중요한 투자일지는 내 문서에 따로 보관합니다.

## 06 · 대시보드 활용 · 이름 하나로 시작하기

① **내 종목 → ＋ 종목 추가**를 엽니다. 기업 이름을 입력하고 내 목록에 추가를 누릅니다. 종목코드는 알고 있을 때만 선택 항목을 펼쳐 넣습니다. 코드가 없어도 이름을 저장할 수 있습니다.

② **조사 요청 · 최신 내용으로 업데이트**를 엽니다. 만들어진 요청문을 복사해서 GitHub 쓰기가 가능한 Codex 대화창에 보냅니다. 현재 앱의 개인 목록을 AI가 저절로 읽는 것이 아니므로, 요청문에 대상 기업이 들어 있는지 확인합니다.

```text
내 GitHub [내아이디/stock-dash]를 기준으로 작업해줘.
삼성전자와 SK하이닉스를 공식 자료로 조사해줘.
매출·누적 영업이익 성장률, 외국인·기관 수급, 적정주가,
일봉·완료 주봉 추세, 경쟁사 영업이익 순위,
종목 특징과 주력 매출 사업을 쉬운 말로 작성해줘.
CHAT-RESEARCH.md 형식으로 research/의 결과를 갱신해줘.
각 항목에 기준일·기간·출처·계산 근거를 붙이고,
확인할 수 없는 자료는 미확인으로 남겨줘.
개인 계좌 정보와 API 키는 파일에 넣지 마.
```

③ AI가 조사·파일 반영을 끝냈는지 확인하고 **반영된 조사 결과 다시 읽기**를 누릅니다. 새 조사 파일이 배포에 적용되기 전에는 이전 결과가 보일 수 있습니다.

④ **종목 한눈에 보기**에서 영업이익 변화·일봉 추세·조사일을 봅니다. 전체 지표가 필요할 때만 **전체 지표 비교**를 펼칩니다.

⑤ **자세히 볼 종목**에서 기업을 선택합니다. 핵심 요약을 읽고 아래 네 탭으로 이동합니다.

| 화면 | 수강생이 확인할 질문 |
|---|---|
| 어떤 기업인가요? | 무엇을 팔아 매출을 올리나? 설명의 원문 근거는? |
| 실적은 어떤가요? | 전년 같은 누적 기간보다 이익이 늘었나? 경쟁사 비교 기준이 같은가? |
| 주가 흐름 | 외국인·기관의 어느 기간 수급인가? 일봉·주봉은 같은 방향인가? |
| 가격과 확인 사항 | 평가 공식과 가정은 무엇인가? 미확인 자료는 무엇인가? |

**완료 확인:** 자료 하나의 출처와 기준일을 열어 보고, 숫자로 확인한 사실과 AI의 해석을 구분할 수 있습니다.

**자료가 비어 있으면:** ‘조사 필요’는 오류나 0점이 아닙니다. 필요한 원천자료를 아직 확보하지 못했다는 뜻입니다. 초기 삼성전자·SK하이닉스 자료는 연간 결산 예시이며 최신 분기·수급·추세·적정주가가 모두 채워진 자료가 아닙니다.

**기존 API 분석도 사용하려면:** 설정 → 필요한 도구 → 종목 분석에서 공식 데이터 검색·분석을 실행합니다. 증권사 키가 없어도 DART·시세 키로 사용할 수 있습니다. 직접 분석과 채팅 조사 결과의 기준일을 각각 확인하세요.

**계좌를 가져오려면:** 계좌 연결에서 한국투자증권 안내를 따라 설정한 뒤 계좌 불러오기·자동 분석을 누릅니다. 상세 입력법은 [계좌 연결 안내](https://github.com/planxs-ai/stock-dash/blob/main/BROKER-START.md)에 있습니다. 수동 추가와 계좌 연결 중 편한 방식으로 시작하면 됩니다.

## 07 · 나의 판단 한 문장 남기기

**이번 목표:** 숫자를 본 뒤 무엇을 다시 확인할지 정합니다.

① 내 종목의 기업 상세 아래 투자일지 남기기를 펼칩니다. 관심 이유와 재검토 조건을 적고 기록 저장을 누릅니다. 조사 결과가 없는 종목은 설정 → 종목 분석의 투자일지에서 기록할 수 있습니다.

② 같은 내용을 내 문서나 개인 메모에도 복사해 둡니다.

③ 공용 PC에서는 앱과 서비스에서 로그아웃합니다.

**완료 확인:** 공식 숫자 하나와 나의 판단 한 문장을 구분해서 설명할 수 있습니다. 기본 실습은 여기서 끝납니다.

**막히면:** 저장된 데이터가 사라졌다면 다시 입력합니다. 클라우드 DB를 연결하지 않은 호스팅에서는 장기 보존을 보장하지 않습니다.

## 강사용 · DART 공개 자료 수집과 갱신

Streamlit에서 DART 통신이 지연되는 경우에 사용하는 보완 경로입니다. 수강생은 먼저 예제 종목으로 화면을 익힙니다.

① GitHub의 내 stock-dash → Settings → Secrets and variables → Actions → New repository secret을 엽니다.

② Name에 DART_CRTFC_KEY, Secret에 DART 인증키를 입력합니다. Streamlit Secrets와 GitHub Actions Secrets는 별개의 보관함입니다.

③ Actions → Public DART data → Run workflow를 누릅니다. 종목코드를 쉼표로 구분해 최대 10개 입력합니다. 예: 005930,000660.

④ 실행 결과가 초록색이고 public-data 폴더에 해당 종목의 JSON 파일이 생겼는지 확인합니다. 앱에서 종목을 다시 분석하고 수집일을 확인합니다.

수집 대상은 공개 기업 정보·연간 실적·사업 원문·최근 공시입니다. 종목코드와 수집본은 공개 저장소에 남습니다. 개인 보유수량·투자일지·키는 넣지 않습니다. 현재는 수동 갱신이며 자동 예약 갱신이 아닙니다.

기본 앱의 보완 수집 경로는 강사 저장소 planxs-ai/stock-dash입니다. 자신의 Fork에서 수집본까지 독립 운영하려면 providers.py의 cached_report에 있는 공개 저장소 주소를 내아이디/stock-dash로 바꿉니다.

## 선택 확장 · SQL과 저장소 키 연결하기

**목표:** 내 종목과 투자일지를 전산실·집에서 이어서 사용합니다. 이 연결은 선택 사항입니다. 한 단계의 완료 확인을 마친 다음 다음 단계로 넘어갑니다.

### 저장 1 · 내 Supabase 프로젝트 열기

① https://supabase.com/dashboard 에 로그인합니다.

② 내 프로젝트를 선택합니다. 없다면 New project를 눌러 이름을 stock-dash로 만들고 준비가 끝날 때까지 기다립니다.

**완료 확인:** 프로젝트 안에 SQL Editor와 Table Editor 메뉴가 보입니다.

### 저장 2 · SQL 코드 복사하기

SQL은 종목과 일지를 담을 보관함을 만드는 명령입니다. 비밀번호나 API 키를 입력하는 곳이 아닙니다.

① https://github.com/planxs-ai/stock-dash/blob/main/schema.sql 을 엽니다.

② Raw를 눌러 코드만 보이는 화면으로 이동합니다.

③ Ctrl+A → Ctrl+C로 전체 코드를 복사합니다. 아래 코드 전체를 복사해도 같습니다.

```sql
-- One personal dashboard per deployment; access only via backend service key.
create table if not exists public.stock_dash_state (
  id text primary key,
  version bigint not null default 0,
  payload jsonb not null default '{}'::jsonb
);
alter table public.stock_dash_state enable row level security;
revoke all on public.stock_dash_state from anon, authenticated;
grant all on public.stock_dash_state to service_role;
insert into public.stock_dash_state(id, payload)
values ('personal', '{"stocks":[],"journal":[],"runs":[]}')
on conflict (id) do nothing;
```

**완료 확인:** 복사한 내용이 create table 등을 포함하는 SQL이며, 웹페이지 주소나 API 키가 아닙니다.

### 저장 3 · SQL 붙여 넣고 실행하기

① Supabase로 돌아가 내 프로젝트의 SQL Editor를 엽니다.

② New query 또는 + 버튼으로 빈 쿼리를 엽니다.

③ 편집 영역을 클릭하고 Ctrl+V로 붙여 넣습니다. 위아래의 세 개짜리 역따옴표나 sql 글자는 넣지 않습니다.

④ Run을 누릅니다. 결과 영역에 오류가 없는지 확인합니다.

⑤ 왼쪽 Table Editor에서 public → stock_dash_state를 엽니다.

**완료 확인:** id가 personal인 행 하나가 보입니다. 이 코드의 초기 행 삽입은 다시 실행해도 기존 personal 데이터를 덮어쓰지 않습니다.

**막히면:** 오류 문구만 강사에게 보여 주세요. SQL 실행 창에 API 키를 넣지 마세요.

### 저장 4 · 프로젝트 URL 복사하기

① 같은 Supabase 프로젝트 상단의 Connect를 엽니다.

② 연결 안내에서 Project URL 또는 SUPABASE_URL 값을 찾습니다. 화면 구성에 따라 프레임워크 선택 후 표시됩니다.

③ https://로 시작하고 .supabase.co로 끝나는 내 프로젝트 API 주소를 복사합니다.

**완료 확인:** 복사한 값은 https://내프로젝트식별자.supabase.co 형태입니다. supabase.com/dashboard로 시작하는 관리 화면 주소나 postgresql://로 시작하는 DB 접속 문자열은 사용하지 않습니다.

### 저장 5 · service_role 키 찾기

① 같은 프로젝트의 Settings(톱니바퀴) → API Keys를 엽니다.

② Legacy API Keys 또는 anon / service_role 항목이 있는 구역을 찾습니다.

③ service_role 항목에서 Reveal 또는 표시 버튼을 누르고 Copy로 전체 값을 복사합니다.

**완료 확인:** 복사한 항목 이름이 service_role입니다. anon 키·DB 비밀번호·DART 키와 구분합니다.

Supabase의 새 화면에는 Publishable key와 Secret key도 있습니다. service_role은 기존 방식의 서버 키입니다. 현재 교재 코드의 연결 예시는 Legacy service_role 키 기준입니다. Legacy 키가 비활성화되어 보이지 않으면 임의로 다른 값을 넣지 말고 강사에게 화면의 항목 이름만 알려 주세요.

이 키는 서버가 내 DB를 읽고 쓰는 열쇠입니다. 실제 값은 채팅·교재·GitHub 코드·스크린샷에 넣지 않습니다.

### 저장 6 · Streamlit Secrets에 넣기

① https://share.streamlit.io 에서 내 앱을 찾고 앱 관리 화면의 Settings → Secrets를 엽니다.

② 아래 두 줄을 기존 설정 아래에 추가합니다.

```toml
SUPABASE_URL = "여기에 저장 4에서 복사한 Project URL"
SUPABASE_SERVICE_ROLE_KEY = "여기에 저장 5에서 복사한 service_role 키"
```

왼쪽 SUPABASE_URL과 SUPABASE_SERVICE_ROLE_KEY는 그대로 둡니다. 오른쪽 따옴표 안의 설명만 실제 값으로 바꾸고, 따옴표는 남깁니다. 각 이름은 한 번씩만 적습니다.

**전체 모양 예시 · 따옴표 안은 전부 내 값으로 교체**

```toml
APP_PASSWORD = "내가 정한 대시보드 비밀번호"
DATA_GO_KR_SERVICE_KEY = "공공데이터포털 Decoding 인증키"
DART_CRTFC_KEY = "DART 인증키"
SUPABASE_URL = "https://내프로젝트식별자.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "service_role 항목에서 복사한 전체 값"
```

③ Save를 누르고 앱을 재시작(Reboot)합니다.

**완료 확인:** SQL 코드는 Supabase SQL Editor에, URL과 키는 Streamlit Secrets에 각각 넣었습니다. 이번 과정에서 GitHub Actions Secrets에 입력할 필요는 없습니다.

### 저장 7 · 실제로 연결됐는지 확인하기

① 앱에 비밀번호로 로그인합니다. 임시 실습 중이었다면 로그아웃하거나 앱을 새로 열어 다시 로그인합니다.

② 화면에 클라우드 저장 안내가 나오는지 확인합니다.

③ 종목 한 개를 저장합니다.

④ Supabase Table Editor → stock_dash_state → personal 행의 payload에 stocks 내용이 들어갔는지 확인합니다.

⑤ 다른 기기에서 같은 앱 주소로 로그인해 같은 종목이 보이는지 확인합니다.

**완료 확인:** 앱에 저장한 종목이 DB와 다른 기기에서 모두 확인됩니다. 키를 입력했다는 사실만으로 연결 성공으로 판단하지 않습니다.

**저장 오류가 나면 확인할 순서**

1. URL과 키가 같은 Supabase 프로젝트에서 나온 것인가?
2. 키 항목이 anon이 아니라 service_role인가?
3. SQL 실행 후 stock_dash_state와 personal 행이 있는가?
4. Secrets에 예시 설명이 남지 않았고 각 이름이 한 번만 있는가?
5. 앱을 재시작했고 임시 실습 모드에서 나왔는가?

기존 로컬 자료는 DB로 자동 이전되지 않습니다. 연결 후 종목을 다시 등록하세요. 개인별 별도 프로젝트를 사용합니다.

공식 키 안내: https://supabase.com/docs/guides/getting-started/api-keys

## 선택 소개 · ChatGPT에서 달력 연결하기

ChatGPT의 설정 → 앱에서 Google Calendar를 찾아 연결하고 Google 로그인과 권한 동의를 진행합니다. 앱/플러그인 메뉴 표시는 환경에 따라 다를 수 있습니다. 수강생이 Cloud Console에서 API 키를 만들 필요는 없습니다.

먼저 “내 캘린더에서 다음 주 일정을 확인해 줘”로 연결을 확인합니다. 일정 생성은 해당 계정에 제공된 동작과 권한을 확인한 뒤 사용합니다. ChatGPT 연결만으로 stock-dash의 데이터가 자동 전달되거나 예약 실행되는 것은 아닙니다.

공식 안내: https://help.openai.com/en/articles/11487775-connectors-in-chatgpt

코드·분석 규칙 상세는 README를 참고합니다. 캘린더 직접 API와 예약 코드는 개발자 참고로만 남기며 기본 비활성 상태를 유지합니다.

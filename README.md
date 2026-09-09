# stock-dash · 내 관심종목 퀀트 보드

종목 저장 → 공식 시세·결산 실적 조회 → 경쟁사 비교 → 나의 가정으로 적정주가 계산 → 투자일지 → 주간 점검 → Google Calendar 기록.

개인별로 복사해서 사용하는 수업용 실행 프로젝트입니다. 한 배포와 한 DB는 한 사람만 사용합니다. 여러 수강생이 같은 DB를 공유하지 않습니다.

## 1. 먼저 화면 열기

Python 3.11 이상을 설치하고 이 폴더에서 실행합니다. Windows는 `start.bat`을 더블클릭할 수 있습니다.

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

처음에는 가상 종목 화면이 열립니다. 실제 종목이나 실제 수익률이 아닙니다.

`.env.example`을 `.env`로 복사하고 `APP_PASSWORD`에 나만의 긴 비밀번호를 입력한 뒤 재실행하세요. 비밀번호를 입력하면 종목 보관함이 열립니다. 비밀번호가 없으면 개인 데이터는 열리지 않습니다.

## 2. 공식 API 키 준비

| 어디서 | 순서 | 저장할 이름 |
|---|---|---|
| [공공데이터포털](https://www.data.go.kr/data/15094808/openapi.do) | 로그인 → 금융위원회 주식시세정보 → 활용신청 → 승인 확인 → 일반 인증키 복사 | `DATA_GO_KR_SERVICE_KEY` |
| [OpenDART](https://opendart.fss.or.kr/) | 로그인 → 인증키 신청 → 사용 목적 입력 → 인증키 확인 | `DART_CRTFC_KEY` |

키를 `.env`의 같은 이름 오른쪽에 붙여 넣습니다. 인증키를 AI 채팅·코드·커밋·스크린샷에 넣지 마세요. 공공데이터 키는 일반 인증키의 디코딩 값을 권장합니다.

시세는 `apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService/getStockPriceInfo`, 인증은 `serviceKey`입니다. 장중 실시간 시세가 아니라 기준일이 있는 일별 시세입니다. 최근 10일에서 조회 가능한 날짜를 찾습니다.

재무는 `opendart.fss.or.kr/api/fnlttSinglAcntAll.json`, 인증은 `crtfc_key`입니다. `corpCode.xml`로 종목코드를 고유번호로 바꾸고, 사업보고서 `reprt_code=11011`의 3개년 매출·영업이익을 읽습니다. 기존 수업의 `fnlttSinglAcnt.json`·`fnlttMultiAcnt.json`은 주요 계정 조회용이고, 이 구현은 전체 계정 API를 사용합니다. 세 해 모두 연결이 있으면 연결, 없으면 세 해 모두 별도로 맞춥니다. 해당 연도 보고서가 없다면 기준연도를 낮추세요.

[KRX OpenAPI](https://openapi.krx.co.kr/)는 이 버전에서 호출하지 않습니다. 연구·백테스트 확장은 별도 이용 승인과 최신 이용조건 확인 후 진행합니다.

## 3. 나의 종목 분석하기

1. 왼쪽에 종목명과 6자리 코드, 보유/관심 구분을 넣고 **종목 저장**.
2. **분석·비교**에서 기준 결산연도와 같은 업종 경쟁사 코드를 입력. 경쟁력 점수에는 비교 가능한 경쟁사가 2개 이상 필요합니다.
3. **공식 데이터 분석**을 누르고 기준일·연결/별도·공시 원문을 확인.
4. 예상 영업이익, EV/영업이익 배수, 순차입금, 희석 주식수를 직접 확인해서 **가정으로 계산·저장**.
5. 주요 사업과 엣지는 공시를 읽고 근거 문장·링크를 저장. **투자일지**에는 보유 이유와 재검토 조건을 기록.

시세·실적·수치 비교는 자동입니다. 사업 요약과 엣지는 원문 검토 방식이며, LLM 자동 요약 API는 아직 연결하지 않았습니다. 적정주가도 자동 예측이 아니라 입력한 가정의 계산 결과입니다.

## 4. 전산실과 집에서 이어 쓰기

GitHub는 코드 보관함이고 Secrets는 서버 실행용 비밀 보관함입니다. 종목과 일지는 Supabase DB에 저장합니다. GitHub Secrets를 앱 브라우저가 읽는 구조가 아닙니다.

1. 내 GitHub에 이 프로젝트를 `stock-dash`로 업로드합니다. 수강생은 원본이 공개된 뒤 **Fork**로 자기 계정에 복사할 수 있습니다. Fork에는 원본의 Secrets가 복사되지 않습니다.
2. [Supabase](https://supabase.com/)에서 개인 프로젝트를 만듭니다. SQL Editor를 열고 `schema.sql` 전체를 붙여 넣어 실행합니다.
3. 프로젝트 URL과 서버용 `service_role` 키를 확인합니다. `.env`의 `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`에 넣습니다.
4. [Streamlit Community Cloud](https://share.streamlit.io/)에서 GitHub 저장소와 `app.py`를 선택합니다. 호스팅 서비스의 Secrets에는 아래 TOML을 설정합니다.

```toml
APP_PASSWORD = "나만의 긴 비밀번호"
SUPABASE_URL = "https://내프로젝트.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "서버용 키"
DATA_GO_KR_SERVICE_KEY = "일반 인증키"
DART_CRTFC_KEY = "DART 인증키"
```

이제 집에서는 같은 앱 주소와 비밀번호로 들어갑니다. 가능하면 호스팅 서비스의 비공개 접근 제어도 함께 사용하세요. 공용 PC에서는 로그아웃하고 내려받은 `.env`를 남기지 마세요. 로컬 저장만 쓰면 `data/state.json`에 저장되며 다른 PC와 동기화되지 않습니다.

## 5. Google Calendar 연결

1. Google Calendar 설정에서 **새 캘린더 만들기** → 이름을 `나의 투자 점검`으로 정합니다.
2. [Google Cloud Console](https://console.cloud.google.com/)에서 프로젝트를 만들고 **API 및 서비스 → 라이브러리 → Google Calendar API → 사용**을 누릅니다.
3. **IAM 및 관리자 → 서비스 계정**에서 계정을 만듭니다. 프로젝트 전체 관리자 역할은 주지 않습니다.
4. 서비스 계정의 **키 → 키 추가 → 새 키 만들기 → JSON**을 선택합니다. 이 파일은 비밀키입니다.
5. JSON의 `client_email` 주소를 복사합니다. Calendar에서 `나의 투자 점검`의 공유 설정에 이 주소를 추가하고 **일정 변경** 권한을 줍니다. 조직에서 서비스 계정 공유를 막으면 관리자 정책 확인이 필요합니다.
6. 같은 Calendar 설정의 **캘린더 통합 → 캘린더 ID**를 복사합니다. 계정 이메일이나 표시 이름과 다를 수 있습니다.
7. GitHub 저장소 **Settings → Secrets and variables → Actions → New repository secret**에 아래 6개를 저장합니다.

| Secret 이름 | 값 |
|---|---|
| `SUPABASE_URL` | 앱과 같은 DB URL |
| `SUPABASE_SERVICE_ROLE_KEY` | 앱과 같은 서버 DB 키 |
| `DATA_GO_KR_SERVICE_KEY` | 시세 API 키 |
| `DART_CRTFC_KEY` | DART 키 |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | JSON 파일 내용 전체, 중괄호 포함 |
| `GOOGLE_CALENDAR_ID` | 전용 캘린더 ID |

JSON 파일은 저장소에 업로드하지 않습니다. 알림은 캘린더 앱의 알림 권한이 켜져 있어야 보입니다. 초대 이메일이나 다른 사람에게 보내는 메시지는 만들지 않습니다.

## 6. 예약 실행은 미리보기부터

1. 앱에서 한 종목을 실제 데이터로 분석한 뒤 **자동 점검 → 이 종목을 주간 점검에 포함 → 저장**.
2. GitHub **Actions → Weekly investment review → Run workflow**에서 `write_calendar`를 끈 채 실행합니다. 최초 미리보기는 데이터 조회만 하며 DB·캘린더에 쓰지 않습니다. 로그의 `processed`가 1 이상이고 `failed`가 0인지 확인합니다.
3. 같은 화면에서 `write_calendar`를 켜고 다시 실행합니다. DB의 분석·일지와 달력 일정을 확인합니다.
4. 자동화를 켜려면 **Settings → Secrets and variables → Actions → Variables**에 `ENABLE_SCHEDULE=true`, `CALENDAR_WRITE=true`를 추가합니다. 기본값은 꺼짐입니다.

예약은 UTC 일요일 23:17, 한국 월요일 08:17입니다. 일정은 해당 주 월요일 20:00에 15분 동안 만들고 10분 전 알림을 설정합니다. 같은 종목·같은 주에 재실행하면 같은 일정을 갱신합니다. 주중 수동 실행도 해당 주 월요일 일정이므로 이미 지난 시간일 수 있습니다. GitHub 예약은 지연될 수 있고 공개 저장소는 장기 비활동 시 예약이 중지될 수 있습니다.

종목 조회 실패 시 이전 분석은 덮어쓰지 않습니다. 캘린더 기록까지 성공한 종목을 갱신합니다. 실적 변화와 이전/현재 가격은 DB 일지에 기록하고 캘린더에는 점검 안내만 남깁니다.

## 점수 읽는 법

수업용 규칙이며 검증된 투자 예측 모델이 아닙니다. 각 항목은 20점입니다.

| 항목 | 계산 |
|---|---|
| 성장성 | 매출 증가율 점수 `clip((증가율+10)/4,0,10)` + 영업이익 증가율 점수 `clip((증가율+20)/7,0,10)` |
| 수익성 | `clip(영업이익률/25×20,0,20)` |
| 경쟁력 | 비교 기업 대비 매출성장률과 이익률 순위, 각 10점; 같은 업종 선정은 사용자 확인 |
| 엣지 | 수주·고객 인증·기술/특허·반복매출·가격결정력의 확인된 공시 근거마다 4점 |
| 가치 | `clip((Base 적정가/현재가−1)×100/2,0,20)` |

전년 이익이 0 이하라 성장률 계산이 무의미하거나 근거가 미확인인 항목은 보류합니다. 5항목이 모두 있어야 종합 점수가 나옵니다. 엣지는 실제 원문 내용의 자동 진위 검증을 하지 않습니다.

가격 공식은 `(예상 영업이익×EV/OP 배수−순차입금)÷희석 주식수`입니다. Bear는 이익 85%·배수 90%, Bull은 이익 115%·배수 110%입니다. 임의의 민감도 예시이며 통계적 신뢰구간이 아닙니다. 금융업 및 복수 주식종류에는 별도 모델이 필요합니다.

## 파일과 확인 방법

`app.py` 화면 · `providers.py` 공식 데이터 · `analysis.py` 계산 · `storage.py` 저장 · `calendar_sync.py` 일정 · `weekly_review.py` 예약 실행 · `.github/workflows` 자동화.

```bash
python -m unittest discover -s tests -v
```

실제 키를 발급받은 뒤 실제 데이터 조회와 Calendar 권한을 최종 확인해야 합니다. 샘플 모드와 테스트는 실계정 연결 성공을 보장하지 않습니다.

공식 도움말: [DART 개발가이드](https://opendart.fss.or.kr/guide/main.do) · [Supabase REST API](https://supabase.com/docs/guides/api/rest) · [Google Calendar 일정 생성](https://developers.google.com/workspace/calendar/api/v3/reference/events/insert) · [GitHub 예약 실행](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule) · [Streamlit Secrets](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management).

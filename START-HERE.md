# 수강생 실습 안내 · 내 종목 하나 분석하기

**오늘 목표: 종목 한 개 입력 → 공식 숫자 확인 → 나의 판단 한 문장 기록.**

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

## 04 · 내 대시보드 주소 만들기

**이번 목표:** 설치 없이 브라우저에서 여는 화면을 만듭니다.

① https://share.streamlit.io 에서 GitHub 계정으로 로그인합니다.

② Create app에서 내아이디/stock-dash 저장소를 고릅니다.

③ Branch는 main, Main file path는 app.py로 정하고 배포합니다.

④ 처음 보이는 가상 종목 화면에서 버튼과 탭을 살펴봅니다.


**완료 확인:** 나만의 앱 주소가 열리고 가상 데이터 안내가 보입니다.

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

**완료 확인:** 왼쪽에 종목 저장 입력칸이 나타납니다.

**막히면:** 이름·등호·따옴표가 예시와 같은지 확인합니다. Supabase를 사용하지 않으면 SUPABASE_URL과 SUPABASE_SERVICE_ROLE_KEY 둘 다 입력하지 않습니다. 기존에 넣었다면 둘 다 지워야 합니다.

**저장 범위:** 이 설정은 실행 서버의 파일에 저장합니다. 웹 호스팅에서는 서버 재시작·재배포로 데이터가 사라질 수 있습니다. 중요한 투자일지는 내 문서에 따로 보관합니다.

## 06 · 내 종목 한 개 분석하기

**이번 목표:** 실제 종목의 기준일과 숫자를 직접 확인합니다.

① 왼쪽에 종목명·6자리 코드·보유 또는 관심·관심 이유를 입력하고 종목 저장을 누릅니다.

② 분석·비교에서 사업보고서가 나온 결산연도를 고릅니다. 경쟁사 입력은 첫 조회에서는 비워도 됩니다.

③ 공식 데이터 분석을 누릅니다.

④ 기준 종가의 날짜, 3개년 결산 매출·영업이익, 연결/별도 표시를 확인합니다.

⑤ 공시 원문 버튼으로 숫자 하나를 직접 대조합니다.


**완료 확인:** 내 종목의 실제 숫자와 공시 원문을 대조했습니다.

**막히면:** 조회 실패 시 키 승인 상태와 결산연도를 확인합니다. 먼저 경쟁사를 비우고 종목 한 개만 조회하세요. 가상 화면은 실제 조회 성공이 아닙니다.

## 07 · 나의 판단 한 문장 남기기

**이번 목표:** 숫자를 본 뒤 무엇을 다시 확인할지 정합니다.

① 투자일지에 관심 이유와 재검토 조건을 한 문장씩 적습니다.

② 같은 내용을 내 문서나 개인 메모에도 복사해 둡니다.

③ 공용 PC에서는 앱과 서비스에서 로그아웃합니다.

**완료 확인:** 공식 숫자 하나와 나의 판단 한 문장을 구분해서 설명할 수 있습니다. 기본 실습은 여기서 끝납니다.

**막히면:** 저장된 데이터가 사라졌다면 다시 입력합니다. 클라우드 DB를 연결하지 않은 호스팅에서는 장기 보존을 보장하지 않습니다.

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

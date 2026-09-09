"""Local DART check. No key storage and no third-party packages."""
import getpass
import json
import socket
import time
import urllib.error
import urllib.parse
import urllib.request


def check(key):
    params = urllib.parse.urlencode({'crtfc_key': key.strip(), 'corp_code': '00126380'})
    request = urllib.request.Request('https://opendart.fss.or.kr/api/company.json?' + params)
    started = time.monotonic()
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            data = json.loads(response.read(100_000))
        status = str(data.get('status', ''))
        messages = {'000': '정상: DART 연결과 인증이 성공했습니다.',
                    '010': 'DART에 등록되지 않은 키입니다.',
                    '011': '사용할 수 없는 키입니다. DART 인증키 상태를 확인하세요.',
                    '012': 'DART에서 접속 IP를 허용하지 않았습니다.',
                    '020': 'DART 호출 한도를 초과했습니다.',
                    '800': 'DART 시스템 점검 중입니다.',
                    '901': 'DART 계정의 개인정보 보유기간이 만료됐습니다.'}
        code = status if status.isdigit() and len(status) == 3 else 'unknown'
        return f"DART 코드: {code}\n{messages.get(status, 'DART가 응답했으나 정상 인증으로 확인되지 않았습니다.')}\n소요 시간: {time.monotonic()-started:.1f}초"
    except urllib.error.HTTPError as error:
        return f'HTTP {error.code}: 서버가 요청을 거절하거나 오류를 반환했습니다.'
    except (TimeoutError, socket.timeout):
        return '시간 초과: 이 PC에서도 DART 응답을 받지 못했습니다. 인증 여부는 알 수 없습니다.'
    except urllib.error.URLError:
        return '연결 실패: 이 PC의 네트워크·DNS·보안 연결을 확인하세요. 인증 여부는 알 수 없습니다.'
    except (ValueError, OSError):
        return '정상적인 JSON 응답을 읽지 못했습니다. 인증 여부는 알 수 없습니다.'


def main():
    print('DART PC 연결 진단 · 키는 저장하거나 출력하지 않습니다.\n')
    key = getpass.getpass('DART 키를 붙여 넣고 Enter를 누르세요 (입력 내용은 보이지 않습니다): ')
    if not key.strip():
        print('키를 입력하지 않아 종료합니다.')
    else:
        print('\n확인 중입니다. 약 15초 기다려 주세요.\n')
        print(check(key))
    key = None
    print('\n위 결과 문구만 복사해서 보내 주세요. 키는 보내지 마세요.')
    input('\n종료하려면 Enter를 누르세요.')


if __name__ == '__main__':
    main()

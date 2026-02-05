#!/usr/bin/env python3
"""
Gmail API Client - OAuth2 인증 (Gmail 전용)
"""

import os
import pickle
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API 스코프
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
]

# OAuth 클라이언트 설정
CREDS_DIR = Path(os.getenv('GOOGLE_CREDS_DIR', str(Path.home() / 'work/vault-worv/.credentials')))
CREDENTIALS_FILE = CREDS_DIR / 'oauth_client.json'
TOKEN_FILE = CREDS_DIR / 'google_token.pickle'


def get_gmail_service():
    """Gmail API 서비스 객체 반환 (OAuth2 방식)"""
    creds = None

    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                raise FileNotFoundError(
                    f"OAuth credentials 파일이 없습니다: {CREDENTIALS_FILE}\n"
                    "Google Cloud Console에서 OAuth 2.0 클라이언트 ID를 생성하고\n"
                    "credentials.json을 다운로드하여 위 경로에 저장하세요."
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)


def _get_service_with_service_account():
    """Service Account + 도메인 위임 방식으로 Gmail 서비스 생성"""
    creds = service_account.Credentials.from_service_account_file(
        str(SERVICE_ACCOUNT_FILE),
        scopes=SCOPES
    )

    # 특정 사용자를 대신하여 작업 (도메인 전체 위임 필요)
    delegated_creds = creds.with_subject(DELEGATED_USER)

    service = build('gmail', 'v1', credentials=delegated_creds)
    return service


def _get_service_with_oauth():
    """OAuth2 클라이언트 방식으로 Gmail 서비스 생성"""
    creds = None

    # 저장된 토큰 확인
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    # 토큰이 없거나 만료된 경우
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # 토큰 갱신
            creds.refresh(Request())
        else:
            # 새로운 인증 필요
            if not CREDENTIALS_FILE.exists():
                raise FileNotFoundError(
                    f"OAuth credentials 파일이 없습니다: {CREDENTIALS_FILE}\n"
                    "Google Cloud Console에서 OAuth 2.0 클라이언트 ID를 생성하고\n"
                    "credentials.json을 다운로드하여 위 경로에 저장하세요."
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES
            )
            creds = flow.run_local_server(port=0)

        # 토큰 저장
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    # Gmail API 서비스 생성
    service = build('gmail', 'v1', credentials=creds)
    return service


def get_user_email(service):
    """현재 인증된 사용자의 이메일 주소 반환"""
    profile = service.users().getProfile(userId='me').execute()
    return profile.get('emailAddress', 'me')


def mark_as_read(service, message_ids):
    """
    메일을 읽음 상태로 변경.

    Args:
        service: Gmail API 서비스 객체
        message_ids: 메일 ID 목록 (단일 ID 또는 리스트)

    Returns:
        성공한 메일 수
    """
    if isinstance(message_ids, str):
        message_ids = [message_ids]

    success_count = 0
    for msg_id in message_ids:
        try:
            service.users().messages().modify(
                userId='me',
                id=msg_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            success_count += 1
        except Exception as e:
            print(f"메일 {msg_id} 처리 실패: {e}")

    return success_count


def mark_as_unread(service, message_ids):
    """메일을 읽지 않음 상태로 변경."""
    if isinstance(message_ids, str):
        message_ids = [message_ids]

    success_count = 0
    for msg_id in message_ids:
        try:
            service.users().messages().modify(
                userId='me',
                id=msg_id,
                body={'addLabelIds': ['UNREAD']}
            ).execute()
            success_count += 1
        except Exception as e:
            print(f"메일 {msg_id} 처리 실패: {e}")

    return success_count


if __name__ == '__main__':
    # 테스트: 인증 및 프로필 확인
    try:
        service = get_gmail_service()
        email = get_user_email(service)
        print(f"Gmail API 연결 성공!")
        print(f"인증된 계정: {email}")
    except FileNotFoundError as e:
        print(f"오류: {e}")
    except Exception as e:
        print(f"Gmail API 연결 실패: {e}")

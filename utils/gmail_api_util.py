import os
import re
import time
import base64
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# 1. Define explicit absolute paths based on this file's location
UTILS_DIR = Path(__file__).resolve().parent
CLIENT_SECRETS_FILE = UTILS_DIR / "client_secret.json"
TOKEN_FILE = UTILS_DIR / "token.json"

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']

def get_oauth_gmail_service():
    """Authenticates via OAuth 2.0 safely inside a headless environment."""
    creds = None
    
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CLIENT_SECRETS_FILE.exists():
                raise FileNotFoundError(f"Missing OAuth file at: {CLIENT_SECRETS_FILE}")
            
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRETS_FILE), SCOPES)
            
            # FIXED FOR HEADLESS: Instructs Google not to open a desktop browser automatically
            creds = flow.run_local_server(
                host='localhost',
                port=8080,
                open_browser=False
            )
            
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)



def fetch_otp_via_oauth(sender_email, timeout=60):
    """Polls Gmail API for unread matching emails and extracts a 6-digit OTP."""
    service = get_oauth_gmail_service()
    start_time = time.time()
    query = f"from:{sender_email} is:unread"
    
    while time.time() - start_time < timeout:
        try:
            results = service.users().messages().list(userId='me', q=query).execute()
            messages = results.get('messages', [])
            
            if messages:
                latest_msg_id = messages[0]['id']  # First item is the newest match
                message = service.users().messages().get(userId='me', id=latest_msg_id, format='full').execute()
                
                # Check snippet first for quick retrieval
                body_text = message.get('snippet', '')
                
                # Fallback: Extract full text payload if snippet is cut off
                payload = message.get('payload', {})
                parts = payload.get('parts', [])
                for part in parts:
                    if part.get('mimeType') == 'text/plain':
                        data = part.get('body', {}).get('data', '')
                        if data:
                            body_text += base64.urlsafe_b64decode(data).decode('utf-8')
                
                otp_match = re.search(r'\b\d{6}\b', body_text)
                if otp_match:
                    # Remove 'UNREAD' label so subsequent test loops don't look at this email
                    service.users().messages().batchModify(
                        userId='me',
                        body={'ids': [latest_msg_id], 'removeLabelIds': ['UNREAD']}
                    ).execute()
                    return otp_match.group(0)
                    
        except Exception as e:
            print(f"Gmail API polling skip: {e}")
            
        time.sleep(5)
        
    raise TimeoutError(f"OTP from {sender_email} not found within {timeout} seconds via OAuth.")

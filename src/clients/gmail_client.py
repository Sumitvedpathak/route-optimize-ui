# src/tools/gmail_tool.py
import os
import os.path 
import base64
import re
from html import unescape
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def _materialize_secret_json(
    env_names: tuple[str, ...],
    fallback_path: Path,
    tmp_filename: str,
) -> Path:
    """
    Prefer JSON from first set Cloud Run secret env var, else local file path.
    Secret-as-env: map Secret Manager to e.g. GMAIL_TOKEN_JSON, GMAIL_CREDENTIALS_JSON.
    """
    for env_name in env_names:
        secret_value = os.getenv(env_name, "").strip()
        if secret_value:
            tmp_path = Path("/tmp") / tmp_filename
            tmp_path.write_text(secret_value, encoding="utf-8")
            return tmp_path
    return fallback_path


# Match common Secret Manager names (GMAIL_CREDENTIALS_JSON vs GMAIL_CREDS_JSON)
credentials_file = _materialize_secret_json(
    ("GMAIL_CREDS_JSON", "GMAIL_CREDENTIALS_JSON"),
    PROJECT_ROOT / "g_creds.json",
    "g_creds.json",
)
token_file = _materialize_secret_json(
    ("GMAIL_TOKEN_JSON",),
    PROJECT_ROOT / "token.json",
    "token.json",
)

def _decode_body_data(data: str) -> str:
    if not data:
        return ""
    try:
        decoded = base64.urlsafe_b64decode(data.encode("utf-8"))
        return decoded.decode("utf-8", errors="ignore")
    except Exception:
        return ""


def _strip_html(html: str) -> str:
    if not html:
        return ""
    text = re.sub(r"<[^>]+>", " ", html)
    text = unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _extract_body(payload: dict) -> str:
    if not payload:
        return ""

    mime_type = payload.get("mimeType", "")
    body_data = payload.get("body", {}).get("data", "")

    if mime_type == "text/plain" and body_data:
        return _decode_body_data(body_data).strip()

    parts = payload.get("parts", [])
    html_fallback = ""
    for part in parts:
        part_body = _extract_body(part)
        if part_body:
            if part.get("mimeType") == "text/plain":
                return part_body
            if part.get("mimeType") == "text/html" and not html_fallback:
                html_fallback = _strip_html(part_body)

    if mime_type == "text/html" and body_data:
        return _strip_html(_decode_body_data(body_data))

    if body_data:
        return _decode_body_data(body_data).strip()

    return html_fallback

def get_gmail_credentials():
    """Handles the OAuth2.0 token flow."""
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Cloud Run / servers: no browser for OAuth. Need token + client JSON via secrets.
            if not Path(credentials_file).exists():
                raise FileNotFoundError(
                    "Gmail client secrets not found. For Cloud Run, map secrets to env vars: "
                    "GMAIL_TOKEN_JSON (authorized user token JSON) and "
                    "GMAIL_CREDENTIALS_JSON or GMAIL_CREDS_JSON (OAuth client JSON). "
                    "Local dev: place g_creds.json and token.json in the project root."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_file), SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_file, 'w', encoding='utf-8') as token:
            token.write(creds.to_json())
    return creds

def fetch_email_content(subject_name: str):
    """
    Searches for an email with the specific subject and returns the body.
    """
    try:
        creds = get_gmail_credentials()
        service = build('gmail', 'v1', credentials=creds)

        # Search query: finds the most recent email with this exact subject
        query = f"subject:({subject_name})"
        results = service.users().messages().list(userId='me', q=query, maxResults=1).execute()
        messages = results.get('messages', [])

        if not messages:
            return f"No emails found with subject: {subject_name}"

        # Fetch the message details
        message = service.users().messages().get(userId='me', id=messages[0]['id'], format='full').execute()
        
        payload = message.get('payload', {})
        body = _extract_body(payload)
        if body:
            return body

        # Fallback to snippet only when full body is unavailable
        return message.get('snippet', '')

    except HttpError as error:
        return f"An error occurred: {error}"

# print(fetch_email_content("Route"))
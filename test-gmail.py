import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# This must match the scope you added in the Google Cloud Console
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def test_connection():
    creds = None
    # 1. Look for existing token
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # 2. If no valid token, start the login flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("No valid token found. Opening browser for login...")
            flow = InstalledAppFlow.from_client_secrets_file('g_creds.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # 3. Save the token for the next time
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            print("Success! 'token.json' has been created.")

    # 4. Try to fetch the last 3 email subjects to prove it works
    service = build('gmail', 'v1', credentials=creds)
    results = service.users().messages().list(userId='me', maxResults=3).execute()
    messages = results.get('messages', [])

    print("\n--- Recent Email Subjects ---")
    for msg in messages:
        m = service.users().messages().get(userId='me', id=msg['id']).execute()
        # Find the 'Subject' in headers
        subject = [h['value'] for h in m['payload']['headers'] if h['name'] == 'Subject']
        print(f"Subject: {subject[0] if subject else 'No Subject'}")

if __name__ == "__main__":
    test_connection()
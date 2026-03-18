import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.agents import create_agent

try:
    from clients.gmail_client import fetch_email_content
    from constants import GMAIL_SYSTEM_PROMPT
except ModuleNotFoundError:
    SRC_ROOT = Path(__file__).resolve().parents[1]
    if str(SRC_ROOT) not in sys.path:
        sys.path.append(str(SRC_ROOT))
    from clients.gmail_client import fetch_email_content
    from constants import GMAIL_SYSTEM_PROMPT

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def extract_itinerary_data(email_text: str):

    
    model = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)
    agent = create_agent(model=model, system_prompt=GMAIL_SYSTEM_PROMPT)

    response = agent.invoke({"messages": [{"role": "user", "content": email_text}]})
    messages = response.get("messages", []) if isinstance(response, dict) else []
    ai_message = messages[-1] if messages else None
    if ai_message is None:
        return {}

    content = ai_message.content
    if isinstance(content, str):
        return json.loads(content)

    text_content = "".join(
        part.get("text", "")
        for part in content
        if isinstance(part, dict)
    )
    return json.loads(text_content) if text_content else {}

@tool(
    "get_routedetails_from_email",
    description="Fetches the email content and extracts the all stop-over addresses. It may have source and destination addresses as well.",
)
def get_routedetails_from_email(email_subject: str):
    """Fetches the email content and extracts the all stop-over addresses. It may have source and destination addresses as well."""
    print("Fetching email content.....")
    email_text = fetch_email_content(email_subject)
    print("Extracting data from email.....")
    data = extract_itinerary_data(email_text)
    return data

# print(get_routedetails_from_email("Route"))

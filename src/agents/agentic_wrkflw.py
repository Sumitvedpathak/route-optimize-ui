import os
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_agent
from dotenv import load_dotenv
from agents.gmail_agent import get_routedetails_from_email
from agents.route_agent import trigger_gmap_agent
from constants import Agentic_Workflow_System_Prompt

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
_agent = None

def get_agentic_workflow_agent():
    global _agent
    if _agent is None:
        model = ChatAnthropic(model="claude-sonnet-4-6", api_key=ANTHROPIC_API_KEY)
        _agent = create_agent(
            model=model,
            tools=[get_routedetails_from_email, trigger_gmap_agent],
            system_prompt=Agentic_Workflow_System_Prompt,
        )
    return _agent

async def trigger_agentic_workflow_agent(user_request):
    agent = get_agentic_workflow_agent()
    if isinstance(user_request, list):
        # Already a valid chat history payload.
        messages = user_request
    else:
        # Single-turn user text.
        messages = [{"role": "user", "content": str(user_request)}]
    result = await agent.ainvoke({"messages": messages})
    return result
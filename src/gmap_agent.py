import os
import asyncio
from dotenv import load_dotenv
# from langchain.chat_models import init_chat_model
from langchain_anthropic import ChatAnthropic
from langchain.tools import tool
from langchain.agents import create_agent
from api_client import get_route_data as fetch_route_data
from constants import Google_Maps_System_Prompt

load_dotenv()


# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
_agent = None
_agent_lock = asyncio.Lock()

@tool(
    "get_route_data_tool",
    description="Gets the optimized routes between source and destination and all the address in between, which are called waypoints",
)
async def get_route_data_tool(source: str, destination: str, waypoints: list[str] = None):
    print(f"Getting route data from {source} to {destination} with waypoints {waypoints}")
    return await fetch_route_data(source, destination, waypoints)

def get_gmap_system_prompt():
    return Google_Maps_System_Prompt

async def get_gmap_agent():
    global _agent
    if _agent is not None:
        return _agent

    async with _agent_lock:
        if _agent is None:
            model = ChatAnthropic(
                model="claude-sonnet-4-6",
                api_key=ANTHROPIC_API_KEY
            )
            _agent = create_agent(
                model=model,
                tools=[get_route_data_tool]
            )
    return _agent

async def trigger_gmap_agent(message_history: list[dict]):
    agent = await get_gmap_agent()
    result = await agent.ainvoke({"messages": message_history})
    return result
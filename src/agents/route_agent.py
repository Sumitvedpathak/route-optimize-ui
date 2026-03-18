import os
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv
# from langchain.chat_models import init_chat_model
from langchain_anthropic import ChatAnthropic
from langchain.tools import tool
from langchain.agents import create_agent

try:
    from clients.gmap_api_client import get_route_data as fetch_route_data
    from constants import Google_Maps_System_Prompt
except ModuleNotFoundError:
    SRC_ROOT = Path(__file__).resolve().parents[1]
    if str(SRC_ROOT) not in sys.path:
        sys.path.append(str(SRC_ROOT))
    from clients.gmap_api_client import get_route_data as fetch_route_data
    from constants import Google_Maps_System_Prompt

load_dotenv()


ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
_agent = None
_agent_lock = asyncio.Lock()

# @tool(
#     "get_route_data_tool",
#     description="Gets the optimized routes between source and destination and all the address in between, which are called waypoints.",
# )
async def get_route_data_tool(source: str, destination: str, waypoints: list[str] = None):
    """Fetch optimized route data from source to destination via route API."""
    print(f"Getting route data from {source} to {destination} with waypoints {waypoints}")
    return await fetch_route_data(source, destination, waypoints)

async def get_gmap_agent():
    global _agent
    if _agent is not None:
        return _agent

    async with _agent_lock:
        if _agent is None:
            model = ChatAnthropic(model="claude-sonnet-4-6",api_key=ANTHROPIC_API_KEY)
            _agent = create_agent(model=model,tools=[get_route_data_tool],system_prompt=Google_Maps_System_Prompt)
    return _agent

# async def trigger_gmap_agent(message_history: list[dict]):
#     print("Triggering GMap agent.....")
#     agent = await get_gmap_agent()
#     print(message_history)
#     print("Recieved map details.....")
#     print("Invoking GMap agent.....")
#     result = await agent.ainvoke({"messages": message_history})
#     print("GMap agent result: ", result)
#     print("GMap agent completed.....")
#     return result

@tool(
    "trigger_gmap_agent",
    description="Gets the optimized routes between source and destination and all the address in between, which are called waypoints.",
)
async def trigger_gmap_agent(source: str, destination: str, waypoints: list[str]):
    print("Triggering GMap agent.....")
    agent = await get_gmap_agent()
    print("Invoking GMap agent.....")
    result = await agent.ainvoke({"messages": [{"role": "user", "content": f"Get the route from {source} to {destination} with waypoints {waypoints}"}]})
    print("GMap agent task completed.....")
    return result
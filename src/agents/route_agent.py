import os
import asyncio
import sys
import json
from pathlib import Path
from urllib.parse import quote
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
    # print(f"Getting route data from {source} to {destination} with waypoints {waypoints}")
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

def generate_gmap_url(content: str, source: str, destination: str, waypoints: list[str]):
    origin_encoded = quote(source, safe="")
    destination_encoded = quote(destination, safe="")
    waypoints = waypoints or []
    waypoint_params = "|".join(quote(wp, safe="") for wp in waypoints)
    gmap_url = (
        "https://www.google.com/maps/dir/?api=1"
        f"&origin={origin_encoded}"
        f"&destination={destination_encoded}"
        + (f"&waypoints={waypoint_params}" if waypoint_params else "")
        + "&travelmode=driving"
    )

    try:
        parsed = json.loads(content) if isinstance(content, str) else content
    except json.JSONDecodeError:
        parsed = {"response": content}

    if isinstance(parsed, dict):
        response_payload = {**parsed, "gmap_url": gmap_url}
    else:
        response_payload = {"data": parsed, "gmap_url": gmap_url}
    return response_payload

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
    description="Gets the optimized routes between source and destination and all the address in between, which are called waypoints. Also returns the Google Maps URL for the route.",
)
async def trigger_gmap_agent(source: str, destination: str, waypoints: list[str]):
    print("Triggering GMap agent.....")
    agent = await get_gmap_agent()
    print("Invoking GMap agent.....")
    result = await agent.ainvoke({"messages": [{"role": "user", "content": f"Get the route from {source} to {destination} with waypoints {waypoints}"}]})
    messages = result.get("messages", []) if isinstance(result, dict) else []
    ai_message = messages[-1] if messages else None
    if ai_message is None:
        content = "Route optimization completed, but no response text was returned."
    else:
        raw_content = getattr(ai_message, "content", "")
        if isinstance(raw_content, str):
            content = raw_content
        else:
            content = "".join(
                part.get("text", "")
                for part in raw_content
                if isinstance(part, dict)
            ) or "Route optimization completed."
    
    response_payload = generate_gmap_url(content, source, destination, waypoints)
    print("GMap agent result: ", response_payload)
    print("GMap agent task completed.....")
    return content

# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(trigger_gmap_agent("34 Finney Terrace, Milton, ON, Canada", "34 Finney Terrace, Milton, ON, Canada", ["6301 Silver Dart Dr, Mississauga, ON L5P 1B2", "Toronto Pearson International Airport", "55 Mill St, Toronto, ON M5A 3C4", "320 Queen St E, Brampton, ON L6V 1C2"]))

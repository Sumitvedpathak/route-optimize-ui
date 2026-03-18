import sys
import re
from pathlib import Path
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

try:
    from agents.gmail_agent import get_routedetails_from_email
    from agents.route_agent import trigger_gmap_agent
except ModuleNotFoundError:
    SRC_ROOT = Path(__file__).resolve().parents[1]
    if str(SRC_ROOT) not in sys.path:
        sys.path.append(str(SRC_ROOT))
    from gmail_agent import get_routedetails_from_email
    from agents.route_agent import trigger_gmap_agent

# 1. Define the Shared State
class AgentState(TypedDict):
    user_request: str
    structured_data: Optional[dict]  # {source: str, destination: str, waypoints: list}
    final_itinerary: Optional[dict]
    error: Optional[str]

# 2. Define the Nodes (The "Step 2" Code)
def _extract_shared_address_from_followup(text: str):
    # Handles phrases like "keep source and destination as 38 Finney terrace, Milton, ON"
    match = re.search(
        r"source\s+and\s+destination(?:\s+address)?\s*(?:as|=)\s*(.+)$",
        text,
        re.IGNORECASE,
    )
    if not match:
        return None
    candidate = match.group(1).strip(" .,\n\t")
    return candidate or None


def gmail_node(state: AgentState):
    """Calls the Gmail agent to find and parse the email."""
    print("--- STEP: FETCHING GMAIL ---")
    try:
        result = get_routedetails_from_email("Route")
        current = state.get("structured_data") or {}
        user_text = state.get("user_request", "")

        # Follow-up turn: keep existing waypoints and only fill missing source/destination.
        if current:
            merged = dict(current)
            if not merged.get("source") or not merged.get("destination"):
                follow_up = result
                if follow_up.get("source"):
                    merged["source"] = follow_up["source"]
                if follow_up.get("destination"):
                    merged["destination"] = follow_up["destination"]

                shared_address = _extract_shared_address_from_followup(user_text)
                if shared_address:
                    if not merged.get("source"):
                        merged["source"] = shared_address
                    if not merged.get("destination"):
                        merged["destination"] = shared_address
            return {"structured_data": merged}

        # Initial turn only: fetch route email content and extract route details.
        # result = get_routedetails_from_email("Route")
        return {"structured_data": result}
    except Exception as e:
        return {"error": f"Gmail Agent failed: {str(e)}"}

async def route_node(state: AgentState):
    """Calls your Cloud Run API using the extracted data."""
    print("--- STEP: OPTIMIZING ROUTE ---")
    structured = state.get("structured_data") or {}
    source = structured.get("source")
    destination = structured.get("destination")
    waypoints = structured.get("waypoints", [])

    if not source or not destination:
        return {"error": "Source and destination are required for optimization."}

    itinerary = await trigger_gmap_agent(source, destination, waypoints)
    if isinstance(itinerary, dict) and itinerary.get("messages"):
        messages = itinerary.get("messages", [])
        ai_message = messages[-1] if messages else None
        if ai_message is None:
            return {"final_itinerary": "Route optimization completed, but no response text was returned."}
        content = ai_message.content
        if isinstance(content, str):
            return {"final_itinerary": content}
        text_content = "".join(
            part.get("text", "")
            for part in content
            if isinstance(part, dict)
        )
        return {"final_itinerary": text_content or "Route optimization completed."}
    return {"final_itinerary": itinerary}


def ask_user_for_info_node(state: AgentState):
    structured = state.get("structured_data") or {}
    missing_fields = []
    if not structured.get("source"):
        missing_fields.append("source")
    if not structured.get("destination"):
        missing_fields.append("destination")
    fields = " and ".join(missing_fields) if missing_fields else "source and destination"
    return {"error": f"Please provide {fields} address."}


def route_decision(state: AgentState):
    """
    The Brain: Decide where to go after fetching the email.
    """
    structured = state.get("structured_data") or {}
    if not structured.get("source") or not structured.get("destination"):
        return "ask_user_for_info"

    return "optimize_route"

# 3. Build the Graph
workflow = StateGraph(AgentState)

workflow.add_node("fetch_email", gmail_node)
workflow.add_node("optimize_route", route_node)
workflow.add_node("ask_user_for_info", ask_user_for_info_node)

# Flow: Start -> Gmail -> Route -> End
workflow.set_entry_point("fetch_email")

workflow.add_conditional_edges(
    "fetch_email",
    route_decision,
    {
        "optimize_route": "optimize_route",
        "ask_user_for_info": "ask_user_for_info"
    }
)

workflow.add_edge("optimize_route", END)
workflow.add_edge("ask_user_for_info", END)

orchestrator_app = workflow.compile()
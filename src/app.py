import chainlit as cl
import json
from dotenv import load_dotenv
# from agents.lg_orchestrator import orchestrator_app
from agents.agentic_wrkflw import trigger_agentic_workflow_agent
from constants import Agentic_Workflow_System_Prompt

# @cl.on_chat_start
# def start_chat():
#     cl.user_session.set(
#         "message_history",
#         [{"role": "system", "content": get_gmap_system_prompt()}],
#     )

#-----------Direct Agent Invocation for google maps api-----------
# @cl.on_message
# async def main(message: cl.Message):
#     message_history = cl.user_session.get("message_history")
#     message_history.append({"role": "user", "content": message.content})
#     cl.user_session.set("message_history", message_history)

#     result = await trigger_gmap_agent(message_history)
#     messages = result.get("messages", []) if isinstance(result, dict) else []
#     ai_message = messages[-1] if messages else None

#     if ai_message is None:
#         response_text = "Sorry, I could not generate a response."
#     elif isinstance(ai_message.content, str):
#         response_text = ai_message.content
#     else:
#         response_text = "".join(
#             part.get("text", "")
#             for part in ai_message.content
#             if isinstance(part, dict)
#         )

#     message_history.append({"role": "assistant", "content": response_text})
#     cl.user_session.set("message_history", message_history)
#     await cl.Message(content=response_text).send()

#-----------LangGraph Orchestrator-----------
# @cl.on_message
# async def main(message: cl.Message):
#     # Initialize the state
#     pending_structured_data = cl.user_session.get("structured_data")
#     inputs = {"user_request": message.content, "structured_data": pending_structured_data}

#     terminal_message_sent = False

#     # Stream the graph execution
#     async for output in orchestrator_app.astream(inputs):
#         for node_name, state_update in output.items():
#             if not isinstance(state_update, dict):
#                 continue

#             if state_update.get("structured_data") is not None:
#                 cl.user_session.set("structured_data", state_update["structured_data"])

#             if state_update.get("error"):
#                 await cl.Message(content=state_update["error"]).send()
#                 terminal_message_sent = True
#                 continue

#             if state_update.get("final_itinerary") is not None:
#                 final_output = state_update["final_itinerary"]
#                 if isinstance(final_output, (dict, list)):
#                     final_output = json.dumps(final_output, indent=2)
#                 await cl.Message(
#                     content=f"Here is your final optimized plan:\n\n{final_output}"
#                 ).send()
#                 cl.user_session.set("structured_data", None)
#                 terminal_message_sent = True

#     if not terminal_message_sent:
#         await cl.Message(content="I could not complete route optimization for this request.").send()

#-----------Agentic Workflow Orchestrator-----------
@cl.on_chat_start
def start_chat():
    cl.user_session.set(
        "message_history",
        [{"role": "system", "content": Agentic_Workflow_System_Prompt}],
    )
@cl.on_message
async def main(message: cl.Message):
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})
    cl.user_session.set("message_history", message_history)
    result = await trigger_agentic_workflow_agent(message_history)
    messages = result.get("messages", []) if isinstance(result, dict) else []
    ai_message = messages[-1] if messages else None
    if ai_message is None:
        response_text = "Sorry, I could not generate a response."
    elif isinstance(ai_message.content, str):
        response_text = ai_message.content
    else:
        response_text = "".join(
            part.get("text", "")
            for part in ai_message.content
            if isinstance(part, dict)
        )
    message_history.append({"role": "assistant", "content": response_text})
    cl.user_session.set("message_history", message_history)
    await cl.Message(content=response_text).send()




@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Optimize Routes",
            message="Provide address list or ",
            icon="/public/route.svg",
        )
    ]
import chainlit as cl
from dotenv import load_dotenv
from gmap_agent import get_gmap_system_prompt, trigger_gmap_agent

@cl.on_chat_start
def start_chat():
    cl.user_session.set(
        "message_history",
        [{"role": "system", "content": get_gmap_system_prompt()}],
    )

@cl.on_message
async def main(message: cl.Message):
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})
    cl.user_session.set("message_history", message_history)

    result = await trigger_gmap_agent(message_history)
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
            message="Explain briefly about blackhole in layman's terms?",
            icon="/public/route.svg",
        )
    ]
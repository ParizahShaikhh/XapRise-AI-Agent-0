import chainlit as cl
import json
import aiohttp
from typing import List, Dict

BASE_URL = "https://health-wellness-agent.vercel.app/stream_response/"


def get_history() -> List[Dict]:
    history = cl.user_session.get("messages")
    if history is None:
        history = []
        cl.user_session.set("messages", history)
    return history


def add_to_history(role: str, content: str):
    history = get_history()
    history.append({"role": role, "content": content})
    cl.user_session.set("messages", history)


@cl.on_chat_start
async def chat_start():
    history = get_history()
    if not history:
        await cl.Message(content="Hey, I'm Health Wellness Agent. How can I help you today?").send()


async def handle_agent_streaming(user_input: str):
    # Add user message to history
    add_to_history("user", user_input)

    # Send history to API
    history = get_history()
    async with aiohttp.ClientSession() as session:
        async with session.post(
            BASE_URL,
            json={
                "user_input": f'user_input : {user_input} \n history : {history}',
                # "history":   # Send history to API
            },
            headers={"Content-Type": "application/json"}
        ) as response:

            msg = cl.Message(content="")
            await msg.send()

            streamed_response = ""  # To collect agent's response

            async for chunk in response.content:
                if not chunk:
                    continue

                try:
                    data = json.loads(chunk.decode().strip())

                    if data["type"] == "text":
                        await msg.stream_token(data["content"])
                        streamed_response += data["content"]  # Collect response

                    elif data["type"] == "agent_handoff" and data["new_agent"] == "health_wellness_agent":
                        continue

                    elif data["type"] == "agent_handoff":
                        transfer_msg = cl.Message(
                            content=data["message"],
                            author=data["new_agent"],
                        )
                        await transfer_msg.send()

                except (json.JSONDecodeError, KeyError) as e:
                    print("Error processing chunk:", e)

            await msg.update()

            # Add agent response to history
            if streamed_response:
                add_to_history("agent", streamed_response)


@cl.on_message
async def main(message: cl.Message):
    await handle_agent_streaming(message.content)
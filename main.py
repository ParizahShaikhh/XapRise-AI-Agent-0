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

@cl.on_chat_start
async def chat_start():
    history = get_history()
    if history:
        for msg in history:
            await cl.Message(content=f"{msg['role']}: {msg['content']}").send()
    else:
        await cl.Message(content="Hey, I'm Health Wellness Agent. How can I help you today?").send()

async def handle_agent_streaming(user_input: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            BASE_URL,
            json={"user_input": user_input},
            headers={"Content-Type": "application/json"}
        ) as response:
            
            msg = cl.Message(content="")
            await msg.send()

            async for line in response.content:
                if not line:
                    continue

                try:
                    decoded = line.decode().strip()
                    if not decoded:
                        continue

                    data = json.loads(decoded)

                    if data["type"] == "text":
                        await msg.stream_token(data["content"])

                    elif data["type"] == "agent_handoff" and data["new_agent"] == "health_wellness_agent":
                        # Already on this agent — don't send anything
                        continue

                    elif data["type"] == "agent_handoff":
                        # Show handoff to another agent
                        transfer_msg = cl.Message(
                            content=data["message"],
                            author=data["new_agent"]
                        )
                        await transfer_msg.send()

                except Exception as e:
                    print("Error parsing chunk:", e)

            await msg.update()

@cl.on_message
async def main(message: cl.Message):
    await handle_agent_streaming(message.content)

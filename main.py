import chainlit as cl
import json
import aiohttp 
from typing import List, Dict

BASE_URL = "https://health-wellness-agent.vercel.app/stream_response/"

def get_history() -> List[Dict]:
    # initialize or fetch existing message history
    history = cl.user_session.get("messages")
    if history is None:
        history = []
        cl.user_session.set("messages", history)
    return history

@cl.on_chat_start
async def chat_start():
    history = get_history()
    if history:
        # replay prior conversation
        for msg in history:
            await cl.Message(content=f"{msg['role']}: {msg['content']}").send()
    else:
        # first‐time greeting
        await cl.Message(content="Hey, I'm Health Wellness Agent. How can I help you today?").send()
async def handle_agent_streaming(user_input: str):
    """Stream agent responses and handoff events"""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            BASE_URL,
            json={"user_input": user_input},
            headers={"Content-Type": "application/json"}
        ) as response:
            
                        
            # Create a placeholder message
            msg = cl.Message(content="")
            await msg.send()
            
            async for chunk in response.content:
                if not chunk:
                    continue
                
                try:
                    # Parse the NDJSON chunk
                    data = json.loads(chunk.decode())
                    
                    if data["type"] == "text":
                        # Stream text content
                        await msg.stream_token(data["content"])
                    
                    elif data["type"] == "agent_handoff" and data["new_agent"] == "health_wellness_agent":
                        continue 
                        
                    elif data["type"] == "agent_handoff":
                        # Create a system message for agent transfer
                        transfer_msg = cl.Message(
                            content=data["message"],
                            author=data["new_agent"],
                            
                        )
                        await transfer_msg.send()
                        
                        # Optionally update the avatar for visual distinction
                        # await msg.update(author=data["new_agent"])
                        
                except json.JSONDecodeError:
                    print("Failed to parse chunk:", chunk)
                except KeyError as e:
                    print("Missing key in response:", e)

            # Finalize the message
            await msg.update()

@cl.on_message
async def main(message: cl.Message):
    """Handle user messages"""
    await handle_agent_streaming(message.content)
# # import chainlit as cl
# # import json
# # import aiohttp
# # from typing import List, Dict

# # BASE_URL = "https://health-wellness-agent.vercel.app/stream_response/"


# # def get_history() -> List[Dict]:
# #     history = cl.user_session.get("messages")
# #     if history is None:
# #         history = []
# #         cl.user_session.set("messages", history)
# #     return history


# # @cl.on_chat_start
# # async def chat_start():
# #     history = get_history()
# #     if history:
# #         for msg in history:
# #             await cl.Message(content=f"{msg['role']}: {msg['content']}").send()
# #     else:
# #         await cl.Message(content="Hey, I'm Health Wellness Agent. How can I help you today?").send()


# # async def handle_agent_streaming(user_input: str):
# #     async with aiohttp.ClientSession() as session:
# #         async with session.post(
# #             BASE_URL,
# #             json={"user_input": user_input},
# #             headers={"Content-Type": "application/json"}
# #         ) as response:

# #             msg = cl.Message(content="")
# #             await msg.send()

# #             async for line in response.content:
# #                 if not line:
# #                     continue

# #                 try:
# #                     decoded = line.decode().strip()
# #                     if not decoded:
# #                         continue

# #                     data = json.loads(decoded)

# #                     if data["type"] == "text":
# #                         await msg.stream_token(data["content"])

# #                     elif data["type"] == "agent_handoff" and data["new_agent"] == "health_wellness_agent":
# #                         continue

# #                     elif data["type"] == "agent_handoff":
# #                         transfer_msg = cl.Message(
# #                             content=data["message"],
# #                             author=data["new_agent"]
# #                         )
# #                         await transfer_msg.send()

# #                 except Exception as e:
# #                     print("Error parsing chunk:", e)

# #             await msg.update()

# # @cl.on_message
# # async def main(message: cl.Message):
# #     await handle_agent_streaming(message.content)
# import chainlit as cl
# import json
# import aiohttp
# from typing import List, Dict

# BASE_URL = "https://health-wellness-agent.vercel.app/stream_response/"

# def get_history() -> List[Dict]:
#     history = cl.user_session.get("messages")
#     if history is None:
#         history = []
#         cl.user_session.set("messages", history)
#     return history

# @cl.on_chat_start
# async def chat_start():
#     history = get_history()
#     # Show greeting only if it's a fresh session
#     if not history:
#         await cl.Message(content="Hey, I'm Health Wellness Agent. How can I help you today?").send()

# async def handle_agent_streaming(user_input: str):
#     async with aiohttp.ClientSession() as session:
#         async with session.post(
#             BASE_URL,
#             json={"user_input": user_input},
#             headers={"Content-Type": "application/json"}
#         ) as response:

#             msg = cl.Message(content="")
#             await msg.send()

#             async for chunk in response.content:
#                 if not chunk:
#                     continue

#                 try:
#                     data = json.loads(chunk.decode().strip())
                    
#                     if data["type"] == "text":
#                         await msg.stream_token(data["content"])

#                     elif data["type"] == "agent_handoff" and data["new_agent"] == "health_wellness_agent":
#                         # Do nothing if already this agent
#                         continue

#                     elif data["type"] == "agent_handoff":
#                         transfer_msg = cl.Message(
#                             content=data["message"],
#                             author=data["new_agent"],
#                         )
#                         await transfer_msg.send()

#                 except (json.JSONDecodeError, KeyError) as e:
#                     print("Error processing chunk:", e)

#             await msg.update()

# @cl.on_message
# async def main(message: cl.Message):
#     """Trigger handoff only if the user mentions the agent"""
#     if "health wellness agent" in message.content.lower():
#         await handle_agent_streaming(message.content)
#     else:
#         await cl.Message(content="I'm here if you want to talk to the Health Wellness Agent. Just type: `health wellness agent`.").send()
# # @cl.on_message
# # async def main(message: cl.Message):
# #     await handle_agent_streaming(message.content)
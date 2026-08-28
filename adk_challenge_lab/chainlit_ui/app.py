import sys
from pathlib import Path
import os
import asyncio
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import chainlit as cl

# Ensure parent directory is in sys.path so paint_agent package is discoverable
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

load_dotenv(project_root / ".env")
load_dotenv()

from google.genai import types
from google.adk.runners import InMemoryRunner
from paint_agent.agent import root_agent

# Check if remote reasoning engine is specified and vertexai is enabled
USE_REMOTE = (
    os.getenv("USE_REMOTE_AGENT", "false").lower() == "true"
    and os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "").lower() == "true"
    and os.getenv("REASONING_ENGINE_NAME")
)

remote_agent = None
if USE_REMOTE:
    try:
        import vertexai
        client = vertexai.Client(
            project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
            location=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1"),
        )
        remote_agent = client.agent_engines.get(name=os.environ["REASONING_ENGINE_NAME"])
        print(f"Connected to remote Vertex AI Agent Engine: {os.environ['REASONING_ENGINE_NAME']}")
    except Exception as e:
        print(f"Remote Agent Engine unreachable, using local ADK InMemoryRunner: {e}")

local_runner = InMemoryRunner(agent=root_agent, app_name="paint_agent")


def convert_img_tags_to_chainlit_images(msg):
    img_list = []
    if not msg.content:
        return msg

    soup = BeautifulSoup(msg.content, "html.parser")
    found_imgs = soup.find_all("img")
    for img_tag in found_imgs:
        if img_tag.has_attr("src"):
            img = cl.Image(url=img_tag["src"], name="swatch", display="inline")
            img_list.append(img)
            img_tag.decompose()

    msg.elements = img_list
    cleaned_text = soup.get_text().strip()
    if cleaned_text:
        msg.content = cleaned_text
    elif img_list:
        msg.content = " "
    return msg


@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Painting Project Help",
            message="Tell me about Cymbal Shops' interior paints.",
            icon="/public/swatches.svg",
        )
    ]


@cl.on_chat_start
async def on_chat_start():
    print("A new chat session has started!")
    user_id = "user"

    try:
        if remote_agent:
            session_details = await cl.make_async(remote_agent.create_session)(user_id=user_id)
            session_id = session_details["id"]
        else:
            session = await local_runner.session_service.create_session(
                app_name="paint_agent", user_id=user_id
            )
            session_id = session.id

        cl.user_session.set("user_id", user_id)
        cl.user_session.set("session_id", session_id)
        cl.user_session.set(
            "message_history",
            [{"role": "system", "content": "You are a helpful assistant."}],
        )
    except Exception as e:
        print(f"Error starting chat: {e}")
        await cl.Message(content="Failed to initialize agent session. Please refresh the page.").send()


@cl.on_message
async def main(message: cl.Message):
    for _ in range(10):
        user_id = cl.user_session.get("user_id")
        session_id = cl.user_session.get("session_id")
        if session_id:
            break
        await asyncio.sleep(0.5)
    else:
        await cl.Message(content="Session initialization is taking longer than expected. Please refresh.").send()
        return

    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})
    msg = cl.Message(content="")

    try:
        if remote_agent:
            async_stream = remote_agent.async_stream_query(
                user_id=user_id,
                session_id=session_id,
                message=message.content,
            )
            async for event in async_stream:
                if isinstance(event, dict):
                    if "error" in event:
                        await cl.Message(content=f"Agent Engine Error: {event['error']}").send()
                        return
                    if "code" in event and "message" in event:
                        continue
                if "content" in event and "parts" in event["content"]:
                    for part in event["content"]["parts"]:
                        if "text" in part:
                            await msg.stream_token(part["text"])
        else:
            msg_content = types.Content(
                role="user", parts=[types.Part.from_text(text=message.content)]
            )
            async for event in local_runner.run_async(
                user_id=user_id, session_id=session_id, new_message=msg_content
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            await msg.stream_token(part.text)

        convert_img_tags_to_chainlit_images(msg)

        actual_content = msg.content.strip() if msg.content else ""
        if actual_content or msg.elements:
            message_history.append({"role": "assistant", "content": msg.content})
            await msg.update()
        else:
            await msg.remove()

    except Exception as e:
        print(f"Error querying agent: {e}")
        await cl.Message(content=f"An error occurred: {str(e)}").send()
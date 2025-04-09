from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
import streamlit as st
import asyncio
from typing import Literal, TypedDict

from dotenv import load_dotenv
load_dotenv()

from app.agents.wiskunde_expert_agent import wiskunde_expert, WiskundeRAGDeps
from app.utils.supabase_client import get_supabase_client

from pydantic_ai.messages import (
    ModelRequest, ModelResponse, TextPart, UserPromptPart,
    ToolCallPart, ToolReturnPart
)

import os

os.environ["STREAMLIT_SERVER_ENABLE_FILE_WATCHER"] = "false" #prevents pytorch internal registration mechanism with module path conflicts

class ChatMessage(TypedDict):
    role: Literal['user', 'model']
    timestamp: str
    content: str

def display_message_part(part):
    """
    Display a single part of a message in the Streamlit UI.
    Customize how you display system prompts, user prompts,
    tool calls, tool returns, etc.
    """
    # system-prompt
    if part.part_kind == 'system-prompt':
        with st.chat_message("system"):
            st.markdown(f"**System**: {part.content}")
    # user-prompt
    elif part.part_kind == 'user-prompt':
        with st.chat_message("user"):
            st.markdown(part.content)
    # text
    elif part.part_kind == 'text':
        with st.chat_message("assistant"):
            st.markdown(part.content)
    # tool-call
    elif part.part_kind == 'tool-call':
        with st.chat_message("assistant"):
            st.markdown(f"**Tool Call**: {part.tool_name} with arguments {part.args}")

async def run_agent_with_streaming(user_input: str):
    deps = WiskundeRAGDeps(supabase=get_supabase_client())

    async with wiskunde_expert.run_stream(
        user_input,
        deps=deps,
        message_history=st.session_state.messages[:-1], # heel gesprek tot nu toe als context
    ) as result:
        partial_text = ""
        placeholder = st.empty()

        # Stream de text en toon deze in real-time in de UI
        async for chunk in result.stream_text(delta=True):
            partial_text += chunk
            placeholder.markdown(partial_text)
        filtered_messages = [
            msg for msg in result.new_messages()
            if not (
                hasattr(msg, 'parts')
                and any(part.part_kind == 'user-prompt' for part in msg.parts)
            )
        ]
        st.session_state.messages.extend(filtered_messages)



async def main():
    st.set_page_config(page_title="Euler RAG Agent", layout="centered")
    st.title("📘 Wiskunde VMBO-TL RAG Agent")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        if isinstance(msg, (ModelRequest, ModelResponse)):
            for part in msg.parts:
                display_message_part(part)

    user_input = st.chat_input("Stel je wiskundevraag...")

    if user_input:
        st.session_state.messages.append(
            ModelRequest(parts=[UserPromptPart(content=user_input)])
        )
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            await run_agent_with_streaming(user_input)

if __name__ == "__main__":
    asyncio.run(main())

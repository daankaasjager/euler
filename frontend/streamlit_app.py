from pathlib import Path
import sys
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

sys.path.append(str(Path(__file__).resolve().parent.parent))

class ChatMessage(TypedDict):
    role: Literal['user', 'model']
    timestamp: str
    content: str

def display_message_part(part):
    if part.part_kind == 'text':
        with st.chat_message("assistant"):
            st.markdown(part.content)
    elif part.part_kind == 'user-prompt':
        with st.chat_message("user"):
            st.markdown(part.content)

def render_tool_log(messages):
    st.markdown("#### 🔧 Gebruikte tools:")
    for msg in messages:
        for part in getattr(msg, "parts", []):
            if isinstance(part, ToolCallPart):
                st.markdown(f"**🛠️ Tool aangeroepen:** `{part.tool_name}` met argumenten `{part.tool_args}`")
            if isinstance(part, ToolReturnPart):
                st.markdown(f"**✅ Tool resultaat:** `{part.return_value}`")

async def run_agent_with_streaming(user_input: str):
    deps = WiskundeRAGDeps(supabase=get_supabase_client())

    async with wiskunde_expert.run_stream(
        user_input,
        deps=deps,
        message_history=st.session_state.messages[:-1],
    ) as result:
        partial_text = ""
        placeholder = st.empty()

        async for delta in result.stream_text(delta=True):
            partial_text += delta
            placeholder.markdown(partial_text)

        # Append final response
        st.session_state.messages.append(
            ModelResponse(parts=[TextPart(content=partial_text)])
        )

        # Render used tools below response
        render_tool_log(result.messages)

        return partial_text

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

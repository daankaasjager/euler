from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
import streamlit as st
import asyncio
from typing import Literal, TypedDict, List

from dotenv import load_dotenv
load_dotenv()

from app.agents.wiskunde_expert_agent import wiskunde_expert, WiskundeRAGDeps
from app.utils import get_supabase_client


class ChatMessage(TypedDict):
    role: Literal['user', 'model']
    timestamp: str
    content: str

def display_message_part(part):
    if part.part_kind == 'text':
        with st.chat_message("assistant"):
            st.markdown(part.content)

def get_subjects() -> List[str]:
    """Get all unique subjects from Supabase."""
    supabase = get_supabase_client()
    response = supabase.table('documents').select('onderwerpen').execute()
    subjects = set()
    
    for row in response.data:
        if row.get('onderwerpen'):
            onderwerpen = row['onderwerpen']
            if isinstance(onderwerpen, str):
                print(f"onderwerpen string: {onderwerpen}")
                for subject in onderwerpen.split(', '):
                    cleaned = subject.strip()
                    if cleaned:
                        subjects.add(cleaned)
            elif isinstance(onderwerpen, list):
                print(f"onderwerpen lijst: {onderwerpen}")
                for subject in onderwerpen:
                    cleaned = str(subject).strip()
                    if cleaned:
                        subjects.add(cleaned)
            else: 
                print(f"format is {type(onderwerpen)}")
                print(f"onderwerpen type: {onderwerpen}")
    return sorted(subjects)

async def run_agent_with_streaming(prompt: str):
    deps = WiskundeRAGDeps(supabase=get_supabase_client())
    async with wiskunde_expert.run_stream(prompt, deps=deps) as result:
        full_response = []
        async for chunk in result.stream_text():
            full_response.append(chunk)
        return "".join(full_response)

def main():
    st.set_page_config(page_title="Wiskunde Expert", layout="centered")
    st.title("Wiskunde Expert")

    if 'messages' not in st.session_state:
        st.session_state.messages = []

    subjects = get_subjects()
    
    st.subheader("Selecteer een onderwerp")
    selected_subject = st.selectbox("Kies een onderwerp", subjects, key='subject_select')

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Geef meer uitleg"):
            if st.session_state.subject_select:
                prompt_path = Path("app/prompts/uitleg_prompt.txt")
                prompt = prompt_path.read_text().replace("[ONDERWERP]", st.session_state.subject_select)
                response = asyncio.run(run_agent_with_streaming(prompt))
                st.session_state.messages.append({"role": "assistant", "content": response})
                
    
    with col2:
        if st.button("Genereer voorbeeld vragen"):
            if st.session_state.subject_select:
                prompt_path = Path("app/prompts/vragen_prompt.txt")
                prompt = prompt_path.read_text().replace("[ONDERWERP]", st.session_state.subject_select)
                response = asyncio.run(run_agent_with_streaming(prompt))
                st.session_state.messages.append({"role": "assistant", "content": response})


    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if __name__ == "__main__":
    main()
import os
import json
import asyncio
from src.utils.llms import call_ollama
from typing import Dict, Any, List
from dataclasses import dataclass
from src.utils.embedding import get_embedding
from dotenv import load_dotenv
import re
import logging
from src.utils.supabase_client import get_supabase_client

"""Code inspired from https://github.com/coleam00/ottomator-agents/blob/main/crawl4AI-agent/crawl_pydantic_ai_docs.py"""


supabase = get_supabase_client()

load_dotenv()
logger = logging.getLogger(__name__)



# Ollama Model for title/summaries
OLLAMA_URL = os.getenv("OLLAMA_URL")
NEDER_MODEL = os.getenv("NEDER_MODEL")

@dataclass
class ProcessedChunk:
    file_name: str
    chunk_nummer: int
    thema: str
    omschrijving: str
    inhoud: str
    metadata: Dict[str, Any]
    embedding: List[float]

def chunk_text(text: str, chunk_size: int = 5000) -> List[str]:
    """Split text into chunks, respecting code blocks and paragraphs."""
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        # Calculate end position
        end = start + chunk_size

        # If we're at the end of the text, just take what's left
        if end >= text_length:
            chunks.append(text[start:].strip())
            break

        # Try to find a code block boundary first (```)
        chunk = text[start:end]
        code_block = chunk.rfind('```')
        if code_block != -1 and code_block > chunk_size * 0.3:
            end = start + code_block

        # If no code block, try to break at a paragraph
        elif '\n\n' in chunk:
            # Find the last paragraph break
            last_break = chunk.rfind('\n\n')
            if last_break > chunk_size * 0.3:  # Only break if we're past 30% of chunk_size
                end = start + last_break

        # If no paragraph break, try to break at a sentence
        elif '. ' in chunk:
            # Find the last sentence break
            last_period = chunk.rfind('. ')
            if last_period > chunk_size * 0.3:  # Only break if we're past 30% of chunk_size
                end = start + last_period + 1

        # Extract chunk and clean it up
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Move start position for next chunk
        start = max(start + 1, end)

    return chunks

def clean_code_fences(raw_content: str) -> str:
    """
    Removes leading/trailing triple backticks (like ```json) and
    the final triple backticks from a string. Returns the remaining text.
    """
    # Strip leading/trailing whitespace first
    raw_content = raw_content.strip()

    # Remove a leading fence: ```json  or just ```
    raw_content = re.sub(r'^```(?:json)?\s*', '', raw_content)

    # Remove a trailing fence: ```
    raw_content = re.sub(r'\s*```$', '', raw_content)

    return raw_content.strip()

async def get_title_and_summary(chunk: str) -> Dict[str, str]:
    """Extract title and chunk_nummer using Ollama."""
    
    system_prompt = """Je bent een AI die thema's en omschrijvingen onttrekt uit wiskunde schoolboeken (vmbo-tl). Je moet strikt één JSON-object retourneren, zonder extra tekst of code fences.
        **Vorm output**
        - Begin direct met `{` en eindig direct met `}`.
        - Gebruik exact de twee keys `"thema"` en `"omschrijving"`.
        - Plaats geen extra velden of uitleg in de output.

        **Toelichting thema**
        - Kies het wiskundige onderwerp dat het meest relevant is voor de gegeven tekst, bijvoorbeeld:
        - "Algebraïsche verbanden"
        - "Rekenen, meten en schatten"
        - "Meetkunde"
        - "Informatieverwerking, statistiek"
        - of een ander passend vmbo-tl wiskunde onderwerp.

        **Toelichting omschrijving**
        - Er zijn precies vier mogelijke waarden:
        1. "theorie" als het fragment alleen theorie bevat.
        2. "voorbeeld" als het fragment alleen een voorbeeld bevat.
        3. "theorie en voorbeeld" als zowel theorie en een voorbeeld aanwezig zijn in de tekst.
        4. "anders" als geen van de bovenstaande categorieën van toepassing is.

        **Voorbeeld van correcte output:**
        {
        "thema": "Meetkunde",
        "omschrijving": "theorie"
        }
        Zorg dat je geen extra tekst of codeblok-markdown toevoegt, en geen tweede JSON-object.
    """
    response = await call_ollama(
        model=NEDER_MODEL,
        system_prompt=system_prompt,
        chunk=chunk,
        max_tokens=300,
        temperature=0.0
    )
    return json.loads(clean_code_fences(response))

async def process_chunk(chunk: str, chunk_nummer: int, file_name: str) -> ProcessedChunk:
    """Process a single chunk of text."""
    # Get title and summary
    extracted = await get_title_and_summary(chunk)
    
    # Get embedding
    embedding = await get_embedding(chunk)
    
    """Hier valt nog veel te halen. Denk aan metadata over het boek, de editie,
     vak (dingen voor later om rekening mee te houden)"""
    metadata = {
        "chunk_size": len(chunk),
        "subject": "wiskunde",
        "niveau": "vmbo-tl",
        "taal": "nl",
        "boek_versie": "2024"
    }
    
    return ProcessedChunk(
        file_name=file_name,
        chunk_nummer=chunk_nummer,
        thema=extracted.get("thema", "Geen thema"),
        omschrijving=extracted.get("omschrijving", "Geen omschrijving"),
        inhoud=chunk,
        metadata=metadata,
        embedding=embedding
    )

async def insert_chunk(chunk: ProcessedChunk):
    """Insert a processed chunk into Supabase."""
    try:
        data = {
            "file_name": chunk.file_name,
            "chunk_nummer": chunk.chunk_nummer,
            "thema": chunk.thema,
            "omschrijving": chunk.omschrijving,
            "inhoud": chunk.inhoud,
            "metadata": chunk.metadata,
            "embedding": chunk.embedding
        }
        
        result = supabase.table("documents").insert(data).execute()
        print(f"Inserted chunk {chunk.chunk_nummer}")
        return result
    except Exception as e:
        print(f"Error inserting chunk: {e}")
        return None

async def process_and_store_md(cfg, md_path: str):
    """Process a document and store its chunks in parallel."""
    semaphore = asyncio.Semaphore(cfg.mode.semaphore) 
    try:
        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()

        file_name = os.path.basename(md_path)
        chunks = chunk_text(content)

        tasks = [
            process_chunk(chunk, i, file_name)
            for i, chunk in enumerate(chunks)
        ]
        async with semaphore:
            processed_chunks = await asyncio.gather(*tasks)
        
        insert_tasks = [
            insert_chunk(chunk)
            for chunk in processed_chunks
        ]
        await asyncio.gather(*insert_tasks)
    except Exception as e:
        print(f"❌ Failed to process {md_path}: {e}")
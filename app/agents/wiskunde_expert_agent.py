from __future__ import annotations as _annotations
from dataclasses import dataclass
from typing import List
from supabase import Client
from pydantic_ai import RunContext
from dotenv import load_dotenv

from app.utils import get_embedding, get_supabase_client, load_prompt
from app.agents.base_agent import create_agent, BaseAgentDeps
import os

# Load environment variables
load_dotenv()

@dataclass
class WiskundeRAGDeps(BaseAgentDeps):
    supabase: Client  # override to be explicit

supabase = get_supabase_client()
OLLAMA_URL = os.getenv("OLLAMA_URL")
NEDER_MODEL = os.getenv("NEDER_MODEL")


system_prompt = load_prompt("wiskunde_expert")

wiskunde_expert = create_agent(
    model_name=NEDER_MODEL,
    base_url=OLLAMA_URL, # this maybe needs to be changed to include /v1
    system_prompt=system_prompt,
    deps_type=WiskundeRAGDeps
)


@wiskunde_expert.tool
async def retrieve_relevant_documentation(ctx: RunContext[WiskundeRAGDeps], user_query: str) -> str:
    """
    Zoekt en retourneert de meest relevante documentatiefragmenten voor een gegeven wiskundevraag met behulp van RAG 
    (Retrieval-Augmented Generation).

        Parameters:
            ctx (RunContext[WiskundeRAGDeps]): Het contextobject dat toegang biedt tot de Supabase-client en andere resources.
            user_query (str): De specifieke wiskundige vraag of onderwerp van de gebruiker.

        Retourneert:
            str: Een samengestelde tekst met maximaal 5 relevante fragmenten uit de documenten, gescheiden door een separator. Als geen 
    relevant materiaal gevonden wordt, retourneert het 'Geen relevante documenten gevonden.'

        Throws:
            Exception: Retourneert een foutmelding als er problemen optreden bij het ophalen van de documentatie.
        
        Note:
            De Supabase-client filtert de zoekresultaten op basis van onderwerp ('wiskunde'). Deze filter kan in de toekomst aangepast 
    worden om specifieke hoofdstukken of subonderwerpen te beperken.
    """
    try:
        # Get the embedding for the query
        query_embedding = await get_embedding(user_query)
        
        # Query Supabase voor relevante documents
        result = ctx.deps.supabase.rpc(
            'match_documents',
            {
                'query_embedding': query_embedding,
                'match_count': 5, # make this configurable later
                'filter': {'subject': 'wiskunde'} # dit kan je nog aanpassen naar hoodstuk, onderwerp, moet allemaal wel eerst in de metadata
            }
        ).execute()
        
        if not result.data:
            return "Geen relevante documenten gevonden."
            
        # Format the results
        formatted_chunks = []
        for doc in result.data:
            chunk_text = f"""
# {doc['thema']}

{doc['inhoud']}
"""
            formatted_chunks.append(chunk_text)
            
        # Join all chunks with a separator
        return "\n\n---\n\n".join(formatted_chunks)
        
    except Exception as e:
        print(f"Error retrieving documentation: {e}")
        return f"Error retrieving documentation: {str(e)}"


@wiskunde_expert.tool
async def list_documentation_pages(ctx: RunContext[WiskundeRAGDeps]) -> List[str]:
    """
    Haal een lijst op van alle unieke onderwerpen uit de wiskunde documentatie.

    Returns:
        List[str]: Lijst van unieke onderwerpen.
    """
    try:
        # Query Supabase for unique file_names where source is wiskunde documents
        result = ctx.deps.supabase.from_('documents') \
            .select('onderwerpen') \
            .eq('metadata->>subject', 'wiskunde') \
            .execute()
        
        if not result.data:
            return []
        
        # Verzamel unieke onderwerpen
        onderwerpen = set()
        for doc in result.data:
            if doc['onderwerpen']:
                onderwerpen.update(doc['onderwerpen'])
        
        return sorted(onderwerpen)
        
    except Exception as e:
        print(f"Fout bij het ophalen van documentatie onderwerpen: {e}")
        return []


@wiskunde_expert.tool
async def get_page_content(ctx: RunContext[WiskundeRAGDeps], onderwerp: str) -> str:
    """
    Haal de volledige inhoud op van documentatiepagina's die overeenkomen met een specifiek onderwerp.

    Args:
        ctx: De context inclusief de Supabase client.
        onderwerp: Het onderwerp waarvoor de inhoud wordt opgehaald.

    Returns:
        str: De gecombineerde inhoud van alle relevante documentatiepagina's.
    """
    try:
        # Query Supabase voor alle chunks die overeenkomen met het gegeven onderwerp
        result = ctx.deps.supabase.from_('documents') \
            .select('titel, inhoud, chunk_nummer') \
            .contains('onderwerpen', [onderwerp]) \
            .eq('metadata->>subject', 'wiskunde') \
            .order('chunk_nummer') \
            .execute()
        print(f"result{result.data}")
        if not result.data:
            return f"Geen inhoud gevonden voor het onderwerp: {onderwerp}"
        
        # Combineer de inhoud van alle relevante chunks
        formatted_content = []
        for chunk in result.data:
            formatted_content.append(f"## {chunk['titel']}\n{chunk['inhoud']}")
        
        return "\n\n".join(formatted_content)
        
    except Exception as e:
        print(f"Fout bij het ophalen van pagina-inhoud: {e}")
        return f"Fout bij het ophalen van pagina-inhoud: {str(e)}"
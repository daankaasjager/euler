from __future__ import annotations as _annotations
from dataclasses import dataclass
from typing import List
from supabase import Client
from pydantic_ai import RunContext

from app.utils.embedding import get_embedding
from app.utils.supabase_client import get_supabase_client
from app.agents.base_agent import create_agent, BaseAgentDeps
from app.utils.prompt_loader import load_prompt
import os

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
    Zoekt de meest relevante documentatiefragmenten voor een gegeven wiskundevraag met behulp van RAG.

    Parameters:
        ctx: De Supabase-client die toegang heeft tot de documenten.
        user_query: De wiskundige vraag van de gebruiker.

    Retourneert:
        Een samengestelde tekst met maximaal 5 relevante fragmenten uit de documenten.
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
    Retrieve a list of all available Wiskunde documentation pages.
    
    Returns:
        List[str]: List of unique file names for all documentation pages
    """
    try:
        # Query Supabase for unique file_names where source is wiskunde documents
        result = ctx.deps.supabase.from_('documents') \
            .select('file_name') \
            .eq('metadata->>subject', 'wiskunde') \
            .execute()
        
        if not result.data:
            return []
        
        file_names = sorted(set(doc['file_name'] for doc in result.data))
        return file_names
        
    except Exception as e:
        print(f"Error retrieving documentation pages: {e}")
        return []


@wiskunde_expert.tool
async def get_page_content(ctx: RunContext[WiskundeRAGDeps], file_name: str) -> str:
    """
    Retrieve the full content of a specific documentation page by combining all its chunks.
    
    Args:
        ctx: The context including the Supabase client
        filename: The URL of the page to retrieve
        
    Returns:
        str: The complete page content with all chunks combined in order
    """
    try:
        # Query Supabase for all chunks of this URL, ordered by chunk_number
        result = ctx.deps.supabase.from_('documents') \
            .select('titel, inhoud, chunk_nummer') \
            .eq('file_name', file_name) \
            .eq('metadata->>subject', 'wiskunde') \
            .order('chunk_nummer') \
            .execute()
        
        if not result.data:
            return f"No content found for file_name: {file_name}"
            
        # Format the page with its title and all chunks
        page_title = result.data[0]['titel'].split(' - ')[0]  # Get the main title
        formatted_content = [f"# {page_title}\n"]
        
        # Add each chunk's content
        for chunk in result.data:
            formatted_content.append(chunk['inhoud'])
            
        # Join everything together
        return "\n\n".join(formatted_content)
        
    except Exception as e:
        print(f"Error retrieving page content: {e}")
        return f"Error retrieving page content: {str(e)}"
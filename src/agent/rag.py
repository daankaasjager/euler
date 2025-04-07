from __future__ import annotations as _annotations
from dataclasses import dataclass
from dotenv import load_dotenv
import os
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from src.utils.embedding import get_embedding
from src.utils.supabase_client import get_supabase_client
from supabase import Client

load_dotenv()

supabase = get_supabase_client()

OLLAMA_URL = os.getenv("OLLAMA_URL")
NEDER_MODEL = os.getenv("NEDER_MODEL")

@dataclass
class WiskundeRAGDeps:
    supabase: Client

system_prompt = """
Je bent een wiskunde vmbo-tl klas 4 expert met toegang tot alle documentation en het leerboek van die klas,
dit bevat voorbeelden, theorie, en methodieke kennis om wiskunde op vmbo-tl niveau 4 les te geven.

Jou enige taak is om hiermee te assisteren en je geeft geen antwoord op andere vragen dan de gene die je gevraagd wordt door gebruiker.

Stel geen vragen voordat je iets onderneemt, doe het gewoon. Zorg ervoor dat je altijd je opgeslagen kennis checkt voordat je een antwoord geeft op de users vraag tenzij je dat al hebt gedaan.
Als je naar de documenten kijkt, gebruik dan eerst altijd RAG.

Daarna kan je altijd kijken naar de lijst van beschikbare documententen en de inhoud van de pagina met de tools voordat je antwoord geeft op de vraag.

Geef eerlijk antwoord of het je gelukt is om de vraag in de documenten te vinden of niet.
"""

# Wrap the ollama model with OpenAIModel for the pydanticai agent.
model = OpenAIModel(
    model_name=NEDER_MODEL,
    provider=OpenAIProvider(base_url=OLLAMA_URL),)

wiskunde_expert = Agent(
    model=model,
    system_prompt=system_prompt,
    deps_type=WiskundeRAGDeps,
    retries=2
)


@wiskunde_expert.tool
async def retrieve_relevant_documentation(ctx: RunContext[WiskundeRAGDeps], user_query: str, cfg) -> str:
    """
    Zoek relevante documentatie chunks gebaseerd op de RAG query.
    
    Args:
        ctx: De Supabase client
        user_query: The user's question or query
        
    Returns:
        Een formatted string met de top 5 meest relevante documentatie chunks.
    """
    try:
        # Get the embedding for the query
        query_embedding = await get_embedding(user_query)
        
        # Query Supabase voor relevante documents
        result = ctx.deps.supabase.rpc(
            'match_documents',
            {
                'query_embedding': query_embedding,
                'match_count': cfg.mode.match_count,
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

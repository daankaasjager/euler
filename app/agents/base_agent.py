from dataclasses import dataclass
from dotenv import load_dotenv
from typing import Type
from supabase import Client
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider


load_dotenv()

@dataclass
class BaseAgentDeps:
    supabase: Client

def create_agent(
    model_name: str,
    base_url: str,
    system_prompt: str,
    deps_type: Type[BaseAgentDeps],
    retries: int = 2,
) -> Agent:
    model = OpenAIModel(
        model_name=model_name,
        provider=OpenAIProvider(base_url=base_url),
    )
    return Agent(
        model=model,
        system_prompt=system_prompt,
        deps_type=deps_type,
        retries=retries
    )

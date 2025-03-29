import os
import asyncio
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from src.ingestion.pdf2md import parse_pdf
from dotenv import load_dotenv
import hydra
from omegaconf import OmegaConf, DictConfig
import logging


load_dotenv()

logger = logging.getLogger(__name__)

# OpenAI Model
ollama_gemma_model = OpenAIModel(model_name=os.getenv("NEDER_MODEL"), 
                                 provider=OpenAIProvider(base_url='http://localhost:11434/v1'))


@hydra.main(version_base=None, config_path='configs',
            config_name='config')
def run(cfg: DictConfig):
    logger.info(OmegaConf.to_yaml(cfg))

    if cfg.mode._name_ == "parse_pdf":
        asyncio.run(parse_pdf(cfg))
    elif cfg.mode._name_ == "serve_api":
        serve_api(cfg)
        
        
    """model = ollama_gemma_model
    agent = Agent(
        model=model,
        system_prompt="Je bent een expert in wiskunde op het vmbo-tl 4 niveau. Je helpt leerlingen op een informele en behulpzame wijze en legt elke stap uit."
    )
    result = agent.run_sync(
        "In 2018 heeft een kasteel 65.000 bezoekers meer dan in 2017. Dat is een toename van 7,6%. " +
        "Hoeveel bezoekers waren er in 2017? Gebruik de procententabel."
    )
    print(result.data)
    print(result.usage())  """


if __name__ == "__main__":
    run()

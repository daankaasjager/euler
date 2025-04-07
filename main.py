import os
import asyncio
from dotenv import load_dotenv
import hydra
from omegaconf import OmegaConf, DictConfig
import logging
from sentence_transformers import SentenceTransformer
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider


load_dotenv()

logger = logging.getLogger(__name__)


async def run(cfg: DictConfig):
    logger.info(OmegaConf.to_yaml(cfg))
    if cfg.mode._name_ == "split_pdf":
        from src.ingestion.split_pdf import split_pdf_by_chapters
        split_pdf_by_chapters(cfg)
    elif cfg.mode._name_ == "parse_and_store":
        from src.ingestion.pdf2md import pdf2md
        # Step 1: PDF to Markdown
        parsed_md_paths = await pdf2md(cfg)

        # Step 2: Process and store the parsed documents
        from src.ingestion.process_and_store_md import process_and_store_md
        tasks = [
            process_and_store_md(cfg, parsed_md_path)
            for _, parsed_md_path in enumerate(parsed_md_paths)
        ]
        await asyncio.gather(*tasks)
    elif cfg.mode._name_ == "test_agent":
        from src.agent.rag import wiskunde_expert
        agent = wiskunde_expert

        result = await agent.run('Wat is een graaf?')
        print(result.data)

    elif cfg.mode._name_ == "serve_api":
        pass
        


@hydra.main(version_base=None, config_path='configs',
            config_name='config')
def main(cfg: DictConfig) -> None:
    asyncio.run(run(cfg))


if __name__ == "__main__":
    main()

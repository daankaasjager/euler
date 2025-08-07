import asyncio
from dotenv import load_dotenv
import hydra
from omegaconf import OmegaConf, DictConfig
import logging
from app.utils.supabase_client import get_supabase_client

load_dotenv()

logger = logging.getLogger(__name__)


async def run(cfg: DictConfig):
    logger.info(OmegaConf.to_yaml(cfg))
    if cfg.mode._name_ == "split_pdf":
        from app.ingestion import split_pdf_by_chapter_map, split_pdf_by_page_range
        chapter_map = {
        8: "Statistiek en kans",
        66: "Verbanden",
        114: "Drie dimensies, afstanden en hoeken",
        174: "Grafieken en vergelijkingen",
        226: "Einde"
        }
        # split_pdf_by_chapters(cfg)
        split_pdf_by_page_range(cfg, start=4, end=5, name="bewerkingen")

    elif cfg.mode._name_ == "parse_and_store":
        from app.ingestion import pdf2md
        # Step 1: PDF to Markdown
        parsed_md_paths = await pdf2md(cfg)

        # Step 2: Process and store the parsed documents
        from app.ingestion.process_and_store_md import process_and_store_md
        tasks = [
            process_and_store_md(cfg, parsed_md_path)
            for _, parsed_md_path in enumerate(parsed_md_paths)
        ]
        await asyncio.gather(*tasks)
    elif cfg.mode._name_ == "test_agent":
        from app.agents.wiskunde_expert_agent import wiskunde_expert, WiskundeRAGDeps
        agent = wiskunde_expert
        deps = WiskundeRAGDeps(supabase=get_supabase_client())
        result = await agent.run('Wat is een kwadraat?', deps=deps)
        print(result.data)

    elif cfg.mode._name_ == "delete_data":
        from app.ingestion.clear_supabase_table import clear_supabase_table
        clear_supabase_table(subject_filter=cfg.mode.subject_filter)


        
@hydra.main(version_base=None, config_path='configs',
            config_name='config')
def main(cfg: DictConfig) -> None:
    if cfg.mode._name_ == "serve_api":
        import subprocess
        subprocess.run(["streamlit", "run", "frontend/streamlit_app.py"])
    else:
        asyncio.run(run(cfg))


if __name__ == "__main__":
    main()

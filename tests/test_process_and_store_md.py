import os
import pytest
import asyncio
from omegaconf import OmegaConf
from dotenv import load_dotenv
from app.ingestion import process_and_store_md
from app.utils.supabase_client import get_supabase_client


load_dotenv()

@pytest.fixture
def test_markdown(tmp_path):
    md_path = tmp_path / "dummy.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("Gemiddelde is het totaal gedeeld door het aantal.")
    return md_path

@pytest.mark.skipif(os.getenv("SUPABASE_TEST") != "1", reason="SUPABASE_TEST not set")
def test_process_and_store_md_cleanup(test_markdown):
    cfg = OmegaConf.create({
        "mode": {
            "chunk_size": 5000,
            "semaphore": 5
        }
    })
    # Run processing
    asyncio.run(process_and_store_md(cfg, str(test_markdown)))

    # Optional: cleanup if you inserted into real Supabase
    from dotenv import load_dotenv
    load_dotenv()

    supabase = get_supabase_client()
    
    # Delete inserted chunks
    file_name = os.path.basename(test_markdown)
    deleted = supabase.table("documents").delete().eq("file_name", file_name).execute()
    print(f"🧽 Deleted test chunks for {file_name}: {deleted}")

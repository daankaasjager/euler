from llama_cloud_services import LlamaParse
from llama_index.core import SimpleDirectoryReader
from dotenv import load_dotenv
import os
import nest_asyncio
import logging

logger = logging.getLogger(__name__)
nest_asyncio.apply()
load_dotenv()

LLAMA_PARSE_KEY = os.getenv("LLAMA_PARSE_KEY")

llama_parser = LlamaParse(
    api_key=LLAMA_PARSE_KEY,
    result_type="markdown",
    num_workers=4,
    verbose=True,
    language="nl",
    base_url='https://api.cloud.eu.llamaindex.ai'
)


async def pdf2md(cfg):
    """
    Parses one or multiple PDFs using LlamaParse and returns structured markdown.
    If `cfg.mode.overwrite` is True, it will overwrite existing markdown files.
    """
    parsed_md_paths = []
    os.makedirs(cfg.mode.md_path, exist_ok=True)

    # Collect PDF files
    pdf_files = (
        [os.path.join(cfg.mode.pdf_path, f) for f in os.listdir(cfg.mode.pdf_path) if f.endswith(".pdf")]
        if cfg.mode.is_directory else [cfg.mode.pdf_path]
    )

    logger.info(f"📄 Found {len(pdf_files)} PDF file(s).")

    for pdf in pdf_files:
        md_filename = os.path.splitext(os.path.basename(pdf))[0] + ".md"
        md_path = os.path.join(cfg.mode.md_path, md_filename)

        # Check overwrite flag
        if os.path.exists(md_path) and not cfg.mode.overwrite:
            logger.info(f"⏭️  Skipping existing (no overwrite): {md_path}")
            parsed_md_paths.append(md_path)
            continue

        try:
            logger.info(f"🔍 Parsing {pdf} → {md_path}")
            file_extractor = {".pdf": llama_parser}
            parsed_docs = SimpleDirectoryReader(input_files=[pdf], file_extractor=file_extractor).load_data()

            with open(md_path, "w", encoding="utf-8") as f:
                for doc in parsed_docs:
                    # safe way
                    if isinstance(doc, dict):
                        f.write(doc.get("text", "").strip() + "\n\n")
                    else:
                        f.write(getattr(doc, "text", "").strip() + "\n\n")

            parsed_md_paths.append(md_path)
            logger.info(f"✅ Written: {md_path}")
        except Exception as e:
            logger.error(f"❌ Failed to parse {pdf}: {e}")

    return parsed_md_paths

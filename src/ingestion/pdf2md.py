from llama_cloud_services import LlamaParse
from llama_index.core import SimpleDirectoryReader
import json
import pypdf
from supabase import create_client, Client
import PyPDF2
from dotenv import load_dotenv
import os
import nest_asyncio


import logging

logger = logging.getLogger(__name__)

# loads supabase, llamaparse and other keys
load_dotenv()

LLAMA_PARSE_KEY = os.getenv("LLAMA_PARSE_KEY")

llama_parser = LlamaParse(
    api_key=LLAMA_PARSE_KEY,  # can also be set in your env as LLAMA_CLOUD_API_KEY
    result_type="markdown",  # "markdown" and "text" are available
    num_workers=4,  # if multiple files passed, split in `num_workers` API calls
    verbose=True,
    language="nl",  # Optionally you can define a language, default=en
    base_url='https://cloud.eu.llamaindex.ai',
    target_pages="2-10"
)

nest_asyncio.apply()

# 🔹 Book Section Mapping (Adjusted Page Numbers)
CHAPTER_MAPPING = {
    8: "Statistiek en kans",
    66: "Verbanden",
    114: "Drie dimensies, afstanden en hoeken",
    174: "Grafieken en vergelijkingen",
    226: "Einde"  # Stop processing after this section
}

async def parse_pdf(file_path: str):
    """
    Parses a PDF document using LlamaParse and returns structured markdown output.
    """
    try:
        # use SimpleDirectoryReader to parse our file
        file_extractor = {".pdf": llama_parser}
        parsed_documents = SimpleDirectoryReader(input_files=['data/pdf_data/leerboek_kgt_1.pdf'], file_extractor=file_extractor).load_data()
        return parsed_documents
    except Exception as e:
        logger.error(f"❌ Error parsing PDF with LlamaParse: {e}")
        return None

def map_text_to_chapters(parsed_data: list) -> list:
    """
    Maps parsed document sections to corresponding book chapters using page numbers.
    """
    structured_data = []
    current_chapter = "Onbekend"

    for section in parsed_data:
        page_number = section.metadata.get("page_number", 0)

        # Find correct chapter based on page number
        for chapter_start, chapter_name in CHAPTER_MAPPING.items():
            if page_number >= chapter_start:
                current_chapter = chapter_name
        
        # Stop processing if we reach the "Einde" section
        if current_chapter == "Einde":
            print(f"🚀 Stopping processing at page {page_number} (Einde reached).")
            break

        structured_data.append({
            "page_number": page_number,
            "chapter": current_chapter,
            "content": section.text
        })

    return structured_data


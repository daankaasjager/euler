from llama_parse import LlamaParse
import json
import pypdf
from supabase import create_client, Client
import PyPDF2
from dotenv import load_dotenv

# loads supabase, llamaparse and other keys
load_dotenv()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


llama_parser = LlamaParse(
    api_key=LLAMA_PARSE_KEY,  # can also be set in your env as LLAMA_CLOUD_API_KEY
    result_type="markdown",  # "markdown" and "text" are available
    num_workers=4,  # if multiple files passed, split in `num_workers` API calls
    verbose=True,
    language="nl",  # Optionally you can define a language, default=en
    base_url='https://cloud.eu.llamaindex.ai',
    target_pages="2-10"
)

# 🔹 Book Section Mapping (Adjusted Page Numbers)
CHAPTER_MAPPING = {
    8: "Statistiek en kans",
    66: "Verbanden",
    114: "Drie dimensies, afstanden en hoeken",
    174: "Grafieken en vergelijkingen",
    226: "Einde"  # Stop processing after this section
}

async def parse_pdf_with_llamaparse(file_path: str):
    """
    Parses a PDF document using LlamaParse and returns structured markdown output.
    """
    try:
        parsed_data = await llama_parser.aload_data(file_path=file_path)
        return parsed_data
    except Exception as e:
        print(f"❌ Error parsing PDF with LlamaParse: {e}")
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

def store_in_supabase(pdf_path: str, structured_data: list):
    """
    Stores the parsed Markdown content into Supabase with appropriate metadata.
    """
    document_data = [
        {
            "file_name": os.path.basename(pdf_path),
            "page_number": item["page_number"],
            "chapter": item["chapter"],
            "content": item["content"],
            "metadata": {
                "source": "Getal & Ruimte VMBO-TL 4",
                "level": "vmbo-tl",
                "language": "Dutch",
                "subject": "Mathematics"
            }
        } for item in structured_data
    ]

    try:
        response = supabase.table("documents").insert(document_data).execute()
        print(f"✅ Supabase upload completed: {response}")
    except Exception as e:
        print(f"❌ Error storing data in Supabase: {e}")


def extract_chapter(pdf_path, start_page, end_page, output_path):
    reader = PyPDF2.PdfReader(pdf_path)
    writer = PyPDF2.PdfWriter()

    # PyPDF2 is zero-indexed, so page 8 in your PDF is reader.pages[7]
    for i in range(start_page - 1, end_page):
        writer.add_page(reader.pages[i])

    with open(output_path, "wb") as f_out:
        writer.write(f_out)


async def process_and_store_document(pdf_path: str):
    """
    Orchestrates the entire pipeline: 
    1️⃣ Parse the PDF with LlamaParse
    2️⃣ Map parsed text to the correct book sections
    3️⃣ Store in Supabase
    """

    from PyPDF2 import PdfReader, PdfWriter

    pdf_in = PdfReader(pdf_path)
    pdf_out = PdfWriter()

    # Suppose you only want pages 1 through 5
    for page_num in range(0, 5):
        pdf_out.add_page(pdf_in.pages[page_num])

    with open("smallfile.pdf", "wb") as out_file:
        pdf_out.write(out_file)

    try:
        parsed_data = await parse_pdf_with_llamaparse(file_path="./smallfile.pdf")
        if parsed_data:
            structured_data = map_text_to_chapters(parsed_data)
            store_in_supabase(pdf_path, structured_data)
    except Exception as e:
        print(f"❌ Error processing document: {e}")
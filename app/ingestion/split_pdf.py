import PyPDF2
import os
import logging
from typing import Dict

logger = logging.getLogger(__name__)

def write_pages_to_pdf(reader, start: int, end: int, output_path: str):
    writer = PyPDF2.PdfWriter()
    total_pages = len(reader.pages)
    for page_num in range(start, min(end, total_pages)):
        writer.add_page(reader.pages[page_num])

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        writer.write(f)
    logger.info(f"✅ Saved PDF: {output_path}")


def split_pdf_by_chapter_map(cfg, chapter_map: Dict[int, str]):
    """
    Splits a PDF into chapters based on a provided mapping {page_start: chapter_title}
    """
    input_path = cfg.mode.input_file
    output_dir = cfg.mode.output_dir

    if not os.path.exists(input_path):
        logger.error(f"❌ File not found: {input_path}")
        return

    reader = PyPDF2.PdfReader(input_path)
    sorted_chapters = sorted(chapter_map.items())

    for i in range(len(sorted_chapters) - 1):
        start_page = sorted_chapters[i][0]
        end_page = sorted_chapters[i + 1][0]
        chapter_name = sorted_chapters[i][1]

        if chapter_name.lower() == "einde":
            continue

        filename = chapter_name.lower().replace(" ", "_") + ".pdf"
        output_path = os.path.join(output_dir, filename)
        write_pages_to_pdf(reader, start_page, end_page, output_path)


def split_pdf_by_page_range(cfg, start: int, end: int, name: str = "custom_selection"):
    """
    Allows slicing a specific page range into a single PDF output.
    """
    input_path = cfg.mode.input_file
    output_dir = cfg.mode.output_dir

    if not os.path.exists(input_path):
        logger.error(f"❌ File not found: {input_path}")
        return

    reader = PyPDF2.PdfReader(input_path)
    output_path = os.path.join(output_dir, f"{name}.pdf")
    write_pages_to_pdf(reader, start, end, output_path)

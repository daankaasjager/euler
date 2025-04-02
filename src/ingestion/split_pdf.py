import PyPDF2
import os
import logging

logger = logging.getLogger(__name__)

# 🔹 Book Section Mapping (Adjusted Page Numbers)
CHAPTER_MAPPING = {
    8: "Statistiek en kans",
    66: "Verbanden",
    114: "Drie dimensies, afstanden en hoeken",
    174: "Grafieken en vergelijkingen",
    226: "Einde"  # Stop processing after this section
}

def split_pdf_by_chapters(cfg):
    """
    Splits a PDF into chapters based on CHAPTER_MAPPING and saves them as new PDFs.
    """
    output_dir = cfg.mode.output_dir
    original_pdf_path = cfg.mode.input_file
    if not os.path.exists(original_pdf_path):   
        logger.error(f"❌ Original PDF not found at {original_pdf_path}")
        return
    
    if not os.path.exists(output_dir):
        logger.info(f"📁 Creating output directory: {output_dir}")
    os.makedirs(output_dir, exist_ok=True)

    reader = PyPDF2.PdfReader(original_pdf_path)
    total_pages = len(reader.pages)

    # Convert CHAPTER_MAPPING to a sorted list of (start_page, name)
    sorted_chapters = sorted(CHAPTER_MAPPING.items())

    for i in range(len(sorted_chapters) - 1):
        start_page = sorted_chapters[i][0]
        end_page = sorted_chapters[i + 1][0]
        chapter_name = sorted_chapters[i][1]

        if chapter_name.lower() == "einde":
            continue  # Skip final marker

        writer = PyPDF2.PdfWriter()
        for page_num in range(start_page, min(end_page, total_pages)):
            writer.add_page(reader.pages[page_num])

        clean_chapter_name = chapter_name.lower().replace(" ", "_")
        output_path = os.path.join(output_dir, f"{clean_chapter_name}.pdf")

        with open(output_path, "wb") as f:
            writer.write(f)

        logger.info(f"✅ Saved chapter '{chapter_name}' to {output_path}")
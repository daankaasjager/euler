import os
import shutil
import pytest
from fpdf import FPDF
from omegaconf import OmegaConf
import asyncio

from src.ingestion.pdf2md import pdf2md

@pytest.fixture
def dummy_pdf(tmp_path):
    pdf_path = tmp_path / "test.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt="Hoofdstuk 1: Gemiddelde\nHet gemiddelde van een reeks getallen is het totaal gedeeld door het aantal.")
    pdf.output(str(pdf_path))
    return pdf_path

def test_pdf2md_single(tmp_path, dummy_pdf):
    cfg = OmegaConf.create({
        "mode": {
            "pdf_path": str(dummy_pdf),
            "md_path": str(tmp_path),
            "is_directory": False,
            "language": "nl",
            "chunk_size": 5000
        }
    })

    markdown_files = asyncio.run(pdf2md(cfg))
    assert len(markdown_files) == 1
    assert os.path.exists(markdown_files[0])

    with open(markdown_files[0], "r", encoding="utf-8") as f:
        content = f.read()
        assert "Gemiddelde" in content

"""
pdf_utils.py
-------------
Utility functions for working with PDF documents.

Responsibilities:
- Validate PDF
- Get PDF information
- Convert PDF pages to images
- Cleanup temporary images
"""

from pathlib import Path
import shutil

import fitz

import config


# ==========================================================
# Validate PDF
# ==========================================================

def validate_pdf(pdf_path: str | Path) -> Path:
    """
    Validate that the PDF exists.

    Returns:
        Path object
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found:\n{pdf_path}")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError("Input file must be a PDF.")

    return pdf_path


# ==========================================================
# Page Count
# ==========================================================

def get_page_count(pdf_path: str | Path) -> int:
    """
    Return number of pages.
    """

    pdf_path = validate_pdf(pdf_path)

    with fitz.open(pdf_path) as doc:
        return len(doc)


# ==========================================================
# PDF Information
# ==========================================================

def get_pdf_info(pdf_path: str | Path) -> dict:
    """
    Return PDF metadata.
    """

    pdf_path = validate_pdf(pdf_path)

    with fitz.open(pdf_path) as doc:

        metadata = doc.metadata

        return {
            "pages": len(doc),
            "title": metadata.get("title"),
            "author": metadata.get("author"),
            "creator": metadata.get("creator"),
            "producer": metadata.get("producer"),
        }


# ==========================================================
# Convert PDF to Images
# ==========================================================

def pdf_to_images(pdf_path: str | Path) -> list[Path]:
    """
    Convert every page into a PNG.

    Returns:
        List of image paths.
    """

    pdf_path = validate_pdf(pdf_path)

    temp_dir = config.TEMP_DIR

    temp_dir.mkdir(exist_ok=True)

    image_paths = []

    zoom = config.PDF_DPI / 72

    matrix = fitz.Matrix(zoom, zoom)

    with fitz.open(pdf_path) as document:

        for page_number, page in enumerate(document, start=1):

            image_path = temp_dir / f"page_{page_number:04d}.png"

            pix = page.get_pixmap(matrix=matrix)

            pix.save(image_path)

            image_paths.append(image_path)

    return image_paths


# ==========================================================
# Cleanup
# ==========================================================

def cleanup_temp():
    """
    Delete temporary images.
    """

    if config.TEMP_DIR.exists():
        shutil.rmtree(config.TEMP_DIR)

    config.TEMP_DIR.mkdir(exist_ok=True)
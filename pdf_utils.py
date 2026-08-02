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
from logger import get_logger
logger = get_logger(__name__)

# Validate PDF This function will validate the pdf file and check if it exists and is a valid pdf file. It will return the path of the pdf file if it is valid, otherwise it will raise an error.

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
    logger.info("Validated PDF : %s", pdf_path)
    return pdf_path

# Page Count This function will count the number of pages in the pdf file and return it as an integer value

def get_page_count(pdf_path: str | Path) -> int:
    """
    Return number of pages.
    """

    pdf_path = validate_pdf(pdf_path)

    with fitz.open(pdf_path) as doc:
        return len(doc)



# PDF Information 


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



#Convert PDF to Images It will conver the pdf to iamges and return a list of image paths 
#You can specify the output directory where the images will be saved. If no output directory is provided, it will use a temporary directory defined in the config.
#Also can specify the DPI (dots per inch) for the image conversion. The default DPI is set in the config file.


def pdf_to_images(pdf_path: str | Path,output_dir: Path | None = None,) -> list[Path]:
    """
    Convert every page into a PNG.

    Returns:
        List of image paths.
    """

    pdf_path = validate_pdf(pdf_path)

    temp_dir = config.TEMP_DIR

    temp_dir.mkdir(parents=True,exist_ok=True,)

    image_paths = []

    zoom = config.PDF_DPI / 72

    matrix = fitz.Matrix(zoom, zoom)

    with fitz.open(pdf_path) as document:

        for page_number, page in enumerate(document, start=1):

            image_path = temp_dir / f"page_{page_number:04d}.png"

            pix = page.get_pixmap(matrix=matrix)

            pix.save(image_path)
            logger.info("Created image : %s",image_path.name,)

            image_paths.append(image_path)
            logger.info("Converted %d pages to images.",len(image_paths),)
    return image_paths



# Cleanup This function will delete the temporary images created during the pdf to image conversion process. It will also create a new temporary directory for the next run. You can specify a custom temporary directory, otherwise it will use the default one defined in the config.


def cleanup_temp(
    temp_dir: Path | None = None,
):
    """
    Delete temporary images.
    """

    temp_dir = temp_dir or config.TEMP_DIR

    if temp_dir.exists():

        shutil.rmtree(temp_dir)

        logger.info("Deleted temporary directory : %s",temp_dir,)

    temp_dir.mkdir(parents=True,exist_ok=True,)

    def create_temp_directory(timestamp: str,) -> Path:
        """
        Create a temporary folder for the current run.
        """

        temp_dir = config.TEMP_DIR / timestamp

        temp_dir.mkdir(parents=True,exist_ok=True,)

        logger.info("Created temporary directory : %s",temp_dir,)

        return temp_dir
    def pdf_name(pdf_path: str | Path,) -> str:
        """
        Return PDF filename without extension.
        """

        return Path(pdf_path).stem
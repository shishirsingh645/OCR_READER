"""
pdf_ocr.py
----------

Main entry point for the OCR Reader application.

Workflow
--------
1. Validate input folder
2. Locate PDF
3. Create timestamped output folder
4. Initialize logger
5. Check/download model
6. Convert PDF to images
7. OCR every page
8. Merge Markdown & JSON
9. Cleanup
10. Print execution summary
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys
import time

import config

from logger import (
    get_logger,
    get_log_file,
)

from pdf_utils import (
    validate_pdf,
    get_pdf_info,
    pdf_to_images,
    cleanup_temp,
)

from ocr_engine import OCREngine
from postprocessor import PostProcessor


class PDFOCR:
    """
    OCR workflow orchestrator.
    """

    def __init__(self):

        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.start_time = time.perf_counter()

        self.engine = OCREngine()

        self.pdf_path = None

        self.output_dir = None

        self.logger = None

        self.summary = {}

    # --------------------------------------------------

    def initialize(self):
        """
        Initialize directories and logger.
        """

        config.INPUT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        config.OUTPUT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        config.LOG_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.logger = get_logger(__name__)

        self.logger.info("=" * 60)
        self.logger.info("OCR Reader Started")
        self.logger.info("Timestamp : %s", self.timestamp)
        self.logger.info("=" * 60)

    # --------------------------------------------------

    def locate_pdf(self):
        """
        Locate a single PDF inside the input directory.
        """

        pdf_files = sorted(
            config.INPUT_DIR.glob("*.pdf")
        )

        if not pdf_files:
            raise FileNotFoundError(
                f"No PDF found in '{config.INPUT_DIR}'."
            )

        if len(pdf_files) > 1:
            raise RuntimeError(
                "Multiple PDFs found. Keep only one PDF inside the input folder."
            )

        self.pdf_path = validate_pdf(pdf_files[0])

        self.logger.info(
            "Input PDF : %s",
            self.pdf_path.name,
        )

    # --------------------------------------------------

    def create_output_directory(self):
        """
        Create timestamped output directory.
        """

        folder_name = (
            f"{self.pdf_path.stem}_{self.timestamp}"
        )

        self.output_dir = (
            config.OUTPUT_DIR /
            folder_name
        )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.logger.info(
            "Output Directory : %s",
            self.output_dir,
        )

    # --------------------------------------------------

    def prepare_engine(self):
        """
        Initialize OCR engine.
        """

        self.logger.info(
            "Checking OCR model..."
        )

        self.engine.initialize()

        self.logger.info(
            "OCR Engine Ready."
        )

    # --------------------------------------------------

    def pdf_information(self):
        """
        Read PDF metadata.
        """

        info = get_pdf_info(
            self.pdf_path
        )

        self.summary.update(info)

        self.logger.info(
            "Total Pages : %d",
            info["pages"],
        )

    # --------------------------------------------------

    def convert_pdf(self):
        """
        Convert PDF pages to images.
        """

        self.logger.info("Converting PDF to images...")

        image_dir = self.output_dir / "images"

        self.images = pdf_to_images(
            self.pdf_path,
            output_dir=image_dir,
        )

        self.logger.info(
            "Generated %d page images.",
            len(self.images),
        )

    # --------------------------------------------------

    def process_pages(self):
        """
        OCR every page.
        """

        self.logger.info("Starting OCR...")

        self.results = []

        total_pages = len(self.images)

        for index, image in enumerate(self.images, start=1):

            self.logger.info(
                "Page %d/%d",
                index,
                total_pages,
            )

            result = self.engine.ocr_image(
                image_path=image,
                output_dir=self.output_dir,
            )

            self.results.append(result)

        self.logger.info(
            "OCR completed for %d pages.",
            len(self.results),
        )

    # --------------------------------------------------

    def merge_outputs(self):
        """
        Merge page-wise Markdown and JSON.
        """

        self.logger.info(
            "Merging OCR outputs..."
        )

        processor = PostProcessor()

        result = processor.process(
            self.output_dir
        )

        merged_md = Path(result["markdown"])
        merged_json = Path(result["json"])

        final_md = (
            self.output_dir /
            f"{self.pdf_path.stem}_{self.timestamp}.md"
        )

        final_json = (
            self.output_dir /
            f"{self.pdf_path.stem}_{self.timestamp}.json"
        )
        if merged_md.exists():
            merged_md.replace(final_md)

        if merged_json.exists():
            merged_json.replace(final_json)

        self.summary.update(
            {
                "markdown": str(final_md),
                "json": str(final_json),
                "pages_processed": len(self.results),
            }
        )

        self.logger.info(
            "Merged Markdown : %s",
            final_md.name,
        )

        self.logger.info(
            "Merged JSON : %s",
            final_json.name,
        )

    # --------------------------------------------------

    def process(self):
        """
        Execute the OCR processing pipeline.
        """

        self.locate_pdf()

        self.create_output_directory()

        self.prepare_engine()

        self.pdf_information()

        self.convert_pdf()

        self.process_pages()

        self.merge_outputs()    # --------------------------------------------------

    def cleanup(self):
        """
        Cleanup resources.
        """

        self.logger.info(
            "Cleaning up temporary resources..."
        )

        cleanup_temp()

        self.engine.cleanup()

        self.logger.info(
            "Cleanup completed."
        )

    # --------------------------------------------------

    def print_summary(self):
        """
        Log execution summary.
        """

        elapsed = round(
            time.perf_counter() - self.start_time,
            2,
        )

        self.summary.update(
            {
                "pdf": str(self.pdf_path),
                "output_directory": str(self.output_dir),
                "processing_time": elapsed,
                "log_file": str(get_log_file()),
            }
        )

        self.logger.info("=" * 60)
        self.logger.info("OCR Processing Completed")
        self.logger.info("=" * 60)
        self.logger.info("PDF              : %s", self.pdf_path.name)
        self.logger.info("Pages            : %d", self.summary["pages"])
        self.logger.info("Output Directory : %s", self.output_dir)
        self.logger.info("Markdown         : %s", self.summary["markdown"])
        self.logger.info("JSON             : %s", self.summary["json"])
        self.logger.info("Log File         : %s", get_log_file())
        self.logger.info("Processing Time  : %.2f seconds", elapsed)
        self.logger.info("=" * 60)

    # --------------------------------------------------

    def run(self):
        """
        Execute the complete OCR workflow.
        """

        try:

            self.initialize()

            self.process()

            self.print_summary()

            return self.summary

        except Exception as exc:

            if self.logger is None:
                self.logger = get_logger(__name__)

            self.logger.exception(
                "OCR workflow failed."
            )

            raise exc

        finally:

            self.cleanup()


# ==========================================================
# Main
# ==========================================================

def main():

    workflow = PDFOCR()

    try:

        workflow.run()

        print("\nOCR completed successfully.")

    except Exception as exc:

        print(f"\nERROR : {exc}")

        sys.exit(1)


if __name__ == "__main__":

    main()
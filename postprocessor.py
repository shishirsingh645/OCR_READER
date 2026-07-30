"""
postprocessor.py
----------------
Merge page-wise OCR outputs into a single Markdown and JSON document.
"""

from __future__ import annotations

import json
from pathlib import Path

from exceptions import OutputWriteError
from logger import get_logger


class PostProcessor:

    def __init__(self):

        self.logger = get_logger(__name__)

    # --------------------------------------------------

    def merge_markdown(
        self,
        markdown_dir: Path,
        output_file: Path,
    ) -> Path:

        markdown_dir = Path(markdown_dir)
        output_file = Path(output_file)

        if not markdown_dir.exists():
            raise FileNotFoundError(markdown_dir)

        pages = sorted(markdown_dir.glob("*.md"))

        if not pages:
            raise FileNotFoundError("No markdown files found.")

        try:

            output_file.parent.mkdir(parents=True, exist_ok=True)

            with output_file.open("w", encoding="utf-8") as outfile:

                for page in pages:

                    outfile.write(f"# {page.stem}\n\n")
                    outfile.write(page.read_text(encoding="utf-8"))
                    outfile.write("\n\n")

            self.logger.info(
                "Merged %d markdown pages -> %s",
                len(pages),
                output_file,
            )

            return output_file

        except Exception as exc:

            self.logger.exception("Markdown merge failed.")

            raise OutputWriteError(str(exc)) from exc

    # --------------------------------------------------

    def merge_json(
        self,
        json_dir: Path,
        output_file: Path,
    ) -> Path:

        json_dir = Path(json_dir)
        output_file = Path(output_file)

        if not json_dir.exists():
            raise FileNotFoundError(json_dir)

        pages = sorted(json_dir.glob("*.json"))

        if not pages:
            raise FileNotFoundError("No json files found.")

        merged = []

        try:

            for page in pages:

                with page.open(
                    "r",
                    encoding="utf-8",
                ) as fp:

                    merged.append(json.load(fp))

            output_file.parent.mkdir(parents=True, exist_ok=True)

            with output_file.open(
                "w",
                encoding="utf-8",
            ) as fp:

                json.dump(
                    merged,
                    fp,
                    indent=4,
                    ensure_ascii=False,
                )

            self.logger.info(
                "Merged %d json pages -> %s",
                len(pages),
                output_file,
            )

            return output_file

        except Exception as exc:

            self.logger.exception("JSON merge failed.")

            raise OutputWriteError(str(exc)) from exc

    # --------------------------------------------------

    def process(
        self,
        output_dir: Path,
    ) -> dict:

        output_dir = Path(output_dir)

        markdown_file = self.merge_markdown(
            output_dir / "markdown",
            output_dir / "merged.md",
        )

        json_file = self.merge_json(
            output_dir / "json",
            output_dir / "merged.json",
        )

        return {
            "markdown": str(markdown_file),
            "json": str(json_file),
        }
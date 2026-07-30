"""
ocr_engine.py
-------------
Model download and loading for Unlimited-OCR.
"""


import torch
from huggingface_hub import snapshot_download
from transformers import AutoModel, AutoTokenizer
import config
import time
from pathlib import Path
import io
import json
from contextlib import redirect_stdout



from exceptions import (
    GPUNotAvailableError,
    InferenceError,
    InvalidImageError,
    ModelDownloadError,
    ModelLoadError,
)
from logger import get_logger

class OCREngine:
    """
    Singleton OCR Engine.
    """

    def __init__(self):

        self.logger = get_logger(__name__)
        self.device = config.DEVICE
        self.model = None
        self.tokenizer = None
        self.initialized = False
# --------------------------------------------------

    def model_exists(self) -> bool:
        """
        Check whether the model is already downloaded.
        """

        if not config.MODEL_DIR.exists():
            return False

        required = [
            "config.json",
            "tokenizer_config.json",
        ]

        for file in required:
            if not (config.MODEL_DIR / file).exists():
                return False

        return any(
            config.MODEL_DIR.glob("*.safetensors")
        ) or (
            config.MODEL_DIR /
            "model.safetensors.index.json"
        ).exists()


    # --------------------------------------------------

    def download_model(self):

        config.MODEL_DIR.mkdir(parents=True, exist_ok=True)

        if self.model_exists():
            self.logger.info("Local model found.")
            return

        self.logger.info("Downloading Unlimited-OCR model...")

        try:

            snapshot_download(
                repo_id=config.MODEL_ID,
                local_dir=config.MODEL_DIR,
                local_dir_use_symlinks=False,
            )

            self.logger.info("Model downloaded successfully.")

        except Exception as exc:
            self.logger.exception("Model download failed.")
            raise ModelDownloadError(str(exc)) from exc

    # --------------------------------------------------

    def load_model(self):

        if self.model is not None:
            return

        self.download_model()

        try:

            self.logger.info("Loading tokenizer...")

            self.tokenizer = AutoTokenizer.from_pretrained(
                config.MODEL_DIR,
                trust_remote_code=True,
            )

            self.logger.info("Loading model...")

            self.model = AutoModel.from_pretrained(
                config.MODEL_DIR,
                trust_remote_code=True,
                use_safetensors=True,
                dtype=torch.bfloat16,
            )

            self.model = self.model.eval().to(self.device)

            self.logger.info("Model loaded successfully.")

        except Exception as exc:

            self.logger.exception("Failed to load model.")

            raise ModelLoadError(str(exc)) from exc
    # --------------------------------------------------
    def initialize(self):

        if self.initialized:
            return

        if self.device.type == "cuda" and not torch.cuda.is_available():
            raise GPUNotAvailableError("CUDA device not available.")

        self.load_model()

        self.initialized = True

    # --------------------------------------------------

    def ocr_image(
        self,
        image_path: Path,
        output_dir: Path,
        prompt: str = "<image>document parsing.",
    ):

        if not self.initialized:
            self.initialize()

        image_path = Path(image_path)

        if not image_path.exists():
            raise InvalidImageError(f"{image_path} not found.")

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        start = time.perf_counter()

        try:

            self.logger.info("Processing page : %s",image_path.name,)

            buffer = io.StringIO()

            with redirect_stdout(buffer):

                self.model.infer(
                    self.tokenizer,
                    prompt=prompt,
                    image_file=str(image_path),
                    output_path=str(output_dir),
                    base_size=config.BASE_SIZE,
                    image_size=config.IMAGE_SIZE,
                    crop_mode=False,
                )

            ocr_text = buffer.getvalue()

            markdown_dir = output_dir / "markdown"
            markdown_dir.mkdir(parents=True, exist_ok=True)

            markdown_file = markdown_dir / f"{image_path.stem}.md"

            markdown_file.write_text(
                ocr_text,
                encoding="utf-8",
            )

            json_dir = output_dir / "json"
            json_dir.mkdir(parents=True, exist_ok=True)

            json_file = json_dir / f"{image_path.stem}.json"

            with open(
                json_file,
                "w",
                encoding="utf-8",
            ) as fp:

                json.dump(
                    {
                        "page": image_path.stem,
                        "ocr": ocr_text,
                    },
                    fp,
                    indent=4,
                    ensure_ascii=False,
                )

            elapsed = time.perf_counter() - start

            self.logger.info("%s completed in %.2f seconds.",image_path.name,elapsed,)

            return {
                "success": True,
                "page": image_path.stem,
                "image": str(image_path),
                "output": str(output_dir),
                "markdown": str(markdown_file),
                "json": str(json_file),
                "device": self.device.type,
                "time": round(elapsed, 2),
                }

        except Exception as exc:

            self.logger.exception("OCR inference failed.")

            raise InferenceError(str(exc)) from exc
    # --------------------------------------------------
    def ready(self):

        return (
            self.initialized and self.model is not None and self.tokenizer is not None
        )
     # --------------------------------------------------

    def health_check(self):

        return {
            "ready": self.ready(),
            "device": self.device.type,
            "model_loaded": self.model is not None,
            "tokenizer_loaded": self.tokenizer is not None,
        }
     # --------------------------------------------------
    def cleanup(self):

        self.model = None
        self.tokenizer = None
        self.initialized = False

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        self.logger.info("OCR engine cleaned up.")

        # --------------------------------------------------

def model_exists(self) -> bool:
    """
    Verify that the required model files exist.
    """

    required_files = [
        "config.json",
        "tokenizer_config.json",
        "model.safetensors.index.json",
    ]

    return all(
        (config.MODEL_DIR / file).exists()
        for file in required_files
    )
"""
ocr_engine.py
-------------
Model download and loading for Unlimited-OCR.
"""

from pathlib import Path

import torch
from huggingface_hub import snapshot_download
from transformers import AutoModel, AutoTokenizer

import config


class OCREngine:
    """
    Singleton OCR Engine.
    """

    def __init__(self):

        self.device = config.DEVICE

        self.model = None

        self.tokenizer = None

    # --------------------------------------------------

    def download_model(self):

        """
        Download the model only if it does not already exist.
        """

        config.MODEL_DIR.mkdir(parents=True, exist_ok=True)

        if any(config.MODEL_DIR.iterdir()):
            print("✓ Local model found.")
            return

        print("Downloading Unlimited-OCR model...")

        snapshot_download(
            repo_id=config.MODEL_ID,
            local_dir=config.MODEL_DIR,
            local_dir_use_symlinks=False,
        )

        print("✓ Model downloaded.")

    # --------------------------------------------------

    def load_model(self):

        """
        Load tokenizer and model.
        """

        if self.model is not None:
            return

        self.download_model()

        print("Loading tokenizer...")

        self.tokenizer = AutoTokenizer.from_pretrained(
            config.MODEL_DIR,
            trust_remote_code=True,
        )

        print("Loading model...")

        self.model = AutoModel.from_pretrained(
            config.MODEL_DIR,
            trust_remote_code=True,
            use_safetensors=True,
            torch_dtype=torch.bfloat16,
        )

        self.model = self.model.eval().to(self.device)

        print("✓ Model loaded successfully.")

    # --------------------------------------------------

    def ready(self):

        return self.model is not None
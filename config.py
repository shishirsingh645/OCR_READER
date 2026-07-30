"""
Project Configuration
---------------------
Centralized configuration for the OCR Reader project.
"""

from pathlib import Path
import torch


# ==========================================================
# Project Root
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent


# ==========================================================
# Directories
# ==========================================================

INPUT_DIR = PROJECT_ROOT / "input"

OUTPUT_DIR = PROJECT_ROOT / "output"

TEMP_DIR = PROJECT_ROOT / "temp"

MODEL_DIR = PROJECT_ROOT / "models" / "Unlimited-OCR"

LOG_DIR = PROJECT_ROOT / "logs"


# ==========================================================
# Hugging Face Model
# ==========================================================

MODEL_ID = "baidu/Unlimited-OCR"


# ==========================================================
# Device
# ==========================================================

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ==========================================================
# OCR Settings
# ==========================================================

PDF_DPI = 300

BASE_SIZE = 1024

IMAGE_SIZE = 1024

PROMPT = "<image>document parsing."


# ==========================================================
# Generation Settings
# ==========================================================

MAX_NEW_TOKENS = 8192

TEMPERATURE = 0.0

DO_SAMPLE = False


# ==========================================================
# Output
# ==========================================================

SAVE_MARKDOWN = True

SAVE_JSON = True


# ==========================================================
# Logging
# ==========================================================

LOG_LEVEL = "INFO"

LOG_FILE = LOG_DIR / "ocr.log"


# ==========================================================
# Create Required Directories
# ==========================================================

for directory in (
    INPUT_DIR,
    OUTPUT_DIR,
    TEMP_DIR,
    MODEL_DIR,
    LOG_DIR,
):
    directory.mkdir(parents=True, exist_ok=True)
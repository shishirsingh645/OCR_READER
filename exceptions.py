"""
exceptions.py
-------------

Custom exception hierarchy for OCR Reader.
"""


class OCRReaderError(Exception):
    """Base exception for the OCR Reader project."""


class ConfigurationError(OCRReaderError):
    """Configuration is invalid."""


class PDFError(OCRReaderError):
    """PDF processing failed."""


class ModelDownloadError(OCRReaderError):
    """Unable to download the model."""


class ModelLoadError(OCRReaderError):
    """Unable to load the model."""


class InferenceError(OCRReaderError):
    """OCR inference failed."""


class GPUNotAvailableError(OCRReaderError):
    """CUDA device is unavailable."""


class InvalidImageError(OCRReaderError):
    """Input image is invalid."""


class OutputWriteError(OCRReaderError):
    """Unable to write OCR output."""
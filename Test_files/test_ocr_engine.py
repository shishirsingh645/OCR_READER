from pathlib import Path

from ocr_engine import OCREngine

engine = OCREngine()

engine.initialize()

result = engine.ocr_image(
    image_path=Path("temp/page_0001.png"),
    output_dir=Path("output/sample_pdf"),
)

print(result)

print(engine.health_check())
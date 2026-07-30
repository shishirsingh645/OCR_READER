from ocr_engine import OCREngine

engine = OCREngine()

engine.load_model()

print(engine.ready())
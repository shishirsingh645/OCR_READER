from pathlib import Path

from postprocessor import PostProcessor

processor = PostProcessor()

result = processor.process(
    Path("output/sample_pdf")
)

print(result)
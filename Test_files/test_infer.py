from transformers import AutoModel, AutoTokenizer
import torch

MODEL_PATH = "models/Unlimited-OCR"

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_PATH,
    trust_remote_code=True,
)

model = AutoModel.from_pretrained(
    MODEL_PATH,
    trust_remote_code=True,
    dtype=torch.bfloat16,
    use_safetensors=True,
).eval().cuda()

result = model.infer(
    tokenizer=tokenizer,
    prompt="<image>document parsing.",
    image_file="temp/page_0001.png",
    output_path="output/test_output",
    base_size=1024,
    image_size=1024,
    crop_mode=False,
    max_length=32768,
    save_results=True,
)

print("=" * 80)
print("RETURN VALUE:")
print(repr(result))
print("=" * 80)
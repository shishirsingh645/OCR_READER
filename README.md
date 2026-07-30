# OCR Reader

OCR Reader is a local Python OCR pipeline for converting a single PDF into page images, running OCR with Baidu's `Unlimited-OCR` Hugging Face model, and saving page-wise plus merged Markdown and JSON output.

The current project is organized as a script-based application. The main entry point is `pdf_ocr.py`; tests are standalone Python scripts under `Test_files/`.

## Features

- Processes one PDF at a time from the `input/` directory.
- Downloads and loads the `baidu/Unlimited-OCR` model into `models/Unlimited-OCR`.
- Uses PyMuPDF to convert PDF pages to PNG images.
- Runs OCR for each page image through the Unlimited-OCR model.
- Writes page-wise Markdown files under `markdown/`.
- Writes page-wise JSON files under `json/`.
- Merges page-wise OCR output into final Markdown and JSON files.
- Creates timestamped output folders under `output/`.
- Logs to console and rotating UTF-8 log files under `logs/`.
- Provides custom exception classes for model, inference, PDF, image, configuration, and output failures.

## Project Structure

```text
OCR READER/
+-- .gitignore
+-- LICENSE
+-- README.md
+-- config.py
+-- exceptions.py
+-- logger.py
+-- ocr_engine.py
+-- pdf_ocr.py
+-- pdf_utils.py
+-- postprocessor.py
+-- requirements.txt
+-- input/
|   +-- *.pdf
+-- logs/
|   +-- OCR_*.log
+-- models/
|   +-- Unlimited-OCR/
|       +-- config.json
|       +-- tokenizer_config.json
|       +-- model-*.safetensors
|       +-- model.safetensors.index.json
|       +-- model/tokenizer support files
+-- output/
|   +-- <pdf_name>_<timestamp>/
|       +-- images/
|       +-- json/
|       |   +-- page_*.json
|       +-- markdown/
|       |   +-- page_*.md
|       +-- <pdf_name>_<timestamp>.json
|       +-- <pdf_name>_<timestamp>.md
+-- temp/
|   +-- page_*.png
+-- cache/
+-- samples/
+-- Test_files/
    +-- test_exceptions.py
    +-- test_infer.py
    +-- test_logger.py
    +-- test_model.py
    +-- test_ocr_engine.py
    +-- test_postprocessor.py
```

Ignored/generated directories include `.venv/`, `__pycache__/`, `input/`, `logs/`, `models/`, `output/`, `temp/`, and `samples/`.

## Source File Summary

| File | Purpose |
| --- | --- |
| `config.py` | Central project configuration, directory paths, model ID, OCR settings, generation settings, and directory creation. |
| `exceptions.py` | Custom exception hierarchy used by the OCR pipeline. |
| `logger.py` | Centralized console and rotating file logger setup. |
| `ocr_engine.py` | Downloads, loads, initializes, runs, checks, and cleans up the Unlimited-OCR model. |
| `pdf_ocr.py` | Main workflow orchestration and CLI entry point. |
| `pdf_utils.py` | PDF validation, metadata extraction, page rendering, and temp cleanup helpers. |
| `postprocessor.py` | Merges page-level Markdown and JSON OCR files. |
| `requirements.txt` | Python dependency list. |

## Prerequisites

Install the following before running the project:

- Python 3.10+ is recommended. The exact Python version is not pinned in the project.
- `pip`
- Git, if cloning from a repository.
- A machine capable of running PyTorch and the Unlimited-OCR model.
- CUDA-compatible GPU is strongly implied by the test scripts because `Test_files/test_infer.py` calls `.cuda()` directly.
- Internet access for the first model download from Hugging Face, unless `models/Unlimited-OCR` is already populated.

Python dependencies are listed in `requirements.txt`:

```text
torch==2.11.0
torchvision
torchaudio
transformers>=4.56.2
accelerate>=1.10.0
huggingface_hub>=0.34.0
safetensors>=0.6.0
sentencepiece
PyMuPDF>=1.26.0
Pillow>=11.3.0
numpy>=2.3.0
tqdm>=4.67.0
requests>=2.32.0
addict
matplotlib
einops
easydict
PyYAML>=6.0
```

No required environment variables are defined in the project code. If Hugging Face authentication is needed for model access in your environment, configure it externally with the Hugging Face tooling; the project itself does not read a token from a project-specific environment variable.

## Local Setup From Scratch

1. Clone or copy the project.

   ```powershell
   git clone <repository-url>
   cd "OCR READER"
   ```

2. Create a virtual environment.

   ```powershell
   python -m venv .venv
   ```

3. Activate the virtual environment.

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation scripts, enable them for the current process:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1
   ```

4. Install dependencies.

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. Put exactly one PDF file in `input/`.

```text
input/
+-- your_file.pdf
```

6. Run the application.

   ```powershell
   python pdf_ocr.py
   ```

## Running the Application

From the project root:

```powershell
python pdf_ocr.py
```

The application performs this workflow:

1. Creates required directories from `config.py`.
2. Finds PDFs in `input/`.
3. Fails if no PDF exists.
4. Fails if more than one PDF exists.
5. Creates `output/<pdf_name>_<timestamp>/`.
6. Downloads the Unlimited-OCR model if required files are not present.
7. Loads the tokenizer and model.
8. Converts the PDF into page PNG files.
9. Runs OCR page by page.
10. Writes page Markdown and JSON files.
11. Merges page outputs into final Markdown and JSON files.
12. Cleans up `temp/`.
13. Writes an execution summary to the log.

Expected output layout:

```text
output/<pdf_name>_<timestamp>/
+-- json/
|   +-- page_0001.json
|   +-- ...
+-- markdown/
|   +-- page_0001.md
|   +-- ...
+-- <pdf_name>_<timestamp>.json
+-- <pdf_name>_<timestamp>.md
```

Logs are written to:

```text
logs/OCR_<timestamp>.log
```

## Configuration

Configuration is defined in `config.py`.

| Setting | Current value | Description |
| --- | --- | --- |
| `PROJECT_ROOT` | Directory containing `config.py` | Project root path. |
| `INPUT_DIR` | `input/` | Directory where the input PDF must be placed. |
| `OUTPUT_DIR` | `output/` | Directory for timestamped OCR output folders. |
| `TEMP_DIR` | `temp/` | Directory for temporary rendered page images. |
| `MODEL_DIR` | `models/Unlimited-OCR` | Local Hugging Face model directory. |
| `LOG_DIR` | `logs/` | Log output directory. |
| `MODEL_ID` | `baidu/Unlimited-OCR` | Hugging Face repository ID used by `snapshot_download`. |
| `DEVICE` | `cuda` if available, otherwise `cpu` | PyTorch device selected at import time. |
| `PDF_DPI` | `300` | PDF rendering DPI. |
| `BASE_SIZE` | `1024` | Passed to model inference. |
| `IMAGE_SIZE` | `1024` | Passed to model inference. |
| `PROMPT` | `<image>document parsing.` | OCR prompt. |
| `MAX_NEW_TOKENS` | `8192` | Defined but not currently passed by `OCREngine.ocr_image`. |
| `TEMPERATURE` | `0.0` | Defined but not currently passed by `OCREngine.ocr_image`. |
| `DO_SAMPLE` | `False` | Defined but not currently passed by `OCREngine.ocr_image`. |
| `SAVE_MARKDOWN` | `True` | Defined but not currently used as a conditional switch. |
| `SAVE_JSON` | `True` | Defined but not currently used as a conditional switch. |
| `LOG_LEVEL` | `INFO` | Root logger level. |
| `LOG_FILE` | `logs/ocr.log` | Defined, but `logger.py` creates timestamped `OCR_*.log` files by default. |

## Tests

The `Test_files/` directory contains standalone Python scripts. They are not structured as `pytest` unit tests and do not contain assertions. Run them manually from the project root.

Before running model or OCR tests, make sure:

- Dependencies are installed.
- `models/Unlimited-OCR` exists or the model can be downloaded.
- `temp/page_0001.png` exists for tests that use it directly.
- `output/sample_pdf/markdown` and `output/sample_pdf/json` contain page files for the postprocessor test.
- A CUDA GPU is available for `test_infer.py`, because that script calls `.cuda()`.

### `Test_files/test_logger.py`

Purpose: Verifies that `get_logger()` initializes the logger and writes info, warning, and error messages.

Run:

```powershell
python Test_files/test_logger.py
```

Expected result:

- Console log messages are printed.
- A timestamped log file is created in `logs/`.

### `Test_files/test_exceptions.py`

Purpose: Confirms that custom exceptions can be imported and raised.

Run:

```powershell
python Test_files/test_exceptions.py
```

Expected result:

- The script raises `exceptions.ModelLoadError: Test exception.`
- This is an intentional failure-style test.

### `Test_files/test_model.py`

Purpose: Instantiates `OCREngine`, calls `engine.load_model()`, and prints `engine.ready()`.

Run:

```powershell
python Test_files/test_model.py
```

Expected result:

- The model is downloaded if missing.
- The tokenizer and model are loaded.
- The script prints `False` because `load_model()` loads model objects but does not set `engine.initialized`; `ready()` requires `initialized` to be `True`.

### `Test_files/test_infer.py`

Purpose: Directly loads the Unlimited-OCR tokenizer/model from `models/Unlimited-OCR` and calls `model.infer()` on `temp/page_0001.png`.

Run:

```powershell
python Test_files/test_infer.py
```

Expected result:

- Requires `models/Unlimited-OCR`.
- Requires `temp/page_0001.png`.
- Requires CUDA because the script calls `.eval().cuda()`.
- Writes model output to `output/test_output`.
- Prints the return value from `model.infer()`.

### `Test_files/test_ocr_engine.py`

Purpose: Exercises the project wrapper class `OCREngine` by initializing the engine, running OCR on `temp/page_0001.png`, and printing the OCR result plus health check.

Run:

```powershell
python Test_files/test_ocr_engine.py
```

Expected result:

- Requires `temp/page_0001.png`.
- Writes OCR output under `output/sample_pdf`.
- Prints a result dictionary with output paths, device, and timing.
- Prints `engine.health_check()`.

### `Test_files/test_postprocessor.py`

Purpose: Merges existing page-wise Markdown and JSON files under `output/sample_pdf`.

Run:

```powershell
python Test_files/test_postprocessor.py
```

Expected result:

- Requires `output/sample_pdf/markdown/*.md`.
- Requires `output/sample_pdf/json/*.json`.
- Writes `output/sample_pdf/merged.md`.
- Writes `output/sample_pdf/merged.json`.
- Prints a dictionary containing the merged file paths.

## Manual Verification Workflow

To manually verify the full pipeline from scratch:

1. Activate the virtual environment.

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

2. Confirm there is exactly one PDF in `input/`.

   ```powershell
   Get-ChildItem input -Filter *.pdf
   ```

3. Run the application.

   ```powershell
   python pdf_ocr.py
   ```

4. Confirm a new timestamped output folder exists.

   ```powershell
   Get-ChildItem output
   ```

5. Confirm final merged files exist inside the newest output folder.

   ```powershell
   Get-ChildItem output\<pdf_name>_<timestamp>
   ```

6. Confirm page-wise files exist.

   ```powershell
   Get-ChildItem output\<pdf_name>_<timestamp>\markdown
   Get-ChildItem output\<pdf_name>_<timestamp>\json
   ```

7. Review the log file.

   ```powershell
   Get-ChildItem logs
   Get-Content logs\<log_file_name>.log
   ```

## Troubleshooting

### `No PDF found in 'input'`

Place one `.pdf` file in the `input/` directory and run `python pdf_ocr.py` again.

### `Multiple PDFs found`

The workflow only supports one input PDF at a time. Leave exactly one PDF in `input/`.

### Model download fails

Check internet access and Hugging Face availability. The project downloads `baidu/Unlimited-OCR` into `models/Unlimited-OCR` using `huggingface_hub.snapshot_download()`.

### Model load fails

Confirm that dependencies from `requirements.txt` are installed and that `models/Unlimited-OCR` contains at least:

```text
config.json
tokenizer_config.json
model.safetensors.index.json
*.safetensors
```

Also confirm that PyTorch can run on the selected device.

### CUDA errors

`config.DEVICE` uses CUDA only when `torch.cuda.is_available()` returns `True`; otherwise it selects CPU. However, `Test_files/test_infer.py` explicitly calls `.cuda()`, so that script requires a CUDA-capable environment.

### `temp/page_0001.png` not found in tests

Some test scripts assume that `temp/page_0001.png` already exists. Generate it by running the PDF conversion step as part of the main workflow, or run the full application once with a valid input PDF.

### Postprocessor test fails with missing Markdown or JSON files

`Test_files/test_postprocessor.py` expects existing files under:

```text
output/sample_pdf/markdown/
output/sample_pdf/json/
```

Run OCR first or create the expected page-wise outputs before running the postprocessor test.

### Output directory has no `images/` files

`PDFOCR.convert_pdf()` passes an output image directory to `pdf_to_images()`, but the current `pdf_to_images()` implementation writes rendered pages to `temp/` instead of the provided `output_dir`. This is a current implementation limitation.

### Logs appear more than once

`logger.py` configures the root logger once per Python process. Re-importing modules in the same process may reuse the existing logger setup.

## Known Limitations and TODOs

- The project does not define a package structure or `pyproject.toml`/`setup.py`.
- The tests are standalone scripts rather than automated unit tests with assertions.
- There is no documented command-line argument support; `pdf_ocr.py` always reads from `input/`.
- Only one PDF in `input/` is supported per run.
- `pdf_to_images()` accepts an `output_dir` argument but currently writes images to `config.TEMP_DIR`.
- `pdf_utils.cleanup_temp()` contains nested helper definitions for `create_temp_directory()` and `pdf_name()`, so those helpers are not available as module-level functions.
- `config.MAX_NEW_TOKENS`, `config.TEMPERATURE`, `config.DO_SAMPLE`, `config.SAVE_MARKDOWN`, and `config.SAVE_JSON` are defined but not currently used as runtime switches in the main OCR call.
- `logger.py` defines `config.LOG_FILE`, but the active logger creates timestamped files named `OCR_<timestamp>.log`.
- `Test_files/test_model.py` prints `False` after `engine.load_model()` because the engine is loaded but not marked initialized.
- `Test_files/test_infer.py` requires CUDA directly via `.cuda()`.

## License

This project is licensed under the MIT License. See `LICENSE` for details.

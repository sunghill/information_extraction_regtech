# Regulatory Requirements Extraction through LLMs (GenAI)

This repository contains a sequence of Python scripts designed to process regulatory PDF documents (e.g., FMVSS 127, UN R152), convert them into structured text, chunk the content, and use a Large Language Model (LLM) to extract normative requirements into JSON and CSV formats.

## Pipeline Overview

The workflow consists of three distinct phases:

1. **PDF to Markdown Conversion:** Uses `docling` to run OCR and extract text from scanned PDFs into clean Markdown files.
2. **Document Chunking:** Uses `langchain` to intelligently split the Markdown files based on headers and character limits, exporting the chunks to pickle (`.pkl`) artifacts.
3. **Requirement Extraction:** Iterates through the chunked data and uses the OpenAI API (`gpt-4o`) to identify and extract normative regulatory requirements, saving the output as JSON and CSV files.

## Prerequisites

Ensure you have Python 3.8+ installed. Install the required dependencies:

```bash
pip install docling langchain langchain-text-splitters openai pandas python-dotenv

```

You must also create a `.env.txt` file in the root directory containing your OpenAI API key:

```text
OPENAI_API_KEY=your_openai_api_key_here

```

## Usage

### Phase 1: Convert PDFs to Markdown

The first set of scripts converts specific PDF files into Markdown. Make sure your source PDFs are located in the `data/` directory.

Run the conversion scripts:

```bash
python pdf_to_md_fmvss.py
python pdf_to_md_unr152.py

```

*Outputs: `data/FMVSS_127.md` and `data/UNR152r2e.md*`

### Phase 2: Ingestion and Chunking

This script scans the `data/` directory for `.md` files, splits them by Markdown headers (`#`, `##`, `###`), and applies a recursive character splitter for large sections.

Run the chunking script:

```bash
python chunking_script.py --source-dir data --output-dir data --chunk-size 1000 --chunk-overlap 200

```

*Outputs: `data/FMVSS_127_chunks.pkl` and `data/UNR152r2e_chunks.pkl*`

### Phase 3: Requirement Extraction

The final scripts read the `.pkl` chunk artifacts and send them to the OpenAI API to extract structured requirements (Actor, Action, Object, Conditions, etc.).

Run the extraction scripts:

```bash
python extract_requirements_fmvss.py
python extract_requirements_unr152.py

```

*Outputs: `data/FMVSS_127_chunks_requirements.json` (and `.csv`), `data/UNR152r2e_chunks_requirements.json` (and `.csv`)*

## Data Structure

The final JSON/CSV outputs contain the following fields for each extracted requirement:

* `id`: Sequential identifier (e.g., 1.1, 1.2)
* `clause_ref`: The regulation clause number
* `requirement_type`: Classification (functional, performance, test, interface, diagnostic, environmental, other)
* `text`: Original verbatim text
* `actor`: Responsible entity
* `action`: Required behavior
* `object`: Target of the action
* `conditions`: Preconditions, triggers, exceptions, or constraints
* `source_clause`: Source location reference

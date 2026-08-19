#this script is to convert R152r2e.pdf to markdown

import time
from docling.document_converter import DocumentConverter

# Path to your scanned PDF file
pdf_path = "data/R152r2e.pdf"

print("Initializing Docling Document Converter...")
converter = DocumentConverter()

print(f"Starting local parsing for: {pdf_path} (This may take a few moments for 253 pages)...")
start_time = time.time()

# Convert the document locally (triggers OCR automatically if text layer is missing)
result = converter.convert(pdf_path)

end_time = time.time()
print(f"Parsing completed in {end_time - start_time:.2f} seconds.")

# Export the parsed output into clean Markdown
markdown_content = result.document.export_to_markdown()

# Save the parsed text locally
output_md_path = "data/UNR152r2e.md"
with open(output_md_path, "w", encoding="utf-8") as f:
    f.write(markdown_content)

print(f"Successfully saved full text to local file: {output_md_path}")
"""
Regulation Ingestion and Chunking Script
  - Processes .md files using header-aware Markdown splitting.
  - Saves individual document chunks to distinct pickle files.
"""

import pathlib
import pickle
import argparse
from typing import List, Tuple
from logger_config import get_logger

# Initialize logger
logger = get_logger(__name__)

try:
    from langchain_text_splitters import (
        MarkdownHeaderTextSplitter,
        RecursiveCharacterTextSplitter
    )
    from langchain_core.documents import Document
except ImportError as exc:
    raise ImportError(
        "Required langchain packages missing. Install with: "
        "pip install langchain langchain-text-splitters"
    ) from exc


def process_markdown_file(
    file_path: pathlib.Path, 
    chunk_size: int = 1000, 
    chunk_overlap: int = 200
) -> List[Document]:
    """Process a Markdown file using header-aware splitting."""
    logger.info(f"  Parsing Markdown structure for: {file_path.name}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        markdown_text = f.read()

    # Define markdown header levels to trace
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]

    # Split strictly by markdown headings
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    header_splits = markdown_splitter.split_text(markdown_text)

    # Sub-chunk large sections if they exceed chunk_size limits
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = text_splitter.split_documents(header_splits)
    return chunks


def process_directory(
    source_dir: str, 
    output_dir: str, 
    chunk_size: int = 1000, 
    chunk_overlap: int = 200
) -> List[Tuple[str, str, int]]:
    """Scans source directory for .md files and processes them."""
    folder = pathlib.Path(source_dir)
    out_folder = pathlib.Path(output_dir)
    
    if not folder.exists():
        raise FileNotFoundError(f"Source folder not found: {source_dir}")
    
    out_folder.mkdir(parents=True, exist_ok=True)
    
    # Locate target files (recursive, handles both .md and .MD)
    files = sorted([
        f for f in folder.rglob("*") 
        if f.is_file() and f.suffix.lower() == ".md"
    ])
    
    if not files:
        raise ValueError(f"No valid .md files found in: {source_dir}")
    
    manifest = []
    
    for file_path in files:
        logger.info("-" * 80)
        logger.info(f"Processing File: {file_path.name}")
        
        try:
            chunks = process_markdown_file(file_path, chunk_size, chunk_overlap)

            # Global metadata injection
            for chunk in chunks:
                chunk.metadata["source_file"] = file_path.name
                if "regulation" not in chunk.metadata:
                    chunk.metadata["regulation"] = file_path.stem

            # Save to individual pickle files
            output_file_path = out_folder / f"{file_path.stem}_chunks.pkl"
            with open(output_file_path, "wb") as f:
                pickle.dump(chunks, f)
                
            logger.info(f"  Created {len(chunks)} chunks -> Saved to {output_file_path.name}")
            manifest.append((file_path.name, str(output_file_path), len(chunks)))
            
        except Exception as e:
            logger.error(f"  Failed to process {file_path.name}: {e}")
            continue
        
    return manifest


def main():
    parser = argparse.ArgumentParser(description="Structure-Aware Markdown Ingestion Script")
    parser.add_argument("--source-dir", type=str, default="data", help="Folder containing Markdown files")
    parser.add_argument("--output-dir", type=str, default="data", help="Directory for output pickle artifacts")
    parser.add_argument("--chunk-size", type=int, default=1000, help="Target chunk size in characters")
    parser.add_argument("--chunk-overlap", type=int, default=200, help="Character overlap between chunks")
    
    args = parser.parse_args()
    
    logger.info("=" * 80)
    logger.info("STRUCTURE-AWARE MARKDOWN INGESTION & CHUNKING")
    logger.info("=" * 80)
    
    try:
        manifest = process_directory(
            source_dir=args.source_dir,
            output_dir=args.output_dir,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap
        )
        
        logger.info("\n" + "=" * 80)
        logger.info("EXECUTION SUMMARY")
        logger.info("=" * 80)
        for name, path, count in manifest:
            logger.info(f"File: {name:<25} Chunks: {count:<6} Output: {path}")
            
    except Exception as e:
        logger.error(f"Critical execution error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
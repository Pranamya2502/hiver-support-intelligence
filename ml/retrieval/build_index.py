"""
Build FAISS vector retrieval index for AmazonHelp customer support conversations.

Encodes customer_text from data/processed/amazonhelp_conversations.csv using
SentenceTransformers (all-MiniLM-L6-v2) and stores L2-normalized embeddings in a
FAISS IndexFlatIP index for exact cosine similarity search.
"""

import os
from pathlib import Path
import sys
import time
import faiss
import numpy as np
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer

# Optimize PyTorch CPU threading
num_cpus = os.cpu_count() or 4
torch.set_num_threads(num_cpus)

# Repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent

INPUT_PATH = REPO_ROOT / "data" / "processed" / "amazonhelp_conversations.csv"
OUTPUT_DIR = REPO_ROOT / "data" / "processed" / "retrieval"
INDEX_PATH = OUTPUT_DIR / "amazonhelp.index"
METADATA_PATH = OUTPUT_DIR / "metadata.csv"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
BATCH_SIZE = 256
MAX_SEQ_LENGTH = 128


def build_retrieval_index():
    print("==================================================")
    print("Building Retrieval Index for AmazonHelp")
    print("==================================================")
    print(f"Loading dataset from: {INPUT_PATH}")

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Processed dataset not found at {INPUT_PATH}. "
            "Please run ml/preprocessing/prepare.py first."
        )

    df = pd.read_csv(INPUT_PATH)
    total_rows = len(df)
    print(f"Loaded {total_rows:,} conversation pairs.")

    print(f"\nLoading embedding model: {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)
    model.max_seq_length = MAX_SEQ_LENGTH
    dimension = model.get_embedding_dimension()

    print(f"Embedding dimension: {dimension}")
    print(f"Max sequence length: {MAX_SEQ_LENGTH}")
    print(f"Using PyTorch CPU threads: {num_cpus}")

    customer_texts = df["customer_text"].fillna("").astype(str).tolist()

    print(f"\nEncoding {total_rows:,} customer messages (batch_size={BATCH_SIZE})...")
    start_time = time.time()

    with torch.inference_mode():
        embeddings = model.encode(
            customer_texts,
            batch_size=BATCH_SIZE,
            show_progress_bar=True,
            normalize_embeddings=True,
            convert_to_numpy=True,
        ).astype(np.float32)

    encode_duration = time.time() - start_time
    print(f"\nEncoding completed in {encode_duration:.2f} seconds ({total_rows / encode_duration:.1f} msgs/sec).")

    # Ensure L2 normalization for Inner Product cosine similarity
    faiss.normalize_L2(embeddings)

    print("\nBuilding FAISS IndexFlatIP...")
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    assert index.ntotal == total_rows, f"Mismatch: index ntotal={index.ntotal} != dataset rows={total_rows}"
    print(f"FAISS index built successfully with {index.ntotal:,} vectors.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\nSaving FAISS index to: {INDEX_PATH}")
    faiss.write_index(index, str(INDEX_PATH))

    # Save metadata mapping with row_id column
    df_meta = df.copy()
    if "row_id" not in df_meta.columns:
        df_meta.insert(0, "row_id", df_meta.index)

    print(f"Saving metadata mapping to: {METADATA_PATH}")
    df_meta.to_csv(METADATA_PATH, index=False)

    index_file_size_mb = INDEX_PATH.stat().st_size / (1024 * 1024)
    metadata_file_size_mb = METADATA_PATH.stat().st_size / (1024 * 1024)

    print("\n==================================================")
    print("Retrieval Index Summary")
    print("==================================================")
    print(f"Indexed Conversations: {index.ntotal:,}")
    print(f"Embedding Model      : {MODEL_NAME}")
    print(f"Embedding Dimension  : {dimension}")
    print(f"FAISS Index Type     : IndexFlatIP")
    print(f"Index File Size      : {index_file_size_mb:.2f} MB")
    print(f"Metadata File Size   : {metadata_file_size_mb:.2f} MB")
    print("==================================================")


if __name__ == "__main__":
    build_retrieval_index()

"""
Historical conversation retriever for AmazonHelp support intelligence.

Loads a FAISS IndexFlatIP index and metadata mapping to retrieve top-k semantically
similar past AmazonHelp customer support conversations for any given query.
"""

from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Union
import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

# Repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent

DEFAULT_INDEX_PATH = REPO_ROOT / "data" / "processed" / "retrieval" / "amazonhelp.index"
DEFAULT_METADATA_PATH = REPO_ROOT / "data" / "processed" / "retrieval" / "metadata.csv"
DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class HistoricalRetriever:
    """Retriever class for FAISS vector similarity search over AmazonHelp conversations."""

    def __init__(
        self,
        index_path: Optional[Union[str, Path]] = None,
        metadata_path: Optional[Union[str, Path]] = None,
        model_name: str = DEFAULT_MODEL_NAME,
    ):
        self.index_path = Path(index_path or DEFAULT_INDEX_PATH)
        self.metadata_path = Path(metadata_path or DEFAULT_METADATA_PATH)
        self.model_name = model_name

        if not self.index_path.exists():
            raise FileNotFoundError(
                f"FAISS index not found at {self.index_path}. "
                "Please run ml/retrieval/build_index.py first."
            )

        if not self.metadata_path.exists():
            raise FileNotFoundError(
                f"Metadata file not found at {self.metadata_path}. "
                "Please run ml/retrieval/build_index.py first."
            )

        print(f"Loading embedding model: {self.model_name}...")
        self.model = SentenceTransformer(self.model_name)

        print(f"Loading FAISS index from: {self.index_path}...")
        self.index = faiss.read_index(str(self.index_path))

        print(f"Loading metadata mapping from: {self.metadata_path}...")
        self.metadata = pd.read_csv(self.metadata_path)

        if self.index.ntotal != len(self.metadata):
            raise ValueError(
                f"Index vector count ({self.index.ntotal}) does not match "
                f"metadata row count ({len(self.metadata)})."
            )

        print(f"HistoricalRetriever initialized with {self.index.ntotal:,} indexed conversations.")

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Search for top-k semantically similar historical conversations.

        Args:
            query: Incoming customer query text.
            top_k: Number of top matches to retrieve.

        Returns:
            List of result dictionaries containing rank, similarity score,
            customer_text, agent_response, and tweet metadata.
        """
        cleaned_query = (query or "").strip()
        if not cleaned_query:
            return []

        # Bound top_k within valid range
        k = max(1, min(top_k, self.index.ntotal))

        # Encode and L2-normalize query vector
        query_vector = self.model.encode(
            [cleaned_query],
            normalize_embeddings=True,
            convert_to_numpy=True,
        ).astype(np.float32)

        faiss.normalize_L2(query_vector)

        # Search FAISS index
        scores, indices = self.index.search(query_vector, k)

        results = []
        for rank, (idx, score) in enumerate(zip(indices[0], scores[0]), start=1):
            if idx < 0 or idx >= len(self.metadata):
                continue

            row = self.metadata.iloc[idx]
            result_item = {
                "rank": rank,
                "score": float(score),
                "row_id": int(row.get("row_id", idx)),
                "tweet_id_customer": str(row.get("tweet_id_customer", "")),
                "tweet_id_reply": str(row.get("tweet_id_reply", "")),
                "customer_text": str(row.get("customer_text", "")),
                "agent_response": str(row.get("agent_response", "")),
                "created_at_customer": str(row.get("created_at_customer", "")),
                "created_at_reply": str(row.get("created_at_reply", "")),
            }
            results.append(result_item)

        return results


def run_sanity_check():
    """Run retrieval sanity check demonstration on sample customer queries."""
    print("\n==================================================")
    print("Historical Retriever Sanity Check")
    print("==================================================")

    retriever = HistoricalRetriever()

    test_queries = [
        "My package has not arrived yet and tracking hasn't updated for 3 days",
        "I was charged twice for my order and need a refund for the duplicate charge",
        "My Fire TV stick screen is completely blank and won't turn on",
        "How do I cancel my Prime subscription renewal fee?",
        "My Amazon account has been locked and I cannot log in",
    ]

    for i, query in enumerate(test_queries, start=1):
        print(f"\n--------------------------------------------------")
        print(f"QUERY [{i}]: {query}")
        print(f"--------------------------------------------------")

        results = retriever.search(query, top_k=3)

        for res in results:
            print(f"\nRESULT {res['rank']} (Similarity Score: {res['score']:.4f})")
            print(f"Customer Tweet ID: {res['tweet_id_customer']}")
            print(f"Customer Text    : {res['customer_text']}")
            print(f"AmazonHelp Reply : {res['agent_response']}")


if __name__ == "__main__":
    run_sanity_check()

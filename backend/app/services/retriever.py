from typing import Any

from ml.retrieval.retriever import HistoricalRetriever


class RetrievalService:
    def __init__(self):
        self.retriever = HistoricalRetriever()

    def search(self, customer_message: str, top_k: int = 5) -> list[dict[str, Any]]:
        return self.retriever.search(customer_message, top_k=top_k)
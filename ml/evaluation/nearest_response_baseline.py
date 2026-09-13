"""
Nearest historical-response baseline.

For each golden-set customer message:
1. Retrieve the most similar historical customer message.
2. Use that historical agent response directly as the baseline reply.
3. Record similarity and source example.
"""

from pathlib import Path
import sys
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ml.retrieval.retriever import HistoricalRetriever


GOLDEN_PATH = (
    REPO_ROOT
    / "data"
    / "golden"
    / "golden_set.csv"
)

OUTPUT_PATH = (
    REPO_ROOT
    / "reports"
    / "nearest_response_results.csv"
)


def run_baseline():
    golden = pd.read_csv(GOLDEN_PATH)

    retriever = HistoricalRetriever()

    results = []

    for index, row in golden.iterrows():

        customer_message = str(
            row["customer_text"]
        )

        matches = retriever.search(
            customer_message,
            top_k=1,
        )

        if matches:

            match = matches[0]

            results.append({
                "row_id": index,
                "customer_text": customer_message,
                "gold_intent": row[
                    "gold_intent"
                ],
                "historical_response": match[
                    "agent_response"
                ],
                "similarity_score": match[
                    "score"
                ],
                "source_customer_text": match[
                    "customer_text"
                ],
                "source_tweet_id": match[
                    "tweet_id_customer"
                ],
            })

        else:

            results.append({
                "row_id": index,
                "customer_text": customer_message,
                "gold_intent": row[
                    "gold_intent"
                ],
                "historical_response": "",
                "similarity_score": 0.0,
                "source_customer_text": "",
                "source_tweet_id": "",
            })

        if (index + 1) % 25 == 0:
            print(
                f"Processed "
                f"{index + 1}/"
                f"{len(golden)}"
            )

    results_df = pd.DataFrame(results)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    results_df.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print("\nNearest-response baseline complete.")

    print(
        f"Saved to: {OUTPUT_PATH}"
    )

    print(
        f"Examples: {len(results_df)}"
    )

    print(
        "Average similarity: "
        f"{results_df['similarity_score'].mean():.4f}"
    )


if __name__ == "__main__":
    run_baseline()
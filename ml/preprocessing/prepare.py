from pathlib import Path
import zipfile
import pandas as pd
import re


ZIP_PATH = Path("data/raw/archive.zip")
OUTPUT_PATH = Path("data/processed/amazonhelp_conversations.csv")

CHUNK_SIZE = 200_000
BRAND = "AmazonHelp"


def clean_text(text: str) -> str:
    """Basic text cleaning while preserving the original meaning."""
    if pd.isna(text):
        return ""

    text = str(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def collect_amazon_replies():
    """Collect AmazonHelp replies and their parent tweet IDs."""
    replies = []

    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        with z.open("twcs/twcs.csv") as f:
            for chunk in pd.read_csv(f, chunksize=CHUNK_SIZE):
                mask = (
                    (chunk["author_id"] == BRAND)
                    & (chunk["inbound"] == False)
                    & (chunk["in_response_to_tweet_id"].notna())
                )

                selected = chunk.loc[
                    mask,
                    [
                        "tweet_id",
                        "created_at",
                        "text",
                        "in_response_to_tweet_id",
                    ],
                ].copy()

                replies.append(selected)

    return pd.concat(replies, ignore_index=True)


def collect_customer_messages(parent_ids):
    """Find customer tweets referenced by AmazonHelp replies."""
    customers = []

    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        with z.open("twcs/twcs.csv") as f:
            for chunk in pd.read_csv(f, chunksize=CHUNK_SIZE):
                mask = (
                    chunk["tweet_id"].isin(parent_ids)
                    & (chunk["inbound"] == True)
                )

                selected = chunk.loc[
                    mask,
                    [
                        "tweet_id",
                        "author_id",
                        "created_at",
                        "text",
                    ],
                ].copy()

                customers.append(selected)

    return pd.concat(customers, ignore_index=True)


def build_dataset():
    print("Collecting AmazonHelp replies...")
    replies = collect_amazon_replies()

    print(f"AmazonHelp replies found: {len(replies):,}")

    parent_ids = set(
        replies["in_response_to_tweet_id"]
        .astype("int64")
        .tolist()
    )

    print("Finding corresponding customer messages...")
    customers = collect_customer_messages(parent_ids)

    print(f"Customer messages found: {len(customers):,}")

    dataset = replies.merge(
        customers,
        left_on="in_response_to_tweet_id",
        right_on="tweet_id",
        suffixes=("_reply", "_customer"),
    )

    dataset["customer_text"] = dataset["text_customer"].apply(clean_text)
    dataset["agent_response"] = dataset["text_reply"].apply(clean_text)

    # Add text-length metadata for quality analysis and evaluation.
    dataset["customer_char_count"] = dataset["customer_text"].str.len()
    dataset["response_char_count"] = dataset["agent_response"].str.len()

    dataset = dataset[
        [
            "tweet_id_customer",
            "tweet_id_reply",
            "author_id",
            "created_at_customer",
            "created_at_reply",
            "customer_text",
            "agent_response",
            "customer_char_count",
            "response_char_count",
        ]
    ]

    dataset = dataset.dropna(
        subset=["customer_text", "agent_response"]
    )

    dataset = dataset[
        (dataset["customer_text"].str.len() > 0)
        & (dataset["agent_response"].str.len() > 0)
    ]

    dataset = dataset.drop_duplicates(
        subset=["tweet_id_customer", "tweet_id_reply"]
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataset.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print("\nProcessing complete.")
    print(f"Final conversation pairs: {len(dataset):,}")
    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    build_dataset()
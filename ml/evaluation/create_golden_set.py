from pathlib import Path
import pandas as pd


INPUT_PATH = Path("data/processed/amazonhelp_conversations.csv")
OUTPUT_PATH = Path("data/golden/golden_set.csv")

SAMPLE_SIZE = 200
RANDOM_STATE = 42


def create_golden_set():
    df = pd.read_csv(INPUT_PATH)

    golden = df.sample(
        n=SAMPLE_SIZE,
        random_state=RANDOM_STATE,
    ).copy()

    golden = golden[
        [
            "tweet_id_customer",
            "tweet_id_reply",
            "customer_text",
            "agent_response",
        ]
    ]

    # Human-labelled fields.
    golden["gold_intent"] = ""
    golden["gold_escalate"] = ""
    golden["label_notes"] = ""

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    golden.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(f"Golden set created: {len(golden)} examples")
    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    create_golden_set()
from pathlib import Path
import pandas as pd


GOLDEN_PATH = Path("data/golden/golden_set.csv")

INTENTS = [
    "order_issue",
    "delivery_issue",
    "return_refund",
    "payment_billing",
    "account_access",
    "prime_subscription",
    "product_issue",
    "digital_content",
    "general_support",
]


def label_golden_set():
    # Read label columns as strings so blank values do not become float64.
    df = pd.read_csv(
        GOLDEN_PATH,
        dtype={
            "gold_intent": "string",
            "gold_escalate": "string",
            "label_notes": "string",
        },
    )

    # Replace empty/NaN labels with empty strings.
    df["gold_intent"] = df["gold_intent"].fillna("")
    df["gold_escalate"] = df["gold_escalate"].fillna("")
    df["label_notes"] = df["label_notes"].fillna("")

    print("\nGolden Set Labeling")
    print("===================")
    print("Enter the intent number and escalation decision for each example.")
    print("Type 'q' to save progress and exit.\n")

    for index, row in df.iterrows():

        # Skip examples that have already been labelled.
        if str(row["gold_intent"]).strip():
            continue

        print("\n" + "=" * 70)
        print(f"Example {index + 1} / {len(df)}")
        print("=" * 70)

        print("\nCUSTOMER:")
        print(row["customer_text"])

        print("\nHISTORICAL AMAZONHELP RESPONSE:")
        print(row["agent_response"])

        print("\nINTENTS:")
        for number, intent in enumerate(INTENTS, start=1):
            print(f"{number}. {intent}")

        # Ask for intent.
        while True:
            choice = input("\nIntent number (1-9) or q: ").strip()

            if choice.lower() == "q":
                df.to_csv(GOLDEN_PATH, index=False)
                print("\nProgress saved.")
                return

            if choice.isdigit() and 1 <= int(choice) <= len(INTENTS):
                intent = INTENTS[int(choice) - 1]
                break

            print("Please enter a number from 1-9.")

        # Ask for escalation decision.
        while True:
            escalate = input(
                "Escalate to human? (y/n): "
            ).strip().lower()

            if escalate in {"y", "n"}:
                break

            print("Please enter y or n.")

        # Ask for a short human reasoning note.
        notes = input("Short reason: ").strip()

        # Save labels.
        df.at[index, "gold_intent"] = intent
        df.at[index, "gold_escalate"] = escalate
        df.at[index, "label_notes"] = notes

        # Save after every example so progress is never lost.
        df.to_csv(GOLDEN_PATH, index=False)

        print("Saved.")


if __name__ == "__main__":
    label_golden_set()
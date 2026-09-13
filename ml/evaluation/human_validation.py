"""
Human validation and failure analysis.

Creates:
1. A 20-example human validation sample for judge verification.
2. A failure-analysis CSV containing the top 5 weakest AI examples.
3. A summary JSON for the evaluation report.

Human agreement is calculated only after the reviewer fills
the human_* columns in the validation CSV.
"""

from pathlib import Path
import json
import sys

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parent.parent.parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


JUDGE_PATH = (
    REPO_ROOT
    / "reports"
    / "llm_judge_results.csv"
)

EVALUATION_PATH = (
    REPO_ROOT
    / "reports"
    / "evaluation_results.csv"
)

VALIDATION_PATH = (
    REPO_ROOT
    / "reports"
    / "human_validation.csv"
)

FAILURE_PATH = (
    REPO_ROOT
    / "reports"
    / "top_5_failures.csv"
)

SUMMARY_PATH = (
    REPO_ROOT
    / "reports"
    / "human_validation_summary.json"
)

SAMPLE_SIZE = 20
RANDOM_STATE = 42


def create_validation_sample():
    """Create a 20-example human validation set."""

    if not JUDGE_PATH.exists():
        raise FileNotFoundError(
            f"Missing judge results: {JUDGE_PATH}"
        )

    judge_df = pd.read_csv(
        JUDGE_PATH
    )

    valid = judge_df[
        judge_df["overall"]
        .notna()
    ].copy()

    if len(valid) == 0:
        print(
            "No successful LLM judge results yet."
        )
        print(
            "Human validation will be created "
            "after the judge runs successfully."
        )
        return None

    sample_size = min(
        SAMPLE_SIZE,
        len(valid),
    )

    sample = valid.sample(
        n=sample_size,
        random_state=RANDOM_STATE,
    ).copy()

    sample = sample[
        [
            "row_id",
            "customer_text",
            "ai_response",
            "historical_response",
            "relevance",
            "groundedness",
            "helpfulness",
            "overall",
            "reason",
        ]
    ]

    # Blank fields for the human reviewer.
    sample["human_relevance"] = ""
    sample["human_groundedness"] = ""
    sample["human_helpfulness"] = ""
    sample["human_overall"] = ""

    sample.to_csv(
        VALIDATION_PATH,
        index=False,
    )

    print(
        f"\nCreated human validation file:"
        f"\n{VALIDATION_PATH}"
    )

    print(
        f"Examples to review: {sample_size}"
    )

    return sample


def calculate_human_agreement():
    """Calculate judge-human agreement if labels exist."""

    if not VALIDATION_PATH.exists():
        return None

    df = pd.read_csv(
        VALIDATION_PATH
    )

    human_columns = [
        "human_relevance",
        "human_groundedness",
        "human_helpfulness",
        "human_overall",
    ]

    # Check whether human labels have been entered.
    for column in human_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    complete = df[
        df[human_columns]
        .notna()
        .all(axis=1)
    ].copy()

    if len(complete) == 0:

        print(
            "\nNo completed human labels yet."
        )

        return None

    metrics = {}

    judge_to_human_columns = {
        "relevance": "human_relevance",
        "groundedness": "human_groundedness",
        "helpfulness": "human_helpfulness",
        "overall": "human_overall",
    }

    for judge_column, human_column in (
        judge_to_human_columns.items()
    ):

        exact_agreement = (
            complete[judge_column]
            == complete[human_column]
        ).mean()

        within_one = (
            (
                complete[judge_column]
                - complete[human_column]
            ).abs()
            <= 1
        ).mean()

        metrics[judge_column] = {
            "exact_agreement": round(
                float(exact_agreement),
                4,
            ),
            "within_one_point": round(
                float(within_one),
                4,
            ),
        }

    summary = {
        "validated_examples": len(
            complete
        ),
        "agreement": metrics,
    }

    SUMMARY_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        SUMMARY_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            summary,
            file,
            indent=2,
        )

    print(
        "\nHuman agreement calculated."
    )

    print(
        f"Validated examples: "
        f"{len(complete)}"
    )

    for metric, values in metrics.items():

        print(
            f"{metric}: "
            f"exact={values['exact_agreement']:.2%}, "
            f"within-1={values['within_one_point']:.2%}"
        )

    return summary


def create_failure_analysis():
    """Create top 5 weakest successful AI examples."""

    if not EVALUATION_PATH.exists():
        print(
            "\nEvaluation results not found."
        )
        return

    evaluation = pd.read_csv(
        EVALUATION_PATH
    )

    # Only successful AI predictions.
    successful = evaluation[
        evaluation[
            "predicted_intent"
        ]
        .fillna("")
        .astype(str)
        .str.strip()
        != ""
    ].copy()

    if len(successful) == 0:
        print(
            "\nNo successful AI evaluations available."
        )
        return

    # --------------------------------------------------------
    # Build a simple error severity score.
    # --------------------------------------------------------

    successful["intent_error"] = (
        successful["gold_intent"]
        != successful["predicted_intent"]
    ).astype(int)

    successful["escalation_error"] = (
        successful["gold_escalate"]
        != successful["predicted_escalate"]
    ).astype(int)

    successful["confidence"] = pd.to_numeric(
        successful["confidence"],
        errors="coerce",
    ).fillna(0)

    # Lower evidence + errors = weaker cases.
    successful["failure_score"] = (
        successful["intent_error"] * 3
        + successful["escalation_error"] * 2
        + (1 - successful["confidence"])
    )

    failures = (
        successful
        .sort_values(
            "failure_score",
            ascending=False,
        )
        .head(5)
        .copy()
    )

    columns = [
        "row_id",
        "customer_text",
        "gold_intent",
        "predicted_intent",
        "gold_escalate",
        "predicted_escalate",
        "confidence",
        "draft_reply",
        "best_evidence_score",
        "intent_error",
        "escalation_error",
    ]

    available_columns = [
        column
        for column in columns
        if column in failures.columns
    ]

    failures[
        available_columns
    ].to_csv(
        FAILURE_PATH,
        index=False,
    )

    print(
        f"\nTop 5 failure examples saved to:"
        f"\n{FAILURE_PATH}"
    )

    print("\nTop 5 failures:")

    for _, row in failures.iterrows():

        print(
            "\n----------------------------------------"
        )

        print(
            f"Row: {int(row['row_id'])}"
        )

        print(
            f"Customer: "
            f"{str(row['customer_text'])[:300]}"
        )

        print(
            f"Gold intent: "
            f"{row['gold_intent']}"
        )

        print(
            f"Predicted intent: "
            f"{row['predicted_intent']}"
        )

        print(
            f"Gold escalation: "
            f"{row['gold_escalate']}"
        )

        print(
            f"Predicted escalation: "
            f"{row['predicted_escalate']}"
        )

        print(
            f"Confidence: "
            f"{float(row['confidence']):.2f}"
        )


def main():

    print("=" * 60)
    print("HIVER - HUMAN VALIDATION & FAILURE ANALYSIS")
    print("=" * 60)

    # Create human-review file.
    create_validation_sample()

    # Calculate agreement if labels already exist.
    calculate_human_agreement()

    # Create top failure examples.
    create_failure_analysis()

    print(
        "\nStep 8C preparation complete."
    )


if __name__ == "__main__":
    main()
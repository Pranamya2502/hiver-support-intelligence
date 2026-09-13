"""
Evaluation harness for Hiver Support Intelligence.

Evaluates:
1. AI agent intent classification
2. AI agent escalation decision
3. TF-IDF + Logistic Regression intent baseline
4. Majority-class intent baseline

The AI evaluation is resumable:
- Successful previous agent results are preserved.
- Failed/API-rate-limited examples are retried later.
- API failures are NOT counted as model mistakes.

Outputs:
- reports/evaluation_results.csv
- reports/evaluation_summary.json
"""

from pathlib import Path
import json
import sys

import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score


REPO_ROOT = Path(__file__).resolve().parent.parent.parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


from backend.app.services.agent import SupportAgent


GOLDEN_PATH = (
    REPO_ROOT
    / "data"
    / "golden"
    / "golden_set.csv"
)

PROCESSED_PATH = (
    REPO_ROOT
    / "data"
    / "processed"
    / "amazonhelp_conversations.csv"
)

OUTPUT_CSV = (
    REPO_ROOT
    / "reports"
    / "evaluation_results.csv"
)

OUTPUT_JSON = (
    REPO_ROOT
    / "reports"
    / "evaluation_summary.json"
)

RANDOM_STATE = 42


# ============================================================
# DATA LOADING
# ============================================================

def load_golden_set():
    """Load and validate the 200-example golden set."""

    if not GOLDEN_PATH.exists():
        raise FileNotFoundError(
            f"Golden set not found: {GOLDEN_PATH}"
        )

    df = pd.read_csv(GOLDEN_PATH)

    required_columns = [
        "customer_text",
        "gold_intent",
        "gold_escalate",
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    if len(df) != 200:
        raise ValueError(
            f"Expected 200 golden examples, found {len(df)}"
        )

    # Normalize human escalation labels.
    df["gold_escalate"] = (
        df["gold_escalate"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    return df


# ============================================================
# MAJORITY BASELINE
# ============================================================

def majority_baseline(golden_df):
    """
    Always predict the most frequent intent.

    This is intentionally simple and establishes
    a lower-bound baseline.
    """

    majority_intent = (
        golden_df["gold_intent"]
        .value_counts()
        .idxmax()
    )

    predictions = [
        majority_intent
        for _ in range(len(golden_df))
    ]

    return predictions, majority_intent


def calculate_majority_metrics(
    golden_df,
    predictions,
):
    """Calculate majority baseline metrics."""

    accuracy = accuracy_score(
        golden_df["gold_intent"],
        predictions,
    )

    macro_f1 = f1_score(
        golden_df["gold_intent"],
        predictions,
        average="macro",
        zero_division=0,
    )

    return {
        "intent_accuracy": round(
            float(accuracy),
            4,
        ),
        "intent_macro_f1": round(
            float(macro_f1),
            4,
        ),
    }


# ============================================================
# TF-IDF + LOGISTIC REGRESSION BASELINE
# ============================================================

def keyword_intent(text):
    """
    Lightweight deterministic intent labeling.

    Used only to create weak training labels for the
    classical baseline.
    """

    text = str(text).lower()

    rules = [
        (
            "delivery_issue",
            [
                "delivery",
                "delivered",
                "package",
                "parcel",
                "shipment",
                "tracking",
                "arrive",
                "arrived",
                "late",
                "missing",
            ],
        ),
        (
            "return_refund",
            [
                "refund",
                "return",
                "returned",
                "replacement",
                "money back",
            ],
        ),
        (
            "payment_billing",
            [
                "charged",
                "charge",
                "payment",
                "billing",
                "invoice",
                "card",
                "credit card",
                "debit card",
            ],
        ),
        (
            "account_access",
            [
                "login",
                "log in",
                "password",
                "account locked",
                "can't access",
                "cannot access",
            ],
        ),
        (
            "prime_subscription",
            [
                "prime membership",
                "prime subscription",
                "amazon prime",
                "prime benefits",
            ],
        ),
        (
            "digital_content",
            [
                "prime video",
                "kindle",
                "ebook",
                "e-book",
                "digital",
                "streaming",
            ],
        ),
        (
            "product_issue",
            [
                "device",
                "fire tv",
                "kindle device",
                "not working",
                "broken",
                "product",
            ],
        ),
        (
            "order_issue",
            [
                "order",
                "ordering",
                "cancel order",
                "change order",
            ],
        ),
    ]

    for intent, keywords in rules:
        if any(
            keyword in text
            for keyword in keywords
        ):
            return intent

    return "general_support"


def build_baseline_training_data(
    processed_df,
):
    """Create weak labels for the classical baseline."""

    texts = (
        processed_df["customer_text"]
        .fillna("")
        .astype(str)
    )

    labels = texts.apply(keyword_intent)

    return texts.tolist(), labels.tolist()


def train_classical_baseline(
    processed_df,
):
    """Train TF-IDF + Logistic Regression."""

    texts, labels = (
        build_baseline_training_data(
            processed_df
        )
    )

    vectorizer = TfidfVectorizer(
        lowercase=True,
        strip_accents="unicode",
        ngram_range=(1, 2),
        min_df=3,
        max_features=50000,
        sublinear_tf=True,
    )

    X = vectorizer.fit_transform(texts)

    classifier = LogisticRegression(
        max_iter=1000,
        random_state=RANDOM_STATE,
        class_weight="balanced",
    )

    classifier.fit(X, labels)

    return vectorizer, classifier


def evaluate_classical_baseline(
    golden_df,
    vectorizer,
    classifier,
):
    """Evaluate TF-IDF + Logistic Regression."""

    X = vectorizer.transform(
        golden_df["customer_text"]
        .fillna("")
        .astype(str)
    )

    predictions = classifier.predict(X)

    accuracy = accuracy_score(
        golden_df["gold_intent"],
        predictions,
    )

    macro_f1 = f1_score(
        golden_df["gold_intent"],
        predictions,
        average="macro",
        zero_division=0,
    )

    return (
        predictions.tolist(),
        accuracy,
        macro_f1,
    )


# ============================================================
# AI AGENT EVALUATION
# ============================================================

def empty_result(
    index,
    row,
    error="",
):
    """Create a standard result row."""

    return {
        "row_id": index,
        "customer_text": str(
            row["customer_text"]
        ),
        "gold_intent": row["gold_intent"],
        "gold_escalate": str(
            row["gold_escalate"]
        ).lower(),
        "predicted_intent": "",
        "confidence": 0.0,
        "decision": "",
        "predicted_escalate": "",
        "draft_reply": "",
        "best_evidence_score": 0.0,
        "error": error,
    }


def evaluate_agent_resumable(
    golden_df,
):
    """
    Run the AI agent while preserving successful previous runs.

    Successful previous rows are reused.
    Failed rows are retried.
    """

    previous_results = None

    if OUTPUT_CSV.exists():

        try:
            previous_results = pd.read_csv(
                OUTPUT_CSV
            )

            print(
                f"\nFound previous evaluation file:"
                f"\n{OUTPUT_CSV}"
            )

        except Exception:
            previous_results = None

    if previous_results is not None:

        successful_rows = previous_results[
            previous_results[
                "predicted_intent"
            ]
            .fillna("")
            .astype(str)
            .str.strip()
            != ""
        ]

        print(
            f"Existing successful agent runs: "
            f"{len(successful_rows)}"
        )

    else:

        successful_rows = pd.DataFrame()

        print(
            "No previous agent results found."
        )

    agent = SupportAgent()

    results = []

    for index, row in golden_df.iterrows():

        # ----------------------------------------------------
        # Reuse successful previous result
        # ----------------------------------------------------

        if not successful_rows.empty:

            previous_match = (
                successful_rows[
                    successful_rows["row_id"]
                    == index
                ]
            )

            if len(previous_match) > 0:

                previous = (
                    previous_match
                    .iloc[0]
                    .to_dict()
                )

                results.append(previous)

                print(
                    f"Skipping {index + 1}/"
                    f"{len(golden_df)} "
                    f"(already evaluated)"
                )

                continue

        # ----------------------------------------------------
        # New API call
        # ----------------------------------------------------

        customer_text = str(
            row["customer_text"]
        )

        print(
            f"Evaluating agent "
            f"{index + 1}/{len(golden_df)}..."
        )

        try:

            response = agent.handle(
                customer_text
            )

            predicted_intent = response.get(
                "intent",
                "",
            )

            confidence = float(
                response.get(
                    "confidence",
                    0.0,
                )
            )

            decision = response.get(
                "decision",
                "",
            )

            escalate = (
                decision == "escalate"
            )

            draft_reply = response.get(
                "draft_reply",
                "",
            )

            evidence = response.get(
                "historical_evidence",
                [],
            )

            best_evidence_score = 0.0

            if evidence:

                best_evidence_score = float(
                    evidence[0].get(
                        "score",
                        0.0,
                    )
                )

            result = {
                "row_id": index,
                "customer_text": customer_text,
                "gold_intent": row[
                    "gold_intent"
                ],
                "gold_escalate": str(
                    row["gold_escalate"]
                ).lower(),
                "predicted_intent": predicted_intent,
                "confidence": confidence,
                "decision": decision,
                "predicted_escalate": str(
                    escalate
                ).lower(),
                "draft_reply": draft_reply,
                "best_evidence_score": (
                    best_evidence_score
                ),
                "error": "",
            }

            results.append(result)

            # Save immediately after success.
            current_results = pd.DataFrame(
                results
            )

            current_results.to_csv(
                OUTPUT_CSV,
                index=False,
            )

        except Exception as exc:

            error_text = str(exc)

            print(
                f"ERROR on example "
                f"{index}: {error_text}"
            )

            result = empty_result(
                index,
                row,
                error_text,
            )

            results.append(result)

            # IMPORTANT:
            # API failures are preserved but not treated
            # as model predictions.
            continue

    return pd.DataFrame(results)


# ============================================================
# AI AGENT METRICS
# ============================================================

def calculate_agent_metrics(
    results_df,
):
    """
    Calculate metrics only over successful runs.

    Intent and escalation metrics use their own valid
    subsets so missing escalation values cannot crash
    sklearn.
    """

    # --------------------------------------------------------
    # Valid intent predictions
    # --------------------------------------------------------

    valid_intent = results_df[
        results_df[
            "predicted_intent"
        ]
        .fillna("")
        .astype(str)
        .str.strip()
        != ""
    ].copy()

    # --------------------------------------------------------
    # Intent metrics
    # --------------------------------------------------------

    if len(valid_intent) > 0:

        intent_accuracy = accuracy_score(
            valid_intent["gold_intent"],
            valid_intent["predicted_intent"],
        )

        intent_macro_f1 = f1_score(
            valid_intent["gold_intent"],
            valid_intent["predicted_intent"],
            average="macro",
            zero_division=0,
        )

    else:

        intent_accuracy = 0.0
        intent_macro_f1 = 0.0

    # --------------------------------------------------------
    # Valid escalation predictions
    # --------------------------------------------------------

    valid_escalation = results_df[
        results_df[
            "predicted_escalate"
        ]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
        .isin(["true", "false"])
    ].copy()

    # --------------------------------------------------------
    # Escalation metrics
    # --------------------------------------------------------

    if len(valid_escalation) > 0:

        gold_escalate = (
            valid_escalation[
                "gold_escalate"
            ]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.lower()
        )

        predicted_escalate = (
            valid_escalation[
                "predicted_escalate"
            ]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.lower()
        )

        escalation_accuracy = (
            accuracy_score(
                gold_escalate,
                predicted_escalate,
            )
        )

    else:

        escalation_accuracy = 0.0

    # --------------------------------------------------------
    # Coverage
    # --------------------------------------------------------

    total_examples = len(results_df)

    successful_runs = len(
        valid_intent
    )

    agent_errors = (
        total_examples
        - successful_runs
    )

    if total_examples > 0:

        coverage = (
            successful_runs
            / total_examples
        )

    else:

        coverage = 0.0

    return {
        "intent_accuracy": round(
            float(intent_accuracy),
            4,
        ),
        "intent_macro_f1": round(
            float(intent_macro_f1),
            4,
        ),
        "escalation_accuracy": round(
            float(escalation_accuracy),
            4,
        ),
        "valid_agent_runs": int(
            successful_runs
        ),
        "agent_errors": int(
            agent_errors
        ),
        "evaluation_coverage": round(
            float(coverage),
            4,
        ),
        "escalation_evaluation_count": int(
            len(valid_escalation)
        ),
    }


# ============================================================
# SAVE RESULTS
# ============================================================

def save_results(
    results_df,
):

    OUTPUT_CSV.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    results_df = (
        results_df
        .sort_values("row_id")
        .reset_index(drop=True)
    )

    results_df.to_csv(
        OUTPUT_CSV,
        index=False,
    )

    print(
        f"\nSaved detailed results to:"
        f"\n{OUTPUT_CSV}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)

    print(
        "HIVER SUPPORT INTELLIGENCE - EVALUATION"
    )

    print("=" * 60)

    # --------------------------------------------------------
    # Golden set
    # --------------------------------------------------------

    golden_df = load_golden_set()

    print(
        f"\nLoaded golden set: "
        f"{len(golden_df)} examples"
    )

    # --------------------------------------------------------
    # Majority baseline
    # --------------------------------------------------------

    print(
        "\nRunning majority-class baseline..."
    )

    (
        majority_predictions,
        majority_intent,
    ) = majority_baseline(
        golden_df
    )

    majority_metrics = (
        calculate_majority_metrics(
            golden_df,
            majority_predictions,
        )
    )

    # --------------------------------------------------------
    # TF-IDF baseline
    # --------------------------------------------------------

    print(
        "\nTraining TF-IDF + Logistic "
        "Regression baseline..."
    )

    if not PROCESSED_PATH.exists():

        raise FileNotFoundError(
            f"Processed dataset not found:"
            f"\n{PROCESSED_PATH}"
        )

    processed_df = pd.read_csv(
        PROCESSED_PATH
    )

    vectorizer, classifier = (
        train_classical_baseline(
            processed_df
        )
    )

    (
        tfidf_predictions,
        tfidf_accuracy,
        tfidf_macro_f1,
    ) = evaluate_classical_baseline(
        golden_df,
        vectorizer,
        classifier,
    )

    tfidf_metrics = {
        "intent_accuracy": round(
            float(tfidf_accuracy),
            4,
        ),
        "intent_macro_f1": round(
            float(tfidf_macro_f1),
            4,
        ),
    }

    # --------------------------------------------------------
    # AI Agent
    # --------------------------------------------------------

    print(
        "\nRunning AI support agent evaluation..."
    )

    agent_results = (
        evaluate_agent_resumable(
            golden_df
        )
    )

    # --------------------------------------------------------
    # Add baseline predictions
    # --------------------------------------------------------

    agent_results[
        "majority_prediction"
    ] = majority_predictions

    agent_results[
        "tfidf_prediction"
    ] = tfidf_predictions

    agent_results[
        "agent_intent_correct"
    ] = (
        agent_results["gold_intent"]
        == agent_results["predicted_intent"]
    )

    agent_results[
        "agent_escalation_correct"
    ] = (
        agent_results["gold_escalate"]
        == agent_results[
            "predicted_escalate"
        ]
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    save_results(
        agent_results
    )

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    agent_metrics = (
        calculate_agent_metrics(
            agent_results
        )
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    summary = {

        "dataset": {
            "brand": "AmazonHelp",
            "golden_examples": len(
                golden_df
            ),
        },

        "agent": agent_metrics,

        "baseline_majority": {
            "majority_intent": (
                majority_intent
            ),
            **majority_metrics,
        },

        "baseline_tfidf_logistic_regression": (
            tfidf_metrics
        ),
    }

    OUTPUT_JSON.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        OUTPUT_JSON,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            summary,
            file,
            indent=2,
        )

    print(
        f"Saved summary to:"
        f"\n{OUTPUT_JSON}"
    )

    # --------------------------------------------------------
    # Results
    # --------------------------------------------------------

    print("\n" + "=" * 60)

    print("RESULTS")

    print("=" * 60)

    print("\nAI Agent:")

    print(
        f"  Intent Accuracy : "
        f"{agent_metrics['intent_accuracy']:.2%}"
    )

    print(
        f"  Intent Macro-F1 : "
        f"{agent_metrics['intent_macro_f1']:.2%}"
    )

    print(
        f"  Escalation Acc. : "
        f"{agent_metrics['escalation_accuracy']:.2%}"
    )

    print(
        f"  Coverage         : "
        f"{agent_metrics['evaluation_coverage']:.2%}"
    )

    print(
        f"  Successful Runs  : "
        f"{agent_metrics['valid_agent_runs']}"
    )

    print(
        f"  API/Run Errors   : "
        f"{agent_metrics['agent_errors']}"
    )

    print(
        f"  Escalation Eval. : "
        f"{agent_metrics['escalation_evaluation_count']}"
    )

    print(
        "\nTF-IDF + Logistic Regression:"
    )

    print(
        f"  Intent Accuracy : "
        f"{tfidf_metrics['intent_accuracy']:.2%}"
    )

    print(
        f"  Intent Macro-F1 : "
        f"{tfidf_metrics['intent_macro_f1']:.2%}"
    )

    print(
        "\nMajority Baseline:"
    )

    print(
        f"  Intent Accuracy : "
        f"{majority_metrics['intent_accuracy']:.2%}"
    )

    print(
        f"  Intent Macro-F1 : "
        f"{majority_metrics['intent_macro_f1']:.2%}"
    )

    print(
        "\nEvaluation complete."
    )


if __name__ == "__main__":
    main()
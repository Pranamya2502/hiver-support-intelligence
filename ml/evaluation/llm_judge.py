"""
LLM-as-judge evaluation.

Compares:
1. AI-generated support reply
2. Nearest historical-response baseline

Rubric:
- Relevance: Does the response address the customer's issue?
- Groundedness: Does it stay supported by the historical evidence?
- Helpfulness: Is it useful and actionable?
- Overall: Overall support quality from 1-5.

Only successfully generated AI replies are judged.
"""

from pathlib import Path
import json
import sys
import time

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.app.services.llm_provider import LLMProvider


AGENT_RESULTS_PATH = (
    REPO_ROOT
    / "reports"
    / "evaluation_results.csv"
)

NEAREST_RESULTS_PATH = (
    REPO_ROOT
    / "reports"
    / "nearest_response_results.csv"
)

OUTPUT_PATH = (
    REPO_ROOT
    / "reports"
    / "llm_judge_results.csv"
)


def build_prompt(
    customer_message,
    historical_response,
    ai_response,
):
    return f"""
You are evaluating customer support responses.

Customer message:
{customer_message}

Historical support response:
{historical_response}

AI-generated response:
{ai_response}

Evaluate the AI-generated response against the customer's
actual issue and the historical support response.

Score each criterion from 1 to 5.

Criteria:

1. Relevance
Does the response directly address the customer's issue?

2. Groundedness
Does the response avoid unsupported claims, invented policies,
invented refunds, invented links, or actions not supported by
the historical evidence?

3. Helpfulness
Would this response be useful to the customer?

4. Overall
Overall quality as a customer-support response.

Return ONLY valid JSON:

{{
  "relevance": 1,
  "groundedness": 1,
  "helpfulness": 1,
  "overall": 1,
  "reason": "short explanation"
}}

Scores must be integers from 1 to 5.
"""


def judge_row(
    provider,
    row,
):
    """Judge one AI response."""

    customer_message = str(
        row["customer_text"]
    )

    historical_response = str(
        row["historical_response"]
    )

    ai_response = str(
        row["draft_reply"]
    )

    prompt = build_prompt(
        customer_message,
        historical_response,
        ai_response,
    )

    response = provider.generate(
        prompt
    )

    result = json.loads(response)

    required = [
        "relevance",
        "groundedness",
        "helpfulness",
        "overall",
        "reason",
    ]

    for field in required:

        if field not in result:
            raise ValueError(
                f"Missing judge field: {field}"
            )

    for field in [
        "relevance",
        "groundedness",
        "helpfulness",
        "overall",
    ]:

        value = int(result[field])

        if value < 1 or value > 5:
            raise ValueError(
                f"Invalid {field} score: {value}"
            )

        result[field] = value

    return result


def main():

    print("=" * 60)
    print("HIVER - LLM JUDGE")
    print("=" * 60)

    if not AGENT_RESULTS_PATH.exists():
        raise FileNotFoundError(
            f"Missing: {AGENT_RESULTS_PATH}"
        )

    if not NEAREST_RESULTS_PATH.exists():
        raise FileNotFoundError(
            f"Missing: {NEAREST_RESULTS_PATH}"
        )

    agent_df = pd.read_csv(
        AGENT_RESULTS_PATH
    )

    nearest_df = pd.read_csv(
        NEAREST_RESULTS_PATH
    )

    # Only successfully generated AI responses.
    agent_df = agent_df[
        agent_df["draft_reply"]
        .fillna("")
        .astype(str)
        .str.strip()
        != ""
    ].copy()

    print(
        f"Successful AI responses available: "
        f"{len(agent_df)}"
    )

    merged = agent_df.merge(
        nearest_df[
            [
                "row_id",
                "historical_response",
                "similarity_score",
            ]
        ],
        on="row_id",
        how="left",
    )

    provider = LLMProvider()

    previous = None

    if OUTPUT_PATH.exists():

        try:
            previous = pd.read_csv(
                OUTPUT_PATH
            )

            print(
                f"Previous judge results found: "
                f"{len(previous)}"
            )

        except Exception:
            previous = None

    results = []

    for _, row in merged.iterrows():

        row_id = int(
            row["row_id"]
        )

        # Reuse previous successful judge result.
        if previous is not None:

            old = previous[
                previous["row_id"]
                == row_id
            ]

            if len(old) > 0:

                results.append(
                    old.iloc[0].to_dict()
                )

                print(
                    f"Skipping row {row_id + 1} "
                    f"(already judged)"
                )

                continue

        print(
            f"Judging {row_id + 1}/"
            f"{len(merged)}..."
        )

        try:

            judgment = judge_row(
                provider,
                row,
            )

            result = {
                "row_id": row_id,
                "customer_text": row[
                    "customer_text"
                ],
                "ai_response": row[
                    "draft_reply"
                ],
                "historical_response": row[
                    "historical_response"
                ],
                "similarity_score": row[
                    "similarity_score"
                ],
                "relevance": judgment[
                    "relevance"
                ],
                "groundedness": judgment[
                    "groundedness"
                ],
                "helpfulness": judgment[
                    "helpfulness"
                ],
                "overall": judgment[
                    "overall"
                ],
                "reason": judgment[
                    "reason"
                ],
                "error": "",
            }

            results.append(result)

            pd.DataFrame(
                results
            ).to_csv(
                OUTPUT_PATH,
                index=False,
            )

        except Exception as exc:

            print(
                f"Judge error on row "
                f"{row_id}: {exc}"
            )

            results.append({
                "row_id": row_id,
                "customer_text": row[
                    "customer_text"
                ],
                "ai_response": row[
                    "draft_reply"
                ],
                "historical_response": row[
                    "historical_response"
                ],
                "similarity_score": row[
                    "similarity_score"
                ],
                "relevance": "",
                "groundedness": "",
                "helpfulness": "",
                "overall": "",
                "reason": "",
                "error": str(exc),
            })

            # Small pause so we don't hammer the API.
            time.sleep(1)

    results_df = pd.DataFrame(
        results
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    results_df.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    numeric_columns = [
        "relevance",
        "groundedness",
        "helpfulness",
        "overall",
    ]

    for column in numeric_columns:

        results_df[column] = pd.to_numeric(
            results_df[column],
            errors="coerce",
        )

    valid = results_df[
        results_df["overall"].notna()
    ]

    print("\n" + "=" * 60)
    print("LLM JUDGE RESULTS")
    print("=" * 60)

    print(
        f"\nJudged responses: "
        f"{len(valid)}"
    )

    if len(valid) > 0:

        print(
            f"Average Relevance: "
            f"{valid['relevance'].mean():.2f}/5"
        )

        print(
            f"Average Groundedness: "
            f"{valid['groundedness'].mean():.2f}/5"
        )

        print(
            f"Average Helpfulness: "
            f"{valid['helpfulness'].mean():.2f}/5"
        )

        print(
            f"Average Overall: "
            f"{valid['overall'].mean():.2f}/5"
        )

    print(
        f"\nSaved to:"
        f"\n{OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
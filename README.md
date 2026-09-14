Hiver Support Intelligence

An AI customer-support agent built for the Hiver SDE Intern take-home assignment using the Customer Support on Twitter (TWCS) dataset.

The system focuses on AmazonHelp and combines intent classification, historical-response retrieval, grounded reply generation, escalation decisions, and evaluation.

Problem Framing

Customer-support teams handle a large number of repetitive requests, but fully automated replies can be risky when the system is uncertain or lacks reliable evidence.

This project builds a support-assistance workflow that:

Classifies an incoming customer message into a small set of support intents.

Retrieves historically similar AmazonHelp conversations.

Uses those historical resolutions as evidence to draft a grounded reply.

Decides whether the case can be auto-handled or should be escalated to a human.

Evaluates the system on a manually labelled golden set.

The design intentionally prioritizes grounded responses and explicit escalation over blindly maximizing automation.

Dataset and Brand Selection

The project uses the Customer Support on Twitter (TWCS) dataset:

thoughtvector/customer-support-on-twitter

The dataset contains approximately 2.8M tweets covering multi-turn customer-support interactions.

Why AmazonHelp?

I selected AmazonHelp based on:

High support-response volume

Strong customer-to-brand reply linkage

Diverse customer issues

Sufficient historical responses for retrieval

The preprocessing pipeline produced:

168,814 customer-agent conversation pairs

Only the required AmazonHelp subset is used throughout the system rather than processing the full dataset at every stage.

Raw dataset files are excluded from Git.

System Architecture

             Customer Message
                    |
                    v
           +------------------+
           | Intent Classifier |
           +------------------+
                    |
             Intent + Confidence
                    |
                    v
           +------------------+
           | Historical       |
           | Retrieval        |
           +------------------+
                    |
             Top-K Similar Cases
                    |
                    v
           +------------------+
           | Escalation       |
           | Decision         |
           +------------------+
                    |
                    v
           +------------------+
           | Grounded Reply   |
           | Generation       |
           +------------------+
                    |
                    v
             Support Agent UI

Intent Taxonomy

A deliberately small taxonomy of 9 intents was created to keep classification practical and avoid overly fine-grained classes.

Intent

Description

order_issue

Problems with placing, changing, or managing an order

delivery_issue

Late, missing, damaged, or incorrect delivery

return_refund

Returns, refunds, replacements, or refund status

payment_billing

Payment failures, charges, invoices, or billing questions

account_access

Login, password, or account-access problems

prime_subscription

Prime membership, subscription, or benefits

product_issue

Problems with a product, device, or product functionality

digital_content

Prime Video, Kindle, apps, or other digital-content issues

general_support

Issues that do not clearly fit another intent

Golden Evaluation Set

A manually labelled 200-example golden set was created from the processed AmazonHelp conversations.

Each example contains:

Customer message

Historical AmazonHelp response

Gold intent

Gold escalation decision

Label notes

The golden set is stored at:

data/golden/golden_set.csv

The golden-set sampling uses a fixed random seed of 42.

Golden-set distribution

Intent

Examples

general_support

81

delivery_issue

63

order_issue

15

payment_billing

13

return_refund

10

digital_content

7

product_issue

5

account_access

3

prime_subscription

3

Total

200

The distribution is intentionally reported because accuracy alone can be misleading on this imbalanced set.

Historical Retrieval

Historical support evidence is retrieved using:

Sentence Transformers

sentence-transformers/all-MiniLM-L6-v2

384-dimensional embeddings

FAISS IndexFlatIP

L2-normalized embeddings

Exact cosine-similarity search

Indexed corpus:

168,814 customer-agent conversation pairs

Build the index

python ml/retrieval/build_index.py

This generates:

data/processed/retrieval/amazonhelp.index
data/processed/retrieval/metadata.csv

Run retrieval sanity checks

python ml/retrieval/retriever.py

Python usage

from ml.retrieval.retriever import HistoricalRetriever

retriever = HistoricalRetriever()

results = retriever.search(
query="My package has not arrived yet and tracking hasn't updated",
top_k=5
)

for result in results:
print(f"Rank: {result['rank']}")
print(f"Score: {result['score']:.4f}")
print(f"Customer: {result['customer_text']}")
print(f"Response: {result['agent_response']}")

AI Support Agent

The agent follows this pipeline:

Customer Message
|
v
Intent Classification
|
v
Historical Retrieval
|
v
Escalation Decision
|
v
Grounded Reply Generation

The LLM is accessed through a provider abstraction so that the model/provider can be changed without changing the overall agent architecture.

The current development configuration uses the Groq OpenAI-compatible API.

The reply-generation prompt instructs the model to:

Ground the response in retrieved historical support evidence

Avoid inventing policies

Avoid inventing refunds or actions

Avoid inventing links

Avoid claiming actions that were not performed

Avoid mentioning the AI system to the customer

Escalation Policy

The current escalation policy uses explicit, inspectable thresholds:

Intent confidence threshold: 0.75

Minimum historical evidence similarity: 0.65

A case is escalated when:

Intent confidence is below 0.75

No historical support evidence is retrieved

The best retrieved evidence has similarity below 0.65

Otherwise, the system marks the case for auto-handling.

This separates the automation decision from free-form LLM reasoning and makes the policy easier to inspect and tune.

Full-Stack Application

Backend

The backend is implemented with:

Python

FastAPI

Pydantic

Uvicorn

Main endpoints:

GET  /health
POST /auth/login
POST /agent/respond

Frontend

The frontend is implemented with:

React

TypeScript

Vite

Tailwind CSS

Lucide icons

The UI provides:

Login screen

Support inbox

Customer message input

Predicted intent

Intent confidence

Auto-handle / escalation decision

Draft support reply

Historical support evidence

Evaluation Methodology

The evaluation compares the AI system against two classification baselines and one reply baseline.

Baseline 1 — Majority Class

Always predicts the most frequent intent in the golden set.

Baseline 2 — TF-IDF + Logistic Regression

Uses TF-IDF text features followed by Logistic Regression.

Reply Baseline — Nearest Historical Response

Retrieves the most similar historical customer message and directly returns its associated historical support response.

This reply baseline is useful as a reference, but it has an important limitation: the golden examples were sampled from the same historical corpus used by the retriever. Therefore, exact historical matches can occur.

It should not be interpreted as an independent production-quality benchmark.

Metrics

The primary intent-classification metrics are:

Intent Accuracy

Intent Macro-F1

Macro-F1 is included because the golden set is highly imbalanced.

The agent also reports:

Escalation accuracy

Evaluation coverage

Number of successful and failed LLM runs

For generated replies, an LLM-as-judge evaluates:

Relevance

Groundedness

Helpfulness

Overall quality

Each judge dimension is scored from 1 to 5.

Human validation is used to compare a sample of judge scores with human scores and measure judge-human agreement.

Current Evaluation Results

The final evaluation successfully processed all 200 examples.

System

Intent Accuracy

Macro-F1

Majority baseline

40.50%

6.41%

TF-IDF + Logistic Regression

66.00%

49.19%

AI Agent

62.00%

51.69%

Additional AI Agent results:

Successful evaluations: 200/200

Coverage: 100.00%

Escalation accuracy: 61.50%

These are the final results from the 200-example golden evaluation. The evaluation completed with 0 API/run errors.

LLM-as-Judge

The LLM judge compares generated support replies with the nearest historical-response baseline using a fixed rubric.

Rubric

Criterion

Score

Relevance

1–5

Groundedness

1–5

Helpfulness

1–5

Overall quality

1–5

The judge also records a short reason for each assessment.

The judge evaluation is resumable and operates only on successfully generated AI responses.

A separate human-validation sample is used to measure agreement between the LLM judge and human assessment.

Final available judge averages:

Relevance: 3.63 / 5

Groundedness: 4.41 / 5

Helpfulness: 3.54 / 5

Overall quality: 3.49 / 5

Human validation used 20 examples. Exact agreement with the LLM judge was 95% for relevance, 95% for groundedness, 100% for helpfulness, and 80% for overall quality, averaging 92.5% exact agreement.

Failure Analysis

The current evaluation surfaced several recurring failure patterns.

Failure 1 — Very short messages

Example:

@AmazonHelp Amazon shipping.

There is very little semantic information, so the classifier can confuse delivery-related messages with general support.

Failure 2 — Context-dependent messages

Example:

@AmazonHelp No. it just diappears.

The meaning depends strongly on the previous conversation. Classifying an isolated tweet loses useful conversational context.

Failure 3 — Multilingual messages

Example:

Clients @115821 attention à l'arnaque qui tourne par mail !!!

The classifier can become less reliable when the message is outside the dominant language distribution.

Failure 4 — Noisy social-media text

Mentions, URLs, abbreviations, spelling errors, and informal language make intent classification harder.

Failure 5 — Low-confidence predictions

Ambiguous examples can produce low intent confidence and are therefore escalated. This improves caution but can reduce automation coverage.

Hypotheses

The main hypotheses from these failures are:

Conversation history should improve classification of short replies.

Multilingual or language-aware preprocessing could improve robustness.

Confidence scores need calibration rather than being treated as directly meaningful probabilities.

Retrieval quality should be evaluated on a held-out corpus to avoid overlap with the golden set.

What Is Misleading About My Headline Number?

The headline AI accuracy should not be interpreted as production accuracy.

There are several reasons:

The golden set contains only 200 examples.

The intent distribution is highly imbalanced.

The golden set contains only 200 examples, so the results should not be treated as production accuracy.

The nearest-response baseline shares its retrieval corpus with the golden examples, allowing exact historical matches.

Social-media messages can be extremely short and context-dependent.

Therefore, the reported metrics should be interpreted as a controlled prototype evaluation, not as an estimate of production performance.

Decision Log

The main non-obvious engineering decisions are documented in:

reports/decision_log.md

Key decisions include:

Selecting AmazonHelp based on support volume and reply linkage

Using a small 9-intent taxonomy

Building a 200-example manually labelled golden set

Using Sentence Transformers + FAISS for semantic retrieval

Using exact cosine similarity through normalized inner-product search

Using top-5 historical evidence for response generation

Separating escalation logic from LLM free-form reasoning

Using explicit confidence and retrieval thresholds

Including TF-IDF + Logistic Regression as a traditional baseline

Including a nearest historical-response reply baseline

Reporting Macro-F1 because of class imbalance

Disclosing retrieval/golden-set overlap in the baseline

Making the evaluation harness resumable because of LLM provider limits

Next-Week Plan

If given another week, I would prioritize:

Add conversation-level context instead of classifying isolated tweets.

Improve multilingual intent classification.

Calibrate intent confidence using human-labelled validation data.

Tune escalation thresholds using validation performance.

Evaluate retrieval using a held-out corpus.

Expand the golden set with harder and more balanced examples.

Add latency and token-cost measurements for production readiness.

Running the Project

Backend

From the project root:

uvicorn backend.app.main --reload

Backend:

http://127.0.0.1:8000

Health check:

http://127.0.0.1:8000/health

Frontend

Open another terminal:

cd frontend
npm install
npm run dev

Frontend:

http://localhost:5173

Demo Login

Email: admin@hiver.com
Password: hiver123

The repository uses demo authentication for the take-home application. API credentials are kept in environment variables and are not committed to Git.

Evaluation Commands

Create the golden set:

python ml/evaluation/create_golden_set.py

Validate the golden set:

python ml/evaluation/complete_golden_set.py

Run the evaluation:

python ml/evaluation/run_evaluation.py

Run the nearest-response baseline:

python ml/evaluation/nearest_response_baseline.py

Run the LLM judge:

python ml/evaluation/llm_judge.py

Prepare human validation and failure analysis:

python ml/evaluation/human_validation.py

Repository Structure

hiver-support-intelligence/
│
├── backend/
│   └── app/
│       ├── api/
│       ├── core/
│       └── services/
│
├── frontend/
│   └── src/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── golden/
│
├── ml/
│   ├── preprocessing/
│   ├── taxonomy/
│   ├── retrieval/
│   └── evaluation/
│
├── reports/
│   ├── decision_log.md
│   ├── evaluation_report.md
│   └── evaluation outputs
│
├── requirements.txt
└── README.md

Reproducibility

The project is organized around reproducible scripts for preprocessing, taxonomy validation, retrieval, evaluation, and application startup.

The golden-set sampling uses a fixed random seed of 42.

Raw dataset files, generated retrieval artifacts, environment files, and API secrets are excluded from Git where appropriate.

The repository contains the code required to rebuild generated artifacts locally.

Project Status

Completed

Dataset analysis

AmazonHelp brand selection

Data preprocessing

9-intent taxonomy

200-example golden set

FAISS historical retrieval

AI support agent

Escalation logic

FastAPI backend

React frontend

Evaluation baselines

LLM-as-judge workflow

Human validation workflow

Failure analysis

Decision log

Finalization

Final evaluation completed (200/200)

Final LLM-judge run completed

Human judge-agreement validation completed

Provisional metrics replaced with final results

Final README/report review
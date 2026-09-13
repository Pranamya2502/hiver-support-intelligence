# Hiver Support Intelligence

An AI customer support agent and evaluation system built on the Customer Support on Twitter (TWCS) dataset, focused on **AmazonHelp**.

---

## 📌 Project Overview

This repository implements the Hiver SDE Intern take-home assignment: an AI-driven support intelligence system designed to classify customer support inquiries, retrieve historical resolution evidence, draft grounded agent responses, and evaluate performance using a hand-annotated golden evaluation set.

---

## 🛠️ Environment & Setup

### Prerequisites
- Python 3.10+
- Virtual environment (`.venv`)

### Installation
```bash
# Activate virtual environment (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Install required packages
pip install -r requirements.txt
```

---

## 📁 Repository Structure

```text
hiver-support-intelligence/
├── data/
│   ├── raw/                      # Raw TWCS archive (ignored by Git)
│   ├── processed/                # Filtered conversation dataset & retrieval index
│   │   ├── amazonhelp_conversations.csv
│   │   └── retrieval/            # FAISS vector index & metadata (ignored by Git)
│   │       ├── amazonhelp.index
│   │       └── metadata.csv
│   └── golden/
│       └── golden_set.csv        # 200-example ground-truth golden evaluation set
├── ml/
│   ├── preprocessing/
│   │   └── prepare.py            # Data pipeline filtering AmazonHelp pairs
│   ├── taxonomy/
│   │   └── intents.py            # Locked 9-intent support taxonomy
│   ├── evaluation/
│   │   ├── create_golden_set.py  # Golden set sampling script (seed 42)
│   │   ├── label_golden_set.py   # Manual labeling CLI tool
│   │   └── complete_golden_set.py# Reproducible golden set completion & validator
│   └── retrieval/
│       ├── build_index.py        # FAISS IndexFlatIP index builder
│       └── retriever.py          # HistoricalRetriever class & sanity check CLI
├── requirements.txt
└── README.md
```

---

## 🚀 Step 5 — Vector Retrieval System

The retrieval module uses **Sentence Transformers** and **FAISS** to find historical AmazonHelp support conversations that are semantically similar to incoming customer messages.

### Key Technical Specifications
- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions)
- **Vector Search Engine**: FAISS (`IndexFlatIP` with $L_2$-normalized embeddings for exact cosine similarity)
- **Indexed Corpus**: 168,814 customer-agent conversation pairs from `data/processed/amazonhelp_conversations.csv`

---

### How to Build the Retrieval Index

To generate the FAISS vector index and metadata mapping locally:

```bash
python ml/retrieval/build_index.py
```

This generates:
- `data/processed/retrieval/amazonhelp.index`
- `data/processed/retrieval/metadata.csv`

---

### How to Run Retrieval Sanity Check

To run the retrieval sanity check on sample customer support queries:

```bash
python ml/retrieval/retriever.py
```

### Python API Usage

```python
from ml.retrieval.retriever import HistoricalRetriever

# Initialize retriever (loads model, FAISS index, and metadata)
retriever = HistoricalRetriever()

# Search for top-5 semantically similar historical support conversations
results = retriever.search(
    query="My package has not arrived yet and tracking hasn't updated",
    top_k=5
)

for res in results:
    print(f"Rank {res['rank']} | Score: {res['score']:.4f}")
    print(f"Customer Text    : {res['customer_text']}")
    print(f"AmazonHelp Reply : {res['agent_response']}\n")
```

# Rhema
### The Internet, One Day at a Time.

Rhema is an automated text intelligence pipeline that ingests daily news articles, extracts keywords, clusters them semantically, and surfaces named topic groups through a clean frontend.

---

## How It Works

```
RSS Feed → Keyword Extraction → Embedding → Dimensionality Reduction → Clustering → Topic Naming → Frontend
```

**1. `process_headlines.py`**
Fetches articles from an RSS feed (configured via environment variable) and writes titles, links, and timestamps to `data/headlines.json`.

**2. `process_nodes.py`**
Runs each headline through YAKE to extract the dominant keyword phrase. Writes a flat list of nodes (phrase, relevance score, title, link) to `data/nodes.json`.

**3. `process_topics.py`**
- Embeds keyword phrases using SentenceTransformers (`all-MiniLM-L6-v2`, 384 dimensions)
- Reduces to 15 dimensions using UMAP (cosine metric, `n_neighbors=8`, `min_dist=0.0`)
- Clusters with EVoC (`approx_n_clusters=10`, `base_min_cluster_size=5`)
- Passes cluster contents to Claude Haiku to generate specific 3-4 word topic names
- Writes named, ranked clusters to `data/topics.json`

**`index.html`**
Reads `data/topics.json` and renders topic clusters as an interactive bubble chart. Click any bubble to see the articles inside.

---

## Stack

| Layer | Library |
|---|---|
| RSS ingestion | `feedparser` |
| Keyword extraction | `yake` |
| Embeddings | `sentence-transformers` |
| Dimensionality reduction | `umap-learn` |
| Clustering | `evoc` |
| Topic naming | `anthropic` (Claude Haiku) |

---

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/BlaiseLM/rhema.git
cd rhema
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Configure environment variables**

Copy `.env.example` to `.env` and fill in:
```
RSS_NEWS=<your RSS feed URL>
HF_TOKEN=<your Hugging Face token>
ANTHROPIC_API_KEY=<your Anthropic API key>
```

---

## Running the Pipeline

### Manually

Run the three scripts in order:
```bash
python scripts/process_headlines.py
python scripts/process_nodes.py
python scripts/process_topics.py
```

Then open `index.html` in your browser.

### Automated (GitHub Actions)

The pipeline runs daily at midnight UTC via `.github/workflows/daily.yml`. Requires RSS_NEWS, HF_TOKEN, and ANTHROPIC_API_KEY set as GitHub Actions secrets.

---

## Project Structure

```
rhema/
├── .github/
│   └── workflows/
│       └── daily.yml           # Automated daily pipeline
├── data/
│   ├── headlines.json          # Raw articles from RSS
│   ├── nodes.json              # Keyword nodes per article
│   └── topics.json             # Named, clustered topics
├── scripts/
│   ├── process_headlines.py
│   ├── process_nodes.py
│   └── process_topics.py
├── index.html
├── requirements.txt
└── .env.example
```

---

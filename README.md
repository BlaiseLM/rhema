# Rhema
### The Internet, One Day at a Time.

Rhema is an automated text intelligence pipeline that ingests daily news articles, extracts keywords, clusters them semantically, and surfaces named topic groups through a clean frontend. It runs end-to-end without manual input.

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

The pipeline runs automatically every day at 12pm UTC via `.github/workflows/daily.yml`. On each run it executes all three scripts, commits the updated `data/` output back to the repo, and the GitHub Pages frontend reflects the new clusters automatically.

To set this up:

**1. Add secrets** — repo → Settings → Secrets and variables → Actions → add the following:
- `RSS_NEWS` — your RSS feed URL
- `HF_TOKEN` — your Hugging Face access token
- `ANTHROPIC_API_KEY` — your Anthropic API key

**2. Enable write permissions** — Settings → Actions → General → Workflow permissions → Read and write permissions

**3. Enable GitHub Pages** — Settings → Pages → source: master branch, root folder

The workflow also includes a `workflow_dispatch` trigger so you can fire it manually from the Actions tab at any time.

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

## What It Is and What It Isn't

Rhema is a **text intelligence and NLP project**. It processes unstructured text and produces structured, labeled topic clusters. It is not a signal processing or RF/sensor project. The data source is configurable — the pipeline is agnostic to what RSS feed or text corpus feeds the top of it.

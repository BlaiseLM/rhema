import json
import os
import re
import traceback
from sentence_transformers import SentenceTransformer
from umap import UMAP
import evoc
import anthropic

model = SentenceTransformer("all-MiniLM-L6-v2", use_auth_token=os.environ.get("HF_TOKEN"))
reducer = UMAP(
    n_components=15, 
    n_neighbors=8, 
    min_dist=0.0, 
    metric="cosine", 
    random_state=42
)
clusterer = evoc.EVoC(
    approx_n_clusters=10, 
    base_min_cluster_size=5, 
    min_samples=3
)

api_key = os.environ.get("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=api_key)

def fetch_phrases(nodes_json): 
    if nodes_json is None: 
        print("nodes_json null")
        return 
    try: 
        phrases = []
        with open(nodes_json, "r+") as f: 
            nodes = json.load(f)
            for node in nodes: 
                phrases.append(node["phrase"])
        if not phrases:
            print("Error occurred while fetching phrases, no phrases found in nodes_json")
            return None
        return phrases
    except Exception as e:
        traceback.print_exc()
        print(f"Error occurred while fetching phrases: {e}")

def create_embeddings(phrases):
    if phrases is None: 
        print("phrases null")
        return 
    try: 
        raw = model.encode(phrases)
        return reducer.fit_transform(raw)
    except Exception as e: 
        traceback.print_exc()
        print(f"Error occurred while encoding phrases: {e}")

def create_topics(embeddings, nodes_json): 
    if embeddings is None: 
        print("embeddings null")
        return
    if nodes_json is None: 
        print("nodes_json null")
        return 
    clusterer_labels = clusterer.fit_predict(embeddings)
    try:
        topics = {}
        with open(nodes_json, "r+") as f: 
            nodes = json.load(f)
            for x in range(len(clusterer_labels)): 
                topic = clusterer_labels[x].item()
                if topic not in topics: 
                    topics[topic] = []
                node = nodes[x]
                simplified_node = {}
                simplified_node["title"] = node["title"]
                simplified_node["link"] = node["link"]
                topics[topic].append(simplified_node)
            return topics
    except Exception as e: 
        traceback.print_exc()
        print(f"Error occurred while creating topics: {e}")

def generate_topic_names(topics):
    try:
        summaries = "\n\n".join(
            f"Cluster {label}:\n" + "\n".join(f"- {a['title']}" for a in articles)
            for label, articles in topics
        )
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": 
                    f"""Label each news article cluster with a short 3-4 word topic name (Title Case, no punctuation).
                    Return ONLY a valid JSON object mapping cluster id as a string key to the label. No generic labels like "AI Development" or "AI Research". Be specific to the articles in the cluster. 
                    Example: {{"4": "Example Title 1", "0": "Example Title 2", "-1": "Misc"}}{summaries}"""
            }]
        )
        raw = message.content[0].text.strip()
        raw = re.sub(r"```(?:json)?", "", raw).strip()
        return json.loads(raw)
    except Exception as e:
        traceback.print_exc()
        print(f"Error occurred while generating topic names: {e}")
        return {}

def populate_topics(topics, names, topic_json): 
    if topics is None: 
        print("topics null")
        return 
    if topic_json is None: 
        print("topic_json null")
        return 
    try:
        named_topics = [
            {
                "cluster": label,
                "name": names.get(str(label), ""),
                "articles": articles
            }
            for label, articles in topics
        ]
        with open(topic_json, "w") as f: 
            json.dump(named_topics, f, indent=2)
    except Exception as e: 
        traceback.print_exc()
        print(f"Error occurred while populating topics: {e}")

raw_topics = create_topics(create_embeddings(fetch_phrases("data/nodes.json")), "data/nodes.json")
if raw_topics is None:
    print("Error occurred while creating topics, raw_topics is null")
    with open("data/topics.json", "w") as f:
        json.dump([], f)
else:
    topics = sorted(raw_topics.items(), key=lambda x: len(x[1]), reverse=True)
    names = generate_topic_names(topics)
    populate_topics(topics, names, "data/topics.json")
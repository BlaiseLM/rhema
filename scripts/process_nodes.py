import yake 
import json
import traceback

kw_extractor = yake.KeywordExtractor()

def extract_keywords(headlines_json): 
    if headlines_json is None: 
        print("headlines_json null")
        return 
    try: 
        with open(headlines_json, "r") as f: 
            entries = json.load(f)
            for entry in entries: 
                title_keywords = kw_extractor.extract_keywords(entry["title"])
                entry["keywords"] = title_keywords  
            return entries
    except Exception as e:
        print(f"Error occurred while opening/modifying headlines_json: {e}")

def create_nodes(entries): 
    if entries is None: 
        print("entries null")
        return 
    try: 
        nodes = []
        for entry in entries: 
            keywords = entry.get("keywords", [])
            if not keywords : 
                continue 
            node = {
                "phrase": keywords[0][0], 
                "relevance": keywords[0][1], 
                "title": entry["title"],
                "link": entry["link"]
            }
            nodes.append(node)
        return nodes
    except Exception as e:
        traceback.print_exc()
        print(f"Error occurred while creating nodes: {e}")

def populate_nodes(headlines_json, nodes_json): 
    if nodes_json is None: 
        print("nodes_json null")
        return 
    try: 
        entries = extract_keywords(headlines_json)
        nodes = create_nodes(entries)
        if nodes is None:
            print("Error occurred while creating nodes, nodes is null")
            nodes = []
        with open(nodes_json, "w") as f: 
            json.dump(nodes, f, indent=2)
    except Exception as e: 
        print(f"Error occured while populating nodes_json: {e}")

def validate_json(filepath):
    try:
        with open(filepath, "r") as f:
            json.load(f)
        print(f"{filepath} is valid JSON")
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in {filepath}: {e}")

populate_nodes("data/headlines.json", "data/nodes.json")
validate_json("data/nodes.json")
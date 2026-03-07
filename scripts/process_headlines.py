import feedparser
import os
import json
import traceback 

feed_url = os.environ.get("RSS_NEWS")
if not feed_url:
    print("Error occured while parsing RSS NEWS environment variable")
    exit(0)

feed = feedparser.parse(feed_url)
if not feed.entries:
    print("Error occured while parsing RSS feed, no entries found")
    import json as _json
    with open("data/headlines.json", "w") as _f:
        _json.dump([], _f)
    exit(0)

def scrape_headline(entry):
    if entry is None: 
        print("entry null")
        return 
    data = { 
        "title": entry.title, 
        "link": entry.link, 
        "datetime": str(entry.published_parsed), 
    }
    return data

def populate_headlines(headlines_json): 
    try: 
        with open(headlines_json, "w") as f: 
            entries = []
            for entry in feed.entries: 
                entryData = scrape_headline(entry)
                entries.append(entryData)
            json.dump(entries, f, indent=2)
    except Exception as e:
        print(f"Error occurred while opening/modifying headlines_json: {e}")
        traceback.print_exc()

def validate_json(filepath):
    try:
        with open(filepath, "r") as f:
            json.load(f)
        print(f"{filepath} is valid JSON")
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in {filepath}: {e}")
        
populate_headlines("data/headlines.json")
validate_json("data/headlines.json")
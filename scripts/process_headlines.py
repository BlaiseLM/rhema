import feedparser
import os
import json
import traceback 

RSS_NEWS = os.environ.get("RSS_NEWS")

def combine_feeds(RSS_NEWS): 
    if RSS_NEWS is None: 
        print("Error occured while accessing RSS_NEWS environment variable")
        return 
    entries = []
    urls = RSS_NEWS.split(",")
    for url in urls:  
        feed = feedparser.parse(url.strip())
        if feed is None or feed.entries is None: 
            print("Error occured while parsing RSS feed")
            continue
        for entry in feed.entries: 
            entries.append(entry)
    if not entries: 
        print("Error occurred while combining feeds, no entries found")
        return None
    return entries    

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
        combined = combine_feeds(RSS_NEWS=RSS_NEWS)
        if combined is None: 
            print("Error occurred while combining feeds, combined is null")
            return 
        with open(headlines_json, "w") as f: 
            entries = []
            for entry in combined: 
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
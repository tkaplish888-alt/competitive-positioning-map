import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

DB_PATH = "data/positioning.db"

# Path to the folder where Project 2 (competitive-intel-monitor) writes its
# scraped competitor text as JSON snapshot files.  Assumes both project folders
# sit side by side in the same parent directory.
SNAPSHOTS_PATH = "../competitive-intel-monitor/snapshots"

COMPETITORS = {
    "valur": {
        "name": "Valur",
        "url": "https://valur.com",
        "color": "#4F46E5",
        "is_you": True,
    },
    "trust_and_will": {
        "name": "Trust & Will",
        "url": "https://trustandwill.com",
        "color": "#10B981",
        "is_you": False,
    },
    "wealth_com": {
        "name": "Wealth.com",
        "url": "https://wealth.com",
        "color": "#F59E0B",
        "is_you": False,
    },
    "vanilla": {
        "name": "Vanilla",
        "url": "https://vanillaonline.com",
        "color": "#EF4444",
        "is_you": False,
    },
    "holistiplan": {
        "name": "Holistiplan",
        "url": "https://holistiplan.com",
        "color": "#8B5CF6",
        "is_you": False,
    },
    "gentreo": {
        "name": "Gentreo",
        "url": "https://gentreo.com",
        "color": "#06B6D4",
        "is_you": False,
    },
}

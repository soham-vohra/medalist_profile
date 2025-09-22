# main.py
# ---------------------------
# This script does a simple ETL on Olympic athlete data.
# Steps:
#   1) Read the athlete_events.csv file from the data/ folder
#   2) Drop unnecessary columns ("City", "Games")
#   3) Add a "did_medal" column = True if Medal is not NA
#   4) Call the REST Countries API to get country populations
#   5) Match each athlete’s NOC/Team to a country population
#   6) Save the cleaned dataset to data/raw/raw_data.csv
# ---------------------------

import os
from pathlib import Path

import pandas as pd
import requests

# Input/output locations
INPUT_PATHS = ["data/athlete_events.csv", "./data/athlete_events.csv"]
OUTPUT_PATH = Path("data/raw/raw_data.csv")

# REST Countries endpoints
RESTCOUNTRIES_URL = "https://restcountries.com/v3.1/all"
# smaller/faster response: only fetch needed fields
RESTCOUNTRIES_URL_FIELDS = "https://restcountries.com/v3.1/all?fields=name,cca3,cioc,population"


def load_csv():
    """Try reading athlete_events.csv from one of the expected locations."""
    for p in INPUT_PATHS:
        if Path(p).exists():
            return pd.read_csv(p)
    raise FileNotFoundError(
        "Couldn't find data/athlete_events.csv (or ./data/athlete_events.csv)."
    )


def build_population_lookup():
    """Fetch country populations from the REST Countries API.
    Build three lookup dictionaries:
      - by IOC code (cioc) e.g. USA, KEN
      - by ISO3 code (cca3) e.g. USA, KEN
      - by common country name (lowercased) e.g. 'kenya'
    """

    import time

    def fetch(url):
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        return r.json()

    # Try the fields URL first (smaller), then fall back if needed
    tries = [RESTCOUNTRIES_URL_FIELDS, RESTCOUNTRIES_URL, RESTCOUNTRIES_URL_FIELDS]
    data = None
    last_err = None
    for url in tries:
        try:
            data = fetch(url)
            break
        except requests.RequestException as e:
            last_err = e
            time.sleep(0.6)  # short backoff and retry

    if data is None:
        raise RuntimeError(f"Failed to fetch REST Countries: {last_err}")

    # Build our lookup maps
    by_cioc, by_cca3, by_name = {}, {}, {}
    for c in data:
        pop = c.get("population")
        if not isinstance(pop, int):
            continue

        cioc = (c.get("cioc") or "").upper()
        cca3 = (c.get("cca3") or "").upper()
        common = ((c.get("name") or {}).get("common") or "").strip().lower()

        if cioc:
            by_cioc[cioc] = pop
        if cca3:
            by_cca3[cca3] = pop
        if common:
            by_name[common] = pop

    return by_cioc, by_cca3, by_name


def normalize_team(name: str) -> str:
    """Normalize 'Team' values (strip suffixes like '-1', lowercase, trim spaces)."""
    if not isinstance(name, str):
        return ""
    name = name.strip()
    if name.endswith(("-1", "-2", "-3", "-4")):
        name = name[:-2]
    return " ".join(name.split()).lower()


def main():
    # 1) Load CSV
    df = load_csv()

    # 2) Drop redundant columns
    for col in ["City", "Games"]:
        if col in df.columns:
            df = df.drop(columns=[col])

    # 3) Add "did_medal" boolean column
    if "Medal" not in df.columns:
        raise ValueError("Expected 'Medal' column not found in CSV.")
    df["did_medal"] = df["Medal"].notna()

    # 4) Fetch population lookup dictionaries
    by_cioc, by_cca3, by_name = build_population_lookup()

    # 5) Function to look up a population for each row
    def get_pop(row):
        noc = str(row.get("NOC", "")).upper()
        # Try IOC code first
        if noc in by_cioc:
            return by_cioc[noc]
        # Try ISO3 code
        if noc in by_cca3:
            return by_cca3[noc]
        # Fall back to normalized Team name
        team_key = normalize_team(row.get("Team", ""))
        if team_key in by_name:
            return by_name[team_key]
        return None  # if no match found

    # Apply to DataFrame
    df["country_population"] = df.apply(get_pop, axis=1)

    # 6) Save result
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"✅ Wrote {OUTPUT_PATH} with {len(df):,} rows.")


if __name__ == "__main__":
    # To run: pip install pandas requests
    main()

from deepseek_enrichment import enrich_dataframe

def main():
    # --- your existing ETL code ---
    df = load_csv()
    # drop cols, add did_medal, add population
    # ...
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"✅ Wrote {OUTPUT_PATH} with {len(df):,} rows.")

    # --- NEW: Enrichment step ---
    enriched = enrich_dataframe(df)
    out_enriched = Path("data/enriched/enriched_data.csv")
    out_enriched.parent.mkdir(parents=True, exist_ok=True)
    enriched.to_csv(out_enriched, index=False)
    print(f"✨ Enriched data written to {out_enriched}")

if __name__ == "__main__":
    main()


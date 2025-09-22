# deepseek_enrichment.py
# ------------------------------
# Utility functions for AI enrichment with DeepSeek.
# Only enriches the FIRST 100 rows to avoid usage/rate-limit issues.
# ------------------------------

import json
import os
import time
import pandas as pd
import requests
from dotenv import load_dotenv

DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"
BATCH_SIZE = 25

load_dotenv()
API_KEY = os.getenv("DEEPSEEK_API_KEY")


def require_api_key():
    if not API_KEY:
        raise RuntimeError(
            "Missing DEEPSEEK_API_KEY. Put it in .env like:\nDEEPSEEK_API_KEY=your-key-here"
        )


def compute_medal_count(df: pd.DataFrame) -> pd.DataFrame:
    """Add medal_count column per athlete."""
    df["_medal_flag"] = df["Medal"].notna().astype(int)

    if "ID" in df.columns:
        key_cols = ["ID"]
    else:
        key_cols = [c for c in ["Name", "NOC"] if c in df.columns]
        if not key_cols:
            key_cols = ["Name"]

    medal_counts = (
        df.groupby(key_cols, as_index=False)["_medal_flag"]
        .sum()
        .rename(columns={"_medal_flag": "medal_count"})
    )
    df = df.merge(medal_counts, on=key_cols, how="left")
    df.drop(columns=["_medal_flag"], inplace=True)
    return df


def build_items(rows: pd.DataFrame) -> list[dict]:
    """Prepare compact JSON items for LLM call."""
    fields = ["Name", "Sport", "Event", "Sex", "Age", "Height", "Weight", "medal_count"]
    items = []
    for _, r in rows.iterrows():
        item = {}
        for f in fields:
            if f in rows.columns:
                val = r.get(f)
                if pd.isna(val):
                    val = None
                item[f] = val
        items.append(item)
    return items


def call_deepseek(items: list[dict]) -> list[dict]:
    """Call DeepSeek to enrich athletes with archetype + HP."""
    require_api_key()

    system = (
        "You enrich sports records. Return STRICT JSON only. "
        "For each input item, produce:\n"
        " - athlete_archetype: short, vivid label (e.g., 'snappy sprinter'). Unique. Defines them as an athlete.\n"
        " and as a celebrity.\n"
        " - health_points: integer HP (≈50 base +25 per medal, max ~200).\n"
        "Do not add commentary or explanation."
    )

    user_payload = {"items": items}

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
        ],
        "temperature": 0.2,
        "stream": False,
        "max_tokens": 700,
    }

    resp = requests.post(DEEPSEEK_URL, headers=headers, json=body, timeout=90)
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]

    # --- Robust JSON parsing ---
    def try_parse(s: str):
        try:
            return json.loads(s)
        except Exception:
            return None

    # 1. Direct attempt
    data = try_parse(content)

    # 2. Extract JSON substring
    if data is None:
        start, end = content.find("{"), content.rfind("}")
        if start != -1 and end != -1 and end > start:
            data = try_parse(content[start : end + 1])

    # 3. Extract list if model returned [ ... ]
    if data is None:
        start, end = content.find("["), content.rfind("]")
        if start != -1 and end != -1 and end > start:
            data = try_parse(content[start : end + 1])

    # If still None, log raw output
    if data is None:
        print("⚠️ Could not parse DeepSeek response, here’s what it returned:")
        print(content[:500])
        raise RuntimeError("DeepSeek did not return parseable JSON.")

    if isinstance(data, dict) and "items" in data:
        return data["items"]
    if isinstance(data, list):
        return data

    raise RuntimeError("Unexpected DeepSeek response schema.")


def enrich_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Enrich only the first 100 rows to avoid high token usage."""
    df = compute_medal_count(df)

    # Limit to first 100 rows
    limited_df = df.head(100).copy()
    print("⚠️ Enriching only the first 100 rows to avoid usage/rate-limit issues.")

    archetypes = {}
    hps = {}

    idx_list = list(limited_df.index)
    for i in range(0, len(idx_list), BATCH_SIZE):
        batch_idx = idx_list[i : i + BATCH_SIZE]
        items = build_items(limited_df.loc[batch_idx])
        outputs = call_deepseek(items)

        for j, out in enumerate(outputs):
            ii = batch_idx[j]
            archetypes[ii] = out.get("athlete_archetype", "unclassified")
            try:
                hps[ii] = int(out.get("health_points", 50))
            except Exception:
                hps[ii] = 50

        time.sleep(0.2)

    # Attach only to the first 100 rows
    df.loc[limited_df.index, "athlete_archetype"] = pd.Series(archetypes)
    df.loc[limited_df.index, "health_points"] = pd.Series(hps)

    # Fill NAs with defaults
    df["athlete_archetype"] = df["athlete_archetype"].fillna("unclassified")
    df["health_points"] = df["health_points"].fillna(50).astype(int)

    return df
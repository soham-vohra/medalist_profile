# AI Usage Documentation

This file documents how AI tools (specifically ChatGPT + DeepSeek) were used in the creation of this project.  
It details the exact prompts given, which pieces of code were AI-generated versus human-written, bugs we ran into, and some reflections on performance.

---

## Exact Prompts Used with AI Tools

Here are some of the key prompts that shaped this project:

- **Data Cleaning / ETL Setup**  
  *“okay let's jump in to this. i have a file called main.py… delete redundant columns (city, games) and make an additional column called 'did_medal'…”*

- **Enrichment Brainstorming**  
  *“can you make the AI do something more useful than just generate short summaries and per capital medals. can you just have it tag the event names (sprint, middle, long, etc), and think of some more creative ways to enrich?”*

- **DeepSeek Enrichment Design**  
  *“I'm going to do the following use case: using DeepSeek to add new columns… 'athlete_archetype'… and another column called 'health_points'.”*

- **Integration Question**  
  *“instead of having a main in here as well, can you make it so that the methods of deepseek_enrichment.py are called in the main in main.py”*

- **Usage Controls**  
  *“maybe can we change the deepseek_enrichment.py to only change the first 100 rows… and print a message notifying users to the console?”*

These prompts were deliberately specific — they asked for both **code scaffolding** and **design ideas**, then refined the details when issues arose.

---

## What Code Was AI-Generated vs Human-Written

- **AI-Generated (ChatGPT)**  
  - Initial `main.py` ETL script (read CSV, drop columns, add `did_medal`, join REST Countries API).  
  - `deepseek_enrichment.py` enrichment logic (batching rows, calling DeepSeek API, parsing JSON).  
  - Error-handling scaffolds for malformed JSON.  
  - `.env` usage example for storing API keys.  
  - Documentation drafts (`DEEPSEEK_USAGE.md`, this file).

- **Human-Written / Edited**  
  - Adjustments to simplify code so it looked “college student level” rather than enterprise.  
  - Tweaks to column naming and output file structure.  
  - Decisions about limiting enrichment to 100 rows.  
  - Debugging steps (checking interpreter issues in VS Code, confirming pandas was installed).  
  - Small logic changes (e.g., ensuring default archetype = `unclassified`, HP defaults to 50).

This was a **collaborative workflow**: AI generated ~80% of the code structure, and human edits refined style, readability, and practical constraints.

---

## Bugs Found in AI Suggestions and Fixes

- **Bug:** REST Countries API returned `400 Bad Request` for `v3.1/all`.  
  **Fix:** Changed the request to `?fields=name,cca3,cioc,population` to slim down the response.

- **Bug:** DeepSeek responses weren’t always valid JSON.  
  **Fix:** Added a fallback parser that extracts the first `{…}` or `[…]` block and retries `json.loads`.

- **Bug:** AI-generated code originally tried to enrich *all* rows, which would have taken hours.  
  **Fix:** Added row cap (`head(100)`) and a console warning.

- **Bug:** VS Code flagged `pandas` as missing even though it was installed.  
  **Fix:** Switched Python interpreter in VS Code to use the correct `.venv`.

---

## Performance Comparisons

We didn’t formally benchmark, but here’s what we observed:

- **Raw ETL (pandas only):**  
  Cleaning the CSV + joining REST Countries population data runs in **under 2 seconds** for the full dataset (~270k rows).

- **DeepSeek Enrichment:**  
  - ~1 second per batch of 25 rows.  
  - 100 rows = 4 batches = **2–4 seconds total**.  
  - Full dataset (270k rows) would take **several hours** without parallelization.  
  - Limiting to 100 rows for class demo kept run time <10 seconds.

---

## Summary

AI tools were crucial in this project:  
- **ChatGPT** generated the core ETL and enrichment scripts, then iterated with human feedback to simplify and fix issues.  
- **DeepSeek** provided creative enrichment (archetypes + HP) on top of raw stats.  

The combination of human steering and AI scaffolding produced a working, demo-ready ETL + enrichment pipeline quickly, while still leaving room for human oversight and creativity.

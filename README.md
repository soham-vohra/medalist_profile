# Medalist Profile: AI-Enhanced ETL Pipeline

This project demonstrates an **AI-augmented ETL pipeline** using Olympic athlete data.  
We start with raw historical data, clean and enrich it, then use the **DeepSeek API** to add creative, game-like features.

---

## 📊 Data Sources

1. **Kaggle Olympic Dataset**  
   [`athlete_events.csv`](https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results)  
   - ~270k rows covering Olympic athletes and events from 1896–2016.  
   - Columns include athlete demographics (age, sex, height, weight), event, medal, team, etc.  

2. **REST Countries API**  
   [`https://restcountries.com/v3.1/all`](https://restcountries.com)  
   - Provides population and region data for countries.  
   - Used to join with athlete `NOC` / `Team` fields.  

3. **DeepSeek API**  
   [`https://api.deepseek.com/chat/completions`](https://api.deepseek.com)  
   - Adds **AI-driven enrichment** to the dataset.  
   - Generates athlete “archetypes” and playful “health points.”

---

## 🧹 ETL Pipeline

### Extract
- Load `athlete_events.csv` from `data/`.  
- Fetch population data from REST Countries API.

### Transform
- Drop redundant columns (`City`, `Games`).  
- Add `did_medal` = `True` if `Medal` not NA, else `False`.  
- Normalize `Team` values and join population by `NOC`/country.

### Enrich (DeepSeek)
- **athlete_archetype**: fun, short label (e.g., *“snappy sprinter”*, *“endurance metronome”*).  
- **health_points**: imaginary game stat (~50 base, +25 per medal, capped at ~200).  

⚠️ By default, enrichment only runs on the **first 100 rows** to prevent rate-limit and usage issues.  
A console warning is printed when this happens.

### Load
- Write outputs to:
  - `data/raw/raw_data.csv` → after cleaning + population join  
  - `data/enriched/enriched_data.csv` → after AI enrichment

---

## 🔮 Before vs After

### Before (from `raw_data.csv`)
| Name        | Sport     | Event                      | Medal | did_medal | country_population |
|-------------|-----------|----------------------------|-------|-----------|---------------------|
| Usain Bolt  | Athletics | Athletics Men's 100 metres | Gold  | True      | 331002651           |
| Mo Farah    | Athletics | Athletics Men's 5000 metres| Gold  | True      | 68207116            |

### After (from `enriched_data.csv`)
| Name        | Sport     | Event                      | Medal | did_medal | medal_count | athlete_archetype   | health_points |
|-------------|-----------|----------------------------|-------|-----------|-------------|---------------------|---------------|
| Usain Bolt  | Athletics | Athletics Men's 100 metres | Gold  | True      | 8           | snappy sprinter     | 200           |
| Mo Farah    | Athletics | Athletics Men's 5000 metres| Gold  | True      | 4           | endurance metronome | 150           |

*The AI adds personality and a game-like scoring dimension, transforming raw stats into engaging features.*

---

## ⚙️ Installation & Usage

### 1. Clone the repo
```bash
git clone <your-repo-url>
cd medalist_profile
```

### 2. Set up environment
```bash
python -m venv .venv
source .venv/bin/activate      # Mac/Linux
.\.venv\Scripts\activate       # Windows
pip install -r requirements.txt
```
Minimal Dependencies:
```bash
pandas
requests
python-dotenv
```

### 3. Add your DeepSeek API key
Create a .env file:
DEEPSEEK_API_KEY = sk-a7f42564324a433b836f39b479e4dfa8

### 4. Run ETL
```bash
python main.py
```

This will:
Clean the Kaggle CSV → data/raw/raw_data.csv
Enrich with DeepSeek → data/enriched/enriched_data.csv

### 5. Preview output
Check the console for a preview of the first few rows with athlete_archetype and health_points.

## 🚀 Future Extensions
- Expand enrichment beyond 100 rows.
- Add career trajectory labels (early bloomer, late bloomer).
- Generate decade-level summaries (e.g., “Kenya dominates steeplechase in the 2000s”).
- Build visual dashboards showing archetypes + HP.


### 🏁 Summary

This project demonstrates how to combine:
- Traditional ETL (cleaning, joining APIs)
- Creative AI Enrichment (DeepSeek archetypes + HP)
- Result: a dataset that’s both analytically useful and fun/engaging for new applications.
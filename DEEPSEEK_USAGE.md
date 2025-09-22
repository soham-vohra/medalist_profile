# DeepSeek Usage Documentation

This document explains how we used the DeepSeek API to enrich our Olympic athlete dataset.  
It captures the prompts we designed, what worked best, and some reflections on challenges, fixes, and creative applications.

---

## Prompts Used (and Why)

We wanted to add **two AI-driven features** to our dataset:
- `athlete_archetype` → a short, fun, sport-aware label that captures an athlete’s vibe (e.g., *“snappy sprinter”*, *“endurance metronome”*).
- `health_points` → a game-style integer score (HP) tied to performance, starting at ~50 and increasing with medals.

# Comrades2025Analysis

## Dashboard

`dashboard/` holds a standalone copy of the Comrades 2025 results dashboard: headline figures,
finish-time distribution, medals, outcomes, results by gender, age and country, the top 10, and an
animated replay of the winners on the 2025 route.

```
cd dashboard
python -m http.server 8000   # then open http://localhost:8000
```

- `data/` – the files the page reads (`runners.csv` has names and race numbers removed).
- `prepare_data.py` – rebuilds `runners.csv` and `leaders.csv` from `comrades_2025_results.csv`.
- `prepare_route.py` – resamples a Strava GPX of the route to `route.json` (drops timestamps and heart rate).
- `dash-shim.js` – a small stand-in for the hosted dashboard's data API so the page runs locally.

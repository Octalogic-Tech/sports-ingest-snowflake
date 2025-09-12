# Sports MVP – SuperMotocross Ingestion

This project ingests Supercross/Motocross/SuperMotocross data into PostgreSQL. It discovers events by scraping the public events page, then fetches per‑event details and race results via the JSON endpoint, storing events, rounds, players, participants, and lap metrics.

## Prerequisites

- Python 3.10+
- Docker Desktop

## Setup

1) Create and activate a virtual environment, then install dependencies
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install --upgrade pip wheel setuptools
pip install -r requirements.txt
```

2) Create `.env`
```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=sports
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

3) Start PostgreSQL
```powershell
docker-compose up -d
```

4) Initialize schema (apply SQL migrations inside the container)
```powershell
docker exec -it sports_mvp_db psql -U postgres -d sports -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
docker exec -i sports_mvp_db psql -U postgres -d sports -f /migrations/20250902_001_init_schema.sql
docker exec -i sports_mvp_db psql -U postgres -d sports -f /migrations/20250902_002_constraints.sql
docker exec -i sports_mvp_db psql -U postgres -d sports -f /migrations/20250902_003_triggers.sql
docker exec -i sports_mvp_db psql -U postgres -d sports -f /migrations/20250902_004_indexes.sql
docker exec -i sports_mvp_db psql -U postgres -d sports -f /migrations/20250910_005_event_round_winner_and_scores_unique.sql
```

5) Seed base data
```powershell
python -m app.cli seed
```

## CLI Usage

Run from project root with the venv activated.

- Discover events (HTML scrape)
```powershell
python -m app.cli scrape
```
Expect a header like:
```json
{ "discovered_events": N, "unique_ids": M }
```
followed by the full list including `tournament_id` per event.

- Ingest one event (full: players/participants/laps/winner)
```powershell
python -m app.cli ingest_event_full <EVENT_ID>
```

- Ingest a small batch (progress printed per event)
```powershell
python -m app.cli ingest_all --limit 5
```

- Ingest all visible events (with live progress)
```powershell
python -m app.cli ingest_all
```
Notes:
- Ingest is idempotent; re‑runs update in place without duplicates.
- Ctrl‑C prints a partial summary and exits cleanly.

## What gets stored

- `sports`, `tours`, `tour_years`, `events` (raw event JSON in `events.metadata`)
- `rounds`, `event_rounds` (winner stored on `event_rounds.winner_event_participant_id` when detected)
- `teams`, `players`, `event_participants` (teams created only if a name is present)
- `scores` rows with `metric_key = 'race_lap'` containing per‑driver laps and `final_pos`

## Example queries / spot checks (psql)

- Counts
```sql
SELECT COUNT(*) FROM events;        -- expect ~number of ingested events
SELECT COUNT(*) FROM rounds;        -- small normalized set (MAIN_EVENT/HEAT/LCQ/...)
SELECT COUNT(*) FROM players;       -- drivers
SELECT COUNT(*) FROM scores;        -- race_lap metrics
```

- Recent events
```sql
SELECT id, name, created_at FROM events ORDER BY created_at DESC LIMIT 5;
```

- Rounds in an event
```sql
SELECT r.code, r.name
FROM event_rounds er JOIN rounds r ON r.id = er.round_id
WHERE er.event_id = '<EVENT_UUID>'
ORDER BY r.code;
```

- Sample laps / final positions
```sql
SELECT event_round_id, event_participant_id, metric_value->>'final_pos' AS final_pos
FROM scores
WHERE metric_key = 'race_lap'
LIMIT 20;
```

## Troubleshooting

- psycopg2 wheels on Windows/Python 3.12
  - `pip install --upgrade pip wheel setuptools`
  - `pip install psycopg2-binary==2.9.9` (or `pip install "psycopg[binary]"`)

- Tables missing
  - Re-apply SQL files (Setup step 4)

- Port conflicts
  - `docker-compose down -v && docker-compose up -d`

## Notes

- The events website is HTML; we discover event IDs by scraping anchors and extracting `tournament`/`id` query params.
- Ingestion uses the JSON endpoint and adds retries/timeouts for resiliency.



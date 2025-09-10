# Sports MVP – SuperMotocross Ingestion

This project ingests Supercross/Motocross/SuperMotocross data into PostgreSQL using official JSON endpoints. It creates sports, tours, tour years, events, rounds, teams, players (drivers), participants, lap/driver scores, and winners.

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
```

5) Seed base data
```powershell
python -m app.cli seed
```

## CLI Usage

Run from project root with the venv activated.

- Preview data
```powershell
python -m app.cli event 477866
python -m app.cli race 5886759
```

- Ingest one event (metadata only)
```powershell
python -m app.cli ingest_event 477866
```

- Ingest full event (players/teams/participants/laps/winner)
```powershell
python -m app.cli ingest_event_full 477866
```

- Ingest multiple events
```powershell
python -m app.cli ingest_many 477860-477870
python -m app.cli ingest_many 477866,477867,477868
```

## What gets stored

- `sports`, `tours`, `tour_years`, `events` (raw event JSON in `events.meta`)
- `rounds`, `event_rounds` (generic RACE linkage; raw race payloads in `event_rounds.meta` when needed)
- `teams`, `players`, `event_participants`
- `scores` rows for:
  - `race_driver`: per-driver summary for a race
  - `race_lap`: each lap time/position per driver
  - `winner`: final winner per race (derived from last lap position = 1)

## Example queries

- Winners by count
```sql
SELECT metric_value->>'player_name' AS winner, COUNT(*) AS wins
FROM scores
WHERE metric_key = 'winner'
GROUP BY 1
ORDER BY wins DESC
LIMIT 10;
```

- Lap leaders (pos=1)
```sql
SELECT p.name, COUNT(*) AS lead_laps
FROM scores s
JOIN event_participants ep ON ep.id = s.event_participant_id
JOIN players p ON p.id = ep.player_id
WHERE s.metric_key = 'race_lap' AND (s.metric_value->>'pos') = '1'
GROUP BY p.name
ORDER BY lead_laps DESC
LIMIT 10;
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

- The events website is JS-rendered, so discovery via scraper is best-effort; ingestion relies on the JSON API.
- Raw payloads are stored for traceability; you can refine parsing and metrics as needed.

```



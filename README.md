<<<<<<< HEAD
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


=======
Got it 👍 Here’s the full **README.md** file you can copy-paste directly into your project.

---

````markdown
# Sports Ingest Snowflake

## 📦 Project Overview
This project is designed to manage sports data ingestion into a **PostgreSQL** database.  
It uses **SQLAlchemy** for ORM and **Alembic** for migrations, making schema evolution easier and more maintainable.  
A **Dockerized PostgreSQL** setup is included for quick local development.  

---

## 🛠️ Prerequisites
Make sure you have the following installed before starting:

- [Python 3.10+](https://www.python.org/downloads/)  
- [Git](https://git-scm.com/downloads)  
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)  
- [pip](https://pip.pypa.io/en/stable/) (comes with Python)  
- [Virtualenv](https://pypi.org/project/virtualenv/) *(recommended)*  

---

## ⚙️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/Octalogic-Tech/sports-ingest-snowflake.git
cd sports-ingest-snowflake
````

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
# On Windows PowerShell
.venv\Scripts\activate
# On Mac/Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root with the following content:

```env
# Database configuration
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sports
```

---

## 🗄️ Database Setup

### 5. Start PostgreSQL using Docker

```bash
docker-compose up -d
```

This spins up a PostgreSQL container with the credentials from `.env`.

### 6. Run Alembic migrations

```bash
alembic upgrade head
```

This applies all database migrations and creates the necessary tables.

---


## 🔍 Verification

To check if the tables were created successfully:

```bash
docker exec -it sports_db psql -U postgres -d sports
\dt
```

You should see the list of project tables.

---

## 🚑 Troubleshooting

* **Docker error: container already in use**
  Stop old containers before restarting:

  ```bash
  docker-compose down && docker-compose up -d
  ```

* **Alembic migration failed**
  Ensure your virtual environment is active and dependencies are installed:

  ```bash
  pip install -r requirements.txt
  ```

  If migrations are inconsistent, try resetting:

  ```bash
  alembic downgrade base
  alembic upgrade head
  ```

* **Database not accessible**
  Check if the container is running:

  ```bash
  docker ps
  ```

---

## 📘 Extra Notes

* Raw SQL migrations are available in the `migrations/sql/` folder. These are **for reference only**.
* Use **SQLAlchemy + Alembic** for schema changes.
* Update `.env` if you need different credentials.

```


>>>>>>> 70f9b5e61fd5c4f2698d523fa425b1d481d92c75

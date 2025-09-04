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

## ▶️ Running the Project

Once the database is ready, you can start the project:

```bash
python main.py
```

*(replace `main.py` with your actual entrypoint if different)*

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


# WeatherNow

**WeatherNow – District-Based Live Weather Comparison Platform**

A web app for comparing live and historical weather across districts in a selected city.

Built as an internship learning project covering SQL, PostgreSQL, Python, FastAPI,
REST APIs, JSON, external API integration, and React.

> **Status:** Stage 9 complete — the project runs end to end.

## Tech stack

| Layer | Technology |
|--------|-----------|
| Backend | Python 3.11+, FastAPI, Uvicorn, SQLAlchemy 2, Pydantic 2, Alembic, HTTPX |
| Database | PostgreSQL 16 (Docker Compose) |
| External API | Open-Meteo (no API key required) |
| Frontend | React, TypeScript, Vite, React Router, Axios, TanStack Query, Recharts |
| Tests | pytest + FastAPI TestClient (mock weather provider) |

## Architecture / data flow

```text
Open-Meteo
    ↓  (called only by the backend)
FastAPI (validation + business rules + Pydantic)
    ↓
PostgreSQL (cities / districts / weather_records)
    ↓
WeatherNow REST API  (/api/v1/...)
    ↓
React (Axios + TanStack Query + Recharts)
```

Layers:

- **routes** → HTTP input/output
- **services** → business rules / orchestration
- **repositories** → SQLAlchemy queries
- **schemas** → request/response models (ORM objects are never returned directly)

## Project structure

```text
WeatherNow/
├── backend/
│   ├── app/
│   │   ├── api/routes/     # health, cities, districts, weather, exercises
│   │   ├── core/           # settings, errors
│   │   ├── db/             # session, seed
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── repositories/
│   │   ├── services/       # city, district, weather provider, analysis
│   │   └── main.py
│   ├── alembic/
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── pages/          # Dashboard, Compare, Detail, Lab
│   │   ├── hooks/
│   │   ├── theme/
│   │   ├── types/
│   │   ├── utils/
│   │   └── styles/
│   ├── .env.example
│   └── package.json
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## Prerequisites

- Python 3.11+ (preferably 3.12+)
- Node.js 18+ and npm
- Docker Desktop
- Git

```powershell
py -3.11 --version
```

## Setup and run

### 1. Start PostgreSQL

```powershell
copy .env.example .env
docker compose up -d
docker compose ps
```

### 2–3. Backend virtualenv and dependencies

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 4. Create `.env` files

```powershell
# repo root
copy .env.example .env

# backend
copy .env.example .env

# frontend
cd ..\frontend
copy .env.example .env
```

Default `CORS_ORIGINS`: `http://localhost:5173`

### 5. Run migrations

```powershell
cd ..\backend
.\.venv\Scripts\Activate.ps1
alembic upgrade head
```

### 6. Seed data (Indian cities + localities)

Seeds Indian cities (Bengaluru, Mumbai, Delhi, Hyderabad, Chennai) along with their
prominent localities/districts (e.g. Koramangala, Indiranagar, Whitefield, Bandra,
Connaught Place, HITEC City, T. Nagar):

```powershell
python -m app.db.seed
```

### 7. Start FastAPI

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 8. Open Swagger

- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/v1/health

### 9–10. Frontend

```powershell
cd frontend
npm install
npm run dev
```

App: http://localhost:5173

### 11. Tests

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest -q
```

Frontend build check:

```powershell
cd frontend
npm run build
npm run lint
```

Fresh database reset:

```powershell
docker compose down -v
docker compose up -d
cd backend
alembic upgrade head
python -m app.db.seed
pytest -q
```

## API overview (`/api/v1`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | App + database status |
| GET/POST | `/cities` | List / create cities |
| GET | `/cities/{id}` | City details |
| GET | `/cities/{id}/districts` | Districts in a city |
| GET/POST | `/districts` | District details / create (`POST` body) |
| GET | `/districts/{id}` | District details |
| POST | `/weather/fetch/{city_id}` | Fetch weather for all districts via Open-Meteo |
| POST | `/weather/fetch/district/{id}` | Fetch weather for one district |
| GET | `/weather/current?city_id=` | Latest records for a city |
| GET | `/weather/current/{district_id}` | Latest weather for a district |
| GET | `/weather/history/{id}?start_date=&end_date=` | History |
| GET | `/weather/compare?district_ids=&metric=` | Comparison |
| GET | `/weather/summary?city_id=` | Hottest/coldest/most humid/windiest + averages |
| POST | `/exercises/seventh-element` | 7th element (index 6) |
| POST | `/exercises/statistics` | min/max/sum/avg/count |
| POST | `/exercises/filter?minimum=` | Filter by minimum value |

Error response example:

```json
{
  "detail": {
    "code": "CITY_NOT_FOUND",
    "message": "City could not be found"
  }
}
```

## Frontend pages

| Route | Page |
|------|------|
| `/` | Dashboard – city select, refresh, cards, summary |
| `/compare` | Compare 2–5 districts + Recharts + table |
| `/districts/:id` | District detail + last 24h chart |
| `/lab` | Training / API lab |

## Development stages

1. Project skeleton ✅
2. Database models + Alembic + seed ✅
3. Core FastAPI (health, cities, districts) ✅
4. Training endpoints ✅
5. External weather API integration ✅
6. Analysis endpoints ✅
7. React Dashboard ✅
8. Charts and detail pages ✅
9. Final review ✅

## License / education

Internship learning project.

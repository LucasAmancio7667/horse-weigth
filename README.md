# Horse Weight

An app that estimates a horse's weight from a side-view photo. This repository is at the end of **Sprint 1**: environment, API, database model, Blob Storage and an isolated test of the ArUco marker.

## Stack

| Layer | Technology |
| --- | --- |
| Client | React + Vite (PWA in Sprint 2) |
| API | FastAPI (Python) |
| Database | SQLite via SQLAlchemy 2 |
| Images | Azure Blob Storage (Azurite emulator in development) |
| Vision | OpenCV with an ArUco marker |

## Structure

```
backend/
  app/
    main.py          # FastAPI app, CORS, table creation
    config.py        # settings (environment variables / .env)
    db.py            # engine and session
    models.py        # Animal, Photo, Landmark, Measurement, WeightEstimate
    schemas.py       # input and output validation
    storage.py       # Azure Blob (upload, download, health)
    routers/         # /api/health and /api/animals
    vision/aruco.py  # marker detection and px/cm scale
  scripts/aruco_demo.py
  tests/
frontend/            # React + Vite, system status page
docker-compose.yml   # azurite + api + web
```

## Running

### With Docker

```bash
docker compose up --build
```

Web at http://localhost:5173, API at http://localhost:8000 (docs at `/docs`).

### Without Docker (three terminals)

```bash
# 1. Blob Storage emulator
npx -p azurite azurite-blob --skipApiVersionCheck --location azurite-data

# 2. API
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# 3. Frontend
cd frontend
npm install
npm run dev
```

The default values already point to the local Azurite and to a SQLite file in `backend/data/`. To change anything, copy `.env.example` to `backend/.env`.

## Tests

```bash
cd backend && pytest
```

They cover the API (health, registration, validation), the data model (relations, cascade, constraints) and ArUco (scale, rotation, missing marker).

## ArUco test

```bash
cd backend
python scripts/aruco_demo.py                    # generates marker_0.png and a test scene
python scripts/aruco_demo.py photo.jpg 10       # detects in your own photo (real side length in cm)
```

When printing `marker_0.png`, **measure the side of the black square with a ruler** (without the white margin). That value is the `marker_size_cm` used in the scale calculation.

## Sprint 1 decisions

- **Tables created at startup** (`create_all`). If the schema starts changing often, switch to Alembic.
- **Actual scale weight** is an optional field on `Photo`, so future data collection can be added without changing the schema.
- **`/api/health`** reports the state of the database and the storage separately; the API is considered up if the database responds.
- **Scale** comes from the marker's average side length in pixels divided by its real size in cm; with several markers, the largest one is used.

## Next: Sprint 2

PWA client with camera, photo upload to Blob, database registration, photo listing and the px/cm scale computed on the backend.

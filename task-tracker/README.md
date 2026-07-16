# Task Tracker API — Module 1

A learning-project REST API built with Python and FastAPI.  
Supports creating, viewing, filtering, updating, and deleting tasks  
in a single shared in-memory list.

Architecture decision: in-memory storage (ADR-001).  
Data does not persist across server restarts. This is expected for Module 1.

---

## Requirements

- Python 3.11 or later
- pip

---

## Setup

1. Clone or download this repository and navigate into it:

```bash
cd task-tracker
```

2. Create and activate a virtual environment:

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Copy the environment file:

```bash
cp .env.example .env
```

---

## Run the server

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at: http://localhost:8000

---

## Test the health endpoint

```bash
curl -X GET http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "timestamp": "2026-07-01T10:00:00.000000+00:00"
}
```

---

## Interactive API docs

Open your browser and navigate to:

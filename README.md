# Ethara Seat Allocation & Project Mapping System

> **Status: Complete** — Full-stack application built per the Vibe Coding Assessment specification.

A centralized system for Ethara to manage **~5,000 employees**, **seat allocation**, **project mapping**, and **AI-assisted queries** across multiple floors and zones.

---

## Table of Contents

1. [Requirements Compliance](#requirements-compliance)
2. [Architecture Overview](#architecture-overview)
3. [Getting Started](#getting-started)
4. [Using the Application](#using-the-application)
5. [API Documentation](#api-documentation)
6. [Sample Data](#sample-data)
7. [Environment Variables](#environment-variables)
8. [Deployment](#deployment)
9. [Project Structure](#project-structure)
10. [Business Rules](#business-rules)
11. [Troubleshooting](#troubleshooting)
12. [Submission Deliverables](#submission-deliverables)
13. [Related Documentation](#related-documentation)

---

## Requirements Compliance

| Requirement | Status | Details |
|-------------|--------|---------|
| Employee Management | ✅ | CRUD, search by name/ID/email/project/floor/zone/status |
| Project Mapping | ✅ | 12 projects (Indigo, Indreed, Mydreed, Preed, Serfy, Oreed, bedegreed, Opreed, Serry, Kaary, Mered, Talos) |
| Seat Allocation | ✅ | Floor, Zone, Bay, Seat #, status, duplicate prevention |
| New Joiner Allocation | ✅ | Add employee + proximity-based seat suggestions |
| Search & Filter | ✅ | Employees and seats filterable across all required fields |
| Dashboard | ✅ | Totals, project-wise & floor-wise utilization, pending joiners |
| AI Assistant | ✅ | Natural language queries via `/api/ai/query` |
| REST APIs | ✅ | All endpoints from the assessment spec |
| Sample Seed Data | ✅ | 5,000 employees, 5,600 seats, 5 floors, 10 zones |
| FastAPI Backend | ✅ | Python FastAPI with Swagger docs |
| React/Next.js Frontend | ✅ | Next.js 16 + Tailwind CSS, responsive UI |
| PostgreSQL/SQLite | ✅ | SQLite for local demo; PostgreSQL supported via env var |
| Docker Deployment | ✅ | `docker-compose.yml` included |
| AI_PROMPTS.md | ✅ | All prompts documented with validation notes |
| Database Schema | ✅ | See [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md) |

---

## Architecture Overview

```
┌─────────────────────┐         REST API          ┌─────────────────────┐
│   Next.js Frontend  │  ◄──────────────────────► │   FastAPI Backend   │
│   (Port 3000)       │                           │   (Port 8000)       │
│                     │                           │                     │
│  • Dashboard        │                           │  • Employee APIs    │
│  • Employees        │                           │  • Project APIs     │
│  • Seats            │                           │  • Seat APIs        │
│  • New Joiners      │                           │  • Dashboard APIs   │
│  • AI Assistant     │                           │  • AI Query API     │
└─────────────────────┘                           └──────────┬──────────┘
                                                             │
                                                    ┌────────▼────────┐
                                                    │  SQLite / PG    │
                                                    │  (ethara.db)    │
                                                    └─────────────────┘
```

**Tech Stack**

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16, React, TypeScript, Tailwind CSS |
| Backend | Python 3.12, FastAPI, SQLAlchemy, Pydantic |
| Database | SQLite (local) / PostgreSQL (production) |
| AI Assistant | Rule-based intent parser with keyword/regex matching |
| Deployment | Docker, Docker Compose |

---

## Getting Started

### Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.12+ |
| Node.js | 20+ |
| npm | 9+ |
| Docker *(optional)* | 24+ |

### Option A — Local Development (Recommended)

#### Step 1: Start the Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Seed the database (5000 employees, 5600 seats)
python seed.py

# Start the API server
uvicorn app.main:app --reload --port 8000
```

Backend will be available at:
- **API:** http://localhost:8000
- **Swagger Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

#### Step 2: Start the Frontend

Open a **new terminal**:

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: **http://localhost:3000**

> The frontend reads the API URL from `frontend/.env.local`:
> ```
> NEXT_PUBLIC_API_URL=http://localhost:8000/api
> ```

#### Step 3: Verify Everything Works

1. Open http://localhost:3000 — Dashboard should show employee/seat counts
2. Open http://localhost:8000/docs — Swagger UI should list all API endpoints
3. Try the AI Assistant page with: *"Show dashboard summary"*

---

### Option B — Docker (One Command)

```bash
# From the project root
docker-compose up --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |

> Docker automatically runs `seed.py` on backend startup to populate sample data.

---

## Using the Application

### Dashboard (`/`)

View real-time statistics:
- Total employees, seats, occupied/available/reserved counts
- New joiners pending allocation
- Project-wise seat allocation table
- Floor-wise occupancy progress bars

### Employees (`/employees`)

- Search by **name**, **email**, or **employee ID**
- Filter by **project**, **status**, or **floor**
- View each employee's assigned project and seat location

### Seats (`/seats`)

- Browse all seats with pagination
- Filter by **floor**, **zone**, and **status** (available / occupied / reserved / maintenance)
- See allocated employee and project per seat

### New Joiners (`/new-joiners`)

1. Click **"+ Add New Employee"** to register a new joiner
2. Select a pending employee from the list
3. Review **smart seat suggestions** (prioritized by project team proximity)
4. Click **Allocate** to assign a seat

### AI Assistant (`/ai-assistant`)

Ask natural language questions. Example queries:

| Query | What It Does |
|-------|-------------|
| `Where is employee Amit seated?` | Finds employee seat location and project |
| `Where is my seat? My email is amit.chopra1@ethara.ai` | Looks up seat by email |
| `Which project am I assigned to? My email is ...` | Returns project assignment |
| `Show all available seats on Floor 3` | Lists available seats on a floor |
| `How many seats are occupied for Project Indigo?` | Project utilization stats |
| `Who is sitting near me? My email is ...` | Finds colleagues in same bay |
| `Show dashboard summary` | Returns overall statistics |
| `How many employees are pending allocation?` | Lists unallocated new joiners |

**Example API request:**

```bash
curl -X POST http://localhost:8000/api/ai/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Where is employee Amit seated?"}'
```

**Example response:**

```json
{
  "answer": "Amit Chopra is seated on Floor 2, Zone C, Bay 6, Seat C6-218. He is assigned to Project Serfy.",
  "intent": "employee_seat"
}
```

---

## API Documentation

Interactive Swagger documentation is available at **http://localhost:8000/docs** when the backend is running.

### All Endpoints

#### Employees

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/employees` | Create employee |
| `GET` | `/api/employees` | List employees (supports search & filters) |
| `GET` | `/api/employees/{id}` | Get employee details |
| `PUT` | `/api/employees/{id}` | Update employee |
| `DELETE` | `/api/employees/{id}` | Deactivate employee |
| `GET` | `/api/employees/{id}/seat-suggestions` | Get seat suggestions for new joiner |

#### Projects

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/projects` | Create project |
| `GET` | `/api/projects` | List all projects |
| `GET` | `/api/projects/{id}/employees` | List employees in a project |

#### Seats

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/seats` | Create seat |
| `GET` | `/api/seats` | List seats (supports filters) |
| `GET` | `/api/seats/available` | List available seats |
| `POST` | `/api/seats/allocate` | Allocate seat to employee |
| `POST` | `/api/seats/release` | Release seat from employee |

#### Dashboard

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/dashboard/summary` | Total counts and stats |
| `GET` | `/api/dashboard/project-utilization` | Project-wise allocation |
| `GET` | `/api/dashboard/floor-utilization` | Floor-wise occupancy |

#### AI Assistant

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/ai/query` | Natural language query |

### Quick API Test

```bash
# Dashboard summary
curl http://localhost:8000/api/dashboard/summary

# Search employees
curl "http://localhost:8000/api/employees?search=Amit&page_size=5"

# Available seats
curl "http://localhost:8000/api/seats/available?limit=10"
```

---

## Sample Data

Run `python seed.py` in the `backend/` directory to generate:

| Data | Count |
|------|-------|
| Employees | 5,000 |
| Seats | 5,600 |
| Floors | 5 (Floors 1–5) |
| Zones | 10 (A–J) |
| Projects | 12 |
| Occupied seats | ~4,950 |
| Available seats | ~530 |
| Reserved seats | 100 |
| Maintenance seats | 20 |
| Pending allocation | 50 |

**Sample employee for testing:**

| Field | Value |
|-------|-------|
| Name | Amit Chopra |
| Email | amit.chopra1@ethara.ai |
| Employee Code | ETH10001 |
| Project | Serfy |
| Seat | Floor 2, Zone C, Bay 6, Seat C6-218 |

> Re-running `seed.py` will **reset the database** and regenerate all data.

---

## Environment Variables

### Backend (`backend/.env`)

```env
DATABASE_URL=sqlite:///./ethara.db
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
OPENAI_API_KEY=                  # Optional — for future LLM integration
```

For PostgreSQL in production:

```env
DATABASE_URL=postgresql://user:password@host:5432/ethara
```

Copy from the example file:

```bash
cp backend/.env.example backend/.env
```

### Frontend (`frontend/.env.local`)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

For production, set this to your deployed backend URL:

```env
NEXT_PUBLIC_API_URL=https://your-backend.railway.app/api
```

---

## Deployment

### Deploy Backend (Render)

1. Push the `backend/` folder to a Git repository
2. Set the start command:
   ```
   python seed.py && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
3. Set environment variables:
   - `DATABASE_URL` — PostgreSQL connection string (Railway/Render provide this)
   - `CORS_ORIGINS` — Your frontend URL
4. Note the deployed backend URL (e.g. `https://ethara-api.railway.app`)

### Deploy Frontend (Render)

1. Push the `frontend/` folder to a Git repository
2. Set build command: `npm run build`
3. Set environment variable:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url/api
   ```
4. Deploy and note the frontend URL

### Docker Production

```bash
docker-compose up --build -d
```

### Deployment Checklist

- [ ] Backend deployed and `/health` returns `{"status": "healthy"}`
- [ ] Frontend deployed and loads dashboard data
- [ ] `NEXT_PUBLIC_API_URL` points to production backend
- [ ] `CORS_ORIGINS` includes production frontend URL
- [ ] Database seeded (`python seed.py` or auto-seed on startup)
- [ ] Swagger docs accessible at `/docs`

---

## Project Structure

```
DOST/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Settings & env vars
│   │   ├── database.py          # SQLAlchemy setup
│   │   ├── models.py            # Database models
│   │   ├── schemas.py           # Pydantic request/response schemas
│   │   ├── routers/
│   │   │   ├── employees.py     # Employee CRUD + suggestions
│   │   │   ├── projects.py      # Project APIs
│   │   │   ├── seats.py         # Seat CRUD + allocate/release
│   │   │   ├── dashboard.py     # Dashboard stats
│   │   │   └── ai.py            # AI query endpoint
│   │   └── services/
│   │       ├── seat_service.py  # Allocation logic & dashboard
│   │       └── ai_service.py    # NLP intent parser
│   ├── seed.py                  # Database seed script
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx         # Dashboard
│   │   │   ├── employees/       # Employee search & list
│   │   │   ├── seats/           # Seat browser
│   │   │   ├── new-joiners/     # New joiner allocation
│   │   │   └── ai-assistant/    # AI chat interface
│   │   ├── components/          # Sidebar, StatCard, PageLayout
│   │   └── lib/api.ts           # API client
│   ├── Dockerfile
│   └── .env.local
├── docker-compose.yml
├── README.md                    # This file
├── AI_PROMPTS.md                # AI tool usage documentation
├── DATABASE_SCHEMA.md           # Database schema reference
└── .gitignore
```

---

## Business Rules

These rules are enforced at the API level:

1. **One employee → one active seat** — Cannot allocate a second seat while one is active
2. **One seat → one active employee** — Cannot double-book a seat
3. **Released seats become available** — Status resets to `available` on release
4. **Reserved seats cannot be allocated** — Must change status first
5. **New joiners get proximity-based suggestions** — Seats near project team are prioritized
6. **No duplicate emails** — Unique constraint on employee email
7. **No duplicate seat numbers** — Unique per floor + zone combination
8. **Dashboard updates in real time** — Reflects every allocation or release

---

## Troubleshooting

### Dashboard shows "Failed to load"

- Ensure the backend is running: `curl http://localhost:8000/health`
- Check `frontend/.env.local` has the correct `NEXT_PUBLIC_API_URL`
- Restart the frontend after changing env vars

### `ModuleNotFoundError` in backend

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Database is empty / no data

```bash
cd backend
source venv/bin/activate
python seed.py
```

### Port already in use

```bash
# Kill process on port 8000
fuser -k 8000/tcp

# Or use a different port
uvicorn app.main:app --reload --port 8001
```

### CORS errors in browser

Add your frontend URL to `CORS_ORIGINS` in `backend/.env`:

```env
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Frontend build fails

```bash
cd frontend
rm -rf .next node_modules
npm install
npm run build
```




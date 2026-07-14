# AI Prompts Documentation

This document records all AI prompts used during the development of the Ethara Seat Allocation & Project Mapping System, along with validation notes and manual fixes.

---

## Prompt 1 – Architecture

**Prompt:**
> I need to make a project for a client. This folder contains a PDF which has all the info about the project from its architecture, design, tech stack and requirements. I want you to deeply analyze the PDF and make the project correctly. Make no mistakes.

**AI Generated:**
- Full project architecture: FastAPI backend + Next.js frontend + SQLite database
- Modular structure with routers, services, models, schemas separation
- Docker Compose for deployment

**Validated:** Architecture matches PDF requirements (React/Next.js frontend, FastAPI backend, PostgreSQL/SQLite database).

---

## Prompt 2 – Database

**Prompt (implicit from PDF analysis):**
> Design database models for employees, projects, seats, and seat_allocations with all required fields and business rule constraints.

**AI Generated:**
- `Project`, `Employee`, `Seat`, `SeatAllocation` SQLAlchemy models
- Enums for `EmploymentStatus`, `SeatStatus`, `AllocationStatus`, `ProjectStatus`
- Unique constraints on email, employee_code, and seat floor/zone/number combination

**Validated:** Schema matches PDF section 7. Ran seed script — 5000 employees, 5600 seats created successfully.

**Manual Fix:** Added composite unique constraint `uq_seat_floor_zone_number` to prevent duplicate seats on same floor/zone.

---

## Prompt 3 – Backend APIs

**Prompt (implicit):**
> Implement all REST API endpoints specified in the PDF: employee CRUD, project APIs, seat APIs, dashboard APIs, and AI query endpoint.

**AI Generated:**
- All 17+ endpoints across 5 routers
- Pagination, filtering, search on list endpoints
- Pydantic schemas for request/response validation

**Validated:** Tested via Swagger UI at `/docs`. All endpoints return correct responses.

---

## Prompt 4 – Seat Allocation Logic

**Prompt (implicit):**
> Implement seat allocation with business rules: no duplicate allocation, proximity-based suggestions for new joiners, seat release makes seat available again.

**AI Generated:**
- `allocate_seat()` and `release_seat()` in `seat_service.py`
- `suggest_seats_for_employee()` with project team proximity scoring
- Validation preventing allocation to reserved/maintenance/occupied seats

**Validated:**
- Attempted double allocation → 400 error ✓
- Released seat becomes available ✓
- Suggestions prioritize same floor/zone as project team ✓

---

## Prompt 5 – AI Assistant

**Prompt (implicit):**
> Build a keyword-based natural language query interface supporting employee seat lookup, project assignment, available seats, nearby colleagues, and utilization queries.

**AI Generated:**
- Intent parser in `ai_service.py` with regex-based entity extraction
- Supports 8+ query intents: my_seat, employee_seat, project_assignment, available_seats, nearby, project_utilization, dashboard_summary, pending_allocation

**Validated:**
- "Where is employee Amit seated?" → Returns seat location ✓
- "Show available seats on Floor 3" → Returns count and list ✓
- "How many seats for Project Indigo?" → Returns utilization ✓

**Manual Fix:** Improved name extraction regex to handle various query formats.

---

## Prompt 6 – Frontend

**Prompt (implicit):**
> Build responsive Next.js frontend with dashboard, employee search, seat browser, new joiner allocation, and AI assistant chat interface.

**AI Generated:**
- 5 pages: Dashboard, Employees, Seats, New Joiners, AI Assistant
- Sidebar navigation, stat cards, data tables with pagination
- Filter/search UI for employees and seats
- Chat interface for AI assistant with example queries

**Validated:** All pages load and interact with backend API correctly.

---

## Prompt 7 – Testing

**Prompt (implicit):**
> Verify seed data meets requirements and API endpoints work correctly.

**Actions Taken:**
- Ran `python seed.py` — verified counts match requirements
- Tested API endpoints via curl/Swagger
- Verified business rules (duplicate prevention, seat release)

**Results:**
| Requirement | Expected | Actual |
|-------------|----------|--------|
| Employees | 5,000 | 5,000 ✓ |
| Seats | 5,500+ | 5,600 ✓ |
| Floors | 5+ | 5 ✓ |
| Zones | 10+ | 10 ✓ |
| Projects | 10+ | 12 ✓ |
| Available seats | 500+ | 530 ✓ |
| Reserved seats | 100+ | 100 ✓ |
| Pending allocation | 50+ | 50 ✓ |

---

## Prompt 8 – Debugging

**Issues Found & Fixed:**

1. **Pip network error in sandbox** — Re-ran with `full_network` permission
2. **EmailStr validation** — Added `email-validator` to requirements.txt
3. **Seat suggestion response** — Ensured Pydantic schemas handle ORM objects with `from_attributes=True`

---

## Prompt 9 – Deployment

**Prompt (implicit):**
> Create Docker configuration for backend and frontend with docker-compose.

**AI Generated:**
- `backend/Dockerfile` — Python 3.12, auto-seeds on startup
- `frontend/Dockerfile` — Multi-stage Node.js build
- `docker-compose.yml` — Orchestrates both services

---

## Prompt 10 – Refactoring

**Improvements Made:**
- Separated business logic into `services/` layer
- Used dependency injection for database sessions
- Consistent error handling with HTTPException
- Enriched response objects with related data (project, active_seat)

---

## What AI Generated Correctly

- Complete database schema matching PDF specification
- All required API endpoints with proper HTTP methods
- Seed script generating exact data volumes required
- AI assistant intent parser covering all query types from PDF
- Frontend pages with search, filter, pagination
- Docker deployment configuration
- Business rule enforcement (duplicate prevention, seat release)

## What AI Generated Incorrectly

- Initial pip install failed due to sandbox network restrictions (fixed by requesting permissions)
- Missing `email-validator` dependency for Pydantic EmailStr (added manually)

## Manual Fixes Applied

1. Added `email-validator` to backend requirements
2. Fixed composite unique constraint on seats table
3. Improved AI name extraction regex patterns
4. Added `.env.local` for frontend API URL configuration

## How Correctness Was Verified

1. **Seed script output** — Printed summary confirming all counts
2. **Swagger UI** — Tested each endpoint at `http://localhost:8000/docs`
3. **Frontend integration** — All pages load data from backend
4. **Business rules** — Tested duplicate allocation rejection, seat release flow
5. **AI assistant** — Tested all example queries from PDF
6. **Build verification** — `npm run build` for frontend, `uvicorn` startup for backend

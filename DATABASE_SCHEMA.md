# Database Schema

## Entity Relationship Diagram

```
┌─────────────┐       ┌──────────────┐       ┌─────────────┐
│   projects  │       │  employees   │       │    seats    │
├─────────────┤       ├──────────────┤       ├─────────────┤
│ id (PK)     │◄──┐   │ id (PK)      │   ┌──►│ id (PK)     │
│ name        │   │   │ employee_code│   │   │ floor       │
│ description │   └───│ project_id   │   │   │ zone        │
│ manager_name│       │ name         │   │   │ bay         │
│ status      │       │ email        │   │   │ seat_number │
│ created_at  │       │ department   │   │   │ status      │
└─────────────┘       │ role         │   │   │ created_at  │
                      │ joining_date │   │   └─────────────┘
                      │ status       │   │
                      │ created_at   │   │
                      │ updated_at   │   │
                      └──────┬───────┘   │
                             │           │
                      ┌──────▼───────────▼──┐
                      │  seat_allocations   │
                      ├─────────────────────┤
                      │ id (PK)             │
                      │ employee_id (FK)    │
                      │ seat_id (FK)        │
                      │ project_id (FK)     │
                      │ allocation_status   │
                      │ allocation_date     │
                      │ released_date       │
                      └─────────────────────┘
```

## Tables

### projects
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY |
| name | VARCHAR(100) | UNIQUE, NOT NULL |
| description | VARCHAR(500) | |
| manager_name | VARCHAR(100) | |
| status | ENUM | DEFAULT 'active' |
| created_at | DATETIME | DEFAULT NOW |

### employees
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY |
| employee_code | VARCHAR(50) | UNIQUE, NOT NULL |
| name | VARCHAR(150) | NOT NULL, INDEX |
| email | VARCHAR(200) | UNIQUE, NOT NULL, INDEX |
| department | VARCHAR(100) | NOT NULL |
| role | VARCHAR(100) | NOT NULL |
| joining_date | DATE | NOT NULL |
| status | ENUM | DEFAULT 'active' |
| project_id | INTEGER | FK → projects.id |
| created_at | DATETIME | DEFAULT NOW |
| updated_at | DATETIME | DEFAULT NOW |

### seats
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY |
| floor | INTEGER | NOT NULL, INDEX |
| zone | VARCHAR(10) | NOT NULL, INDEX |
| bay | VARCHAR(20) | NOT NULL |
| seat_number | VARCHAR(30) | NOT NULL |
| status | ENUM | DEFAULT 'available', INDEX |
| created_at | DATETIME | DEFAULT NOW |
| | | UNIQUE(floor, zone, seat_number) |

### seat_allocations
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY |
| employee_id | INTEGER | FK → employees.id, NOT NULL |
| seat_id | INTEGER | FK → seats.id, NOT NULL |
| project_id | INTEGER | FK → projects.id |
| allocation_status | ENUM | DEFAULT 'active', INDEX |
| allocation_date | DATE | NOT NULL |
| released_date | DATE | |

## Enums

- **EmploymentStatus:** active, inactive, pending_allocation
- **ProjectStatus:** active, inactive
- **SeatStatus:** available, occupied, reserved, maintenance
- **AllocationStatus:** active, released

## Indexes

- `employees.employee_code` — unique lookup
- `employees.email` — unique lookup
- `employees.name` — search
- `seats.floor`, `seats.zone`, `seats.status` — filter queries
- `seat_allocations.allocation_status` — active allocation lookup

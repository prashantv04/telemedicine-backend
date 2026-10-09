# Telemedicine Backend

[![CI](https://github.com/prashantv04/telemedicine-backend/actions/workflows/ci.yml/badge.svg)](https://github.com/prashantv04/telemedicine-backend/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen)](https://github.com/prashantv04/telemedicine-backend/actions/workflows/ci.yml)

Production-grade backend powering a high-concurrency telemedicine platform.

Designed with **transactional correctness, concurrency safety, scalability, and security as first-class concerns**, not as afterthoughts.

---

# 🧠 System Vision

This system models a transactional telemedicine workflow with strict domain boundaries and enforced state transitions.

Core behaviors:

- Doctors publish time-bound availability
- Patients book consultations with idempotent guarantees
- Consultation states follow validated transitions
- Prescriptions are issued only after completion
- Payments are recorded with lifecycle tracking
- All operations remain safe under retries and high concurrency

Architectural priorities:

- Strong consistency over eventual consistency
- Deterministic booking under contention
- Database-enforced invariants
- Stateless horizontal scalability

---

# 🏗 Architecture

## High-Level Flow

```
Client  
↓  
FastAPI (Stateless API Layer)  
↓  
PostgreSQL (ACID-compliant transactional store)  
↓  
Background Tasks (notifications / async jobs)
```

### Architectural Principles

- Stateless application layer (horizontal scaling ready)
- Strict transactional boundaries
- Idempotent write APIs
- Row-level locking for conflict prevention
- Database-enforced integrity
- Role-based access control (RBAC)
- Infrastructure-agnostic deployment (Docker-based)

---

# 🚀 Tech Stack

- Python 3.11+
- FastAPI
- PostgreSQL
- SQLAlchemy (2.0 style)
- JWT (HS256)
- bcrypt
- Docker + Docker Compose
- OpenAPI (Swagger UI)
- Prometheus (metrics instrumentation)

---

# ⚙️ Production-Grade Features

## Pagination for Search APIs
- Search endpoints support `page` and `limit` query parameters.
- **Example:**  
```bash
  GET /consultations/search?page=1&limit=20
```
  
## Rate Limiting

- **Signup**: 3 requests/min
- **Login**: 5 requests/min
- **Prevents** brute-force attacks and API abuse via **SlowAPI**.

## Metrics / Observability

- Prometheus-compatible metrics exposed at `/metrics`.
- Tracks request counts, latency, CPU/memory usage, and garbage collection stats.

## Background Jobs (Async Processing)

- Heavy tasks like sending booking confirmations or other notifications run asynchronously using FastAPI `BackgroundTasks`.
- Non-blocking requests improve API responsiveness.

## Structured Audit Logging

- Logs user actions with `user_id`, `action`, `status_code`, and timestamp.
- Supports compliance, security audits, and debugging.
- Logs can be queried via:

```bash
  GET /audit/
```

---

# 🎯 Performance Targets

The system is designed to support high booking concurrency while maintaining low API latency and transactional consistency.

| Metric | Target |
|---|---:|
| Daily Consultation Capacity | 100,000+ |
| p95 Read Latency | < 200 ms |
| p95 Write Latency | < 500 ms |
| Availability Goal | 99.95% |

These are design targets; production capacity and availability require validation in a production-like environment.

## 🚀 Load Testing & Performance Validation

To evaluate API latency and concurrency behavior, the system was stress-tested using [Locust](https://locust.io/). The test focused on the booking and consultation-search endpoints.

### Testing Environment

- **Hardware:** Intel Core i5 (13th Gen), NVMe SSD
- **Deployment:** Local Docker Engine (single node)
- **Test duration:** 2 minutes
- **Concurrent users:** 150 virtual users (VUs)
- **Test setup:** FastAPI, PostgreSQL, and the Locust load generator running on the same host

### Database & Connection Pool Configuration

| Setting | Value |
|---|---:|
| PostgreSQL `max_connections` | 300 |
| SQLAlchemy `pool_size` | 50 |
| SQLAlchemy `max_overflow` | 100 |

These settings were used for the benchmark. Actual throughput and connection queueing depend on workload characteristics, database resources, and contention.

### Locust Test Results

The following response-time percentiles are reported by Locust and are approximate.

| Method | Endpoint | p50 | p90 | p95 | p99 | p99.9 | Max | Requests |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| POST | `/bookings` | 14 ms | 26 ms | 32 ms | 64 ms | 100 ms | 130 ms | 1,930 |
| GET | `/consultations/search?page=1&limit=20` | 10 ms | 20 ms | 28 ms | 53 ms | 100 ms | 120 ms | 5,960 |
| **Aggregated** | **All endpoints** | **11 ms** | **22 ms** | **29 ms** | **57 ms** | **100 ms** | **130 ms** | **7,890** |

### Results vs. Performance Targets

| Metric | Observed Result | Target | Result |
|---|---:|---:|---|
| Read latency (p95) | 28 ms | < 200 ms | Within target |
| Write latency (p95) | 32 ms | < 500 ms | Within target |
| Total requests | 7,890 | — | — |
| Booking requests | 1,930 | — | — |
| Search requests | 5,960 | — | — |

### Benchmark Summary

During the two-minute test, Locust recorded **7,890 requests** across the booking and consultation-search endpoints.

- **Booking:** p95 response time of 32 ms, with a maximum observed response time of 130 ms.
- **Consultation search:** p95 response time of 28 ms, with a maximum observed response time of 120 ms.
- **Aggregated:** p95 response time of 29 ms across both endpoints.

Both endpoints remained below their respective p95 latency targets in this test environment.

### Concurrency & Transactional Correctness

Booking operations use PostgreSQL transactional guarantees to prevent conflicting slot allocations under concurrent requests:

- **Row-level locking:** `SELECT ... FOR UPDATE` serializes competing transactions attempting to allocate the same availability slot.
- **Database constraints:** Unique constraints help enforce booking and idempotency invariants.
- **Atomic transactions:** Slot allocation and consultation creation are performed within a transaction.
- **Idempotent writes:** Repeated requests using the same idempotency key do not create duplicate bookings.

These mechanisms prioritize transactional correctness when multiple patients attempt to book the same slot.

### Benchmark Limitations

These results represent a local, single-node benchmark and do not independently establish production capacity of 100,000 daily consultations or 99.95% availability. Production validation would require longer sustained-load tests, realistic booking-contention scenarios, resource utilization measurements, failure-recovery testing, and multi-instance deployment tests.

The supplied Locust output does not include a failure count, so an error rate is not claimed here.

---

# 🔐 Security Model

- Stateless JWT authentication
- Role-Based Access Control (Admin, Doctor, Patient)
- bcrypt password hashing
- Strict request validation (Pydantic)
- Environment-based secret management
- Parameterized queries via ORM
- Audit logging for critical operations
- Database-level double-booking prevention
- Idempotent write guarantees

### Extension Points

The authentication layer can be extended to support MFA, key rotation,
and rate limiting without architectural changes.

---

## 🧪 Testing & Continuous Integration

The project includes automated integration tests and CI validation to ensure transactional integrity, idempotency, and concurrency safety.

- **Testing Framework:** pytest
- **Database (CI):** PostgreSQL 15
- **Coverage:** ~85% of core modules
- **CI:** GitHub Actions workflow running tests on every push

### 🔍 What is validated

- Idempotent booking behavior
- Concurrency & double-booking prevention
- Authentication & RBAC enforcement
- Payment lifecycle validation
- Webhook simulation
- Admin-only refund enforcement
- Consultation state transition validation

Run tests locally:

```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-cov psycopg2-binary

# Run tests
pytest --cov=app -v
```

---

# 🧵 Concurrency Strategy

Booking conflicts are resolved via:

- `SELECT ... FOR UPDATE` row-level locking
- Unique constraints on slot allocation
- Atomic transaction boundaries

Why not optimistic locking?

Because under high contention (e.g., popular doctors), deterministic locking ensures correctness without retry storms.

The system prioritizes correctness over premature micro-optimizations.

---

# 🔄 Idempotent Booking Design

## Problem

Network retries must not create duplicate bookings.

Under high concurrency, the system must:

- Prevent double allocation of slots
- Return consistent results for repeated requests

## Solution

- Mandatory `idempotency-key` header
- Unique constraint on idempotency keys
- Row-level locking on availability slots
- Single-transaction slot allocation

### Guarantee

Reusing the same `idempotency-key`:

- Returns the original booking
- Never allocates a new slot
- Remains safe under concurrent retries

### Side Effects

Post-booking side effects such as **notifications** are executed asynchronously using
FastAPI `BackgroundTasks`.

This ensures:

- Booking transactions remain fast and atomic
- External operations (e.g., notifications or integrations) do not block the API response
- Idempotent booking guarantees remain unaffected by retry behavior

The idempotency model can be extended to financial operations,
ensuring safe retries in distributed payment flows.

---

# 🧩 Tradeoffs & Constraints
- Strong consistency chosen over eventual consistency
- Row-level locking preferred over optimistic retries
- No distributed cache to reduce complexity
- Webhook-based payment state updates instead of polling

---

# 📈 Scalability Model

- Stateless API layer (horizontal scaling friendly)
- Safe for multi-instance deployments
- Transactional consistency enforced at database level
- No reliance on sticky sessions

Redis intentionally excluded to reduce operational complexity for this scope.

---

# 📦 Core Domain Modules

## Admin Analytics
Aggregated system metrics:
- Users
- Doctors
- Consultations
- Completed consultations
- Payments

## Audit Logging
- Consultation status changes tracked
- Action-based audit trail entries

## Authentication & Users
- JWT-based login/signup
- Role enforcement
- MFA-ready schema

## Consultations
Supported state flow:
- `scheduled`
- `completed`
- `cancelled`

Guarantees:
- Valid transitions only
- Immutable once completed
- Role-restricted mutation

## Doctor Availability
- Time-slot-based modeling
- Conflict-safe allocation
- Concurrency-safe booking guarantees

## Prescriptions
- Only allowed for completed consultations
- Doctor-only creation
- Strict relational integrity

## Payments Module
- Idempotent payment creation
- Webhook-driven status updates
- Admin-only refund enforcement
- Database-enforced constraint preventing duplicate successful payments per consultation
- Payment lifecycle (Deterministic State Machine)
```
pending → authorized → succeeded → refunded
           │
           └────────→ failed
```
- State Definitions
  - **pending** – Payment record created, awaiting gateway processing
  - **authorized** – Payment authorized by gateway but not yet captured
  - **succeeded** – Payment successfully completed and captured
  - **failed** – Payment attempt failed (terminal state)
  - **refunded** – Successful payment reversed by admin (terminal state)

- Invariants & Guarantees
  - A consultation may have multiple payment attempts.
  - Only one `succeeded` payment is allowed per consultation (database enforced).
  - Refunds are allowed only after a payment reaches `succeeded`.
  - `succeeded` payments are immutable except for a valid transition to `refunded`.
  - All state transitions are controlled and validated server-side.

---
# 🎯 Design Goals

- Deterministic payment recording
- Idempotent-safe financial operations
- Strict relational integrity
- Audit-ready transaction logging

---

# ⚙️ Capabilities

- Payments linked to consultations (1:M)
- Supports multiple payment attempts per consultation
- Explicit payment status tracking (`pending`, `authorized`, `succeeded`, `failed`, `refunded`)
- Strong foreign key enforcement
- Audit logging for financial traceability

---

# 🛡 Integrity Guarantees

- Payment must reference a valid consultation
- No orphan transactions
- Immutable completed payments
- Database-enforced relational constraints
  
Designed using patterns inspired by high-throughput transactional systems (idempotency keys, row-level locking, DB-enforced invariants).

---

# 🗄 Database Design

## Core Tables

- users
- profiles
- doctors
- availability_slots
- consultations
- prescriptions
- payments
- idempotency_keys
- audit_logs

## Integrity Guarantees

- 1:1 and 1:M relationships enforced via foreign keys
- Unique idempotency constraint
- Slot → consultation exclusivity
- Row-level locking for allocation safety
- Indexed high-cardinality lookup paths

PostgreSQL chosen for:

- Strong ACID guarantees
- Mature concurrency model
- Proven production reliability
- Deterministic transactional semantics

---

# 📊 Observability

## Current

- Prometheus metrics exposure
- Structured logging
- Audit logging for critical state changes
- Health endpoint

## Designed to Integrate With

- Metrics systems (e.g., Prometheus)
- Distributed tracing tools
- Background job processing

---
# 🧠 Engineering Principles

This system was designed around:

- Deterministic behavior under retries and failure
- Strong transactional guarantees
- Concurrency-safe resource allocation
- Database-enforced invariants
- Explicit architectural tradeoffs
- Stateless, horizontally scalable API design

---

# 🐳 Running with Docker
Ensure Docker Desktop and Docker Compose v2+ are installed.

## 1. Clone Repository

```bash
git clone <your-repo-url>
cd telemedicine-backend
```

##  2. Build Containers

```bash
docker compose build
```

## 3. Start Services

```bash
docker compose up -d
```

##  4. Stop Services
```bash
docker compose down
```

##  5. Access API

- Swagger UI:
http://localhost:8000/docs
- OpenAPI schema: http://localhost:8000/openapi.json

---

# 🔧 Local Development
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```
---
# 🌍 Environment Variables

Create a .env file in the project root:

```bash
DATABASE_URL=postgresql://postgres:postgres@db:5432/postgres
SECRET_KEY=supersecret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```
For local (non-Docker) development, adjust `DATABASE_URL` accordingly.

---

# 📸 API Preview
![Swagger UI](/docs/screenshots/swagger.jpg)
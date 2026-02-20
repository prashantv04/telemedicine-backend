# Telemedicine Backend

Production-grade backend powering a high-concurrency telemedicine platform.

Designed with **transactional correctness, concurrency safety, scalability, and security as first-class concerns** — not as afterthoughts.

---

# 🧠 System Vision

This system models a real-world telemedicine workflow where:

- Doctors expose time-bound availability
- Patients book consultations
- State transitions are strictly enforced
- Prescriptions are issued post-consultation
- Financial transactions are tracked
- All operations remain safe under retries and concurrency

The architecture prioritizes:

- Strong consistency over eventual consistency
- Deterministic booking behavior
- Database-enforced invariants
- Stateless horizontal scalability

---

# 🏗 Architecture

## High-Level Flow

Client  
↓  
FastAPI (Stateless API Layer)  
↓  
PostgreSQL (ACID-compliant transactional store)

### Architectural Principles

- Stateless application layer (horizontal scaling ready)
- Strict transactional boundaries
- Idempotent write APIs
- Row-level locking for conflict prevention
- Database-enforced integrity
- Role-based access control (RBAC)
- Infrastructure-agnostic deployment

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

---

# 🎯 Performance Targets

| Metric | Target |
|--------|--------|
| Daily Consultations | 100,000+ |
| p95 Read Latency | < 200ms |
| p95 Write Latency | < 500ms |
| Availability | 99.95% |

Designed for high booking concurrency during peak consultation windows.

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

Future-ready for:

- Multi-factor authentication (MFA)
- Key rotation
- Rate limiting
- TLS termination
- Dependency scanning

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

This mirrors patterns used in high-scale payment systems.

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

# 📦 Core Domain Modules

## Authentication & Users
- JWT-based login/signup
- Role enforcement
- MFA-ready schema

## Doctor Availability
- Time-slot-based modeling
- Conflict-safe allocation
- Concurrency-safe booking

## Consultations
Supported state flow:
- `scheduled`
- `completed`
- `cancelled`

Guarantees:
- Valid transitions only
- Immutable once completed
- Role-restricted mutation

## Prescriptions
- Only allowed for completed consultations
- Doctor-only creation
- Strict relational integrity

## Payments
- Linked to consultations
- Supports 1:M relationship
- Audit-safe tracking

## Admin Analytics
Aggregated system metrics:
- Users
- Doctors
- Consultations
- Completed consultations
- Payments

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

# 📈 Scalability Model

- Stateless API → horizontal scaling ready
- Safe for multi-instance deployments
- Read replica compatible (future)
- Partition-ready consultation table
- Kubernetes-ready architecture
- No reliance on sticky sessions

Redis intentionally excluded to reduce operational complexity for this scope.

---

# 📊 Observability

## Current

- Structured logging
- Audit logging
- Health endpoint
- Transaction-level correctness guarantees

## Future

- Prometheus metrics
- Distributed tracing
- Background workers (Celery)
- Redis caching
- Rate limiting
- CI/CD pipeline
- Kubernetes deployment

---

# 🧪 Testing Strategy

Planned automated coverage for:

- Authentication & RBAC
- Idempotent booking behavior
- Concurrency safety
- Consultation state transitions
- Role-based restrictions

Future additions:

- Integration tests
- Load & stress testing
- CI/CD automation

---

# 🐳 Running with Docker
Ensure Docker Desktop and Docker Compose v2+ are installed.

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd telemedicine-backend
```

###  2. Build Containers

```bash
docker compose build
```

### 3. Start Services

```bash
docker compose up -d
```

###  4. Stop Services
```bash
docker compose down
```

###  5. Access API

Swagger UI:
http://localhost:8000/docs

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

# 🌍 Environment Variables

Create a .env file in the project root:

```bash
DATABASE_URL=postgresql://postgres:postgres@db:5432/postgres
SECRET_KEY=supersecret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Swagger UI:
http://localhost:8000/docs

---

# 🏁 Design Philosophy

This backend emphasizes:

- Deterministic behavior under failure
- Strong transactional guarantees
- Concurrency safety by design
- Security-first architecture 
- Explicit tradeoffs 
- Production-oriented thinking

# 📌 What This Project Demonstrates

- Distributed systems thinking 
- Concurrency control strategy 
- Idempotent API design 
- Database-level invariant enforcement 
- Stateless scalable backend architecture 
- Security-conscious implementation 
- Clean domain modeling

---

# 📸 Screenshots
![Swagger UI](/docs/screenshots/swagger.jpg)

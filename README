# Telemedicine Backend

Production-grade backend powering a scalable telemedicine platform.

This system implements secure, scalable, and transaction-safe telemedicine workflows including authentication, doctor availability management, idempotent booking, consultation lifecycle control, and prescription handling.

Designed with scalability, reliability, security, and observability as first-class concerns.

---

# 🚀 Tech Stack

- **Language:** Python 3.11+
- **Framework:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Authentication:** JWT (HS256)
- **Password Hashing:** bcrypt
- **Containerization:** Docker + Docker Compose
- **API Documentation:** OpenAPI (Swagger UI)

---

# 🎯 System Goals

| Metric | Target |
|--------|--------|
| Daily Consultations | 100,000+ |
| p95 Read Latency | < 200ms |
| p95 Write Latency | < 500ms |
| Availability | 99.95% |

---

# 🏗 Architecture Overview

## High-Level Flow

Client  
↓  
FastAPI Application (Stateless API Layer)  
↓  
PostgreSQL (ACID-compliant transactional store)

### Architectural Principles

- Modular domain-oriented structure
- Clear separation of concerns
- Stateless API design
- Idempotent write operations
- Transactional correctness
- DB-enforced invariants
- Infrastructure-agnostic deployment

---

# Core Features

## 1. Authentication & User Lifecycle

- JWT-based authentication
- Role-Based Access Control (Admin, Doctor, Patient)
- Secure password hashing via bcrypt
- Token-protected endpoints
- Environment-based secret configuration

---

## 2. Doctor Availability Management

- Time-slot-based availability creation
- Slot allocation with row-level locking
- Concurrency-safe booking enforcement
- Double-booking prevention at database level

---

## 3. Idempotent Booking System

The booking endpoint requires an `idempotency-key` header to guarantee safe retries.

### Problem

Network retries or client-side failures must not create duplicate bookings.

### Solution

- Required `idempotency-key` header
- Unique DB constraint on idempotency key
- Transaction-level atomic slot allocation
- Safe under concurrent requests

### Behavior

If the same `idempotency-key` is reused:
- Returns the previously created booking
- Prevents duplicate slot allocation

Example:

```http
POST /bookings/
idempotency-key: 9f1d2c3b-1234

{
  "slot_id": 10
}

```

---

## 4. Consultation Lifecycle Management

### Supported Status Flow

- `scheduled`
- `completed`
- `cancelled`

### Guarantees

- Only valid state transitions allowed
- Immutable once completed
- Transaction-safe updates
- Role-restricted transitions

---

## 5. Prescription Module

- Only doctors can create prescriptions
- Strictly linked to completed consultations
- Patients can retrieve their prescriptions
- Enforced relational integrity

---

## 6. Audit Logging

Critical operations are logged for:

- Traceability
- Compliance
- Security monitoring
- Post-incident investigation

---

# 📦 Core API Endpoints

## Authentication
- `POST /auth/login`

## Availability
- `POST /availability/`
- `GET /availability/`

## Booking
- `POST /bookings/`
- Requires `idempotency-key` header

## Consultation
- `GET /consultations/my`
- `PATCH /consultations/{id}/status`

## Prescription
- `POST /prescriptions/`
- `GET /prescriptions/my`

---

# 🗄 Database Design

## Core Tables

- `users`
- `availability_slots`
- `consultations`
- `prescriptions`
- `idempotency_keys`
- `audit_logs`

## Relationships

- One user → many consultations
- One availability slot → one consultation
- One consultation → one prescription
- One booking request → one idempotency key

PostgreSQL is used to leverage:

- Strong ACID guarantees
- Transaction isolation
- Row-level locking
- Unique constraints for integrity enforcement
- Proven reliability at scale

---

# 🔐 Security Controls

- JWT authentication (stateless)
- Role-based access control (RBAC)
- bcrypt password hashing
- Idempotent writes
- Pydantic request validation
- Environment variable secrets
- No hardcoded credentials
- Transaction management
- Audit logging
- Defense against double-spend booking attacks via DB constraints

---

# ⚙️ Scalability & Concurrency Strategy

- Stateless API (horizontal scaling ready)
- Safe for multi-instance deployments
- Row-level locking for slot allocation
- Unique constraints to prevent duplication
- Database-level guarantees over application-level assumptions
- Designed for high concurrency scenarios such as peak consultation booking windows.
- Safe under horizontal pod autoscaling (Kubernetes-ready design)

---

# 🔄 Design Decisions & Tradeoffs

- PostgreSQL selected for transactional correctness over eventual consistency.
- Row-level locking chosen over optimistic locking to guarantee booking safety.
- JWT stateless authentication selected for horizontal scalability.
- Redis intentionally excluded to minimize infrastructure complexity.
- Background workers excluded to keep assignment scope focused.
- Prioritized correctness and integrity over premature optimization.

---

# 📋 Prerequisites

- Docker Desktop (Windows/Mac/Linux)
- Docker Compose v2+
- GIT

---

# 🐳 Running the Project (Docker)

## 1. Clone Repository

```bash
git clone <your-repo-url>
cd amrutam-backend
```

## 2. Build Containers

```bash
docker compose build
```

## 3. Start Services

```bash
docker compose up -d
```

## 4. Stop Services
```bash
docker compose down
```

## 4. Access API

Swagger UI:
http://localhost:8000/docs

---

# 🔧 Local Development (Without Docker)

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```
---

# 🛠 Environment Variables

```bash
Create a .env file in the project root:

DATABASE_URL=postgresql://postgres:postgres@db:5432/postgres
SECRET_KEY=supersecret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

---

# 📊 Observability (Current & Future)

## Current

- Structured logging
- Transaction-level integrity
- Audit logs for critical operations

---

## Future Enhancements

- Redis caching layer
- Background workers (Celery)
- Prometheus metrics
- Distributed tracing
- Rate limiting
- Multi-factor authentication
- CI/CD pipeline
- Kubernetes deployment

---

# 🧪 Testing

Automated tests are planned for the following core workflows:

- Authentication & authorization
- Idempotent booking handling
- Concurrency safety
- Consultation state transitions
- Role-based access control

Future improvements include:
- Integration testing
- Load & stress testing
- CI pipeline automation

---

# 🏁 Final Notes

This backend emphasizes
- Transactional correctness
- Concurrency safety
- Scalable stateless architecture
- Security by design
- Production-oriented engineering decisions

Designed not just to work — but to work reliably under load.

---

# 📸 Screenshots

![Swagger UI](/docs/screenshots/swagger.jpg)

---
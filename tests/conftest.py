import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.session import engine
from app.db.base import Base
import pytest


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
# -------------------------
# Async Test Client
# -------------------------

@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# -------------------------
# User Fixtures
# -------------------------

async def create_and_login(async_client, email, password, role):
    await async_client.post("/auth/signup", json={
        "email": email,
        "password": password,
        "role": role
    })

    login = await async_client.post("/auth/login", json={
        "email": email,
        "password": password
    })

    print("LOGIN RESPONSE:", login.status_code, login.json())
    return login.json()["access_token"]


@pytest_asyncio.fixture
async def patient_token(async_client):
    return await create_and_login(
        async_client,
        "patient@test.com",
        "password",
        "patient"
    )


@pytest_asyncio.fixture
async def patient_token_1(async_client):
    return await create_and_login(
        async_client,
        "patient1@test.com",
        "password",
        "patient"
    )


@pytest_asyncio.fixture
async def patient_token_2(async_client):
    return await create_and_login(
        async_client,
        "patient2@test.com",
        "password",
        "patient"
    )


@pytest_asyncio.fixture
async def doctor_token(async_client):
    return await create_and_login(
        async_client,
        "doctor@test.com",
        "password",
        "doctor"
    )


# -------------------------
# Availability Slot
# -------------------------

@pytest_asyncio.fixture
async def slot_id(async_client, doctor_token):
    response = await async_client.post(
        "/availability/",
        json={
            "start_time": "2026-03-01T10:00:00",
            "end_time": "2026-03-01T10:30:00"
        },
        headers={"Authorization": f"Bearer {doctor_token}"}
    )

    print("SLOT RESPONSE:", response.status_code, response.json())

    return response.json()["id"]


# -------------------------
# Consultation Fixtures
# -------------------------


@pytest_asyncio.fixture
async def consultation_id(async_client, patient_token, slot_id):
    response = await async_client.post(
        "/bookings/",
        json={"slot_id": slot_id},
        headers={
            "Authorization": f"Bearer {patient_token}",
            "idempotency-key": "consultation-test"
        }
    )
    data = response.json()
    print("BOOKING RESPONSE:", response.status_code, data)
    return data["consultation_id"]


@pytest_asyncio.fixture
async def completed_consultation_id(async_client, doctor_token, consultation_id):
    await async_client.patch(
        f"/consultations/{consultation_id}/status",
        json={"status": "completed"},
        headers={"Authorization": f"Bearer {doctor_token}"}
    )

    return consultation_id
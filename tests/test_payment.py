import uuid
from decimal import Decimal

import pytest


def auth(token):
    return {"Authorization": f"Bearer {token}"}


# -----------------------------------------
# Create Payment
# -----------------------------------------

@pytest.mark.asyncio
async def test_create_payment_success(
        async_client,
        patient_token,
        consultation_id
):
    response = await async_client.post(
        "/payments/",
        json={
            "consultation_id": consultation_id,
            "amount": 1000,
            "idempotency_key": str(uuid.uuid4())
        },
        headers=auth(patient_token)
    )

    assert response.status_code == 201

    data = response.json()
    assert data["consultation_id"] == consultation_id
    assert Decimal(data["amount"]) == Decimal("1000.00")
    assert data["status"] == "pending"


# -----------------------------------------
# Invalid Consultation Should Fail
# -----------------------------------------

@pytest.mark.asyncio
async def test_payment_invalid_consultation(
        async_client,
        patient_token
):
    response = await async_client.post(
        "/payments/",
        json={
            "consultation_id": "00000000-0000-0000-0000-000000000000",
            "amount": 1000,
            "idempotency_key": str(uuid.uuid4())
        },
        headers=auth(patient_token)
    )

    assert response.status_code in (400, 404)


# -----------------------------------------
# Only Patient Can Create Payment
# -----------------------------------------

@pytest.mark.asyncio
async def test_doctor_cannot_create_payment(
        async_client,
        doctor_token,
        consultation_id
):
    response = await async_client.post(
        "/payments/",
        json={
            "consultation_id": consultation_id,
            "amount": 1000,
            "idempotency_key": str(uuid.uuid4())
        },
        headers=auth(doctor_token)
    )

    assert response.status_code == 404


# -----------------------------------------
# Completed Payment Cannot Be Modified
# -----------------------------------------

@pytest.mark.asyncio
async def test_completed_payment_is_immutable(
        async_client,
        patient_token,
        consultation_id
):
    # Step 1: Create Payment
    create = await async_client.post(
        "/payments/",
        json={
            "consultation_id": consultation_id,
            "amount": 1000,
            "idempotency_key": str(uuid.uuid4())
        },
        headers=auth(patient_token)
    )

    assert create.status_code == 201

    data = create.json()
    payment_id = data["id"]
    provider_reference = data["provider_reference"]

    assert data["consultation_id"] == consultation_id
    assert Decimal(data["amount"]) == Decimal("1000.00")
    assert data["status"] == "pending"

    # Step 2: Simulate Gateway Authorization
    authorize = await async_client.post(
        "/payments/webhook",
        json={
            "provider_reference": provider_reference,
            "status": "authorized"
        }
    )

    assert authorize.status_code == 200
    assert authorize.json()["status"] == "authorized"

    # Step 3: Simulate Gateway Success
    succeed = await async_client.post(
        "/payments/webhook",
        json={
            "provider_reference": provider_reference,
            "status": "succeeded"
        }
    )

    assert succeed.status_code == 200
    assert succeed.json()["status"] == "succeeded"

    # Step 4: Attempt Refund (patient should fail)
    refund = await async_client.post(
        f"/payments/{payment_id}/refund",
        headers=auth(patient_token)
    )

    assert refund.status_code == 403


# -----------------------------------------
# Admin Can Refund Successful Payment
# -----------------------------------------

@pytest.mark.asyncio
async def test_admin_can_refund_successful_payment(
        async_client,
        patient_token,
        admin_token,
        consultation_id
):
    create = await async_client.post(
        "/payments/",
        json={
            "consultation_id": consultation_id,
            "amount": 1000,
            "idempotency_key": str(uuid.uuid4())
        },
        headers=auth(patient_token)
    )

    assert create.status_code == 201

    data = create.json()
    payment_id = data["id"]
    provider_reference = data["provider_reference"]

    await async_client.post(
        "/payments/webhook",
        json={
            "provider_reference": provider_reference,
            "status": "authorized"
        }
    )

    await async_client.post(
        "/payments/webhook",
        json={
            "provider_reference": provider_reference,
            "status": "succeeded"
        }
    )

    refund = await async_client.post(
        f"/payments/{payment_id}/refund",
        headers=auth(admin_token)
    )

    assert refund.status_code == 200
    assert refund.json()["status"] == "refunded"


# -----------------------------------------
# Idempotency Test
# -----------------------------------------

@pytest.mark.asyncio
async def test_payment_idempotency(
        async_client,
        patient_token,
        consultation_id
):
    key = str(uuid.uuid4())

    payload = {
        "consultation_id": consultation_id,
        "amount": 1000,
        "idempotency_key": key
    }

    first = await async_client.post(
        "/payments/",
        json=payload,
        headers=auth(patient_token)
    )

    second = await async_client.post(
        "/payments/",
        json=payload,
        headers=auth(patient_token)
    )

    assert first.status_code == 201
    assert second.status_code == 201

    assert first.json()["id"] == second.json()["id"]


# -----------------------------------------
# Invalid State Transition
# -----------------------------------------

@pytest.mark.asyncio
async def test_invalid_payment_transition(
        async_client,
        patient_token,
        consultation_id
):
    create = await async_client.post(
        "/payments/",
        json={
            "consultation_id": consultation_id,
            "amount": 1000,
            "idempotency_key": str(uuid.uuid4())
        },
        headers=auth(patient_token)
    )

    provider_reference = create.json()["provider_reference"]

    # Attempt invalid transition
    response = await async_client.post(
        "/payments/webhook",
        json={
            "provider_reference": provider_reference,
            "status": "succeeded"
        }
    )

    assert response.status_code == 400
import asyncio
from unittest.mock import patch

import pytest


@pytest.mark.asyncio
async def test_idempotent_booking(async_client, patient_token, slot_id):
    headers = {
        "Authorization": f"Bearer {patient_token}",
        "idempotency-key": "unique-key-123"
    }

    payload = {"slot_id": slot_id}

    first = await async_client.post("/bookings/", json=payload, headers=headers)
    second = await async_client.post("/bookings/", json=payload, headers=headers)

    assert first.status_code == 201
    assert second.status_code == 200
    assert first.json()["id"] == second.json()["id"]


@pytest.mark.asyncio
async def test_double_booking_prevention(
    async_client,
    slot_id,
    patient_token_1,
    patient_token_2
):

    async def book(token):
        return await async_client.post(
            "/bookings/",
            json={"slot_id": slot_id},
            headers={
                "Authorization": f"Bearer {token}",
                "idempotency-key": token
            }
        )

    results = await asyncio.gather(
        book(patient_token_1),
        book(patient_token_2)
    )

    status_codes = [r.status_code for r in results]

    assert 201 in status_codes
    assert 409 in status_codes

@pytest.mark.asyncio
async def test_booking_triggers_notification(
    async_client,
    patient_token,
    slot_id
):
    headers = {
        "Authorization": f"Bearer {patient_token}",
        "idempotency-key": "notify-test-key"
    }

    payload = {"slot_id": slot_id}

    # patch where the function is USED (router), not defined
    with patch("app.modules.bookings.routers.send_booking_notification") as mock_task:

        response = await async_client.post(
            "/bookings/",
            json=payload,
            headers=headers
        )

        assert response.status_code == 201

        # verify background task was scheduled
        mock_task.assert_called_once()
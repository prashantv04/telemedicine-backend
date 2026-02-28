import asyncio
import pytest

@pytest.mark.asyncio
async def test_double_booking_prevention(async_client, slot_id, patient_token_1, patient_token_2):

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
    assert 409 in status_codes  # conflict
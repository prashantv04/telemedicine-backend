import pytest


@pytest.mark.asyncio
async def test_valid_state_transition(async_client, doctor_token, consultation_id):
    response = await async_client.patch(
        f"/consultations/{consultation_id}/status",
        json={"status": "completed"},
        headers={"Authorization": f"Bearer {doctor_token}"}
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_invalid_transition(
    async_client,
    doctor_token,
    completed_consultation_id
):
    response = await async_client.patch(
        f"/consultations/{completed_consultation_id}/status",
        json={"status": "scheduled"},
        headers={"Authorization": f"Bearer {doctor_token}"}
    )

    assert response.status_code == 400
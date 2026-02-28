import pytest


@pytest.mark.asyncio
async def test_patient_cannot_access_admin_endpoint(
    async_client,
    patient_token
):
    response = await async_client.get(
        "/admin/analytics",
        headers={"Authorization": f"Bearer {patient_token}"}
    )

    assert response.status_code == 403
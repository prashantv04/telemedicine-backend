import pytest


@pytest.mark.asyncio
async def test_user_signup_and_login(async_client):
    signup_data = {
        "email": "test@example.com",
        "password": "strongpassword",
        "role": "patient"
    }

    response = await async_client.post("/auth/signup", json=signup_data)
    assert response.status_code == 201

    login_response = await async_client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "strongpassword"
    })

    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
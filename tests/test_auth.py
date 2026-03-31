import pytest

pytestmark = pytest.mark.asyncio


async def register(client, *, login, name, email, password="1234567890", password_confirm=None):
    if password_confirm is None:
        password_confirm = password

    return await client.post(
        "/auth/register",
        json={
            "login": login,
            "name": name,
            "email": email,
            "password": password,
            "password_confirm": password_confirm,
        },
    )


async def login(client, *, email, password):
    return await client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )


async def auth_headers(access_token: str):
    return {"Authorization": f"Bearer {access_token}"}


async def test_register_user(client):
    response = await register(
        client,
        login="test_reg",
        name="Test User",
        email="test_reg@test.ru",
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["login"] == "test_reg"
    assert data["name"] == "Test User"
    assert data["email"] == "test_reg@test.ru"
    assert "id" in data


async def test_register_user_wrong_email(client):
    response = await client.post(
        "/auth/register",
        json={
            "login": "wrong_email",
            "name": "Test User",
            "email": "wrong_email",
            "password": "1234567890",
            "password_confirm": "1234567890",
        },
    )
    assert response.status_code == 422, response.text


async def test_register_user_short_password(client):
    response = await client.post(
        "/auth/register",
        json={
            "login": "short_pass",
            "name": "Test User",
            "email": "short_pass@test.ru",
            "password": "123",
            "password_confirm": "123",
        },
    )
    assert response.status_code == 422, response.text


async def test_register_user_password_mismatch(client):
    response = await client.post(
        "/auth/register",
        json={
            "login": "mismatch",
            "name": "Test User",
            "email": "mismatch@test.ru",
            "password": "1234567890",
            "password_confirm": "wrong_password",
        },
    )
    assert response.status_code in (400, 422), response.text


async def test_register_user_duplicate_email(client):
    payload = {
        "login": "dup_test",
        "name": "Dup User",
        "email": "dup@test.ru",
        "password": "1234567890",
        "password_confirm": "1234567890",
    }

    first = await client.post("/auth/register", json=payload)
    assert first.status_code == 201, first.text

    second = await client.post("/auth/register", json=payload)
    assert second.status_code in (400, 409), second.text


async def test_login_user(client):
    reg = await register(
        client,
        login="login_test",
        name="Login User",
        email="login@test.ru",
    )
    assert reg.status_code == 201, reg.text

    response = await login(client, email="login@test.ru", password="1234567890")
    assert response.status_code == 200, response.text

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_wrong_password(client):
    reg = await register(
        client,
        login="wrongpass_test",
        name="Wrong Pass User",
        email="wrongpass@test.ru",
    )
    assert reg.status_code == 201, reg.text

    response = await login(client, email="wrongpass@test.ru", password="badpassword")
    assert response.status_code in (400, 401), response.text


async def test_login_wrong_email(client):
    reg = await register(
        client,
        login="wrongemail_test",
        name="Wrong Email User",
        email="wrongemail@test.ru",
    )
    assert reg.status_code == 201, reg.text

    response = await login(client, email="bademail@test.ru", password="1234567890")
    assert response.status_code in (400, 401), response.text


async def test_login_not_registered_user(client):
    response = await login(client, email="missing@test.ru", password="1234567890")
    assert response.status_code in (400, 401), response.text


async def test_refresh_token(client):
    reg = await register(
        client,
        login="refresh_test",
        name="Refresh User",
        email="refresh@test.ru",
    )
    assert reg.status_code == 201, reg.text

    login_response = await login(client, email="refresh@test.ru", password="1234567890")
    assert login_response.status_code == 200, login_response.text

    access_token = login_response.json()["access_token"]

    response = await client.post(
        "/auth/refresh",
        headers=await auth_headers(access_token),
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_refresh_token_without_header(client):
    response = await client.post("/auth/refresh")
    assert response.status_code in (401, 403), response.text


async def test_refresh_token_invalid_token(client):
    response = await client.post(
        "/auth/refresh",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code in (401, 403), response.text


async def test_logout_user(client):
    reg = await register(
        client,
        login="logout_test",
        name="Logout User",
        email="logout@test.ru",
    )
    assert reg.status_code == 201, reg.text

    login_response = await login(client, email="logout@test.ru", password="1234567890")
    assert login_response.status_code == 200, login_response.text

    access_token = login_response.json()["access_token"]

    response = await client.post(
        "/auth/logout",
        headers=await auth_headers(access_token),
    )
    assert response.status_code == 204, response.text


async def test_logout_without_token(client):
    response = await client.post("/auth/logout")
    assert response.status_code in (401, 403), response.text


async def test_logout_invalid_token(client):
    response = await client.post(
        "/auth/logout",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code in (401, 403), response.text

async def test_logout_blocks_refresh(client):
    reg = await register(
        client,
        login="logout_refresh_test",
        name="Logout Refresh User",
        email="logout_refresh@test.ru",
    )
    assert reg.status_code == 201, reg.text

    login_response = await login(
        client,
        email="logout_refresh@test.ru",
        password="1234567890",
    )
    assert login_response.status_code == 200, login_response.text

    access_token = login_response.json()["access_token"]

    logout_response = await client.post(
        "/auth/logout",
        headers=await auth_headers(access_token),
    )
    assert logout_response.status_code == 204, logout_response.text

    refresh_response = await client.post(
        "/auth/refresh",
        headers=await auth_headers(access_token),
    )
    assert refresh_response.status_code in (401, 403), refresh_response.text
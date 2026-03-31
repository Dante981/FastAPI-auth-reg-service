import pytest

pytestmark = pytest.mark.asyncio


async def register_and_login(client, login, name, email):
    reg = await client.post(
        "/auth/register",
        json={
            "login": login,
            "name": name,
            "email": email,
            "password": "1234567890",
            "password_confirm": "1234567890",
        },
    )
    assert reg.status_code == 201, reg.text

    login_response = await client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "1234567890",
        },
    )
    assert login_response.status_code == 200, login_response.text

    return login_response.json()["access_token"]


async def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


async def test_get_me(client):
    access_token = await register_and_login(
        client,
        login="me_test",
        name="Me Test",
        email="me@test.ru",
    )

    response = await client.get(
        "/users/me",
        headers=await auth_headers(access_token),
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "me@test.ru"
    assert data["login"] == "me_test"
    assert data["name"] == "Me Test"


async def test_get_me_without_token(client):
    response = await client.get("/users/me")
    assert response.status_code in (401, 403), response.text


async def test_get_me_invalid_token(client):
    response = await client.get(
        "/users/me",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code in (401, 403), response.text


async def test_update_me(client):
    access_token = await register_and_login(
        client,
        login="update_test",
        name="Update Test",
        email="update@test.ru",
    )

    response = await client.patch(
        "/users/me",
        json={
            "name": "Updated Name",
        },
        headers=await auth_headers(access_token),
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["email"] == "update@test.ru"
    assert data["login"] == "update_test"


async def test_update_me_without_token(client):
    response = await client.patch(
        "/users/me",
        json={"name": "Updated Name"},
    )
    assert response.status_code in (401, 403), response.text


async def test_update_me_invalid_token(client):
    response = await client.patch(
        "/users/me",
        json={"name": "Updated Name"},
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code in (401, 403), response.text


async def test_update_me_empty_body(client):
    access_token = await register_and_login(
        client,
        login="empty_update_test",
        name="Empty Update Test",
        email="empty_update@test.ru",
    )

    response = await client.patch(
        "/users/me",
        json={},
        headers=await auth_headers(access_token),
    )
    assert response.status_code == 422, response.text


async def test_soft_remove_me(client):
    access_token = await register_and_login(
        client,
        login="delete_test",
        name="Delete Test",
        email="delete@test.ru",
    )

    delete_response = await client.delete(
        "/users/me",
        headers=await auth_headers(access_token),
    )

    assert delete_response.status_code == 204, delete_response.text


async def test_soft_remove_me_without_token(client):
    response = await client.delete("/users/me")
    assert response.status_code in (401, 403), response.text


async def test_soft_remove_me_invalid_token(client):
    response = await client.delete(
        "/users/me",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code in (401, 403), response.text


async def test_soft_remove_then_get_me(client):
    access_token = await register_and_login(
        client,
        login="delete_then_get_test",
        name="Delete Then Get Test",
        email="delete_then_get@test.ru",
    )

    delete_response = await client.delete(
        "/users/me",
        headers=await auth_headers(access_token),
    )
    assert delete_response.status_code == 204, delete_response.text

    me_response = await client.get(
        "/users/me",
        headers=await auth_headers(access_token),
    )
    assert me_response.status_code in (401, 403, 404), me_response.text
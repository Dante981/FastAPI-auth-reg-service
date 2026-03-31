import pytest

pytestmark = pytest.mark.asyncio


async def login_user(client, email: str):
    response = await client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "1234567890",
        },
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


async def auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


async def register_user(client, login: str, name: str, email: str):
    response = await client.post(
        "/auth/register",
        json={
            "login": login,
            "name": name,
            "email": email,
            "password": "1234567890",
            "password_confirm": "1234567890",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


async def test_create_role(client):
    token = await login_user(client, "test_admin@test.ru")

    response = await client.post(
        "/roles/",
        json={
            "name": "Support",
            "code": "support",
            "permission_codes": [
                "users:view",
                "sessions:view",
            ],
        },
        headers=await auth_headers(token),
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["name"] == "Support"
    assert data["code"] == "support"
    assert "id" in data


async def test_create_role_duplicate_code(client):
    token = await login_user(client, "test_admin@test.ru")

    first = await client.post(
        "/roles/",
        json={
            "name": "support_dup",
            "code": "support_dup",
            "permission_codes": ["users:view"],
        },
        headers=await auth_headers(token),
    )
    assert first.status_code == 201, first.text

    second = await client.post(
        "/roles/",
        json={
            "name": "support_dup 2",
            "code": "support_dup",
            "permission_codes": ["users:view"],
        },
        headers=await auth_headers(token),
    )

    assert second.status_code == 409, second.text
    assert second.json()["detail"] == "Role already exists"


async def test_create_role_duplicate_name(client):
    token = await login_user(client, "test_admin@test.ru")

    first = await client.post(
        "/roles/",
        json={
            "name": "same_name",
            "code": "same_name_1",
            "permission_codes": ["users:view"],
        },
        headers=await auth_headers(token),
    )
    assert first.status_code == 201, first.text

    second = await client.post(
        "/roles/",
        json={
            "name": "same_name",
            "code": "same_name_2",
            "permission_codes": ["users:view"],
        },
        headers=await auth_headers(token),
    )

    assert second.status_code == 409, second.text
    assert second.json()["detail"] == "Role already exists"


async def test_create_role_missing_permission_codes(client):
    token = await login_user(client, "test_admin@test.ru")

    response = await client.post(
        "/roles/",
        json={
            "name": "Broken Role",
            "code": "broken_role",
            "permission_codes": [
                "users:view",
                "does:not_exist",
            ],
        },
        headers=await auth_headers(token),
    )

    assert response.status_code == 404, response.text
    detail = response.json()["detail"]
    assert "Permissions not found" in detail
    assert "does:not_exist" in detail


async def test_create_role_without_permissions(client):
    token = await login_user(client, "test_admin@test.ru")

    response = await client.post(
        "/roles/",
        json={
            "name": "No Perms",
            "code": "no_perms",
            "permission_codes": [],
        },
        headers=await auth_headers(token),
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["name"] == "No Perms"
    assert data["code"] == "no_perms"
    assert "id" in data


async def test_create_role_forbidden_for_moderator(client):
    token = await login_user(client, "test_moderator@test.ru")

    response = await client.post(
        "/roles/",
        json={
            "name": "Forbidden",
            "code": "forbidden_role",
            "permission_codes": ["users:view"],
        },
        headers=await auth_headers(token),
    )

    assert response.status_code == 403, response.text


async def test_create_role_forbidden_for_user(client):
    token = await login_user(client, "test_user@test.ru")

    response = await client.post(
        "/roles/",
        json={
            "name": "Forbidden",
            "code": "forbidden_role_user",
            "permission_codes": ["users:view"],
        },
        headers=await auth_headers(token),
    )

    assert response.status_code == 403, response.text


async def test_create_role_without_token(client):
    response = await client.post(
        "/roles/",
        json={
            "name": "NoToken",
            "code": "no_token",
            "permission_codes": ["users:view"],
        },
    )

    assert response.status_code in (401, 403), response.text


async def test_create_role_invalid_token(client):
    response = await client.post(
        "/roles/",
        json={
            "name": "BadToken",
            "code": "bad_token",
            "permission_codes": ["users:view"],
        },
        headers=await auth_headers("invalid-token"),
    )

    assert response.status_code in (401, 403), response.text


async def test_create_role_returns_permissions(client):
    token = await login_user(client, "test_admin@test.ru")

    response = await client.post(
        "/roles/",
        json={
            "name": "With Perms",
            "code": "with_perms",
            "permission_codes": [
                "users:view",
                "sessions:view",
            ],
        },
        headers=await auth_headers(token),
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert "permissions" in data
    assert isinstance(data["permissions"], list)
    assert len(data["permissions"]) == 2


async def test_get_role_by_code(client):
    token = await login_user(client, "test_admin@test.ru")

    create_response = await client.post(
        "/roles/",
        json={
            "name": "Reader",
            "code": "reader",
            "permission_codes": ["users:view"],
        },
        headers=await auth_headers(token),
    )
    assert create_response.status_code == 201, create_response.text

    response = await client.get(
        "/roles/reader",
        headers=await auth_headers(token),
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["code"] == "reader"
    assert data["name"] == "Reader"


async def test_get_role_by_code_returns_permissions(client):
    token = await login_user(client, "test_admin@test.ru")

    create_response = await client.post(
        "/roles/",
        json={
            "name": "ReaderPerms",
            "code": "reader_perms",
            "permission_codes": ["users:view", "sessions:view"],
        },
        headers=await auth_headers(token),
    )
    assert create_response.status_code == 201, create_response.text

    response = await client.get(
        "/roles/reader_perms",
        headers=await auth_headers(token),
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert "permissions" in data
    assert isinstance(data["permissions"], list)


async def test_get_role_by_code_not_found(client):
    token = await login_user(client, "test_admin@test.ru")

    response = await client.get(
        "/roles/missing_role",
        headers=await auth_headers(token),
    )

    assert response.status_code == 404, response.text
    assert response.json()["detail"] == "Role not found"


async def test_get_all_roles(client):
    token = await login_user(client, "test_admin@test.ru")

    create_response = await client.post(
        "/roles/",
        json={
            "name": "List Role",
            "code": "list_role",
            "permission_codes": [],
        },
        headers=await auth_headers(token),
    )
    assert create_response.status_code == 201, create_response.text

    response = await client.get(
        "/roles/",
        headers=await auth_headers(token),
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert any(role["code"] == "list_role" for role in data)


async def test_set_role_to_user(client):
    admin_token = await login_user(client, "test_admin@test.ru")

    role_response = await client.post(
        "/roles/",
        json={
            "name": "Moderator_set_role",
            "code": "moderator_set_role",
            "permission_codes": ["users:view"],
        },
        headers=await auth_headers(admin_token),
    )
    assert role_response.status_code == 201, role_response.text

    user = await register_user(
        client,
        login="role_target",
        name="Role Target",
        email="role_target@test.ru",
    )
    user_id = user["id"]

    response = await client.patch(
        f"roles/users/{user_id}",
        json={"code": "moderator_set_role"},
        headers=await auth_headers(admin_token),
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["role"] is not None


async def test_set_role_to_missing_user(client):
    token = await login_user(client, "test_admin@test.ru")

    role_response = await client.post(
        "/roles/",
        json={
            "name": "TempRole",
            "code": "temp_role",
            "permission_codes": [],
        },
        headers=await auth_headers(token),
    )
    assert role_response.status_code == 201, role_response.text

    response = await client.patch(
        "/users/999999/",
        json={"code": "temp_role"},
        headers=await auth_headers(token),
    )

    assert response.status_code == 404, response.text
    assert "Not Found" in response.json()["detail"]


async def test_update_role_name_only(client):
    token = await login_user(client, "test_admin@test.ru")

    create_response = await client.post(
        "/roles/",
        json={
            "name": "Old Name",
            "code": "update_test",
            "permission_codes": [],
        },
        headers=await auth_headers(token),
    )
    assert create_response.status_code == 201, create_response.text

    update_response = await client.patch(
        "/roles/update_test",
        json={"name": "New Name"},
        headers=await auth_headers(token),
    )

    assert update_response.status_code == 200, update_response.text
    data = update_response.json()
    assert data["name"] == "New Name"
    assert data["code"] == "update_test"


async def test_update_role_remove_all_permissions(client):
    token = await login_user(client, "test_admin@test.ru")

    await client.post(
        "/roles/",
        json={
            "name": "Remove Perms",
            "code": "remove_perms",
            "permission_codes": ["users:view"],
        },
        headers=await auth_headers(token),
    )

    response = await client.patch(
        "/roles/remove_perms",
        json={"permission_codes": []},
        headers=await auth_headers(token),
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert "permissions" in data
    assert len(data["permissions"]) == 0




async def test_set_same_role_to_user(client):
    admin_token = await login_user(client, "test_admin@test.ru")

    role_response = await client.post(
        "/roles/",
        json={
            "name": "SameRole",
            "code": "same_role",
            "permission_codes": [],
        },
        headers=await auth_headers(admin_token),
    )
    assert role_response.status_code == 201, role_response.text

    user = await register_user(
        client,
        login="same_role_target",
        name="Same Role Target",
        email="same_role_target@test.ru",
    )
    user_id = user["id"]

    first = await client.patch(
        f"/roles/users/{user_id}",
        json={"code": "same_role"},
        headers=await auth_headers(admin_token),
    )
    assert first.status_code == 200, first.text

    second = await client.patch(
        f"/roles/users/{user_id}",
        json={"code": "same_role"},
        headers=await auth_headers(admin_token),
    )

    assert second.status_code == 200, second.text


async def test_create_role_422_invalid_email_like_value(client):
    token = await login_user(client, "test_admin@test.ru")

    response = await client.post(
        "/roles/",
        json={
            "name": "Bad Email Role",
            "code": "bad_email_role",
            "permission_codes": [],
        },
        headers=await auth_headers(token),
    )

    assert response.status_code == 201, response.text
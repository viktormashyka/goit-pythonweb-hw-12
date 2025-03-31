import pytest
from unittest.mock import patch
from conftest import test_user, admin_user


@pytest.mark.asyncio
async def test_get_me(client, get_token):
    with patch("src.services.auth.redis_client") as redis_mock:
        redis_mock.exists.return_value = False
        headers = {"Authorization": f"Bearer {get_token}"}
        response = client.get("/api/users/me", headers=headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["username"] == test_user["username"]
        assert data["email"] == test_user["email"]
        assert "avatar" in data
        assert data["role"] == "USER"


@pytest.mark.asyncio
async def test_get_me_unauthorized(client):
    with patch("src.services.auth.redis_client") as redis_mock:
        redis_mock.exists.return_value = False
        response = client.get("/api/users/me")
        assert response.status_code == 401, response.text


@patch("src.services.upload_file.UploadFileService.upload_file")
@pytest.mark.asyncio
async def test_update_avatar_user_non_admin_forbidden(mock_upload_file, client, get_token):
    mock_upload_file.return_value = "http://example.com/avatar.jpg"
    headers = {"Authorization": f"Bearer {get_token}"}
    file_data = {"file": ("avatar.jpg", b"fake image content", "image/jpeg")}

    with patch("src.services.auth.redis_client") as redis_mock:
        redis_mock.exists.return_value = False
        response = client.patch("/api/users/avatar", headers=headers, files=file_data)

        assert response.status_code == 403, response.text
        data = response.json()
        assert data["detail"] == "Недостатньо прав доступу для виконання цієї дії"
        mock_upload_file.assert_called_once()


@pytest.mark.asyncio
async def test_update_avatar_user_invalid_file_type(client, get_token):
    headers = {"Authorization": f"Bearer {get_token}"}
    file_data = {"file": ("avatar.txt", b"not an image", "text/plain")}

    with patch("src.services.auth.redis_client") as redis_mock:
        redis_mock.exists.return_value = False
        response = client.patch("/api/users/avatar", headers=headers, files=file_data)
        assert response.status_code == 403, response.text


@pytest.mark.asyncio
async def test_update_avatar_user_empty_file(client, get_token):
    headers = {"Authorization": f"Bearer {get_token}"}
    file_data = {"file": ("avatar.jpg", b"", "image/jpeg")}

    with patch("src.services.auth.redis_client") as redis_mock:
        redis_mock.exists.return_value = False
        response = client.patch("/api/users/avatar", headers=headers, files=file_data)
        assert response.status_code == 403, response.text


@patch("src.services.upload_file.UploadFileService.upload_file")
@pytest.mark.asyncio
async def test_update_avatar_user_admin_success(mock_upload_file, client, get_admin_token):
    fake_url = "http://example.com/admin_avatar.jpg"
    mock_upload_file.return_value = fake_url

    headers = {"Authorization": f"Bearer {get_admin_token}"}
    file_data = {"file": ("avatar.jpg", b"fake image content", "image/jpeg")}

    with patch("src.services.auth.redis_client") as redis_mock:
        redis_mock.exists.return_value = False
        response = client.patch("/api/users/avatar", headers=headers, files=file_data)
        assert response.status_code == 200, response.text

        data = response.json()
        assert data["username"] == admin_user["username"]
        assert data["email"] == admin_user["email"]
        assert data["avatar"] == fake_url
        mock_upload_file.assert_called_once()


@pytest.mark.asyncio
async def test_admin_route_access(client, get_admin_token):
    headers = {"Authorization": f"Bearer {get_admin_token}"}

    with patch("src.services.auth.redis_client") as redis_mock:
        redis_mock.exists.return_value = False
        response = client.get("/api/users/admin", headers=headers)
        assert response.status_code == 200
        assert "адміністративний маршрут" in response.json()["message"]


@pytest.mark.asyncio
async def test_admin_route_forbidden_for_user(client, get_token):
    headers = {"Authorization": f"Bearer {get_token}"}

    with patch("src.services.auth.redis_client") as redis_mock:
        redis_mock.exists.return_value = False
        response = client.get("/api/users/admin", headers=headers)
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_moderator_route_access_as_moderator(client, get_moderator_token):
    headers = {"Authorization": f"Bearer {get_moderator_token}"}

    with patch("src.services.auth.redis_client") as redis_mock:
        redis_mock.exists.return_value = False
        response = client.get("/api/users/moderator", headers=headers)
        assert response.status_code == 200
        assert "модераторів" in response.json()["message"]


@pytest.mark.asyncio
async def test_moderator_route_access_as_admin(client, get_admin_token):
    headers = {"Authorization": f"Bearer {get_admin_token}"}

    with patch("src.services.auth.redis_client") as redis_mock:
        redis_mock.exists.return_value = False
        response = client.get("/api/users/moderator", headers=headers)
        assert response.status_code == 200
        assert "модераторів" in response.json()["message"]


@pytest.mark.asyncio
async def test_moderator_route_forbidden_for_user(client, get_token):
    headers = {"Authorization": f"Bearer {get_token}"}

    with patch("src.services.auth.redis_client") as redis_mock:
        redis_mock.exists.return_value = False
        response = client.get("/api/users/moderator", headers=headers)
        assert response.status_code == 403

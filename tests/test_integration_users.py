import pytest
from unittest.mock import patch
from conftest import test_user, admin_user


@pytest.mark.asyncio
async def test_get_me(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("api/users/me", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == test_user["username"]
    assert data["email"] == test_user["email"]
    assert "avatar" in data
    assert data["role"] == "USER"

@pytest.mark.asyncio
async def test_get_me_unauthorized(client):
    response = client.get("/api/users/me")
    assert response.status_code == 401, response.text


@patch("src.services.upload_file.UploadFileService.upload_file")
@pytest.mark.asyncio
async def test_update_avatar_user_failed(mock_upload_file, client, get_token):
    # Mock the response from the file upload service
    fake_url = "http://example.com/avatar.jpg"
    mock_upload_file.return_value = fake_url

    # Authorization token
    headers = {"Authorization": f"Bearer {get_token}"}

    # File to be sent
    file_data = {"file": ("avatar.jpg", b"fake image content", "image/jpeg")}

    # Send PATCH request
    response = client.patch("/api/users/avatar", headers=headers, files=file_data)

    # Check that the request was denied for non-admin users
    assert response.status_code == 403, response.text

    # Check the response
    data = response.json()
    assert data["detail"] == "Недостатньо прав доступу для виконання цієї дії"

    # Check that the upload_file function was called with the UploadFile object
    mock_upload_file.assert_called_once()

@pytest.mark.asyncio
async def test_update_avatar_user_invalid_file(client, get_token):
    # Authorization token for a non-admin user
    headers = {"Authorization": f"Bearer {get_token}"}

    # File to be sent
    file_data = {"file": ("avatar.jpg", b"fake image content", "text/plain")}

    # Send PATCH request
    response = client.patch("/api/users/avatar", headers=headers, files=file_data)

    # Check that the request is forbidden for non-admin users
    assert response.status_code == 403, response.text

@pytest.mark.asyncio
async def test_update_avatar_user_empty_file(client, get_token):
    # Authorization token for a non-admin user
    headers = {"Authorization": f"Bearer {get_token}"}

    # File to be sent
    file_data = {"file": ("avatar.jpg", b"", "image/jpeg")}

    # Send PATCH request
    response = client.patch("/api/users/avatar", headers=headers, files=file_data)

    # Check that the request is forbidden for non-admin users
    assert response.status_code == 403, response.text


@patch("src.services.upload_file.UploadFileService.upload_file")
@pytest.mark.asyncio
async def test_update_avatar_user_admin_success(mock_upload_file, client, get_admin_token):
    fake_url = "http://example.com/admin_avatar.jpg"
    mock_upload_file.return_value = fake_url

    headers = {"Authorization": f"Bearer {get_admin_token}"}
    file_data = {"file": ("avatar.jpg", b"fake image content", "image/jpeg")}

    response = client.patch("/api/users/avatar", headers=headers, files=file_data)
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["username"] == admin_user["username"]
    assert data["email"] == admin_user["email"]
    assert data["avatar"] == fake_url
    mock_upload_file.assert_called_once()



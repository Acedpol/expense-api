def test_register_and_login(client):
    response = client.post(
        "/auth/register", json={"email": "a@example.com", "password": "secret123"}
    )
    assert response.status_code == 201
    assert response.json()["email"] == "a@example.com"

    response = client.post(
        "/auth/login", data={"username": "a@example.com", "password": "secret123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_register_duplicate_email_fails(client):
    client.post(
        "/auth/register", json={"email": "dup@example.com", "password": "secret123"}
    )
    response = client.post(
        "/auth/register", json={"email": "dup@example.com", "password": "secret123"}
    )
    assert response.status_code == 400


def test_login_wrong_password_fails(client):
    client.post(
        "/auth/register", json={"email": "b@example.com", "password": "secret123"}
    )
    response = client.post(
        "/auth/login", data={"username": "b@example.com", "password": "wrong"}
    )
    assert response.status_code == 401


def test_expenses_require_auth(client):
    response = client.get("/expenses")
    assert response.status_code == 401


def test_create_category_and_expense(client, auth_headers):
    response = client.post("/categories", json={"name": "Food"}, headers=auth_headers)
    assert response.status_code == 201
    category_id = response.json()["id"]

    response = client.post(
        "/expenses",
        json={
            "amount": 12.5,
            "description": "Lunch",
            "date": "2026-08-01",
            "category_id": category_id,
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["description"] == "Lunch"

    response = client.get("/expenses", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1

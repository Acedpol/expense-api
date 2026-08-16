def test_get_category_returns_owned_category(client, auth_headers):
    create_response = client.post(
        "/categories", json={"name": "Transporte"}, headers=auth_headers
    )
    category_id = create_response.json()["id"]

    response = client.get(f"/categories/{category_id}", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {"id": category_id, "name": "Transporte"}


def test_get_category_404_when_missing(client, auth_headers):
    response = client.get("/categories/999", headers=auth_headers)
    assert response.status_code == 404


def test_get_category_404_when_owned_by_another_user(client, auth_headers):
    create_response = client.post(
        "/categories", json={"name": "Ocio"}, headers=auth_headers
    )
    category_id = create_response.json()["id"]

    client.post(
        "/auth/register", json={"email": "other@example.com", "password": "secret123"}
    )
    login_response = client.post(
        "/auth/login", data={"username": "other@example.com", "password": "secret123"}
    )
    other_user_headers = {
        "Authorization": f"Bearer {login_response.json()['access_token']}"
    }

    response = client.get(f"/categories/{category_id}", headers=other_user_headers)

    assert response.status_code == 404


def test_get_category_requires_auth(client):
    response = client.get("/categories/1")
    assert response.status_code == 401


def test_list_categories_respects_skip_and_limit(client, auth_headers):
    for name in ["Comida", "Transporte", "Ocio", "Salud"]:
        client.post("/categories", json={"name": name}, headers=auth_headers)

    response = client.get("/categories?skip=1&limit=2", headers=auth_headers)

    assert response.status_code == 200
    names = [category["name"] for category in response.json()]
    assert names == ["Transporte", "Ocio"]

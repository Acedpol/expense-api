def _create_category(client, auth_headers, name="Comida"):
    response = client.post("/categories", json={"name": name}, headers=auth_headers)
    return response.json()["id"]


def _create_expense(client, auth_headers, category_id, **overrides):
    payload = {
        "amount": 12.5,
        "description": "Almuerzo",
        "date": "2026-01-01",
        "category_id": category_id,
        **overrides,
    }
    response = client.post("/expenses", json=payload, headers=auth_headers)
    return response.json()["id"]


def test_create_and_get_expense(client, auth_headers):
    category_id = _create_category(client, auth_headers)
    expense_id = _create_expense(client, auth_headers, category_id)

    response = client.get(f"/expenses/{expense_id}", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["description"] == "Almuerzo"


def test_update_expense_date(client, auth_headers):
    """Regression test: ExpenseUpdate.date was shadowed by the `date`
    field name in a way that made Pydantic generate `{"type": "null"}`
    for it, so the API rejected any real date and only accepted null.
    """
    category_id = _create_category(client, auth_headers)
    expense_id = _create_expense(client, auth_headers, category_id, date="2026-01-01")

    response = client.patch(
        f"/expenses/{expense_id}", json={"date": "2026-02-15"}, headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["date"] == "2026-02-15"


def test_update_expense_amount_and_description(client, auth_headers):
    category_id = _create_category(client, auth_headers)
    expense_id = _create_expense(client, auth_headers, category_id)

    response = client.patch(
        f"/expenses/{expense_id}",
        json={"amount": 30, "description": "Cena"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["amount"] == 30
    assert body["description"] == "Cena"


def test_update_expense_category_revalidates_ownership(client, auth_headers):
    category_id = _create_category(client, auth_headers)
    expense_id = _create_expense(client, auth_headers, category_id)

    response = client.patch(
        f"/expenses/{expense_id}", json={"category_id": 9999}, headers=auth_headers
    )

    assert response.status_code == 404


def test_delete_expense(client, auth_headers):
    category_id = _create_category(client, auth_headers)
    expense_id = _create_expense(client, auth_headers, category_id)

    response = client.delete(f"/expenses/{expense_id}", headers=auth_headers)
    assert response.status_code == 204

    response = client.get(f"/expenses/{expense_id}", headers=auth_headers)
    assert response.status_code == 404


def test_list_expenses_respects_skip_and_limit(client, auth_headers):
    category_id = _create_category(client, auth_headers)
    for i in range(4):
        _create_expense(client, auth_headers, category_id, description=f"Gasto {i}", date=f"2026-01-0{i + 1}")

    response = client.get("/expenses?skip=1&limit=2", headers=auth_headers)

    assert response.status_code == 200
    assert len(response.json()) == 2

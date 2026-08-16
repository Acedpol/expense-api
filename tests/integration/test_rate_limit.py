def test_login_is_rate_limited_after_five_attempts_per_minute(client):
    client.post(
        "/auth/register",
        json={"email": "ratelimit@example.com", "password": "secret123"},
    )

    for _ in range(5):
        response = client.post(
            "/auth/login",
            data={"username": "ratelimit@example.com", "password": "wrong"},
        )
        assert response.status_code == 401

    response = client.post(
        "/auth/login",
        data={"username": "ratelimit@example.com", "password": "wrong"},
    )

    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json()["error"]

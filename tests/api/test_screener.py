def test_screener_minimum_roe_returns_only_qualifying_companies(client):
    response = client.get("/api/v1/screener", params={"min_roe": 15})

    assert response.status_code == 200
    payload = response.json()
    assert payload["filters"]["min_roe"] == 15
    assert payload["count"] == len(payload["companies"])
    assert payload["companies"]
    assert all(company["roe"] >= 15 for company in payload["companies"])


def test_screener_rejects_invalid_filter_value(client):
    response = client.get("/api/v1/screener", params={"min_roe": "not-a-number"})

    assert response.status_code == 400

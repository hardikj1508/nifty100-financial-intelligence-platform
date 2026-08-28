def test_sectors_returns_all_available_sectors(client):
    response = client.get("/api/v1/sectors")

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 10
    assert payload["count"] == len(payload["sectors"])


def test_information_technology_endpoint_returns_only_technology_companies(client):
    response = client.get("/api/v1/sectors/Information%20Technology/companies")

    assert response.status_code == 200
    payload = response.json()
    assert payload["sector"] == "Information Technology"
    assert payload["companies"]
    assert all(company["sector"] == "Information Technology" for company in payload["companies"])

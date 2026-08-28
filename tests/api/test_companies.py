def test_companies_returns_all_92_companies(client):
    response = client.get("/api/v1/companies")

    assert response.status_code == 200
    assert len(response.json()) == 92


def test_company_profile_returns_tcs(client):
    response = client.get("/api/v1/companies/TCS")

    assert response.status_code == 200
    assert response.json()["company"]["id"] == "TCS"


def test_unknown_company_returns_not_found(client):
    response = client.get("/api/v1/companies/INVALID")

    assert response.status_code == 404
    assert response.json()["detail"] == "Company 'INVALID' not found"

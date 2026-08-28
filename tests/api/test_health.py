from src.api.routers.health import TABLES


def test_health_returns_ok_and_all_database_tables(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert set(payload["db_row_counts"]) == set(TABLES)


def test_health_reports_non_negative_row_counts(client):
    counts = client.get("/api/v1/health").json()["db_row_counts"]

    assert all(isinstance(count, int) and count >= 0 for count in counts.values())

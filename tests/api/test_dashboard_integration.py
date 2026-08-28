from src.dashboard.utils.api import screener_dataframe


def test_dashboard_screener_table_matches_api_response(client):
    response = client.get("/api/v1/screener", params={"min_roe": 15})

    assert response.status_code == 200
    payload = response.json()
    dashboard_table = screener_dataframe(payload)

    assert len(dashboard_table) == payload["count"]
    assert dashboard_table["ticker"].tolist() == [
        company["ticker"] for company in payload["companies"]
    ]
    assert (dashboard_table["roe"] >= 15).all()

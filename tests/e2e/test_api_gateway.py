"""
Module: tests/e2e/test_api_gateway.py
Package: pakistan-constitution-ai
Purpose: End-to-end API gateway integration tests using FastAPI TestClient
"""


def test_health_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["HEALTHY", "DEGRADED"]
    assert "database" in data
    assert data["database"] == "UP"
    assert data["articles_indexed"] > 0


def test_get_article_by_number(client):
    response = client.get("/api/v1/articles/25")
    assert response.status_code == 200
    data = response.json()
    assert data["article_number"] == 25
    # Matches either Constitution Article 25 or PPC Section 25
    assert "25" in data["title"] or "Equality" in data["title"]
    assert "full_text" in data
    assert len(data["clauses"]) >= 1


def test_query_endpoint_e2e(client):
    payload = {
        "query": "What is the age limit for compulsory education under Article 25A?",
        "history": []
    }
    response = client.post("/api/v1/query", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Verify JSON schema compliance
    assert "request_id" in data
    assert "answer" in data
    assert "citations" in data
    assert "latency" in data
    assert "metrics" in data

    # Verify content correctness
    assert len(data["answer"]) > 20
    assert any("25A" in str(c) for c in data["citations"]) or ("25A" in data["answer"])


def test_analytics_dashboard_endpoint(client):
    response = client.get("/api/v1/analytics/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "overview" in data
    assert "cache" in data
    assert "recent_queries" in data
    assert data["overview"]["total_queries"] >= 0
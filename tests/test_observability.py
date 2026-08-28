from fastapi import status
from fastapi.testclient import TestClient


def test_metrics_endpoint_accessible(client: TestClient):
    """Verifica que el endpoint de Prometheus /metrics responda 200 y contenga métricas estándar."""
    response = client.get("/metrics")
    assert response.status_code == status.HTTP_200_OK
    assert (
        "http_requests_total" in response.text
        or "http_request_duration_seconds" in response.text
    )


def test_request_id_header_injected(client: TestClient):
    """Verifica que cada respuesta HTTP contenga los encabezados X-Request-ID y X-Process-Time."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert "x-request-id" in response.headers
    assert "x-process-time" in response.headers


def test_request_id_preserved_when_provided(client: TestClient):
    """Verifica que si el cliente envía un X-Request-ID, el servidor lo preserve en la respuesta."""
    custom_trace_id = "test-distributed-trace-id-12345"
    response = client.get("/", headers={"X-Request-ID": custom_trace_id})
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["x-request-id"] == custom_trace_id

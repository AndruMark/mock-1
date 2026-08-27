from fastapi import status
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "ok"


def test_create_task_success(client: TestClient, auth_headers: dict[str, str]):
    payload = {
        "title": "Configurar Pytest",
        "description": "Pruebas de integración automatizadas",
        "completed": False,
    }
    response = client.post("/tasks/", json=payload, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["completed"] is False
    assert "id" in data
    assert "created_at" in data


def test_create_task_unauthorized(client: TestClient):
    # Intento de creación sin token (debe devolver 401)
    response = client.post("/tasks/", json={"title": "Sin token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_task_validation_error(client: TestClient, auth_headers: dict[str, str]):
    payload = {"title": "ab", "description": "Demasiado corto"}
    response = client.post("/tasks/", json=payload, headers=auth_headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_read_tasks_empty(client: TestClient, auth_headers: dict[str, str]):
    response = client.get("/tasks/", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_read_task_by_id_success(client: TestClient, auth_headers: dict[str, str]):
    create_res = client.post(
        "/tasks/",
        json={"title": "Tarea de consulta", "description": None},
        headers=auth_headers,
    )
    task_id = create_res.json()["id"]

    response = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == task_id


def test_read_task_not_found(client: TestClient, auth_headers: dict[str, str]):
    response = client.get("/tasks/99999", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_task_success(client: TestClient, auth_headers: dict[str, str]):
    create_res = client.post(
        "/tasks/",
        json={"title": "Tarea Original", "completed": False},
        headers=auth_headers,
    )
    task_id = create_res.json()["id"]

    update_payload = {"title": "Tarea Modificada", "completed": True}
    response = client.put(
        f"/tasks/{task_id}", json=update_payload, headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["completed"] is True


def test_delete_task_success(client: TestClient, auth_headers: dict[str, str]):
    create_res = client.post(
        "/tasks/", json={"title": "Tarea para eliminar"}, headers=auth_headers
    )
    task_id = create_res.json()["id"]

    delete_res = client.delete(f"/tasks/{task_id}", headers=auth_headers)
    assert delete_res.status_code == status.HTTP_204_NO_CONTENT

    get_res = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert get_res.status_code == status.HTTP_404_NOT_FOUND

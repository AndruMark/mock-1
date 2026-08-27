from fastapi import status
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "ok"


def test_create_task_success(client: TestClient):
    payload = {
        "title": "Configurar Pytest",
        "description": "Pruebas de integración automatizadas",
        "completed": False,
    }
    response = client.post("/tasks/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["completed"] is False
    assert "id" in data
    assert "created_at" in data


def test_create_task_validation_error(client: TestClient):
    # Longitud menor a 3 caracteres (debe fallar por validación de Pydantic)
    payload = {"title": "ab", "description": "Demasiado corto"}
    response = client.post("/tasks/", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_read_tasks_empty(client: TestClient):
    response = client.get("/tasks/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_read_task_by_id_success(client: TestClient):
    # 1. Crear tarea previa
    create_res = client.post(
        "/tasks/", json={"title": "Tarea de consulta", "description": None}
    )
    task_id = create_res.json()["id"]

    # 2. Consultar por ID
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == task_id
    assert response.json()["title"] == "Tarea de consulta"


def test_read_task_not_found(client: TestClient):
    response = client.get("/tasks/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Task with id 99999 not found"


def test_update_task_success(client: TestClient):
    # 1. Crear tarea inicial
    create_res = client.post(
        "/tasks/", json={"title": "Tarea Original", "completed": False}
    )
    task_id = create_res.json()["id"]

    # 2. Actualizar estado y título
    update_payload = {"title": "Tarea Modificada", "completed": True}
    response = client.put(f"/tasks/{task_id}", json=update_payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Tarea Modificada"
    assert data["completed"] is True


def test_update_task_not_found(client: TestClient):
    response = client.put("/tasks/99999", json={"title": "No existe"})
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_task_success(client: TestClient):
    # 1. Crear tarea
    create_res = client.post("/tasks/", json={"title": "Tarea para eliminar"})
    task_id = create_res.json()["id"]

    # 2. Eliminarla
    delete_res = client.delete(f"/tasks/{task_id}")
    assert delete_res.status_code == status.HTTP_204_NO_CONTENT

    # 3. Confirmar que ya no existe (404)
    get_res = client.get(f"/tasks/{task_id}")
    assert get_res.status_code == status.HTTP_404_NOT_FOUND


def test_delete_task_not_found(client: TestClient):
    response = client.delete("/tasks/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND

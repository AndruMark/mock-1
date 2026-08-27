import fakeredis
from fastapi import status
from fastapi.testclient import TestClient

import app.core.cache as cache_module


def test_cache_hit_and_invalidation(
    client: TestClient, auth_headers: dict[str, str], monkeypatch
):
    # Mockear el cliente de Redis con fakeredis en memoria RAM
    fake_server = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(cache_module, "redis_client", fake_server)
    monkeypatch.setattr(cache_module, "REDIS_AVAILABLE", True)

    # 1. Crear tarea (invalida la cache previa)
    create_res = client.post(
        "/tasks/",
        json={"title": "Tarea para Cachear", "description": "Cache Test"},
        headers=auth_headers,
    )
    assert create_res.status_code == status.HTTP_201_CREATED
    task_id = create_res.json()["id"]

    # 2. Primera lectura: genera Cache Miss y escribe en la cache
    res1 = client.get("/tasks/", headers=auth_headers)
    assert res1.status_code == status.HTTP_200_OK
    assert len(res1.json()) >= 1

    # 3. Segunda lectura: debe responder Cache Hit identico
    res2 = client.get("/tasks/", headers=auth_headers)
    assert res2.status_code == status.HTTP_200_OK
    assert res1.json() == res2.json()

    # 4. Mutacion (Eliminar tarea): debe purgar la clave en Redis
    del_res = client.delete(f"/tasks/{task_id}", headers=auth_headers)
    assert del_res.status_code == status.HTTP_204_NO_CONTENT

    # 5. Tercera lectura tras invalidacion
    res3 = client.get("/tasks/", headers=auth_headers)
    assert res3.status_code == status.HTTP_200_OK

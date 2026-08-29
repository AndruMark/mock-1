# Mock-1: Enterprise Distributed Microservice & Real-Time Task Platform

[![CI Pipeline](https://github.com/AndruMark/mock-1/actions/workflows/ci.yml/badge.svg)](https://github.com/AndruMark/mock-1/actions)
[![Python 3.14](https://img.shields.io/badge/python-3.14-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Coverage](https://img.shields.io/badge/coverage-92%25-brightgreen.svg)](https://pytest.org)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![PostgreSQL 17](https://img.shields.io/badge/PostgreSQL-17-336791.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis 7](https://img.shields.io/badge/Redis-7-DC382D.svg?logo=redis&logoColor=white)](https://redis.io/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Plataforma fullstack de alto rendimiento diseñada bajo principios de arquitectura limpia, aislamiento estricto multi-inquilino (*Multi-Tenancy*), sincronización reactiva bidireccional (*WebSockets*), capa de aceleración en memoria (*Cache-Aside con Redis*) y observabilidad estandarizada para entornos de producción.

---

## 🏗️ Topología del Sistema y Arquitectura

```text
                                  ┌────────────────────────┐
                                  │      Web Browser       │
                                  │ (React + TS + Vite SPA)│
                                  └───────────┬────────────┘
                                              │
                         ┌────────────────────┴────────────────────┐
                         │ HTTP (REST + JWT)                       │ WebSocket (Full-Duplex)
                         ▼                                         ▼
            ┌─────────────────────────────────────────────────────────────┐
            │                  FastAPI Application Gateway                │
            │  ┌───────────────────────────────────────────────────────┐  │
            │  │ RequestTracingMiddleware (X-Request-ID + Latency JSON)│  │
            │  └───────────────────────────────────────────────────────┘  │
            │                                                             │
            │  ┌──────────────┐   ┌──────────────┐   ┌─────────────────┐  │
            │  │ /auth Router │   │ /tasks Router│   │ /ws Endpoint    │  │
            │  └──────┬───────┘   └──────┬───────┘   └────────┬────────┘  │
            └─────────┼──────────────────┼────────────────────┼───────────┘
                      │                  │                    │
         ┌────────────┼──────────────────┼────────────────────┘
         │            │                  │
         │ (Bcrypt /  │ (Cache-Aside /   │ (ConnectionManager
         │  PyJWT)    │  Invalidation)   │  Broadcast por Tenant)
         ▼            ▼                  ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  PostgreSQL 17  │ │     Redis 7     │ │ Prometheus SRE  │
│  (Persistencia  │ │ (Caché en RAM + │ │  Telemetría en  │
│  Relacional +   │ │   Background    │ │    /metrics     │
│  Alembic DDL)   │ │     Audit)      │ │   (P95/P99)     │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

---

## ⚡ Decisiones Técnicas y Patrones de Diseño

* **Aislamiento Multi-Tenant Relacional:** Relación estricta `tasks.owner_id -> users.id` con eliminación en cascada (`ON DELETE CASCADE`). Todas las operaciones CRUD están confinadas al token del inquilino autenticado.
* **Autenticación Criptográfica sin Estado:** Tokens JWT firmados con algoritmo `HS256` y contraseñas hasheadas mediante `bcrypt` con salting dinámico (`gensalt()`).
* **Patrón Cache-Aside con Invalidación Reactiva:** Las consultas `GET /tasks/` se resuelven en memoria RAM con Redis (`TTL 300s`) con respuesta en `< 2ms`. Toda mutación (`POST`, `PUT`, `DELETE`) purga atómicamente la clave `user:{id}:tasks`.
* **Degradación Elegante (*Graceful Degradation*):** El microservicio detecta la disponibilidad del socket de Redis. Si el servicio de caché no responde, conmuta en caliente a la base de datos relacional sin emitir errores `500`.
* **Sincronización en Tiempo Real por Salas:** Gestor `ConnectionManager` que mapea sockets activos por `user_id`, emitiendo eventos `TASK_CREATED`, `TASK_UPDATED` y `TASK_DELETED` a todas las sesiones concurrentes de un mismo usuario.
* **Observabilidad y Trazabilidad Distribuida:** Middleware `RequestTracingMiddleware` que inyecta encabezados `X-Request-ID` (UUID4) y `X-Process-Time`, con métricas OpenMetrics expuestas en `/metrics` para scraping de Prometheus.
* **Migraciones DDL Atómicas:** Control de esquema relacional gestionado por **Alembic** con soporte de transacciones batch (`render_as_batch=True`).

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología | Propósito |
| :--- | :--- | :--- |
| **Backend Core** | FastAPI + Python 3.14 | Microservicio asíncrono tipado de alto rendimiento |
| **ORM & DDL** | SQLAlchemy 2.0 + Alembic | Mapeo objeto-relacional y control de versiones de esquema |
| **Bases de Datos** | PostgreSQL 17 / SQLite | Motores relacionales para producción y entornos de prueba |
| **Caché en Memoria**| Redis 7 + fakeredis | Reducción de latencia de lectura y testing desacoplado |
| **Seguridad** | PyJWT + Bcrypt | Tokens portadores OAuth2 y hashing unidireccional |
| **Frontend** | React 18/19 + TypeScript + Vite | SPA reactiva con tipado estricto y suscripción a WebSockets |
| **Monitoreo** | Prometheus Instrumentator | Extracción de latencias P50/P90/P99 y throughput HTTP |
| **DevOps / CI** | Docker Compose + GitHub Actions | Contenerización multi-stage y pipelines automatizados |

---

## 📂 Estructura del Repositorio

```text
mock-1/
├── .github/workflows/
│   └── ci.yml               # Pipeline CI/CD dual (Ruff, Pytest y Vite Build)
├── alembic/                 # Migraciones versionadas DDL (upgrade / downgrade)
│   ├── versions/            # Scripts de evolución del esquema relacional
│   └── env.py               # Configuración de contexto dinámico y modo batch
├── app/
│   ├── core/
│   │   ├── cache.py         # Cliente Redis con degradación elegante
│   │   ├── middleware.py    # RequestTracingMiddleware (X-Request-ID y JSON logging)
│   │   ├── security.py      # Hashing Bcrypt y firma/decodificación JWT
│   │   └── ws_manager.py    # ConnectionManager singleton para routing WebSockets
│   ├── models/              # Modelos declarativos SQLAlchemy (User, Task)
│   ├── routers/             # Endpoints modulares (/auth, /tasks, /ws)
│   ├── schemas/             # DTOs Pydantic v2 para validación estricta y serialización
│   ├── services/            # Capa de lógica de negocio desacoplada (Auth, Task, Audit)
│   ├── database.py          # Factoría de sesiones y configuración de motor SQLAlchemy
│   ├── dependencies.py      # Inyección de dependencias (CurrentUserDep, SessionDep)
│   └── main.py              # Punto de entrada, middlewares y Prometheus Instrumentator
├── frontend/
│   ├── src/
│   │   ├── services/api.ts  # Cliente de red e interceptor Bearer Token
│   │   ├── types/           # Contratos de interfaz TypeScript (Task, User, Auth)
│   │   ├── App.tsx          # Dashboard, gestión de Toasts, Modal y WebSockets
│   │   └── App.css          # Sistema de diseño reactivo y badges de estado
│   ├── Dockerfile           # Build multi-stage con Nginx Alpine
│   └── package.json
├── tests/
│   ├── conftest.py          # Fixtures aisladas en memoria RAM y cliente HTTP
│   ├── test_auth.py         # Pruebas de registro, OAuth2 y verificación de JWT
│   ├── test_cache.py        # Pruebas del patrón Cache-Aside con fakeredis
│   ├── test_observability.py# Pruebas de /metrics y propagación de Request-ID
│   ├── test_tasks.py        # Pruebas CRUD y aislamiento multi-inquilino
│   └── test_ws.py           # Pruebas de ciclo de vida y handshake WebSocket
├── docker-compose.yml       # Orquestación de infraestructura distribuida
├── Dockerfile               # Imagen del backend basada en uv y Python 3.14-slim
└── pyproject.toml           # Manifiesto de dependencias y configuración de herramientas
```

---

## 🚀 Puesta en Marcha

### Opción 1: Infraestructura Contenerizada con Docker Compose (Recomendado)

Levanta PostgreSQL 17, Redis 7, el Backend FastAPI y el Frontend en Nginx con un único comando:

```bash
# 1. Clonar el repositorio
git clone git@github.com:AndruMark/mock-1.git
cd mock-1

# 2. Construir imágenes e inicializar servicios en segundo plano
docker compose up --build -d

# 3. Aplicar migraciones de base de datos dentro del contenedor backend
docker compose exec backend alembic upgrade head
```

Acceso a servicios:
* **Frontend Web Application:** `http://localhost:5173`
* **API Interactive OpenAPI / Swagger:** `http://localhost:8000/docs`
* **Métricas OpenMetrics:** `http://localhost:8000/metrics`

---

### Opción 2: Modo Desarrollo Local

#### Requisitos Previos
* **Python 3.14+** administrado con [`uv`](https://github.com/astral-sh/uv).
* **Node.js 22+** y `npm`.

#### 1. Backend (Terminal 1)
```powershell
# Sincronizar dependencias del entorno virtual
uv sync

# Ejecutar migraciones de base de datos
uv run alembic upgrade head

# Iniciar servidor Uvicorn con recarga en caliente
uv run uvicorn app.main:app --reload --port 8000
```

#### 2. Frontend (Terminal 2)
```powershell
cd frontend
npm install
npm run dev
```

---

## 🧪 Pruebas Automatizadas y Calidad de Código

El proyecto mantiene una suite de integración con base de datos en memoria RAM (`StaticPool`) y emulación de Redis (`fakeredis`), garantizando ejecuciones herméticas e independientes de servicios externos.

```powershell
# Formateo y análisis estático con Ruff
uv run ruff check --fix .
uv run ruff format .

# Verificación estricta de tipos en el frontend
cd frontend && npm run build && cd ..

# Ejecutar suite de pruebas con reporte de cobertura
uv run pytest -v --cov=app
```

### Métricas de Cobertura Obtenidas
```text
============================== tests coverage ==============================
Name                            Stmts   Miss  Cover
---------------------------------------------------
app/core/cache.py                  46      8    83%
app/core/middleware.py             20      0   100%
app/core/security.py               21      0   100%
app/core/ws_manager.py             32      7    78%
app/database.py                    16      4    75%
app/dependencies.py                24      3    88%
app/main.py                        17      0   100%
app/models/task_model.py           13      0   100%
app/models/user_model.py           12      0   100%
app/routers/auth_router.py         24      1    96%
app/routers/task_router.py         52      2    96%
app/routers/ws_router.py           24      3    88%
app/schemas/task_schema.py         14      0   100%
app/schemas/user_schema.py         11      0   100%
app/services/audit_service.py       8      0   100%
app/services/auth_service.py       25      0   100%
app/services/task_service.py       36      2    94%
---------------------------------------------------
TOTAL                             395     30    92%
======================== 19 passed in ~3.5s ========================
```

---

## 📡 Catálogo de Endpoints Principales

| Dominio | Método | Ruta | Autenticación | Descripción |
| :--- | :---: | :--- | :---: | :--- |
| **Health** | `GET` | `/` | Pública | Verificación de estado del servicio |
| **Auth** | `POST` | `/auth/register` | Pública | Registro de nuevos usuarios con hash Bcrypt |
| **Auth** | `POST` | `/auth/login` | Pública | Obtención de Bearer Token (`x-www-form-urlencoded`) |
| **Auth** | `GET` | `/auth/me` | Bearer | Extracción del perfil del usuario activo |
| **Tasks** | `GET` | `/tasks/` | Bearer | Listado multi-tenant acelerado con Redis |
| **Tasks** | `POST` | `/tasks/` | Bearer | Creación, invalidación de caché y broadcast WebSocket |
| **Tasks** | `PUT` | `/tasks/{id}` | Bearer | Actualización parcial y sincronización en tiempo real |
| **Tasks** | `DELETE`| `/tasks/{id}` | Bearer | Eliminación física, purga de caché y emisión en vivo |
| **Realtime**| `WS` | `/ws?token={jwt}` | Query Param | Conexión WebSocket para eventos full-duplex |
| **Metrics** | `GET` | `/metrics` | Pública | Telemetría OpenMetrics para Prometheus |

---

## 📄 Licencia

Este proyecto se distribuye bajo la licencia **MIT**. Consulte el archivo `LICENSE` para más información.

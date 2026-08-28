import json
import logging
import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)

logger = logging.getLogger("api.access")


class RequestTracingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # 1. Preservar Request-ID si viene del cliente/gateway o generar un UUID4 nuevo
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        start_time = time.perf_counter()

        # 2. Procesar la petición HTTP
        response = await call_next(request)

        # 3. Calcular duración en milisegundos
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # 4. Inyectar encabezados de observabilidad en la respuesta
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{duration_ms}ms"

        # 5. Emitir log estructurado en JSON (solo para rutas de negocio)
        if not request.url.path.startswith(("/metrics", "/docs", "/openapi.json")):
            log_data = {
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            }
            logger.info(json.dumps(log_data))

        return response

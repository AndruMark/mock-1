import json
import logging
import os
from typing import Any

import redis
from redis.exceptions import RedisError

logger = logging.getLogger("cache")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

try:
    redis_client: redis.Redis | None = redis.Redis.from_url(
        REDIS_URL, decode_responses=True, socket_timeout=2
    )
    redis_client.ping()
    REDIS_AVAILABLE = True
except RedisError, OSError:
    logger.warning(
        "Redis no disponible localmente. Operando en modo directo a base de datos."
    )
    redis_client = None
    REDIS_AVAILABLE = False


class CacheService:
    @staticmethod
    def get(key: str) -> Any | None:
        if not REDIS_AVAILABLE or not redis_client:
            return None
        try:
            val = redis_client.get(key)
            return json.loads(val) if val else None
        except (RedisError, json.JSONDecodeError, TypeError) as e:
            logger.error(f"Error al leer de cache key={key}: {e}")
            return None

    @staticmethod
    def set(key: str, value: Any, ttl: int = 300) -> None:
        """Guarda un valor serializado en JSON con TTL en segundos (default 5 min)."""
        if not REDIS_AVAILABLE or not redis_client:
            return
        try:
            redis_client.set(key, json.dumps(value), ex=ttl)
        except (RedisError, TypeError) as e:
            logger.error(f"Error al escribir en cache key={key}: {e}")

    @staticmethod
    def invalidate(key: str) -> None:
        """Elimina una clave especifica de la cache."""
        if not REDIS_AVAILABLE or not redis_client:
            return
        try:
            redis_client.delete(key)
        except RedisError as e:
            logger.error(f"Error al invalidar cache key={key}: {e}")

    @staticmethod
    def invalidate_user_tasks(user_id: int) -> None:
        """Invalida todas las tareas cacheadas para un usuario especifico."""
        CacheService.invalidate(f"user:{user_id}:tasks")

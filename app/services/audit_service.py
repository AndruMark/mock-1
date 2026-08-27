import logging
from datetime import UTC, datetime

logger = logging.getLogger("audit")


class AuditService:
    @staticmethod
    def log_task_event(action: str, task_id: int, user_email: str) -> None:
        """Tarea asincrona en segundo plano para auditoria transaccional."""
        timestamp = datetime.now(UTC).isoformat()
        logger.info(
            f"[AUDIT] {timestamp} | Action: {action.upper()} | Task ID: {task_id} | User: {user_email}"
        )

"""Admin audit middleware.

Records structured audit events for every request routed through the
``/api/admin`` prefix.  The audit log captures:

* request method and path
* client IP (``request.client.host``)
* SHA-256 hash of the bearer token (when present) so operators can
  correlate events without storing plaintext credentials.

"""

from __future__ import annotations

import hashlib
import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

log = logging.getLogger(__name__)


class AdminAuditMiddleware(BaseHTTPMiddleware):
    """Audit-log every request to the admin API surface."""

    ADMIN_PREFIX = "/api/admin"

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith(self.ADMIN_PREFIX):
            ip = request.client.host if request.client else "unknown"
            auth_header = request.headers.get("authorization", "")
            token_hash = (
                hashlib.sha256(auth_header.encode()).hexdigest()
                if auth_header
                else None
            )
            log.info(
                "admin.access",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "ip": ip,
                    "token_sha256": token_hash,
                },
            )
        return await call_next(request)

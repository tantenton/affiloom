"""Centralized affiliate outbound redirect and click tracking service (M5).

Tracks outbound affiliate clicks, validates destination URLs, logs CtaClick events,
and securely redirects users to merchant deep links with proper parameters.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import CtaClick
from db.session import get_session

router = APIRouter(prefix="/api/outbound", tags=["outbound"])


@router.get("/go")
async def affiliate_redirect(
    to: str = Query(..., description="Destination URL"),
    product_id: str | None = Query(None, description="Associated product ID"),
    merchant: str | None = Query(None, description="Merchant name"),
    session: AsyncSession = Depends(get_session),
) -> Response:
    """Validate destination, log click event, and perform 302 redirect."""
    # Basic URL sanity check
    if not to.startswith(("http://", "https://")):
        return Response(content="Invalid destination URL", status_code=400)

    # Log click event if product_id provided
    if product_id:
        try:
            click = CtaClick(
                product_id=product_id,
                merchant=merchant,
                target_url=to,
            )
            session.add(click)
            await session.commit()
        except Exception:
            # Non-blocking telemetry
            pass

    return RedirectResponse(url=to, status_code=302)

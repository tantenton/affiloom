"""Shared FastAPI dependencies.

The catalog adapter is a process-lifetime singleton: a deterministic in-memory
demo. When a real partner adapter is wired in (Shopee Affiliate API, Tokopedia
Affiliate API, etc.), this is the seam to swap.
"""

from __future__ import annotations

from functools import lru_cache

from adapters.provider import DeterministicDemoAdapter, demo_items


@lru_cache(maxsize=1)
def get_catalog_adapter() -> DeterministicDemoAdapter:
    seed = {item.id: item for item in demo_items()}
    return DeterministicDemoAdapter(seed)

"""Shared route response helpers."""

from typing import Any, Dict

from fastapi import HTTPException


def require_success(result: Dict[str, Any], status_code: int = 400) -> Dict[str, Any]:
    """Raise an HTTP error when a legacy service result reports failure."""
    if not result.get("success"):
        raise HTTPException(status_code=status_code, detail=result.get("error", "Request failed"))
    return result

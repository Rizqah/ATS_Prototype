"""Persistence for recruiter screening workspaces."""

import json
import os
from datetime import datetime
from typing import Any, Dict


RECRUITER_WORKSPACES_FILE = os.path.join("careerhub_data", "recruiter_workspaces.json")


def _load() -> Dict[str, Any]:
    try:
        with open(RECRUITER_WORKSPACES_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save(data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(RECRUITER_WORKSPACES_FILE), exist_ok=True)
    with open(RECRUITER_WORKSPACES_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def get_workspace(email: str) -> Dict[str, Any]:
    return {"success": True, "workspace": _load().get(email)}


def save_workspace(email: str, workspace: Dict[str, Any]) -> Dict[str, Any]:
    data = _load()
    persisted = dict(workspace)
    persisted["recruiter_email"] = email
    persisted["updated_at"] = datetime.now().isoformat()
    data[email] = persisted
    _save(data)
    return {"success": True, "workspace": persisted}


def delete_workspace(email: str) -> Dict[str, Any]:
    data = _load()
    data.pop(email, None)
    _save(data)
    return {"success": True}


__all__ = ["delete_workspace", "get_workspace", "save_workspace"]

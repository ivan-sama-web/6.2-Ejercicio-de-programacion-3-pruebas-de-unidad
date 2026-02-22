"""JSON-based persistence layer for the Reservation System.

Provides thread-safe read/write operations for JSON data files.
Handles corrupt or missing files gracefully.

Author: Ivan Troy Santaella Martinez
"""

from __future__ import annotations

import json
import os
from typing import Any


def load_json(filepath: str) -> list[dict[str, Any]]:
    """Load a list of records from a JSON file.

    Returns an empty list when the file is missing or contains
    invalid JSON, printing a warning to the console.

    Args:
        filepath: Path to the JSON file.

    Returns:
        A list of dictionaries loaded from the file.
    """
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"[WARNING] Could not read '{filepath}': {exc}")
        return []
    if not isinstance(data, list):
        print(
            f"[WARNING] Expected a list in '{filepath}', "
            f"got {type(data).__name__}. Returning empty list."
        )
        return []
    return data


def save_json(filepath: str, data: list[dict[str, Any]]) -> None:
    """Persist a list of records to a JSON file.

    Args:
        filepath: Destination path.
        data: List of dictionaries to write.

    Raises:
        OSError: If the file cannot be written.
    """
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)

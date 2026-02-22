#!/usr/bin/env python3
"""Generate sample data for the Hotel Reservation System.

Running this script creates the ``data/`` directory with three JSON
files containing example hotels, customers, and reservations.

Usage::

    python -m reservation_system.generate_sample_data

Author: Ivan Troy Santaella Martinez
"""

from __future__ import annotations

import json
import os

SAMPLE_DIR = "data"

HOTELS = [
    {
        "hotel_id": "h001",
        "name": "Grand Palace Hotel",
        "address": "100 Main Street, New York, NY",
        "total_rooms": 50,
        "rooms_available": 48,
    },
    {
        "hotel_id": "h002",
        "name": "Ocean Breeze Resort",
        "address": "200 Beach Blvd, Miami, FL",
        "total_rooms": 30,
        "rooms_available": 30,
    },
    {
        "hotel_id": "h003",
        "name": "Mountain View Inn",
        "address": "5 Summit Road, Denver, CO",
        "total_rooms": 20,
        "rooms_available": 15,
    },
]

CUSTOMERS = [
    {
        "customer_id": "c001",
        "name": "Alice Johnson",
        "email": "alice@example.com",
    },
    {
        "customer_id": "c002",
        "name": "Bob Smith",
        "email": "bob@example.com",
    },
    {
        "customer_id": "c003",
        "name": "Carol White",
        "email": "carol@example.com",
    },
]

RESERVATIONS = [
    {
        "reservation_id": "r001",
        "customer_id": "c001",
        "hotel_id": "h001",
        "check_in": "2026-03-10",
        "check_out": "2026-03-15",
    },
    {
        "reservation_id": "r002",
        "customer_id": "c002",
        "hotel_id": "h001",
        "check_in": "2026-04-01",
        "check_out": "2026-04-05",
    },
]


def generate() -> None:
    """Write sample JSON files to the data directory."""
    os.makedirs(SAMPLE_DIR, exist_ok=True)
    for filename, records in (
        ("hotels.json", HOTELS),
        ("customers.json", CUSTOMERS),
        ("reservations.json", RESERVATIONS),
    ):
        path = os.path.join(SAMPLE_DIR, filename)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(records, fh, indent=2, ensure_ascii=False)
        print(f"  ✓ {path} ({len(records)} records)")


def main() -> None:
    """Entry point for command-line execution."""
    print("Generating sample data …")
    generate()
    print("Done.")


if __name__ == "__main__":  # pragma: no cover
    main()

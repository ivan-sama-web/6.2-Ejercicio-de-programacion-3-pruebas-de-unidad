"""Hotel Reservation System.

A lightweight, JSON-backed hotel reservation system built with
pure Python (no external dependencies).

Exports:
    Hotel, Customer, Reservation — domain models.
    HotelManager, CustomerManager, ReservationManager — CRUD managers.

Author: Ivan Troy Santaella Martinez
"""

from reservation_system.models import Customer, Hotel, Reservation
from reservation_system.managers import (
    CustomerManager,
    HotelManager,
    ReservationManager,
)

__all__ = [
    "Hotel",
    "Customer",
    "Reservation",
    "HotelManager",
    "CustomerManager",
    "ReservationManager",
]

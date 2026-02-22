"""Domain models for the Hotel Reservation System.

This module defines the core data classes: Hotel, Customer, and Reservation.
Each class supports JSON serialization/deserialization and validation.

Author: Ivan Troy Santaella Martinez
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field, asdict
from datetime import date
from typing import Any


def _generate_id() -> str:
    """Generate a unique identifier string."""
    return uuid.uuid4().hex[:12]


# ------------------------------------------------------------------
# Hotel
# ------------------------------------------------------------------
@dataclass
class Hotel:
    """Represents a hotel with rooms available for reservation.

    Attributes:
        hotel_id: Unique identifier for the hotel.
        name: Display name of the hotel.
        address: Physical address.
        total_rooms: Total number of rooms in the hotel.
        rooms_available: Number of rooms currently available.
    """

    name: str
    address: str
    total_rooms: int
    rooms_available: int = -1
    hotel_id: str = field(default_factory=_generate_id)

    def __post_init__(self) -> None:
        """Set rooms_available equal to total_rooms when not provided."""
        if self.rooms_available == -1:
            self.rooms_available = self.total_rooms
        self.validate()

    # -- validation ------------------------------------------------
    def validate(self) -> None:
        """Validate hotel data, raising *ValueError* on problems."""
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Hotel name must be a non-empty string.")
        if not isinstance(self.address, str) or not self.address.strip():
            raise ValueError("Hotel address must be a non-empty string.")
        if not isinstance(self.total_rooms, int) or self.total_rooms <= 0:
            raise ValueError("total_rooms must be a positive integer.")
        if not isinstance(self.rooms_available, int):
            raise ValueError("rooms_available must be an integer.")
        if self.rooms_available < 0:
            raise ValueError("rooms_available cannot be negative.")
        if self.rooms_available > self.total_rooms:
            raise ValueError(
                "rooms_available cannot exceed total_rooms."
            )

    # -- serialisation ---------------------------------------------
    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Hotel:
        """Construct a Hotel from a dictionary.

        Raises:
            ValueError: If required keys are missing or values invalid.
        """
        required = {"name", "address", "total_rooms", "hotel_id"}
        missing = required - data.keys()
        if missing:
            raise ValueError(f"Missing hotel fields: {missing}")
        return cls(
            hotel_id=data["hotel_id"],
            name=data["name"],
            address=data["address"],
            total_rooms=int(data["total_rooms"]),
            rooms_available=int(
                data.get("rooms_available", data["total_rooms"])
            ),
        )

    def __str__(self) -> str:
        return (
            f"Hotel({self.hotel_id}): {self.name}, {self.address} "
            f"[{self.rooms_available}/{self.total_rooms} available]"
        )


# ------------------------------------------------------------------
# Customer
# ------------------------------------------------------------------
@dataclass
class Customer:
    """Represents a customer who can make reservations.

    Attributes:
        customer_id: Unique identifier.
        name: Full name of the customer.
        email: Contact e-mail address.
    """

    name: str
    email: str
    customer_id: str = field(default_factory=_generate_id)

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        """Validate customer data."""
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Customer name must be a non-empty string.")
        if (
            not isinstance(self.email, str)
            or "@" not in self.email
            or "." not in self.email.split("@")[-1]
        ):
            raise ValueError(
                "Customer email must be a valid email address."
            )

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Customer:
        """Construct a Customer from a dictionary."""
        required = {"name", "email", "customer_id"}
        missing = required - data.keys()
        if missing:
            raise ValueError(f"Missing customer fields: {missing}")
        return cls(
            customer_id=data["customer_id"],
            name=data["name"],
            email=data["email"],
        )

    def __str__(self) -> str:
        return (
            f"Customer({self.customer_id}): {self.name} <{self.email}>"
        )


# ------------------------------------------------------------------
# Reservation
# ------------------------------------------------------------------
@dataclass
class Reservation:
    """Represents a room reservation linking a Customer to a Hotel.

    Attributes:
        reservation_id: Unique identifier.
        customer_id: ID of the customer making the reservation.
        hotel_id: ID of the hotel being booked.
        check_in: Check-in date (ISO-8601 string).
        check_out: Check-out date (ISO-8601 string).
    """

    customer_id: str
    hotel_id: str
    check_in: str
    check_out: str
    reservation_id: str = field(default_factory=_generate_id)

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        """Validate reservation data."""
        if not self.customer_id:
            raise ValueError("customer_id is required.")
        if not self.hotel_id:
            raise ValueError("hotel_id is required.")
        try:
            ci = date.fromisoformat(self.check_in)
            co = date.fromisoformat(self.check_out)
        except (ValueError, TypeError) as exc:
            raise ValueError(
                "check_in and check_out must be valid ISO dates "
                "(YYYY-MM-DD)."
            ) from exc
        if co <= ci:
            raise ValueError("check_out must be after check_in.")

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Reservation:
        """Construct a Reservation from a dictionary."""
        required = {
            "customer_id", "hotel_id",
            "check_in", "check_out", "reservation_id",
        }
        missing = required - data.keys()
        if missing:
            raise ValueError(f"Missing reservation fields: {missing}")
        return cls(
            reservation_id=data["reservation_id"],
            customer_id=data["customer_id"],
            hotel_id=data["hotel_id"],
            check_in=data["check_in"],
            check_out=data["check_out"],
        )

    def __str__(self) -> str:
        return (
            f"Reservation({self.reservation_id}): "
            f"customer={self.customer_id} hotel={self.hotel_id} "
            f"[{self.check_in} → {self.check_out}]"
        )
